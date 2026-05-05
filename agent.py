"""
Agent newsletter M&A hôtelier — Experimental Group.

Pipeline :
  1. Collecte  → 14 requêtes Tavily en parallèle
  2. Dédup     → par URL et similarité de titre
  3. Analyse   → Claude API (filtre + rédaction newsletter)
  4. Envoi     → Resend API (HTML)
"""

import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from difflib import SequenceMatcher

import anthropic
import resend
from tavily import TavilyClient
from dotenv import load_dotenv

from config import (
    QUERIES,
    TAVILY_PARAMS,
    CLAUDE_MODEL,
    CLAUDE_MAX_TOKENS,
    SYSTEM_PROMPT,
)

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Clients API ───────────────────────────────────────────────────────────────

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
resend.api_key = os.getenv("RESEND_API_KEY")

# ── Étape 1 : Collecte ────────────────────────────────────────────────────────


def _fetch_one(query: str) -> list[dict]:
    """Exécute une requête Tavily et renvoie les résultats (silencieux en cas d'erreur)."""
    try:
        response = tavily.search(
            query=query,
            max_results=TAVILY_PARAMS["max_results"],
            days=TAVILY_PARAMS["days"],
            search_depth=TAVILY_PARAMS["search_depth"],
            include_answer=False,
        )
        return response.get("results", [])
    except Exception as exc:
        log.error(f"[ERREUR] Tavily — requête échouée : {exc}")
        return []


def collect() -> list[dict]:
    """Lance les 14 requêtes en parallèle et agrège les résultats."""
    all_results: list[dict] = []

    with ThreadPoolExecutor(max_workers=len(QUERIES)) as pool:
        futures = {pool.submit(_fetch_one, q): q for q in QUERIES}
        for future in as_completed(futures):
            all_results.extend(future.result())

    log.info(f"[COLLECTE] {len(all_results)} articles bruts récupérés")
    return all_results


# ── Étape 2 : Dédoublonnage ───────────────────────────────────────────────────


def _similar(a: str, b: str) -> float:
    """Ratio de similarité entre deux chaînes (insensible à la casse)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate(articles: list[dict]) -> list[dict]:
    """Supprime les doublons par URL et par titre (seuil 80 %)."""
    seen_urls: set[str] = set()
    seen_titles: list[str] = []
    unique: list[dict] = []

    for art in articles:
        url = art.get("url", "")
        title = art.get("title", "") or ""

        if url and url in seen_urls:
            continue

        is_dup = any(_similar(title, t) > 0.8 for t in seen_titles if title and t)
        if is_dup:
            continue

        if url:
            seen_urls.add(url)
        if title:
            seen_titles.append(title)
        unique.append(art)

    log.info(f"[DÉDUP] {len(unique)} articles uniques après dédoublonnage")
    return unique


# ── Étape 3 : Analyse Claude ──────────────────────────────────────────────────


def _format_articles(articles: list[dict]) -> str:
    """Sérialise la liste d'articles en texte structuré pour Claude."""
    blocks = []
    for i, art in enumerate(articles, 1):
        content = art.get("content") or art.get("snippet") or ""
        blocks.append(
            f"[Article {i}]\n"
            f"Titre   : {art.get('title', 'N/A')}\n"
            f"URL     : {art.get('url', 'N/A')}\n"
            f"Date    : {art.get('published_date', 'N/A')}\n"
            f"Contenu : {content[:600]}"
        )
    return "\n\n".join(blocks)


def analyze(articles: list[dict]) -> str:
    """
    Envoie les articles à Claude pour filtrage et rédaction.
    Retry unique en cas d'échec.
    """
    # Limiter à 200 articles pour éviter de dépasser la fenêtre de contexte
    batch = articles[:200]
    user_msg = (
        f"Voici {len(batch)} articles collectés cette semaine :\n\n"
        f"{_format_articles(batch)}\n\n"
        "Applique les étapes FILTRE, ANALYSE et génère la NEWSLETTER."
    )

    for attempt in range(2):
        try:
            response = claude.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            newsletter = response.content[0].text
            log.info(f"[FILTRE] Analyse terminée ({len(batch)} articles analysés)")
            return newsletter
        except Exception as exc:
            if attempt == 0:
                log.warning(f"[ERREUR] Claude API — retry dans 5 s : {exc}")
                time.sleep(5)
            else:
                log.error(f"[ERREUR] Claude API — échec après retry : {exc}")
                raise


# ── Étape 4 : Envoi email ─────────────────────────────────────────────────────


def _to_html(newsletter: str) -> str:
    """Convertit le texte structuré de la newsletter en lignes HTML."""
    html_lines = []
    for raw in newsletter.splitlines():
        line = raw.strip()
        if not line:
            html_lines.append("<br>")
        elif line.startswith("──") or line.endswith("──"):
            # En-têtes de section
            title = line.replace("─", "").strip()
            html_lines.append(
                f'<p style="font-weight:bold;font-size:14px;'
                f'margin-top:20px;margin-bottom:6px;color:#111;">'
                f"{title}</p>"
            )
        elif line.startswith("- ") or line.startswith("• "):
            item = line[2:].strip()
            html_lines.append(
                f'<p style="margin:5px 0 5px 14px;font-size:13px;">{item}</p>'
            )
        else:
            html_lines.append(f'<p style="margin:4px 0;font-size:13px;">{line}</p>')
    return "\n".join(html_lines)


def build_html(newsletter: str, week: int, date_str: str) -> str:
    """Construit l'email HTML complet."""
    body = _to_html(newsletter)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:Arial,sans-serif;background:#fff;color:#1a1a1a;
             max-width:680px;margin:0 auto;padding:24px 20px;">

  <div style="border-bottom:1px solid #eee;padding-bottom:14px;margin-bottom:22px;">
    <p style="font-weight:bold;font-size:18px;margin:0;">
      M&amp;A Hôtelier &mdash; Semaine {week} &middot; {date_str}
    </p>
  </div>

  <div style="line-height:1.75;">
    {body}
  </div>

  <div style="border-top:1px solid #eee;margin-top:32px;padding-top:12px;">
    <p style="color:#aaa;font-size:11px;margin:0;">
      Experimental Group &middot; Généré automatiquement &middot; {date_str}
    </p>
  </div>

</body>
</html>"""


def send(html: str, week: int, date_str: str) -> None:
    """Envoie la newsletter via Resend."""
    email_from = os.getenv("EMAIL_FROM", "newsletter@experimental.com")
    raw_to = os.getenv("EMAIL_TO", "")

    if not raw_to:
        log.error("[ERREUR] Variable EMAIL_TO non définie dans .env")
        return

    recipients = [addr.strip() for addr in raw_to.split(",") if addr.strip()]

    params = {
        "from": email_from,
        "to": recipients,
        "subject": f"M&A Hôtelier — Semaine {week} · {date_str}",
        "html": html,
    }

    resend.Emails.send(params)
    log.info(f"[EMAIL] Newsletter envoyée à {len(recipients)} destinataire(s)")


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    now = datetime.now()
    week = now.isocalendar()[1]
    date_str = now.strftime("%d/%m/%Y")

    log.info(f"=== Newsletter M&A Hôtelier — Semaine {week} — {date_str} ===")

    # 1. Collecte
    raw = collect()

    # 2. Dédoublonnage
    unique = deduplicate(raw)

    if not unique:
        log.error("[ERREUR] Aucun article disponible. Vérifiez la clé TAVILY_API_KEY.")
        return

    # 3. Analyse
    newsletter = analyze(unique)

    # 4. Email
    html = build_html(newsletter, week, date_str)
    send(html, week, date_str)

    log.info("=== Terminé avec succès ===")


if __name__ == "__main__":
    main()

"""
Agent newsletter M&A hôtelier — Experimental Group.

Pipeline :
  1. Collecte  → 14 requêtes Tavily en parallèle
  2. Dédup     → par URL et similarité de titre
  3. Analyse   → Claude API (filtre + rédaction newsletter)
  4. Envoi     → Resend API (HTML)

Options :
  --test  : mode test sans appels API réels (mocks Tavily, Claude, Resend)
"""

import os
import sys
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

TEST_MODE = "--test" in sys.argv

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Clients API ───────────────────────────────────────────────────────────────

if not TEST_MODE:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resend.api_key = os.getenv("RESEND_API_KEY")

# ── Données mock (mode test) ──────────────────────────────────────────────────

_MOCK_ARTICLES = [
    {"title": "Accor acquiert 5 hôtels lifestyle en Espagne pour 280 M€", "url": "https://example.com/accor-espagne", "published_date": "2026-05-01", "content": "Accor finalise l'acquisition de cinq établissements lifestyle sur la côte ibérique dans le cadre de son plan d'expansion méditerranéen."},
    {"title": "Marriott rachète la chaîne boutique Nomad Collection", "url": "https://example.com/marriott-nomad", "published_date": "2026-05-02", "content": "La transaction valorise Nomad Collection à 420 M$ et renforce le portefeuille lifestyle de Marriott en Europe du Sud."},
    {"title": "IHG envisage une cession de 12 hôtels Holiday Inn en Europe centrale", "url": "https://example.com/ihg-cession", "published_date": "2026-05-02", "content": "IHG explore une vente d'actifs midscale pour se recentrer sur ses marques premium Voco et Kimpton."},
    {"title": "Blackstone lève 2,1 Md€ pour un nouveau fonds hôtelier lifestyle", "url": "https://example.com/blackstone-fonds", "published_date": "2026-04-30", "content": "Le fonds ciblera des hôtels indépendants 4 et 5 étoiles en zone urbaine européenne avec une thèse value-add."},
    {"title": "Hilton signe un accord de management pour 3 hôtels LXR à Paris", "url": "https://example.com/hilton-lxr-paris", "published_date": "2026-04-29", "content": "LXR Hotels & Resorts confirme son implantation parisienne avec trois signatures dans le Triangle d'Or."},
    {"title": "Accor va ouvrir des hôtels lifestyle en Espagne", "url": "https://example.com/accor-espagne-2", "published_date": "2026-05-01", "content": "Article doublon — même information sur l'expansion méditerranéenne d'Accor."},
    {"title": "Groupe Barrière cède deux casinos-hôtels à un fonds souverain qatari", "url": "https://example.com/barriere-qatar", "published_date": "2026-04-28", "content": "La cession s'inscrit dans la stratégie asset-light du groupe français, valorisant les actifs à 310 M€."},
    {"title": "Pandox AB acquiert un portefeuille de 8 hôtels Scandic en Scandinavie", "url": "https://example.com/pandox-scandic", "published_date": "2026-04-27", "content": "La transaction, valorisée à 640 M€, consolide la position de Pandox comme premier investisseur hôtelier nordique."},
    {"title": "Minor Hotels rachète NH Hotel Group — point sur l'intégration 2026", "url": "https://example.com/minor-nh-integration", "published_date": "2026-05-03", "content": "Minor Hotels présente l'état d'avancement de l'intégration NH et annonce 15 conversions de marque supplémentaires."},
    {"title": "Covivio cède un portefeuille d'hôtels ibis à La Salle Investment", "url": "https://example.com/covivio-ibis", "published_date": "2026-04-26", "content": "La transaction porte sur 22 établissements budget en France et Allemagne pour une valeur totale de 480 M€."},
    {"title": "Hyatt étend sa présence lifestyle via l'acquisition d'une marque espagnole", "url": "https://example.com/hyatt-espagne-lifestyle", "published_date": "2026-05-01", "content": "Hyatt confirme le rachat de la marque lifestyle ibérique Alma Hotels pour environ 195 M€."},
    {"title": "Starwood Capital Group entre en exclusivité sur 4 palaces parisiens", "url": "https://example.com/starwood-paris", "published_date": "2026-04-25", "content": "Les quatre actifs, valorisés à 1,2 Md€, figurent parmi les plus emblématiques du segment luxe à Paris."},
    {"title": "Club Med finalise son expansion en Europe du Nord avec 3 nouvelles adresses", "url": "https://example.com/clubmed-nord", "published_date": "2026-04-24", "content": "Club Med ouvre à Amsterdam, Copenhague et Stockholm dans le cadre de sa stratégie premium urbaine."},
    {"title": "Wyndham Hotels lance un plan de conversion de 200 franchises en Europe", "url": "https://example.com/wyndham-europe", "published_date": "2026-04-23", "content": "Le groupe américain vise la conversion d'hôtels indépendants 3 étoiles sous sa bannière Wyndham Garden."},
    {"title": "Foncière des Murs acquiert un hôtel Marriott à Lyon pour 95 M€", "url": "https://example.com/fdm-lyon", "published_date": "2026-04-22", "content": "La foncière spécialisée renforce son portefeuille hôtelier français avec cette acquisition en sale & leaseback."},
    {"title": "Kempinski signe 6 lettres d'intention pour des ouvertures en Méditerranée", "url": "https://example.com/kempinski-med", "published_date": "2026-04-21", "content": "Le groupe suisse accélère son développement en Grèce, Italie et Croatie avec des hôtels resort de luxe."},
    {"title": "Radisson Hotel Group finalise la cession de son siège européen à Bruxelles", "url": "https://example.com/radisson-bruxelles", "published_date": "2026-04-20", "content": "Dans le cadre d'une opération sale & leaseback, Radisson cède son siège bruxellois pour 75 M€."},
    {"title": "Meliá Hotels rachète un resort 5 étoiles aux Canaries pour 160 M€", "url": "https://example.com/melia-canaries", "published_date": "2026-04-19", "content": "Meliá renforce son ancrage dans les îles Canaries avec cette acquisition stratégique dans le segment luxe resort."},
    {"title": "Investors signal growing appetite for European luxury hotel assets", "url": "https://example.com/luxury-appetite", "published_date": "2026-05-04", "content": "European luxury hotel transaction volume rose 34% in Q1 2026 versus prior year, driven by US and Gulf sovereign wealth funds."},
    {"title": "Accor acquiert des hôtels lifestyle en Espagne — communiqué officiel", "url": "https://example.com/accor-espagne-3", "published_date": "2026-05-01", "content": "Troisième doublon sur l'opération Accor Méditerranée pour tester le déduplication."},
]

_MOCK_NEWSLETTER = """── DEALS & TRANSACTIONS ──

- Accor finalise l'acquisition de 5 hôtels lifestyle en Espagne pour 280 M€, renforçant sa présence méditerranéenne.
- Marriott rachète Nomad Collection (420 M$), consolidant son portefeuille lifestyle en Europe du Sud.
- Starwood Capital Group entre en exclusivité sur 4 palaces parisiens valorisés à 1,2 Md€.
- Pandox AB acquiert 8 hôtels Scandic pour 640 M€, devenant le premier investisseur hôtelier nordique.
- Covivio cède 22 hôtels ibis à La Salle Investment pour 480 M€ dans une logique asset-light.

── SIGNAUX MARCHÉ & FLUX DE CAPITAL ──

- Blackstone lève 2,1 Md€ pour un fonds value-add ciblant des hôtels lifestyle urbains européens.
- Les volumes de transactions hôtelières luxe en Europe progressent de +34 % en T1 2026 vs N-1.
- Les fonds souverains du Golfe et les family offices américains dominent les flux entrants sur le segment palace.
- IHG explore la cession de 12 Holiday Inn en Europe centrale pour se recentrer sur Voco et Kimpton.

── MOUVEMENTS OPÉRATEURS ──

- Hyatt acquiert Alma Hotels (Espagne) pour ~195 M€ et accélère sur le lifestyle ibérique.
- Minor Hotels présente l'avancement de l'intégration NH : 15 conversions de marque supplémentaires annoncées.
- Hilton signe 3 hôtels LXR dans le Triangle d'Or parisien — signal fort sur le luxe indépendant.
- Wyndham lance un plan de conversion de 200 franchises indépendantes en Europe sous Wyndham Garden.
- Kempinski signe 6 LOI pour des resorts luxe en Grèce, Italie et Croatie.

── RADAR EXPERIMENTAL GROUP ──

- Opportunité à surveiller : le pipeline de cessions IHG (midscale Europe centrale) pourrait libérer des actifs repositionnables lifestyle.
- Le closing Starwood/palaces parisiens confirme la prime de liquidité sur les actifs trophy — cohérent avec nos marchés cibles.
- Le fonds Blackstone value-add lifestyle est un compétiteur direct sur les acquisitions <300 M€ en zone urbaine.
- Meliá acquiert un resort 5 étoiles aux Canaries (160 M€) — marché expansion pertinent pour notre pipeline medium-term."""

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
    if TEST_MODE:
        log.info(f"[COLLECTE] {len(_MOCK_ARTICLES)} articles bruts récupérés [MODE TEST]")
        return list(_MOCK_ARTICLES)

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
    if TEST_MODE:
        log.info(f"[FILTRE] Analyse terminée ({len(articles)} articles analysés) [MODE TEST]")
        return _MOCK_NEWSLETTER

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
    raw_to = os.getenv("EMAIL_TO", "test@experimental.com")

    if TEST_MODE:
        recipients = [addr.strip() for addr in raw_to.split(",") if addr.strip()] or ["test@experimental.com"]
        log.info(f"[EMAIL] Newsletter envoyée à {len(recipients)} destinataire(s) [MODE TEST — non envoyée]")
        print("\n" + "─" * 60)
        print("APERÇU HTML (extrait) :")
        print("─" * 60)
        print(html[:800] + "\n[… HTML tronqué pour l'aperçu …]")
        print("─" * 60)
        return

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

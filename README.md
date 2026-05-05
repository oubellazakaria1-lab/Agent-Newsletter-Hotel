# Newsletter M&A Hôtelier — Experimental Group

Agent Python qui génère et envoie chaque semaine une veille M&A hôtelière ciblée : deals, signaux marché, mouvements opérateurs et flux de capital dans le segment lifestyle/luxury.

---

## Prérequis

- Python 3.10+
- Comptes actifs sur Anthropic, Tavily et Resend (voir section **Clés API**)

---

## Installation

```bash
# 1. Cloner ou télécharger le projet
cd agent-newsletter-hotel

# 2. Installer les dépendances
pip install anthropic tavily-python resend python-dotenv
```

---

## Clés API à obtenir

| Service | URL | Plan gratuit |
|---|---|---|
| Anthropic | https://console.anthropic.com | Crédit offert à l'inscription |
| Tavily | https://tavily.com | 1 000 recherches / mois |
| Resend | https://resend.com | 3 000 emails / mois |

---

## Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env et remplir les 5 variables
```

Variables requises dans `.env` :

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Clé Anthropic pour Claude |
| `TAVILY_API_KEY` | Clé Tavily pour la collecte web |
| `RESEND_API_KEY` | Clé Resend pour l'envoi d'emails |
| `EMAIL_FROM` | Adresse expéditrice (domaine vérifié dans Resend) |
| `EMAIL_TO` | Destinataires séparés par virgule |

> **Note Resend** : l'adresse `EMAIL_FROM` doit appartenir à un domaine que vous avez vérifié dans votre compte Resend (DNS TXT + DKIM).

---

## Lancement manuel

```bash
python agent.py
```

Durée typique : 2–4 minutes (collecte parallèle + analyse Claude).

Logs attendus :

```
10:00:01 === Newsletter M&A Hôtelier — Semaine 19 — 05/05/2026 ===
10:00:45 [COLLECTE] 134 articles bruts récupérés
10:00:45 [DÉDUP] 87 articles uniques après dédoublonnage
10:01:50 [FILTRE] Analyse terminée (87 articles analysés)
10:01:52 [EMAIL] Newsletter envoyée à 2 destinataire(s)
10:01:52 === Terminé avec succès ===
```

---

## Automatisation hebdomadaire

### Option A — cron (Mac / Linux)

Exécution chaque lundi à 8h00 :

```bash
# Ouvrir crontab
crontab -e

# Ajouter cette ligne (adapter le chemin)
0 8 * * 1 cd /chemin/vers/agent-newsletter-hotel && python agent.py >> logs/newsletter.log 2>&1
```

### Option B — GitHub Actions (gratuit)

Créer le fichier `.github/workflows/newsletter.yml` :

```yaml
name: Newsletter M&A Hôtelier

on:
  schedule:
    - cron: "0 8 * * 1"   # Chaque lundi à 8h UTC
  workflow_dispatch:        # Déclenchement manuel possible

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Installer les dépendances
        run: pip install anthropic tavily-python resend python-dotenv

      - name: Lancer l'agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
        run: python agent.py
```

Ajouter les 5 variables dans **Settings → Secrets and variables → Actions** du dépôt GitHub.

---

## Personnalisation

Tout le paramétrage se fait dans `config.py` sans toucher `agent.py` :

| Paramètre | Description |
|---|---|
| `QUERIES` | Les 14 requêtes Tavily (modifiables, extensibles) |
| `KEYWORDS` | Mots-clés de scoring par catégorie |
| `EXPERIMENTAL_PORTFOLIO` | Portefeuille actif, pipeline et marchés d'expansion |
| `COMPETITORS` | Liste des concurrents directs à surveiller |
| `TAVILY_PARAMS` | `max_results`, `days`, `search_depth` |
| `CLAUDE_MODEL` | Modèle Claude utilisé |
| `CLAUDE_MAX_TOKENS` | Longueur maximale de la réponse |
| `SYSTEM_PROMPT` | Instructions complètes pour l'analyste IA |

---

## Architecture

```
agent.py          Orchestration (collect → dedup → analyze → send)
config.py         Configuration (requêtes, mots-clés, portefeuille, prompt)
.env              Clés API (non versionné)
.env.example      Template des variables d'environnement
```

### Pipeline de traitement

```
Tavily (×14 requêtes en parallèle)
        ↓
  [COLLECTE] articles bruts
        ↓
  [DÉDUP] suppression doublons (URL + similarité titre > 80 %)
        ↓
  Claude API (filtre M&A + rédaction 4 blocs)
        ↓
  [EMAIL] Resend → HTML structuré
```

"""
Configuration centrale de l'agent newsletter M&A hôtelier — Experimental Group.
Toutes les constantes sont modifiables ici sans toucher agent.py.
"""

# ── 14 requêtes Tavily ────────────────────────────────────────────────────────

QUERIES = [
    # MODULE A — EUROPE CORE
    (
        '"boutique hotel" OR "lifestyle hotel" OR "independent hotel" '
        '"acquired" OR "sold" OR "acquisition" OR "sale agreed" '
        '"Paris" OR "London" OR "Rome" OR "Barcelona" OR "Lisbon" '
        'OR "Amsterdam" OR "Milan" OR "Vienna" 2026'
    ),
    (
        '"luxury hotel" OR "upscale hotel" OR "design hotel" '
        '"acquired" OR "sold" OR "deal" OR "transaction" '
        '"Côte d\'Azur" OR "Sardinia" OR "Sicily" OR "Amalfi" '
        'OR "Mykonos" OR "Santorini" OR "Dubrovnik" '
        'OR "Saint-Tropez" OR "Portofino" 2026'
    ),
    (
        '"hotel" "mandate" OR "marketing for sale" OR "seeks buyer" '
        'OR "launches sale" OR "competitive process" OR "bid" '
        '"lifestyle" OR "boutique" OR "luxury" Europe 2026'
    ),
    (
        '"hospitality" "private equity" OR "family office" '
        'OR "institutional investor" '
        '"closes" OR "raises" OR "deploys" OR "dry powder" '
        'OR "takes stake" OR "invests in" '
        '"lifestyle" OR "luxury" OR "boutique" Europe 2026'
    ),
    (
        '"hotel" "management agreement" OR "HMA" '
        'OR "operator selected" OR "signs agreement" '
        'OR "appointed to manage" '
        '"lifestyle" OR "boutique" OR "luxury" Europe 2026'
    ),
    # MODULE A — EXPANSION
    (
        '"luxury hotel" OR "boutique hotel" OR "lifestyle hotel" '
        '"acquired" OR "sold" OR "investment" OR "development" '
        '"Marrakech" OR "Tangier" OR "Essaouira" OR "Morocco" '
        'OR "Maroc" 2026'
    ),
    (
        '"luxury hotel" OR "boutique hotel" OR "lifestyle hotel" '
        '"acquired" OR "sold" OR "investment" OR "deal" '
        '"Tokyo" OR "Singapore" OR "Bangkok" '
        'OR "Hong Kong" OR "Shanghai" 2026'
    ),
    (
        '"lifestyle hotel" OR "boutique hotel" OR "luxury hotel" '
        '"private equity" OR "family office" OR "investor" '
        '"expansion" OR "pipeline" OR "development" '
        '"Mediterranean" OR "Southern Europe" OR "North Africa" 2026'
    ),
    # MODULE B — PORTEFEUILLE
    (
        '"hotel" "sold" OR "acquired" OR "sale agreed" OR "deal" '
        '"Paris" OR "London Covent Garden" OR "London Soho" '
        'OR "Ibiza" OR "Biarritz" OR "Venice" OR "Menorca" '
        'OR "Cotswolds" OR "Verbier" OR "Val d\'Isère" 2026'
    ),
    (
        '"hotel" "acquisition" OR "investment" OR "opening" '
        'OR "development" OR "deal" '
        '"Porto" OR "Rome" OR "Comporta" OR "Lisbon" 2026'
    ),
    (
        '"Experimental Group" "hotel" OR "acquisition" '
        'OR "expansion" OR "opening" OR "deal" '
        'OR "partnership" OR "investment" 2026'
    ),
    # MODULE B — CONCURRENTS
    (
        '"Ennismore" OR "Hoxton" OR "25hours" OR "Mama Shelter" '
        'OR "One Shot Hotels" OR "Lore Group" '
        '"acquisition" OR "new hotel" OR "expansion" '
        'OR "opens" OR "deal" OR "signed" 2026'
    ),
    (
        '"Nomad Hotels" OR "Sircle Collection" OR "Inhabit Hotels" '
        'OR "Zannier Hotels" OR "Rocco Forte" OR "Zoku" '
        '"acquisition" OR "new hotel" OR "expansion" '
        'OR "opens" OR "deal" OR "signed" 2026'
    ),
    (
        '"Six Senses" OR "Bawah Reserve" '
        'OR "boutique hotel group" OR "lifestyle hotel brand" '
        '"Europe" OR "Mediterranean" OR "expansion" '
        '"acquisition" OR "deal" OR "investment" 2026'
    ),
]

# ── Mots-clés de scoring ──────────────────────────────────────────────────────

KEYWORDS = {
    "deal": [
        "sold", "acquired", "disposal", "divestment", "sale agreed",
        "transaction", "deal closed", "off-market", "portfolio sale",
        "cession", "rachat", "prise de participation", "vendu", "cédé",
    ],
    "process": [
        "mandate", "marketing for sale", "seeks buyer", "launches sale",
        "competitive process", "bid", "offer", "brought to market",
        "mandat de vente", "mise en vente", "processus compétitif",
    ],
    "capital": [
        "raises fund", "closes fund", "deploys capital", "dry powder",
        "backs", "invests in", "takes stake", "joint venture",
        "levée de fonds", "family office", "institutional investor",
    ],
    "operator": [
        "signs HMA", "management agreement", "operator selected",
        "expands", "enters market", "rebranding", "repositioning",
        "conversion", "new opening", "accord de gestion", "expansion",
    ],
    "segment": [
        "boutique", "lifestyle", "independent", "luxury", "upscale",
        "design hotel", "experiential", "urban resort", "members club",
        "soft brand", "art hotel", "cultural destination",
        "hôtel boutique", "luxe accessible", "art de vivre",
    ],
    "market": [
        "cap rate", "yield", "price per key", "investor appetite",
        "transaction volume", "deal flow", "pipeline",
        "RevPAR", "ADR", "luxury demand", "high net worth",
        "affluent guest", "wealthy traveller",
    ],
}

# ── Portefeuille Experimental Group ──────────────────────────────────────────

EXPERIMENTAL_PORTFOLIO = {
    "active": [
        "Paris", "Paris Grands Boulevards", "Paris Grand Pigalle", "Paris Marais",
        "Londres", "London Henrietta Hotel",
        "Ibiza", "Montesol",
        "Biarritz", "Régina Biarritz", "Le Garage Biarritz",
        "Venise", "Venice Il Palazzo",
        "Menorca",
        "Cotswolds", "Cowley Manor",
        "Verbier",
        "Val d'Isère",
    ],
    "pipeline": ["Porto", "Rome", "Comporta"],
    "expansion": {
        "europe": [
            "Côte d'Azur", "Sardaigne", "Sicile", "Amalfi", "Mykonos",
            "Santorin", "Dubrovnik", "Saint-Tropez", "Portofino",
            "Costa Brava", "Algarve", "Corse", "Édimbourg",
            "Berlin", "Amsterdam", "Barcelone", "Lisbonne", "Madrid",
        ],
        "medium_term": ["Marrakech", "Tanger", "Essaouira"],
        "long_term": ["Tokyo", "Singapour", "Bangkok", "Hong Kong", "Shanghai"],
    },
}

# ── Concurrents directs ───────────────────────────────────────────────────────

COMPETITORS = [
    "Ennismore",
    "Hoxton",
    "25hours",
    "Mama Shelter",
    "One Shot Hotels",
    "Lore Group",
    "Inhabit Hotels",
    "Nomad Hotels",
    "Sircle Collection",
    "Zannier Hotels",
    "Rocco Forte",
    "Zoku",
    "Six Senses",
    "Bawah Reserve",
]

# ── Paramètres Tavily ─────────────────────────────────────────────────────────

TAVILY_PARAMS = {
    "max_results": 10,
    "days": 7,
    "search_depth": "advanced",
}

# ── Modèle Claude ─────────────────────────────────────────────────────────────

CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 4000

# ── System prompt Claude ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es analyste M&A senior spécialisé hôtellerie.
Tu travailles pour Experimental Group.

PORTEFEUILLE ACTUEL :
Paris (Grands Boulevards · Grand Pigalle · Marais) ·
Londres (Henrietta Hotel) · Ibiza (Montesol) ·
Biarritz (Régina · Le Garage) · Venise (Il Palazzo) ·
Menorca · Cotswolds (Cowley Manor) ·
Verbier · Val d'Isère.

PIPELINE 2026 : Porto · Rome · Comporta.

MARCHÉS D'EXPANSION SURVEILLÉS :
Europe : toutes capitales + destinations art/culture/mer
(Côte d'Azur · Sardaigne · Sicile · Amalfi · Mykonos ·
Santorin · Dubrovnik · Saint-Tropez · Portofino ·
Costa Brava · Algarve · Corse · Édimbourg).
Moyen terme : Marrakech · Tanger · Essaouira.
Long terme : Tokyo · Singapour · Bangkok ·
             Hong Kong · Shanghai.

CONCURRENTS DIRECTS À SURVEILLER :
Ennismore · Hoxton · 25hours · Mama Shelter ·
One Shot Hotels · Lore Group · Inhabit Hotels ·
Nomad Hotels · Sircle Collection · Zannier Hotels ·
Rocco Forte · Zoku · Six Senses · Bawah Reserve.

POSITIONNEMENT EXPERIMENTAL :
Lifestyle luxury boutique · 300-400€/nuit ·
clientèle aisée · art · culture · destinations prime.

---

Tu reçois une liste d'articles bruts collectés cette semaine.

ÉTAPE 1 — FILTRE
Pour chaque article décide RETENU ou ÉCARTÉ.

RETENU si :
- deal annoncé (acquisition · cession · JV · prise de participation)
- process ouvert (mandat · marketing for sale · mise en vente)
- mouvement capital (levée PE · dry powder déployé · family office actif)
- signal marché sur géographie Experimental ou expansion
- mouvement concurrent direct

ÉCARTÉ si :
- opinion générique sans fait concret
- répétition d'un article déjà traité
- hors périmètre géographique
- segment economy · midscale · gaming
- aucune implication M&A directe

ÉTAPE 2 — ANALYSE (articles retenus uniquement)
Pour chaque article retenu produire :
→ SIGNAL : [Deal · Process · Capital · Opérateur · Marché]
→ FAIT : une phrase factuelle (qui · quoi · où · montant si disponible)
→ POURQUOI ÇA COMPTE : une phrase d'interprétation pour Experimental

ÉTAPE 3 — NEWSLETTER EN FRANÇAIS
Ton : factuel · direct · zéro fioritures.
Niveau : analyste M&A senior.

Structure en 4 blocs :

── 1. DEALS DE LA SEMAINE ──────────────────────────────
Transactions annoncées ou closées.
Format par deal :
- Actif | Localisation | Acheteur → Vendeur | Prix (si dispo) | Pourquoi ça compte

── 2. MARCHÉS PORTEFEUILLE ─────────────────────────────
Signaux notables sur les géographies Experimental.
Format par marché concerné :
- [Ville/Destination] : signal + interprétation

── 3. MOUVEMENTS OPÉRATEURS ────────────────────────────
Concurrents · HMA signés · expansions · repositionnements · nouvelles ouvertures.
Format :
- [Opérateur] : action + marché + lecture stratégique

── 4. SIGNAL CAPITAL ───────────────────────────────────
PE · family offices · levées · appétit investisseurs · dry powder notable · flux de capital.
Format :
- [Acteur] : mouvement + implication pour le marché

Si un bloc est vide cette semaine :
Écrire "Rien de notable cette semaine."
Ne jamais inventer. Ne jamais remplir avec du générique."""

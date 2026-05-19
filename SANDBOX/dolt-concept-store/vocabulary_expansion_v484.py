# -*- coding: utf-8 -*-
"""
vocabulary_expansion_v484.py — v4.8.4 vocabulary expansion
═══════════════════════════════════════════════════════════
Date:   2026-02-21
Focus:  Massive EN base-form injection + FI/IT/ES/FR/DE/EO remaining gaps

v4.8.4 targets a structural EN weakness: many common English base words
(eye, drink, win, express, steal, wife, etc.) were never assigned to any
atom, so their inflected forms (eyelids, drank, won, expressed, stole,
wives) could not resolve via Snowball stemming (Strategy 8). Adding the
base form automatically covers all inflections.

Also targets remaining high-frequency uncovered words in other languages.
"""

# ══════════════════════════════════════════════════════════════════════════════
# KEYWORDS — {atom: {lang: [words]}}
# ══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V484 = {
    # ─── COMMUNICATION ────────────────────────────────────────────────────
    "COMMUNICATION": {
        "en": [
            # Base forms for inflected uncovered words
            "express", "expression", "expressed", "expressing",
            "inspire", "inspired", "inspiration",
            "assist", "assistance", "assisted",
            "excuse", "excused", "excusing",
            "render", "rendered", "rendering",
            "introduce", "introduced", "introduction",
            "proceed", "proceeded", "proceeding",
            "conclude", "concluded", "necessity",
            "necessarily", "necessary",
            "sonnets", "sonnet", "verse", "verses",
            "poets", "poet", "poetry",
            "opera", "operas",
            "military", "royal",
            "urban", "suburb", "suburban",
            "universe", "universal",
            "sunday", "virgin",
        ],
        "fr": [
            "enlever", "enlevé", "enlève",
            "publiques", "publique",
            "fierté", "fier", "fière",
            "pénétrer", "pénétré", "pénètre",
            "lointain", "lointaine", "lointains",
            "conclut", "conclure",
            "poètes", "poète", "poésie",
            "convulsions", "convulsion",
            "politesses", "politesse",
            "perçante", "perçant",
            "banquier", "banquiers",
        ],
        "it": [
            "forza", "forzare", "forzato",
            "delicatezza", "delicato", "delicate",
            "prego", "pregare",
            "facciamo", "faccia",
            "motto", "motti",
            "archi", "arco",
            "trarre", "tratto",
        ],
        "es": [
            "discreta", "discreto", "discreción",
            "convulsiones", "convulsión",
            "urbanidad", "urbano",
            "juramento", "jurar", "juró",
            "merecen", "merecer", "merecía",
            "poetas", "poeta", "poesía",
            "ingleses", "inglés",
        ],
        "de": [
            "entgegnete", "entgegnen",
            "kunststücke", "kunststück",
            "anzureden", "anreden",
            "beachtete", "beachten",
            "anzubieten", "anbieten",
            "begreife", "begreifen", "begriff",
        ],
        "fi": [
            "suvaitsette", "suvaitsen",
            "lahjoittanut", "lahjoittaa",
            "toimittivat", "toimittaa",
        ],
        "eo": [
            "versajxoj", "versajxo",
            "konversaciojn", "konversacio",
            "kritikojn", "kritiko",
            "admonon", "admono", "admoni",
        ],
    },

    # ─── AGENT ─────────────────────────────────────────────────────────────
    "AGENT": {
        "en": [
            "wife", "wives",
            "gauntlet", "gauntlets",
            "mulattoes", "mulatto",
            "biscayner",
            "tawnies",
        ],
        "fr": [
            "mulâtres", "mulâtre",
            "biscayen", "biscayens",
            "eunuques", "eunuque",
            "janissaires", "janissaire",
        ],
        "it": [
            "stampatori", "stampatore",
            "persuasa", "persuaso",
        ],
        "es": [
            "mulatos", "mulato",
            "genízaros", "genízaro",
            "eunucos", "eunuco",
            "nosotras",
            "ama", "amo",
            "clérigos", "clérigo",
        ],
        "de": [
            "mama",
            "frettchen",
            "unke",
            "esel",
        ],
        "fi": [
            "poloinen",
        ],
        "eo": [
            "jxurintaro",
            "frenezuloj", "frenezulo",
            "bretoj", "breto",
        ],
    },

    # ─── LIEU ──────────────────────────────────────────────────────────────
    "LIEU": {
        "en": [
            "mount", "mounts",
            "hedge", "hedges",
        ],
        "fr": [
            "gazon", "gazons",
            "sérail", "sérails",
            "tillac",
        ],
        "it": [
            "palchetto", "palchi",
        ],
        "es": [
            "pradera", "praderas",
            "cuna", "cunas",
            "serrallo",
            "inmediaciones",
        ],
        "de": [
            "erzbischof",
            "zuckerplätzchen",
            "glaceehandschuhe",
            "draußen",
        ],
        "fi": [
            "lissabonin",
            "inkvisitsionin",
            "hirressä",
        ],
        "eo": [
            "fokeno",
            "kilometroj", "kilometro",
        ],
    },

    # ─── MOUVEMENT ─────────────────────────────────────────────────────────
    "MOUVEMENT": {
        "en": [
            "stole", "steal", "stolen",
            "ripped", "rip", "ripping",
            "picking", "pick", "picked",
            "food", "foods",
            "drank", "drink", "drunk", "drinking",
            "won", "win", "winning", "winner",
            "bark", "barking", "barked",
            "wild", "wildly",
            "nibbling", "nibble", "nibbled",
        ],
        "fr": [
            "jeux", "jeu",
            "essuyé", "essuyer",
            "pommade", "pommades",
            "pistoles", "pistole",
            "impitoyablement",
        ],
        "it": [
            "faranno", "farà", "faremo",
            "mosse", "mossa", "mosso",
            "avrei", "avrò", "avremmo",
            "ebbi", "ebbe", "ebbero",
            "scambiate", "scambiare", "scambio",
            "farne", "farlo", "farci",
            "glielo", "gliela",
            "inforcò", "inforcare",
        ],
        "es": [
            "sirviéron", "servir",
            "satisfizo", "satisfacer",
            "conduxéron", "conducir",
            "echáron", "echar",
            "muriéron", "morir",
            "esquadra", "escuadra",
            "víveres",
            "esmeraldas",
        ],
        "de": [
            "gewonnen", "gewinnen",
            "entfernten", "entfernen", "entfernt",
            "bücken", "bückte",
            "wendend", "wenden",
            "gestemmt", "stemmen",
            "faßte", "fassen",
            "aufgaben", "aufgabe",
        ],
        "fi": [
            "aikoi", "aikoa",
            "tiuskasi", "tiuskata",
            "irvisti", "irvistää",
            "röhki", "röhkiä",
            "hankki", "hankkia",
            "saavutti", "saavuttaa",
            "herätti", "herättää",
            "punastui", "punastua",
            "pääsisi", "päästä",
            "varastaa", "varastaminen",
            "aivastaa", "aivastus",
        ],
        "eo": [
            "kondukis", "konduki",
            "kondukas",
            "demetis", "demeti",
            "vetkuro",
            "tralego",
        ],
    },

    # ─── PERCEPTION ────────────────────────────────────────────────────────
    "PERCEPTION": {
        "en": [
            "eye", "eyes", "eyelids", "eyelid",
            "blushed", "blush", "blushing",
            "convulsions", "convulsion",
        ],
        "fr": [
            "lunettes", "lunette",
            "poil", "poils",
        ],
        "it": [
            "quanta", "quanto", "quanti",
            "dì", "diro",
            "studiai", "studiare",
            "conoscesse", "conoscere",
            "attimo", "attimi",
            "senape",
            "tromba", "trombe",
        ],
        "es": [
            "beldad", "belleza",
            "friolera",
            "sosiego",
        ],
        "de": [
            "nützt", "nützen",
            "mäuschen", "mäuslein",
            "blaß", "blass",
            "unbehaglich", "behagen",
            "unwillig", "unwille",
            "betrübt", "betrüben",
        ],
        "fi": [
            "kimeällä", "kimeä",
            "pelokkaasti", "pelokas",
            "kyllästynyt", "kyllästyä",
            "rakkaus", "rakastaa",
        ],
        "eo": [
            "gxemante", "gxemi",
            "subpremita", "subpremi",
            "kruela", "kruelo",
        ],
    },

    # ─── COGNITION ─────────────────────────────────────────────────────────
    "COGNITION": {
        "en": [
            "ma",
        ],
        "fr": [
            "chacune", "chacun",
            "fussions", "fût", "sût",
            "n'ayez",
        ],
        "it": [
            "nol",
            "teco",
            "ognun", "ognuno",
            "voghiamo",
            "purchè",
            "sieno",
        ],
        "es": [
            "exîstencia", "existencia",
            "forzoso", "forzosa",
            "mias", "mía",
            "baxo", "bajo",
        ],
        "de": [
            "dadurch",
            "demnach",
            "wenigen", "wenig",
            "einzelne", "einzeln",
            "gutmüthig", "gutmütig",
            "errieth", "erraten",
            "getraute", "getrauen",
            "sieh", "sehen",
        ],
        "fi": [
            "etteivät",
            "viimeksi",
            "itsekään",
            "taikka",
            "ymmälle",
            "myöten",
            "nykyään",
            "johtuu", "johtua",
            "ennättänyt",
            "keinon", "keino",
        ],
        "eo": [
            "jugxato", "jugxi",
            "detale", "detalo",
            "omara",
            "duope",
            "iafoje",
            "tiajxo",
            "nulo",
        ],
    },

    # ─── POSSESSION ────────────────────────────────────────────────────────
    "POSSESSION": {
        "fr": [
            "sequins",
        ],
        "it": [
            "abita", "abitare", "abitazione",
            "marzo",
            "piena", "pieno",
        ],
        "es": [
            "banquero", "banqueros",
            "cayena",
        ],
        "de": [
            "anzuklopfen", "anklopfen",
        ],
        "fi": [
            "piipun", "piippu",
            "seurue",
            "ylhäisyydelleen", "ylhäisyys",
        ],
        "eo": [
            "pencojn", "penco",
            "barilo", "bariloj",
            "marmeladujon", "marmelado",
        ],
    },

    # ─── EXISTENCE ─────────────────────────────────────────────────────────
    "EXISTENCE": {
        "it": [
            "dispetto", "dispetti",
            "sinistra", "sinistro",
            "piacque", "piacere",
        ],
        "de": [
            "hm",
        ],
        "fi": [
            "kaukaa", "kauas",
            "lienten",
            "syönyt", "syödä",
            "hirtetty", "hirttää",
        ],
        "eo": [
            "poluras",
            "falante", "fali",
            "falego",
            "fojo", "fojoj",
            "fojojn",
        ],
    },

    # ─── DESTRUCTION ───────────────────────────────────────────────────────
    "DESTRUCTION": {
        "en": [
            "ripped", "tore",
        ],
        "de": [
            "schämen",
        ],
        "eo": [
            "frakasata", "frakasi",
        ],
    },

    # ─── SEEKING ───────────────────────────────────────────────────────────
    "SEEKING": {
        "eo": [
            "promesas", "promeso",
            "prokrasto",
        ],
    },

    # ─── FEAR ──────────────────────────────────────────────────────────────
    "FEAR": {
        "it": [
            "cautamente", "cauto", "cauta",
        ],
        "fi": [
            "inkvisitsionin",
        ],
    },

    # ─── CARE ──────────────────────────────────────────────────────────────
    "CARE": {
        "eo": [
            "babiladis", "babili",
            "plua",
            "ensxovis",
        ],
    },

    # ─── CHALEUR (heat/cold) ──────────────────────────────────────────────
    "CHALEUR": {
        "eo": [
            "sovagxaj", "sovagxa",
            "kurteno", "kurtenoj",
        ],
    },

    # ─── LUMIÈRE ───────────────────────────────────────────────────────────
    "LUMIÈRE": {
        "eo": [
            "ludejo", "ludi",
        ],
    },

    # ─── MATIÈRE ───────────────────────────────────────────────────────────
    "MATIÈRE": {
        "de": [
            "aepfel", "apfel",
        ],
        "eo": [
            "tubo",
        ],
    },

    # ─── CORPS ─────────────────────────────────────────────────────────────
    "CORPS": {
        "eo": [
            "konis", "koni",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# STOP WORDS — function words, archaic particles, pronouns
# ══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V484 = {
    "fr": [
        "n'ayez", "fussions", "sût", "chacune", "chacun",
        "xxxi",
    ],
    "it": [
        "nol", "teco", "ognun", "glielo", "gliela",
        "m'è", "l'erba", "purchè", "sieno", "voghiamo",
        "dì", "farne", "farlo", "farci",
    ],
    "es": [
        "nosotras", "mias", "baxo", "exîstencia",
        "sirviéron", "conduxéron", "echáron", "muriéron",
    ],
    "fi": [
        "etteivät", "viimeksi", "itsekään", "taikka",
        "ymmälle", "myöten", "nykyään", "ennättänyt",
        "kaukaa", "lienten",
    ],
    "de": [
        "demnach", "dadurch", "hm", "sieh",
        "is",
    ],
    "en": [
        "ma",
    ],
    "eo": [
        "duope", "iafoje", "nulo", "plua",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# PROPER NOUNS — place names, person names appearing in corpus
# ══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V484 = {
    "fr": [
        "alger", "azof", "fernando", "lampourdos",
        "dey",
    ],
    "it": [
        "taylor",
    ],
    "es": [
        "palestrina", "fernando", "ibarra",
        "mascareñas", "lampurdan", "souza",
        "dey", "cayena",
    ],
    "en": [
        "palestrina", "carara",
    ],
    "de": [
        "northumbria",
    ],
    "fi": [
        "lissabonin", "issaskar",
    ],
    "eo": [
        "omara",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# ARCHAIC FORMS — old orthography → modern mapping
# ══════════════════════════════════════════════════════════════════════════════

ARCHAIC_FORMS_V484 = {
    "de": {
        "gutmüthig": "gutmütig",
        "errieth": "erriet",
        "blaß": "blass",
        "faßte": "fasste",
        "aepfel": "äpfel",
    },
    "es": {
        "baxo": "bajo",
        "exîstencia": "existencia",
        "esquadra": "escuadra",
        "sirviéron": "sirvieron",
        "conduxéron": "condujeron",
        "echáron": "echaron",
        "muriéron": "murieron",
    },
    "fr": {
        "d'ibaraa": "d'ibarra",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# ACCESS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_keywords_v484():
    """Return KEYWORDS_V484 dict."""
    return KEYWORDS_V484


def get_stop_words_v484():
    """Return STOP_WORDS_V484 dict."""
    return STOP_WORDS_V484


def get_proper_nouns_v484():
    """Return PROPER_NOUNS_V484 dict."""
    return PROPER_NOUNS_V484


def get_archaic_forms_v484():
    """Return ARCHAIC_FORMS_V484 dict."""
    return ARCHAIC_FORMS_V484


# ══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    total_kw = sum(len(ws) for atom in KEYWORDS_V484.values()
                   for ws in atom.values())
    total_sw = sum(len(ws) for ws in STOP_WORDS_V484.values())
    total_pn = sum(len(ns) for ns in PROPER_NOUNS_V484.values())
    total_af = sum(len(ms) for ms in ARCHAIC_FORMS_V484.values())

    print(f"v4.8.4 Vocabulary Expansion:")
    print(f"  Keywords:      {total_kw:4d} across {len(KEYWORDS_V484)} atoms")
    print(f"  Stop words:    {total_sw:4d}")
    print(f"  Proper nouns:  {total_pn:4d}")
    print(f"  Archaic forms: {total_af:4d}")
    print(f"  TOTAL:         {total_kw + total_sw + total_pn + total_af:4d}")

    # Per-language breakdown
    langs = set()
    for atom in KEYWORDS_V484.values():
        langs.update(atom.keys())
    for sw_langs in STOP_WORDS_V484:
        langs.add(sw_langs)
    for lang in sorted(langs):
        kw = sum(len(atom.get(lang, [])) for atom in KEYWORDS_V484.values())
        sw = len(STOP_WORDS_V484.get(lang, []))
        pn = len(PROPER_NOUNS_V484.get(lang, []))
        af = len(ARCHAIC_FORMS_V484.get(lang, {}))
        print(f"    {lang}: {kw:3d} kw + {sw:2d} sw + {pn:2d} pn + {af:2d} af = {kw+sw+pn+af}")

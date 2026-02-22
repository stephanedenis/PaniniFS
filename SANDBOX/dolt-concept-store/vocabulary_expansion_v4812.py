#!/usr/bin/env python3
"""vocabulary_expansion_v4812.py — v4.8.12: Expanded corpus proper nouns + keywords

Corpus expanded from 11 → 62 files (5.9M words, 12 languages).
Coverage dropped from 91.2% → 50.5% (weighted) due to:
 - CJK/NL/RU/SA languages (not target for this expansion)
 - Proper nouns from new literary works (Zarathustra, Holmes, Pencroff...)
 - Archaic Italian from Dante's Divina Commedia
 - Common words missing from expanded EN/FR/DE/ES texts
 - ES bilingual contamination (English words in Don Quijote annotations)

Strategy:
 - Massive proper noun injection (character names dominate uncovered)
 - IT archaic/medieval forms from Dante (sé, ché, sanza, elli, quivi...)
 - DE/FR/EN/ES high-frequency common words
 - ES stop words for annotation artifacts (cf, =page, a=, =a)

Created: 2026-02-22 by Copilot (Claude Opus 4.6) on hauru
"""

# ══════════════════════════════════════════════════════════════════════════════
# PROPER NOUNS — Character names, places, proper nouns from expanded corpus
# ══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4812 = {
    "de": [
        # Faust (Goethe)
        "zarathustra", "zarathustra's", "mephistopheles", "faust", "gretchen",
        "wagner", "altmayer", "brander", "mephisto",
        # Kabale und Liebe (Schiller)
        "luise", "luisen", "ferdinand", "walter", "wurm", "sophie",
        # Die Leiden des jungen Werthers
        "lotte", "lotten", "lottens", "albert", "werther",
        # Also sprach Zarathustra (Nietzsche)
        # Other
        "milady", "julius", "wahlheim",
    ],
    "en": [
        # The Mill on the Floss (Eliot)
        "maggie", "maggie's",
        # Various
        "mackenzie", "mackenzie's", "holmes", "sherlock", "watson",
        "joan", "dorian", "darcy", "reid", "lorry",
        "scrooge", "bennet", "helsing", "defarge",
        "swan", "bingley", "gray", "stubb", "lucy",
        "huck", "mina", "beowulf", "jonathan", "carlson",
        "basil", "manette", "joe", "pross", "arthur",
        "carton", "darnay", "caroline", "lydia", "medlock",
        "lucie", "skeaton", "harker", "robin", "thurston",
        "jerry", "stryver", "becky", "lizzy", "kurtz",
        "katherine", "avies", "godalming", "sibyl", "seward",
        "quincey", "magnus", "netherfield", "morrel",
        # Kalevala (EN translation)
        "wainamoinen", "lemminkainen", "pohyola", "ilmarinen",
        "kalevala", "louhi",
        # Beowulf
        "hrothgar", "grendel", "hygelac", "wiglaf",
        # Moby-Dick
        "pequod", "nantucket", "queequeg", "ahab", "starbuck",
        "tashtego", "ishmael",
        # Secret Garden
        "weatherstaff",
        # A Christmas Carol
        "christmas", "cratchit", "fezziwig", "marley",
        # Heart of Darkness
        # Various
        "harry", "bob",
    ],
    "es": [
        # Don Quijote
        "panza", "rocinante", "toboso", "lotario", "anselmo",
        "rucio", "dorotea", "cardenio", "luscinda", "zoraida",
        "sansón", "altisidora", "basilio", "parrón",
        # Other
        "mercedes", "ramón", "roque", "badajoz",
    ],
    "fr": [
        # L'Île mystérieuse (Jules Verne)
        "pencroff", "cyrus", "harbert", "spilett", "ayrton",
        "nab", "gédéon", "lincoln", "maston", "ardan",
        "nemo", "tabor", "nicholl", "jup",
        # Le Comte de Monte-Cristo (Dumas)
        "dantès", "edmond", "fernand", "mercédès", "pharaon",
        "jacopo", "coclès", "blacas", "villefort", "morrel",
        # De la Terre à la Lune (Jules Verne)
        "columbiad", "barbicane",
        # Descartes
        "descartes", "newton",
        # Lieux
        "marseille", "pacifique",
        # Other
        "michel", "napoléon", "renée", "julie", "emmanuel",
        "césar", "catalans", "d'ayrton", "d'elbe", "d'if",
    ],
    "it": [
        # Divina Commedia
        "virgilio", "beatrice", "bëatrice",
        # Pinocchio (already covered in prior expansions)
        "purgatorio",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# KEYWORDS — High-frequency common words missing from expanded corpus
# ══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4812 = {
    # ─── COMMUNICATION ──────────────────────────────────────────
    "COMMUNICATION": {
        "de": [
            "präsident", "präsidenten", "hofmarschall", "marschall",
            "doktor", "jüngling", "mädel", "gnädige", "gnädiger",
        ],
        "en": [
            "professor", "forward", "magic", "trust", "future",
            "engaged", "sake", "crew", "burst", "pipe",
            "drove", "moonlight", "wagon", "aside", "excited",
            "confidence", "hidden", "slept", "dad",
        ],
        "fr": [
            "président", "bâtiment", "substance", "substances",
            "réalité", "faculté", "géométrie", "démonstrations",
            "diamètre", "substitut", "capable", "immobile",
            "trace", "retraite", "gaz", "néant", "demi",
            "actuellement", "soigneusement", "feindre",
            "littoral", "lisière", "barque", "canal", "chariot",
            "fonte", "ballon", "boulet", "rayons", "dollars",
        ],
        "es": [
            "escudero", "escuderos", "adelante", "rostro",
            "bachiller", "famoso", "fama", "locura",
            "hidalgo", "labrador", "hazañas", "pergamino",
            "resolución", "negocio", "hacienda", "cautivo",
        ],
        "it": [
            "ingegno", "sembiante", "cagione", "cagion",
            "turba", "raggio", "raggi", "croce",
            "pioggia", "nube", "fonte", "cibo",
        ],
    },

    # ─── AGENT ──────────────────────────────────────────
    "AGENT": {
        "de": [
            "weib", "weibe", "pöbel", "gesindel",
            "zauberer", "pudel", "kuppler",
        ],
        "en": [
            "warlock", "leviathan", "harpooneer",
            "train",
        ],
        "fr": [
            "geôlier", "naufragés",
        ],
        "es": [
            "asno", "jumento", "dueña", "dueñas", "dueño",
            "sobrina", "cabrero", "renegado",
        ],
        "it": [
            "spirto", "spirti", "dolente",
        ],
    },

    # ─── MOUVEMENT ──────────────────────────────────────────
    "MOUVEMENT": {
        "de": [
            "tritt", "liegt", "wirft", "wirkt", "klingt",
            "hängt", "gilt", "treiben",
        ],
        "en": [
            "bent", "lot", "moor",
        ],
        "fr": [
            "grève", "nord", "sud", "départ", "baie",
            "muraille",
        ],
        "es": [
            "daño", "toca", "puesta",
        ],
    },

    # ─── PERCEPTION ──────────────────────────────────────────
    "PERCEPTION": {
        "de": [
            "busen", "leib", "leibe", "glut",
            "trübsal", "neid", "honig",
        ],
        "en": [
            "spake",
        ],
        "fr": [
            "l'horizon", "l'embouchure", "l'atmosphère",
            "l'astre", "l'essence",
            "l'anglais", "l'union", "l'opération",
            "l'îlot", "l'ingénieur",
        ],
        "es": [
            "cuán", "cuál", "cuales",
        ],
        "it": [
            "fama", "maraviglia",
        ],
    },

    # ─── COGNITION ──────────────────────────────────────────
    "COGNITION": {
        "de": [
            "eignen", "eigne", "kunst", "zukunft", "ziel", "ziele",
            "staat", "werk", "gegend", "opfer",
            "dünkt", "sonderlich", "heimlich",
        ],
        "en": [
            "northland",
        ],
        "fr": [
            "conçois", "concevons", "conçoit",
            "dépend", "police", "octobre",
        ],
        "es": [
            "acuerdo", "efeto", "asimismo",
            "usted", "tenga",
        ],
        "it": [
            "quantunque", "alquanto", "guisa", "senno",
        ],
    },

    # ─── POSSESSION ──────────────────────────────────────────
    "POSSESSION": {
        "de": [
            "degen", "bock", "limonade",
            "kalt", "gram",
        ],
        "es": [
            "sazón", "paz", "albarda",
            "letras", "plática", "cuidado",
            "muestras", "muestra",
        ],
    },

    # ─── LIEU ──────────────────────────────────────────
    "LIEU": {
        "it": [
            "scoglio", "dosso",
        ],
    },

    # ─── DESTRUCTION ──────────────────────────────────────────
    "DESTRUCTION": {
        "it": [
            "percosse", "tolse", "vinse", "sofferse",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# STOP WORDS — Function words missing from expanded corpus
# ══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4812 = {
    "de": [
        "heisst", "hiess", "läßt", "wohlan", "andre",
        "darob", "stets", "aufs", "dran", "desto",
        "gerne", "geschah", "getan", "musst", "möcht",
        "unsrer", "kennt", "nennt", "geschieht", "welch",
        "sonderlich", "geschwind", "verzeiht", "ha",
        "unserm", "bunten", "trank",
    ],
    "en": [
        "th", "tha", "eh",
    ],
    "es": [
        "mesmo", "mesma", "agora", "sean", "oh",
        "cf", "vr", "ansí", "doña",
        "haga", "hago", "doy", "darme", "vea",
        "conozco", "entiendo",
    ],
    "fr": [
        "seroit", "étoient", "j.-t", "j'eusse",
        "s'agissait", "jusques", "hurrah",
    ],
    "it": [
        # Old/medieval Italian function words (Dante)
        "ché", "sé", "né", "sù", "ond", "ove", "quivi",
        "poscia", "sovra", "sovr", "ciascun", "quand",
        "piè", "fia", "el", "eran", "fé",
        "d'ogne", "puote", "puoi", "ch'elli", "ch'el",
        "cor", "cotanto", "cotal", "ïo", "ivi",
        "fummo", "furon", "vuo", "sanz",
        "l'etterno", "etterno", "etterna", "fïate",
        "sùbito", "vòlto", "l'umana", "l'atto",
        "acciò", "medesmo", "omo", "cu", "duol",
        "intra", "ambo", "dintorno",
        "fec", "fosti", "fosser", "eravam",
        "puose", "ratto", "rispuose", "rispuos",
        "discese", "quai", "mo",
        # Old Italian content indicators treated as function words
        "sanza", "elli", "s'elli", "foco",
        # v4.8.12b: additional archaic verb forms from Divina Commedia
        "onde", "vanno", "atto", "dee", "nullo", "tolto",
        "dimanda", "fei", "fosso", "mei", "porse",
        "tai", "conobbi", "seder", "aperse", "torse",
        "vòlti", "sarei", "drizza", "surge", "avvegna",
        "udi", "penne", "ciglia", "merto", "roccia",
        "sie", "sazia", "uso", "intelletto",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# ARCHAIC FORMS — Old spellings → modern equivalents
# ══════════════════════════════════════════════════════════════════════════════

ARCHAIC_FORMS_V4812 = {
    "de": {
        "heisst": "heißt",
        "hiess": "hieß",
        "thorheit": "torheit",
    },
    "fr": {
        "seroit": "serait",
        "étoient": "étaient",
        "jusques": "jusque",
    },
    "it": {
        "sanza": "senza",
        "elli": "egli",
        "quivi": "qui",
        "poscia": "poi",
        "sovra": "sopra",
        "puote": "può",
        "foco": "fuoco",
        "cotanto": "tanto",
        "cotal": "tale",
        "medesmo": "medesimo",
        "omo": "uomo",
        "rispuose": "rispose",
        "maraviglia": "meraviglia",
        "letizia": "letizia",
        "l'etterno": "l'eterno",
        "etterno": "eterno",
        "etterna": "eterna",
    },
    "es": {
        "mesmo": "mismo",
        "mesma": "misma",
        "agora": "ahora",
        "ansí": "así",
        "efeto": "efecto",
        "sazón": "sazón",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# ES ANNOTATION STOP WORDS — markup artifacts in the Don Quijote edition
# ══════════════════════════════════════════════════════════════════════════════

ES_ANNOTATION_STOPS = [
    "=page", "a=", "=a", "que=", "=por",
]


# ══════════════════════════════════════════════════════════════════════════════
# ACCESS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_keywords_v4812():
    return KEYWORDS_V4812

def get_stop_words_v4812():
    combined = dict(STOP_WORDS_V4812)
    # Merge ES annotation stops
    if "es" in combined:
        combined["es"] = combined["es"] + ES_ANNOTATION_STOPS
    else:
        combined["es"] = ES_ANNOTATION_STOPS
    return combined

def get_proper_nouns_v4812():
    return PROPER_NOUNS_V4812

def get_archaic_forms_v4812():
    return ARCHAIC_FORMS_V4812


# ══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    kw = sum(len(ws) for atom in KEYWORDS_V4812.values() for ws in atom.values())
    sw = sum(len(ws) for ws in get_stop_words_v4812().values())
    pn = sum(len(ns) for ns in PROPER_NOUNS_V4812.values())
    af = sum(len(ms) for ms in ARCHAIC_FORMS_V4812.values())
    total = kw + sw + pn + af

    print(f"v4.8.12 Vocabulary Expansion (expanded corpus):")
    print(f"  Keywords:      {kw:4d} across {len(KEYWORDS_V4812)} atoms")
    print(f"  Stop words:    {sw:4d}")
    print(f"  Proper nouns:  {pn:4d}")
    print(f"  Archaic forms: {af:4d}")
    print(f"  TOTAL:         {total:4d}")
    print()

    langs = set()
    for atom in KEYWORDS_V4812.values():
        langs.update(atom.keys())
    for lang in sorted(langs):
        lkw = sum(len(atom.get(lang, [])) for atom in KEYWORDS_V4812.values())
        lsw = len(get_stop_words_v4812().get(lang, []))
        lpn = len(PROPER_NOUNS_V4812.get(lang, []))
        laf = len(ARCHAIC_FORMS_V4812.get(lang, {}))
        print(f"    {lang}: {lkw:3d} kw + {lsw:2d} sw + {lpn:2d} pn + {laf:2d} af = {lkw+lsw+lpn+laf}")

    # Verify proper nouns are strings
    for lang, names in PROPER_NOUNS_V4812.items():
        for name in names:
            assert isinstance(name, str), f"Not a string: {name}"
    print("\nAll proper nouns are strings ✓")

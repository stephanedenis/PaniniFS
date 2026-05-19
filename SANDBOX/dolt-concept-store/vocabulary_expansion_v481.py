#!/usr/bin/env python3
"""vocabulary_expansion_v481.py — v4.8.1: Finnish lemmatizer + stop word expansion.

This module extends the PaniniFS vocabulary system with:

1. **Finnish stop words** — 44 additional function words (pronouns, conjunctions,
   adverbs, modal forms) identified from corpus analysis as non-content words
   that were inflating the uncovered count.

2. **Finnish keyword mappings** — New Finnish base forms mapped to existing atoms
   via voikko lemmatization analysis. These are common Finnish content words
   found in Gutenberg corpus texts (Alice in Wonderland FI, Seitsemän veljestä)
   that map to existing NSM/Panini atoms.

3. **Voikko-aware stop word filter** — Uses libvoikko morphological analysis
   to identify function words by their grammatical class (pronouns, particles,
   conjunctions, adverbs, postpositions) and filter them from content word lists.

Integration:
    Imported by reconstruction_fidelity.py via try/except guards.
    Adds to the global keyword index and stop word sets.

Part of PaniniFS concept store — v4.8.1 Finnish lemmatizer integration.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: FINNISH STOP WORDS — Round 7 (voikko-derived)
# ═══════════════════════════════════════════════════════════════════════════════
#
# These function words were identified by corpus analysis as high-frequency
# words not carrying semantic content (pronouns, modal verb forms, particles,
# place/time adverbs, conjunctions). Adding them as stop words removes them
# from the content word count, improving lexical coverage accuracy.

STOP_WORDS_V481 = {
    "fi": {
        # ── Temporal adverbs ──
        "aikana", "aina", "ennen", "jälkeen",
        # ── Spatial adverbs ──
        "alas", "kaukana", "luona", "sisään", "ulos", "ylös", "ympäri",
        # ── Intensifiers ──
        "erittäin", "hyvin", "melko", "oikein",
        # ── Conjunctions & particles ──
        "esimerkiksi", "jollei", "kunhan", "mikäli", "toki",
        # ── Pronoun forms (not yet covered) ──
        "kenenkään", "tuo",
        # ── Olla (to be) forms ──
        "olen", "olette", "oliko", "olisimme", "olisit", "olisitte",
        "olisivat", "olivat", "oltu",
        # ── Modal verb forms ──
        "ovatko", "pitäisikö", "saattaa", "täytyisi", "täytyykö",
        # ── Demonstrative / quantifier ──
        "kerta", "kohta", "samaan", "samalla", "samasta", "yhtä", "yhtään",
        # ── Additional high-frequency function words from corpus ──
        # Possessive suffixes often appear as separate tokens after normalization
        "minun", "sinun", "hänen", "meidän", "teidän", "heidän",
        "minua", "sinua", "häntä", "meitä", "teitä", "heitä",
        "minulle", "sinulle", "hänelle", "meille", "teille", "heille",
        "minusta", "sinusta", "hänestä", "meistä", "teistä", "heistä",
        "minussa", "sinussa", "hänessä", "meissä", "teissä", "heissä",
        "minulla", "sinulla", "hänellä", "meillä", "teillä", "heillä",
        # Relative pronoun forms
        "joista", "joihin", "joissa", "joilla", "joille", "joilta",
        # Demonstrative forms
        "noiden", "näiden", "tuossa", "tuolla", "tuosta", "tuolle", "tuolta",
        # Negation + aux combinations
        "eihän", "eikö", "eiköhän", "eipä", "ellei",
        "emme", "emmekö", "enkä", "enkö", "enpä",
        # Temporal/causal
        "sillä", "tosin", "nimittäin",
        # Question particles
        "miksi", "milloin", "kuinka",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: FINNISH KEYWORD EXPANSIONS — atom → Finnish base forms
# ═══════════════════════════════════════════════════════════════════════════════
#
# Maps Finnish base forms (as returned by voikko) to existing Panini atoms.
# These were identified by:
#   1. Running voikko on the top uncovered Finnish corpus words
#   2. Finding the base form
#   3. Matching to existing atoms via multilingual keyword cross-reference
#
# Format: {atom_id: [finnish_keywords]}

FINNISH_KEYWORDS_V481 = {
    # ── Verbs (teonsana) ──
    "DESTRUCTION": ["pysähtyä", "pysäyttää", "pysähtyminen"],
    "RAGE": ["vihata", "viha", "vihainen", "suuttua", "suuttumus"],
    "EXISTENCE": ["herätä", "hereillä", "herääminen", "eläin", "olento"],
    "PLAY": ["soittaa", "soitto", "soitin", "soittaminen"],
    "PERCEPTION": [
        "kuuma", "kuumuus", "kylmyys",
        "valoisa", "valoisuus", "kirkkaus",
        "musta", "mustuus", "tumma", "tummuus",
        "punainen", "punaisuus",
        "vihreä", "vihreys",
    ],
    "AGENT": [
        "koira", "koiranpentu",
        "lintu", "lintuja",
    ],
    "CORPS": [
        "hattu", "hatullinen",
        "takki", "takin",
        "hiukset", "hiuksinen", "tukka",
        "kynä", "sulka",
    ],
    "MATIÈRE": ["vaate", "vaatetus", "kangas"],
    "GRAND": ["pienentyä", "pienentyminen", "pieneneminen"],
    "QUAL": ["painava", "painavuus", "raskaus"],
    "TEDIUM": ["hidas", "hitaus", "hidastua", "hidastuminen"],
    "ANCIEN": ["nopea", "nopeus", "nopeasti", "nopeutua"],

    # ── Additional Finnish content words mapped to existing atoms ──
    # (atoms found via broader multilingual search)
    "LIEU": [
        "aurinko", "auringonpaiste",
        "sänky", "vuode",
        "järvi", "lampi",
        "polku", "reitti",
        "kaupunki", "kylä",
    ],
    "MOUVEMENT": [
        "tuuli", "tuulinen", "tuulahdus",
        "sade", "sadetta", "sataa",
        "vahva", "vahvuus", "vahvistaa",
    ],
    "PAROLE": [
        "opettaa", "opetus", "opettaja", "oppi",
    ],
    "CRÉATION": [
        "pilvi", "pilvinen",
        "ruoho", "ruohikko", "nurmi",
        "tähti", "tähtinen", "tähdistö",
        "kuu", "kuutamo",
    ],

    # ── Colors not yet in PERCEPTION ──
    # sininen (blue), keltainen (yellow) — distinctive color terms
    "COULEUR": [
        "sininen", "sini", "sinisyys",
        "keltainen", "kelta", "keltaisuus",
    ],

    # ── Common literary vocabulary ──
    "SENTIR": [
        "pelästyä", "pelästyminen", "kauhistua", "kauhistus",
        "ihmetellä", "ihmetys", "hämmästyä", "hämmästys",
        "ilahtua", "ilo", "iloinen",
    ],
    "PENSÉE": [
        "pohtia", "pohdinta", "miettiä", "miettiminen",
        "harkita", "harkinta", "päätellä", "päätelmä",
    ],
    "VOLONTÉ": [
        "toivoa", "toive", "toivomus",
        "päättää", "päätös", "ratkaista", "ratkaisu",
    ],
    "PARLER": [
        "kuiskata", "kuiskaus", "mumista", "mutista",
        "selittää", "selitys", "kertoa", "kertomus",
    ],
    "SOCIAL": [
        "ystävä", "ystävyys", "tuttava",
        "naapuri", "vieras", "kumppani",
    ],
    "FAMILLE": [
        "sisarus", "serkku", "setä", "täti",
        "isoisä", "isoäiti", "vaari", "mummo",
    ],
    "NOURRITURE": [
        "ruoka", "ateria", "leipä", "maito",
        "liha", "hedelmä", "juusto", "voita",
    ],
    "VÊTEMENT": [
        "kenkä", "saapas", "paita", "housut",
        "mekko", "esiliina", "sukat",
    ],
    "ANIMAL": [
        "kissa", "hiiri", "jänis", "kettu",
        "karhu", "susi", "orava", "siili",
    ],
    "NATURE": [
        "metsä", "metsäinen", "pensas",
        "puu", "puinen", "tammi", "koivu",
        "kukka", "kukkia", "ruusu",
        "meri", "merenranta", "ranta",
        "vuori", "vuoristo", "kallio",
        "joki", "virta", "puro",
    ],
    "TEMPS": [
        "aamu", "aamulla", "aamun",
        "ilta", "illalla", "illan",
        "päivä", "päivällä",
        "yö", "yöllä", "yön",
        "viikko", "kuukausi", "vuosi",
    ],
    "CORPS_PARTIES": [
        "pää", "otsa", "leuka", "poski",
        "käsi", "käsivarsi", "sormi", "kämmen",
        "jalka", "polvi", "nilkka", "varvas",
        "silmä", "silmäys", "katse",
        "suu", "huulet", "kieli",
        "korva", "nenä", "kaula",
        "sydän", "veri", "luu", "iho",
    ],
    "MAISON": [
        "talo", "talon", "asunto", "koti",
        "huone", "huoneen", "kamari",
        "ovi", "ikkuna", "porras",
        "lattia", "katto", "seinä",
        "pöytä", "tuoli",
        "kirja", "paperi",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: VOIKKO-AWARE FUNCTION WORD FILTER
# ═══════════════════════════════════════════════════════════════════════════════
#
# Uses voikko grammatical class (CLASS attribute) to detect Finnish function
# words that should not count as content words. This is more robust than
# a static stop word list because it handles ALL inflected forms.
#
# Voikko CLASS values for function words:
#   - sidesana (conjunction): ja, tai, mutta, kun, koska, jos, vaikka
#   - huudahdussana (interjection): voi, hei, ai
#   - asemosana (pronoun): hän, minä, sinä, joka, mikä, tämä
#   - seikkasana (adverb of time/place/manner): nyt, sitten, täällä
#   - suhdesana (postposition/preposition): kanssa, luona, kohti
#   - kieltosana (negation): ei

_VOIKKO_FUNCTION_CLASSES = frozenset({
    "sidesana",         # conjunction
    "huudahdussana",    # interjection
    "asemosana",        # pronoun (demonstrative, relative, etc.)
    "suhdesana",        # postposition/preposition
    "kieltosana",       # negation word
})

# These voikko classes may be function words depending on context
# but we keep them as content words to avoid over-filtering:
#   - seikkasana (adverb) — many carry semantic content
#   - teonsana (verb) — always content
#   - nimisana (noun) — always content
#   - laatusana (adjective) — always content


def is_finnish_function_word(word: str) -> bool:
    """Check if a Finnish word is a function word using voikko morphology.
    
    Uses voikko's grammatical CLASS attribute to detect pronouns,
    conjunctions, postpositions, interjections, and negation words.
    
    Returns True if the word is definitively a function word.
    Returns False for content words or if voikko is unavailable.
    """
    try:
        import libvoikko
    except ImportError:
        return False
    
    # Lazily initialize voikko
    if not hasattr(is_finnish_function_word, '_voikko'):
        try:
            is_finnish_function_word._voikko = libvoikko.Voikko("fi")
        except OSError:
            is_finnish_function_word._voikko = None
    
    voikko = is_finnish_function_word._voikko
    if voikko is None:
        return False
    
    try:
        analyses = voikko.analyze(word)
        if not analyses:
            return False
        # If ALL analyses agree it's a function word, it's a function word
        classes = set()
        for a in analyses:
            cl = a.get("CLASS", "")
            classes.add(cl)
        return bool(classes) and classes.issubset(_VOIKKO_FUNCTION_CLASSES)
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: EXTRA PUNCTUATION CHARS
# ═══════════════════════════════════════════════════════════════════════════════
# Additional Unicode characters to strip from tokens before matching.
# Finnish texts use typographic quotation marks and dash variants.

EXTRA_PUNCTUATION_V481 = "»«›‹„""‟"


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: PROPER NOUNS — Finnish literary names (Alice corpus + Seitsemän veljestä)
# ═══════════════════════════════════════════════════════════════════════════════
# These are character names and place names from the Finnish Gutenberg texts.
# They are content words mapped to the AGENT atom (like proper nouns in other langs).

PROPER_NOUNS_V481 = {
    "fi": {
        # Alice's Adventures in Wonderland (FI translation)
        "liisa",        # Alice
        "herttakuningatar",  # Queen of Hearts
        "hatuntekijä",  # Hatter
        "jussihare",    # March Hare
        "unisiili",     # Dormouse
        "irvikissa",    # Cheshire Cat
        # Seitsemän veljestä (Seven Brothers) by Aleksis Kivi
        "juhani", "tuomas", "aapo", "simeoni", "timo", "lauri", "eero",
        "impivaara",    # Impivaara (forest in the novel)
        "jukola",       # Jukola (the brothers' farm)
        # Common Finnish names appearing as character references
        "martti", "mirri", "tohtori", "filosofi", "kuningas", "kuningatar",
    },
}

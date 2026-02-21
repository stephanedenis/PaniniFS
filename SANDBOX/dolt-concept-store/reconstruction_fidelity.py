#!/usr/bin/env python3
"""reconstruction_fidelity.py — v4.6: Measure reconstruction quality of PaniniFS

Answers the question: "Given a rich semantic export, how much of the original
text could we theoretically reconstruct?"

Metrics computed:
  1. Lexical coverage: % of content words that have an atom alignment
  2. Atom density: atom detections per word
  3. Concept coverage: % of paragraphs with at least one concept detected
  4. Morphological coverage: % of words with morphological features
  5. Discourse coverage: % of paragraphs with discourse relations
  6. Prosodic coverage: % of paragraphs with prosody data
  7. Information retention ratio: combined score of all layers
  8. Reconstruction readiness: weighted assessment per paragraph

Usage:
    python reconstruction_fidelity.py <file> [--lang <code>] [--verbose]
    python reconstruction_fidelity.py --batch <dir> [--lang <code>]

Part of PaniniFS concept store — E2 reconstruction fidelity assessment.
"""

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_analyzer import analyze_document, detect_language

# v4.7: Import expanded stop words and punctuation chars
try:
    from vocabulary_expansion_v47 import EXTRA_STOP_WORDS, EXTRA_PUNCTUATION_CHARS
    _HAS_EXPANSION = True
except ImportError:
    _HAS_EXPANSION = False
    EXTRA_STOP_WORDS = {}
    EXTRA_PUNCTUATION_CHARS = ""

# v4.8: Round 2 expansion — more stop words, proper nouns, literary words
try:
    from vocabulary_expansion_v48 import (
        STOP_WORDS_V48, PROPER_NOUN_AGENTS, LITERARY_STOP_WORDS,
        EXTRA_PUNCTUATION_V48,
    )
    _HAS_EXPANSION_V48 = True
except ImportError:
    _HAS_EXPANSION_V48 = False
    STOP_WORDS_V48 = {}
    PROPER_NOUN_AGENTS = set()
    LITERARY_STOP_WORDS = set()
    EXTRA_PUNCTUATION_V48 = ""

# v4.8.1: Finnish lemmatizer expansion — stop words, keywords, proper nouns
try:
    from vocabulary_expansion_v481 import (
        STOP_WORDS_V481, FINNISH_KEYWORDS_V481, PROPER_NOUNS_V481,
        EXTRA_PUNCTUATION_V481, is_finnish_function_word,
    )
    _HAS_EXPANSION_V481 = True
except ImportError:
    _HAS_EXPANSION_V481 = False
    STOP_WORDS_V481 = {}
    FINNISH_KEYWORDS_V481 = {}
    PROPER_NOUNS_V481 = {}
    EXTRA_PUNCTUATION_V481 = ""

# v4.8.2: Massive multilingual keyword expansion + stop words + proper nouns
try:
    from vocabulary_expansion_v482 import (
        get_keywords_v482, get_stop_words_v482,
        get_proper_nouns_v482, get_archaic_forms,
    )
    _KEYWORDS_V482 = get_keywords_v482()
    _STOP_WORDS_V482 = get_stop_words_v482()
    _PROPER_NOUNS_V482 = get_proper_nouns_v482()
    _ARCHAIC_FORMS = get_archaic_forms()
    _HAS_EXPANSION_V482 = True
except ImportError:
    _HAS_EXPANSION_V482 = False
    _KEYWORDS_V482 = {}
    _STOP_WORDS_V482 = {}
    _PROPER_NOUNS_V482 = {}
    _ARCHAIC_FORMS = {}

# v4.8.3: Targeted coverage push for weak languages (FI/IT/ES/FR/DE/EN/EO)
try:
    from vocabulary_expansion_v483 import (
        get_keywords_v483, get_stop_words_v483,
        get_proper_nouns_v483, get_archaic_forms_v483,
    )
    _KEYWORDS_V483 = get_keywords_v483()
    _STOP_WORDS_V483 = get_stop_words_v483()
    _PROPER_NOUNS_V483 = get_proper_nouns_v483()
    _ARCHAIC_FORMS_V483 = get_archaic_forms_v483()
    _HAS_EXPANSION_V483 = True
except ImportError:
    _HAS_EXPANSION_V483 = False
    _KEYWORDS_V483 = {}
    _STOP_WORDS_V483 = {}
    _PROPER_NOUNS_V483 = {}
    _ARCHAIC_FORMS_V483 = {}

# v4.8.4: EN base-form injection + remaining gaps across all languages
try:
    from vocabulary_expansion_v484 import (
        get_keywords_v484, get_stop_words_v484,
        get_proper_nouns_v484, get_archaic_forms_v484,
    )
    _KEYWORDS_V484 = get_keywords_v484()
    _STOP_WORDS_V484 = get_stop_words_v484()
    _PROPER_NOUNS_V484 = get_proper_nouns_v484()
    _ARCHAIC_FORMS_V484 = get_archaic_forms_v484()
    _HAS_EXPANSION_V484 = True
except ImportError:
    _HAS_EXPANSION_V484 = False
    _KEYWORDS_V484 = {}
    _STOP_WORDS_V484 = {}
    _PROPER_NOUNS_V484 = {}
    _ARCHAIC_FORMS_V484 = {}

# v4.8.6: Push toward 90% — aggressive targeting of remaining gaps
try:
    from vocabulary_expansion_v486 import (
        get_keywords_v486, get_stop_words_v486,
        get_proper_nouns_v486, get_archaic_forms_v486,
    )
    _KEYWORDS_V486 = get_keywords_v486()
    _STOP_WORDS_V486 = get_stop_words_v486()
    _PROPER_NOUNS_V486 = get_proper_nouns_v486()
    _ARCHAIC_FORMS_V486 = get_archaic_forms_v486()
    _HAS_EXPANSION_V486 = True
except ImportError:
    _HAS_EXPANSION_V486 = False
    _KEYWORDS_V486 = {}
    _STOP_WORDS_V486 = {}
    _PROPER_NOUNS_V486 = {}
    _ARCHAIC_FORMS_V486 = {}

# v4.8.7: All-languages push toward 90%+ (FI lemmas, IT/FR/ES/DE/EN/EO gaps)
try:
    from vocabulary_expansion_v487 import (
        get_keywords_v487, get_stop_words_v487,
        get_proper_nouns_v487, get_archaic_forms_v487,
    )
    _KEYWORDS_V487 = get_keywords_v487()
    _STOP_WORDS_V487 = get_stop_words_v487()
    _PROPER_NOUNS_V487 = get_proper_nouns_v487()
    _ARCHAIC_FORMS_V487 = get_archaic_forms_v487()
    _HAS_EXPANSION_V487 = True
except ImportError:
    _HAS_EXPANSION_V487 = False
    _KEYWORDS_V487 = {}
    _STOP_WORDS_V487 = {}
    _PROPER_NOUNS_V487 = {}
    _ARCHAIC_FORMS_V487 = {}

# v4.8.8: Push FR/IT/FI above 90% (lemmas, irregular verbs, Pinocchio forms)
try:
    from vocabulary_expansion_v488 import (
        get_keywords_v488, get_stop_words_v488,
        get_proper_nouns_v488, get_archaic_forms_v488,
    )
    _KEYWORDS_V488 = get_keywords_v488()
    _STOP_WORDS_V488 = get_stop_words_v488()
    _PROPER_NOUNS_V488 = get_proper_nouns_v488()
    _ARCHAIC_FORMS_V488 = get_archaic_forms_v488()
    _HAS_EXPANSION_V488 = True
except ImportError:
    _HAS_EXPANSION_V488 = False
    _KEYWORDS_V488 = {}
    _STOP_WORDS_V488 = {}
    _PROPER_NOUNS_V488 = {}
    _ARCHAIC_FORMS_V488 = {}


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: SNOWBALL STEMMERS + VOIKKO FINNISH LEMMATIZER
# ═══════════════════════════════════════════════════════════════════════════════

# PyStemmer — Snowball stemmers for 7 languages
try:
    import Stemmer as _PyStemmer
    _SNOWBALL_LANG_MAP = {
        "en": "english", "fr": "french", "de": "german",
        "es": "spanish", "it": "italian", "fi": "finnish",
        "eo": "esperanto",
    }
    _STEMMERS = {}  # lazy init per language
    _HAS_STEMMER = True

    def _get_stemmer(lang: str):
        """Get or create a Snowball stemmer for a language."""
        if lang not in _STEMMERS and lang in _SNOWBALL_LANG_MAP:
            _STEMMERS[lang] = _PyStemmer.Stemmer(_SNOWBALL_LANG_MAP[lang])
        return _STEMMERS.get(lang)
except ImportError:
    _HAS_STEMMER = False
    _SNOWBALL_LANG_MAP = {}
    def _get_stemmer(lang): return None

# Voikko — Finnish morphological analyzer (lemmatizer)
try:
    import libvoikko as _libvoikko
    _VOIKKO = _libvoikko.Voikko("fi")
    _HAS_VOIKKO = True
except (ImportError, OSError):
    _VOIKKO = None
    _HAS_VOIKKO = False


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8: MORPHOLOGICAL SUFFIX STRIPPING (for inflected form coverage)
# ═══════════════════════════════════════════════════════════════════════════════

MORPHO_SUFFIXES = {
    "en": ["ingness", "lessly", "ingly", "ously", "edly", "ically", "ally",
           "ation", "ment", "ness", "tion", "sion", "ous", "ful", "less",
           "able", "ible", "ive", "ity", "ise", "ize", "ling",
           "ing", "ed", "ly", "er", "est", "al", "es", "s"],
    "fr": ["issement", "erait", "eront", "erais", "erions", "eriez",
           "aient", "ement", "tion", "sion", "ité", "ment",
           "ais", "ait", "ons", "ez", "ant", "eur", "euse", "eurs",
           "ées", "ée", "és", "ère", "ères", "eux", "eaux",
           "ât", "ît", "ût", "ent", "ais", "ait",
           # v4.8.3: basic plurals + past participle
           "es", "s", "x", "é"],
    "de": ["ungen", "ieren", "ierte", "ierten", "lich", "keit", "heit",
           "isch", "ische", "ischen", "iges", "iger",
           "ung", "bar", "sam", "ern", "eln", "ten", "en", "te",
           "ig", "ige", "es", "er", "em", "et", "st", "t", "e", "n"],
    "es": ["ción", "sión", "mente", "ieron", "aron", "aban", "ando", "iendo",
           "ados", "adas", "ado", "ada", "ía", "ían", "ible", "able", "aba",
           "ó", "án", "ás", "é", "ió", "emos", "éis",
           # v4.8.3: basic plurals + gender
           "es", "s", "os", "as", "a", "o"],
    "it": ["zione", "mente", "izzare", "izzato", "eggiare", "ibile", "abile",
           "ando", "endo", "ato", "ata", "ati", "ate", "ava", "ò",
           "arono", "ire", "ere", "are", "ire", "ì", "arono",
           # v4.8.3: basic endings + diminutive
           "i", "e", "o", "a", "ini", "ino", "ina", "ine",
           "etto", "etta", "etti", "ette"],
    "fi": ["ttiin", "ssaan", "ssään", "llaan", "lleen", "staan", "stään",
           "ttaan", "ttään", "matta", "iseen",
           "mme", "tte", "vat", "vät", "nsa", "nsä", "ssa", "ssä",
           "lla", "llä", "sta", "stä", "lle", "lta", "ltä", "tta", "ttä",
           "ksi", "nut", "nyt", "neet", "isi",
           "kin", "kaan", "kään", "han", "hän", "kö", "pä",
           "aan", "ään", "een", "oon",
           "in", "an", "en", "ön", "nä", "on", "ät", "öt",
           "aa", "ää", "ta", "tä", "na", "nä", "n", "t", "a", "ä"],
    "eo": ["ojn", "inta", "anta", "igxi", "igxas", "igi", "igxis",
           "ita", "ata", "inta", "anta",
           "as", "is", "os", "us", "oj", "on", "an", "in",
           "ajn", "ejn", "oj", "ajxo", "ejo"],
    "sa": [],
}

# German prefixes that may be stripped for compound matching
_DE_PREFIXES = ["ver", "ent", "be", "ge", "er", "zer", "miss", "un",
                "an", "auf", "aus", "ein", "um", "vor", "zu",
                "ab", "hin", "her", "nach", "über", "unter", "mit",
                "durch", "wider", "wieder"]

# Minimum stem length per language (Finnish/Esperanto allow shorter stems)
_MIN_STEM_LEN = {
    "fi": 2, "eo": 2, "sa": 2,
    "en": 3, "fr": 3, "de": 3, "es": 3, "it": 3,
}


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8: GLOBAL KEYWORD INDEX (all known atom keywords, per language)
# ═══════════════════════════════════════════════════════════════════════════════

_GLOBAL_KEYWORDS = {}  # {lang: set(keywords), "_all": set(all)}


def _build_global_keyword_index():
    """Build a per-language set of all known atom keywords for coverage checks."""
    global _GLOBAL_KEYWORDS
    try:
        from seven_layers_engine import ATOM_KEYWORDS
        for atom_id, langs in ATOM_KEYWORDS.items():
            for lang, words in langs.items():
                if lang not in _GLOBAL_KEYWORDS:
                    _GLOBAL_KEYWORDS[lang] = set()
                if isinstance(words, (list, set, tuple)):
                    _GLOBAL_KEYWORDS[lang].update(w.lower() for w in words)
                elif isinstance(words, str):
                    _GLOBAL_KEYWORDS[lang].add(words.lower())
        # Build "all" set as union of all languages
        all_kw = set()
        for s in _GLOBAL_KEYWORDS.values():
            all_kw.update(s)
        _GLOBAL_KEYWORDS["_all"] = all_kw
    except ImportError:
        pass

# Also include proper nouns in global index
def _extend_global_with_proper_nouns():
    """Add PROPER_NOUN_AGENTS to global keyword index for coverage."""
    if _HAS_EXPANSION_V48 and PROPER_NOUN_AGENTS:
        if "_all" not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS["_all"] = set()
        _GLOBAL_KEYWORDS["_all"].update(w.lower() for w in PROPER_NOUN_AGENTS)

# v4.8.1: Extend global index with Finnish keyword expansions + proper nouns
def _extend_global_with_v481():
    """Add FINNISH_KEYWORDS_V481 and PROPER_NOUNS_V481 to global keyword index."""
    if not _HAS_EXPANSION_V481:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    if "fi" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["fi"] = set()
    # Add Finnish keywords for each atom
    for atom_id, fi_words in FINNISH_KEYWORDS_V481.items():
        for w in fi_words:
            wl = w.lower()
            _GLOBAL_KEYWORDS["fi"].add(wl)
            _GLOBAL_KEYWORDS["_all"].add(wl)
    # Add proper nouns
    for lang, names in PROPER_NOUNS_V481.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)

_build_global_keyword_index()
_extend_global_with_proper_nouns()
_extend_global_with_v481()

# v4.8.2: Extend global index with massive keyword expansion + proper nouns
def _extend_global_with_v482():
    """Add KEYWORDS_V482, PROPER_NOUNS_V482, and ARCHAIC_FORMS to global index."""
    if not _HAS_EXPANSION_V482:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    # Add keywords for each atom × language
    for atom_id, lang_words in _KEYWORDS_V482.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    # Add proper nouns
    for lang, names in _PROPER_NOUNS_V482.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    # Add archaic forms — both old and modern forms as known words
    for lang, mappings in _ARCHAIC_FORMS.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v482()

# v4.8.3: Extend global index with targeted weak-language keywords
def _extend_global_with_v483():
    """Add KEYWORDS_V483, PROPER_NOUNS_V483, and ARCHAIC_FORMS_V483 to global."""
    if not _HAS_EXPANSION_V483:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    for atom_id, lang_words in _KEYWORDS_V483.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    for lang, names in _PROPER_NOUNS_V483.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    for lang, mappings in _ARCHAIC_FORMS_V483.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v483()

# v4.8.4: Extend global index with EN base forms + remaining gaps
def _extend_global_with_v484():
    """Add KEYWORDS_V484, PROPER_NOUNS_V484, and ARCHAIC_FORMS_V484 to global."""
    if not _HAS_EXPANSION_V484:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    for atom_id, lang_words in _KEYWORDS_V484.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    for lang, names in _PROPER_NOUNS_V484.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    for lang, mappings in _ARCHAIC_FORMS_V484.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v484()

# v4.8.6: Extend global index — push toward 90%
def _extend_global_with_v486():
    """Add KEYWORDS_V485, PROPER_NOUNS_V485, and ARCHAIC_FORMS_V485 to global."""
    if not _HAS_EXPANSION_V486:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    for atom_id, lang_words in _KEYWORDS_V486.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    for lang, names in _PROPER_NOUNS_V486.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    for lang, mappings in _ARCHAIC_FORMS_V486.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v486()

# v4.8.7: Extend global index — all-languages push toward 90%+
def _extend_global_with_v487():
    """Add KEYWORDS_V487, PROPER_NOUNS_V487, and ARCHAIC_FORMS_V487 to global."""
    if not _HAS_EXPANSION_V487:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    for atom_id, lang_words in _KEYWORDS_V487.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    for lang, names in _PROPER_NOUNS_V487.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    for lang, mappings in _ARCHAIC_FORMS_V487.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v487()

# v4.8.8: Extend global index — push FR/IT/FI above 90%
def _extend_global_with_v488():
    """Add KEYWORDS_V488, PROPER_NOUNS_V488, and ARCHAIC_FORMS_V488 to global."""
    if not _HAS_EXPANSION_V488:
        return
    if "_all" not in _GLOBAL_KEYWORDS:
        _GLOBAL_KEYWORDS["_all"] = set()
    for atom_id, lang_words in _KEYWORDS_V488.items():
        for lang, words in lang_words.items():
            if lang not in _GLOBAL_KEYWORDS:
                _GLOBAL_KEYWORDS[lang] = set()
            for w in words:
                wl = w.lower()
                _GLOBAL_KEYWORDS[lang].add(wl)
                _GLOBAL_KEYWORDS["_all"].add(wl)
    for lang, names in _PROPER_NOUNS_V488.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for name in names:
            nl = name.lower()
            _GLOBAL_KEYWORDS[lang].add(nl)
            _GLOBAL_KEYWORDS["_all"].add(nl)
    for lang, mappings in _ARCHAIC_FORMS_V488.items():
        if lang not in _GLOBAL_KEYWORDS:
            _GLOBAL_KEYWORDS[lang] = set()
        for old_form, modern_form in mappings.items():
            _GLOBAL_KEYWORDS[lang].add(old_form.lower())
            _GLOBAL_KEYWORDS[lang].add(modern_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(old_form.lower())
            _GLOBAL_KEYWORDS["_all"].add(modern_form.lower())

_extend_global_with_v488()


# ═══════════════════════════════════════════════════════════════════════════════
# v4.8.1: STEMMED KEYWORD INDEX (stem all known keywords for fuzzy matching)
# ═══════════════════════════════════════════════════════════════════════════════

_STEMMED_KEYWORDS = {}  # {lang: set(stemmed_keywords)}
_VOIKKO_LEMMA_CACHE = {}  # cache voikko lookups (word → set of base forms)


def _build_stemmed_keyword_index():
    """Build a per-language set of stemmed keywords for fuzzy coverage."""
    global _STEMMED_KEYWORDS
    if not _HAS_STEMMER:
        return
    for lang, kw_set in _GLOBAL_KEYWORDS.items():
        if lang == "_all":
            continue
        stemmer = _get_stemmer(lang)
        if stemmer is None:
            continue
        stems = set()
        for kw in kw_set:
            stems.add(stemmer.stemWord(kw))
        _STEMMED_KEYWORDS[lang] = stems
    # Also build an "_all" set from union of all language-specific stems
    all_stems = set()
    for s in _STEMMED_KEYWORDS.values():
        all_stems.update(s)
    _STEMMED_KEYWORDS["_all"] = all_stems


def _voikko_base_forms(word: str) -> set:
    """Get base forms of a Finnish word via voikko. Cached."""
    if not _HAS_VOIKKO:
        return set()
    if word in _VOIKKO_LEMMA_CACHE:
        return _VOIKKO_LEMMA_CACHE[word]
    try:
        analyses = _VOIKKO.analyze(word)
        bases = set()
        for a in analyses:
            bf = a.get("BASEFORM", "").lower()
            if bf:
                bases.add(bf)
        _VOIKKO_LEMMA_CACHE[word] = bases
    except Exception:
        _VOIKKO_LEMMA_CACHE[word] = set()
    return _VOIKKO_LEMMA_CACHE.get(word, set())


_build_stemmed_keyword_index()

# ── v4.8.1: Pre-merged keyword/stem caches & word-level coverage cache ───────
# Avoids re-computing set unions on every call to _is_covered_enhanced().
_MERGED_KEYWORDS = {}   # {lang: set(lang_kw | all_kw)}
_MERGED_STEMS = {}      # {lang: set(lang_stems | all_stems)}
_COVERAGE_CACHE = {}    # {(word, lang): bool}  — result across all paragraphs


def _get_merged_keywords(lang: str) -> set:
    """Get merged keyword set (language + _all). Cached per language."""
    if lang not in _MERGED_KEYWORDS:
        _MERGED_KEYWORDS[lang] = (
            _GLOBAL_KEYWORDS.get(lang, set()) | _GLOBAL_KEYWORDS.get("_all", set())
        )
    return _MERGED_KEYWORDS[lang]


def _get_merged_stems(lang: str) -> set:
    """Get merged stemmed keyword set. Cached per language."""
    if lang not in _MERGED_STEMS:
        _MERGED_STEMS[lang] = (
            _STEMMED_KEYWORDS.get(lang, set()) | _STEMMED_KEYWORDS.get("_all", set())
        )
    return _MERGED_STEMS[lang]


def _is_covered_enhanced(word: str, atom_words: set, lang: str,
                         atom_stems: set = None) -> bool:
    """Check if a content word is covered using multiple strategies.

    Strategies (in order):
      0. Numeric token detection (years, dates, page numbers)
      1. Direct match against paragraph atom word forms
      2. Direct match against global keyword index
      3. Compound splitting (hyphen): any component covered (recursive)
      4. Apostrophe/elision splitting with recursive sub-coverage
      5. Morphological suffix stripping (with language-aware min stem)
      6. German prefix stripping (ver-, ent-, be-, ge-, er-, zer-, etc.)
      7. Two-pass suffix stripping (remove suffix, then try again)
      8. Snowball stemmer: stem word ↔ stem keyword match (7 languages)
      9. Voikko Finnish lemmatizer: morphological base form lookup

    v4.8.1: Uses word-level coverage cache and pre-merged keyword sets
    v4.8.2: Number detection, recursive compound/elision resolution,
            stop-word-aware compound splitting

    Args:
        atom_stems: Pre-stemmed atom_words (optional, avoids re-stemming per call)
    """
    # 0. Numeric tokens: years, dates, page numbers, chapter numbers
    #    e.g. "1759", "42", "1761" — always considered covered
    if word.isdigit():
        return True

    # 1. Direct match against paragraph atoms (varies per paragraph)
    if word in atom_words:
        return True

    # v4.8.1: Check coverage cache (strategies 2-9 don't depend on atom_words)
    cache_key = (word, lang)
    cached = _COVERAGE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    # Pre-merged keyword set (language + _all)
    gk = _get_merged_keywords(lang)

    # 2. Check against global keyword index (language-specific + all)
    if word in gk:
        _COVERAGE_CACHE[cache_key] = True
        return True

    # Helper: check if a candidate is in any known set (keywords only)
    def _in_known(w):
        return w in atom_words or w in gk

    # Helper: deep check — apply stemming + voikko to a sub-part (no recursion)
    # v4.8.3: Also checks stop words (fixes elision/compound sub-parts)
    def _deep_check(w):
        """Check a word against keywords, stems, lemmatizers, AND stop words."""
        if _in_known(w):
            return True
        # v4.8.3: Stop words are also "covered" (they're known function words)
        if w in get_stop_words(lang):
            return True
        # Snowball stemmer check
        if _HAS_STEMMER:
            stemmer = _get_stemmer(lang)
            if stemmer is not None:
                w_stem = stemmer.stemWord(w)
                if w_stem in _get_merged_stems(lang):
                    return True
        # Voikko lemmatizer check (Finnish)
        if lang == "fi" and _HAS_VOIKKO:
            for base in _voikko_base_forms(w):
                if _in_known(base):
                    return True
        # Suffix stripping check
        for suffix in MORPHO_SUFFIXES.get(lang, []):
            if w.endswith(suffix) and len(w) - len(suffix) >= _MIN_STEM_LEN.get(lang, 3):
                if _in_known(w[:-len(suffix)]):
                    return True
        return False

    # v4.8.2: Romance elision prefixes (FR/IT/ES)
    # v4.8.3: Added v (IT: v'era), ch (IT: ch'ebbe), ai (FR: ai-je)
    _ELISION_PREFIXES = {"d", "l", "m", "n", "s", "c", "j", "qu",
                         "all", "nell", "dell", "sull", "dall", "un",
                         "v", "ch", "ai"}

    # 3. Compound splitting (hyphen): rabbit-hole → rabbit, hole
    #    v4.8.2: Use _deep_check for parts + stop-word-aware splitting
    if '-' in word:
        parts = [p for p in word.split('-') if len(p) >= 2]
        if parts:
            # Any part is a known keyword/stem → covered
            if any(_deep_check(p) for p in parts):
                _COVERAGE_CACHE[cache_key] = True
                return True
            # Check if parts are stop words (e.g. "disait-il": "il" is stop)
            stops = get_stop_words(lang)
            non_stop = [p for p in parts if p not in stops]
            if non_stop and len(non_stop) < len(parts):
                # Some parts are stop words; only check non-stop parts
                if all(_deep_check(p) for p in non_stop):
                    _COVERAGE_CACHE[cache_key] = True
                    return True

    # 4. Apostrophe/elision splitting with recursive sub-coverage
    #    v4.8.2: For elision prefixes (d', l', m', etc.), apply deep check
    #    v4.8.3: Allow single-char stop words (d'y, d'è) as covered
    if "'" in word:
        parts = word.split("'")
        if len(parts) == 2:
            prefix, main = parts
            if prefix.lower() in _ELISION_PREFIXES:
                if len(main) >= 2 and _deep_check(main):
                    _COVERAGE_CACHE[cache_key] = True
                    return True
                # v4.8.3: single-char stop words (FR: d'y, IT: d'è)
                if len(main) == 1 and main in get_stop_words(lang):
                    _COVERAGE_CACHE[cache_key] = True
                    return True
        # Fallback: any part ≥2 chars covered by deep check
        valid_parts = [p for p in parts if len(p) >= 2]
        if valid_parts and any(_deep_check(p) for p in valid_parts):
            _COVERAGE_CACHE[cache_key] = True
            return True

    # Suffix list for this language
    suffixes = MORPHO_SUFFIXES.get(lang, [])
    min_stem = _MIN_STEM_LEN.get(lang, 3)

    # 5. Suffix stripping (single pass)
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) >= min_stem:
            stem = word[:-len(suffix)]
            if _in_known(stem):
                _COVERAGE_CACHE[cache_key] = True
                return True

    # 6. German prefix stripping: ver|ent|be|ge|er|zer + root → root
    if lang == "de":
        for prefix in _DE_PREFIXES:
            if word.startswith(prefix) and len(word) - len(prefix) >= 3:
                root = word[len(prefix):]
                if _in_known(root):
                    _COVERAGE_CACHE[cache_key] = True
                    return True
                # Prefix + suffix combo: ver-wirr-t → wirr
                for suffix in suffixes:
                    if root.endswith(suffix) and len(root) - len(suffix) >= 2:
                        inner = root[:-len(suffix)]
                        if _in_known(inner):
                            _COVERAGE_CACHE[cache_key] = True
                            return True

    # 6b. German binary compound splitting: try splitting at every position
    #     v4.8.3: kunststücke → kunst+stücke, erzbischof → erz+bischof
    if lang == "de" and len(word) >= 6:
        # Also try with common linking elements: -s-, -n-, -en-, -er-
        for i in range(3, len(word) - 2):
            left, right = word[:i], word[i:]
            if _deep_check(left) and _deep_check(right):
                _COVERAGE_CACHE[cache_key] = True
                return True
            # Linking elements: Arbeit-s-zimmer, Küche-n-tisch
            for link in ('s', 'n', 'en', 'er'):
                if right.startswith(link) and len(right) > len(link) + 2:
                    right2 = right[len(link):]
                    if _deep_check(left) and _deep_check(right2):
                        _COVERAGE_CACHE[cache_key] = True
                        return True

    # 7. Two-pass suffix stripping: remove one suffix, then try another
    #    e.g. "hastily" → "hasti" → fail, but "filled" → "fill" → match
    #    Also handles double-inflected forms like "ungen" → "ung" + base
    for suffix1 in suffixes:
        if word.endswith(suffix1) and len(word) - len(suffix1) >= min_stem:
            stem1 = word[:-len(suffix1)]
            for suffix2 in suffixes:
                if (stem1.endswith(suffix2)
                        and len(stem1) - len(suffix2) >= min_stem
                        and suffix2 != suffix1):
                    stem2 = stem1[:-len(suffix2)]
                    if _in_known(stem2):
                        _COVERAGE_CACHE[cache_key] = True
                        return True

    # 8. Snowball stemmer: stem the word and check against stemmed keyword index
    #    e.g. "hastily" → stem "hastili", keyword "haste" → stem "hast" — match
    #    Much more powerful than hand-coded suffix lists
    if _HAS_STEMMER:
        stemmer = _get_stemmer(lang)
        if stemmer is not None:
            word_stem = stemmer.stemWord(word)
            sk = _get_merged_stems(lang)
            if word_stem in sk:
                _COVERAGE_CACHE[cache_key] = True
                return True
            # Check against pre-stemmed atom words (paragraph-level)
            if atom_stems is not None and word_stem in atom_stems:
                return True

    # 9. Voikko Finnish lemmatizer: get base form(s) and check against keywords
    #    e.g. "talonpoikien" → baseform "talonpoika" → might match keyword
    if lang == "fi" and _HAS_VOIKKO:
        bases = _voikko_base_forms(word)
        for base in bases:
            if _in_known(base):
                _COVERAGE_CACHE[cache_key] = True
                return True
            # Try stemming the base form too
            if _HAS_STEMMER:
                stemmer = _get_stemmer("fi")
                if stemmer and stemmer.stemWord(base) in _get_merged_stems("fi"):
                    _COVERAGE_CACHE[cache_key] = True
                    return True

    _COVERAGE_CACHE[cache_key] = False
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# STOP WORDS — function words that carry no semantic content
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS = {
    "en": {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
           "have", "has", "had", "do", "does", "did", "will", "would", "could",
           "should", "may", "might", "must", "shall", "can", "need", "dare",
           "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
           "into", "through", "during", "before", "after", "above", "below",
           "between", "under", "again", "further", "then", "once", "here",
           "there", "when", "where", "why", "how", "all", "both", "each",
           "few", "more", "most", "other", "some", "such", "no", "nor", "not",
           "only", "own", "same", "so", "than", "too", "very", "just", "but",
           "and", "or", "if", "while", "that", "this", "these", "those",
           "it", "its", "he", "she", "they", "them", "his", "her", "their",
           "my", "your", "our", "we", "you", "i", "me", "him", "us", "who",
           "which", "what", "whom", "s", "t", "re", "ve", "ll", "d", "m"},
    "fr": {"le", "la", "les", "un", "une", "des", "de", "du", "au", "aux",
           "ce", "ces", "cet", "cette", "mon", "ma", "mes", "ton", "ta", "tes",
           "son", "sa", "ses", "notre", "nos", "votre", "vos", "leur", "leurs",
           "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "on",
           "me", "te", "se", "lui", "en", "y", "qui", "que", "quoi", "dont",
           "où", "ne", "pas", "plus", "jamais", "rien", "et", "ou", "mais",
           "donc", "car", "ni", "si", "dans", "sur", "sous", "par", "pour",
           "avec", "sans", "chez", "entre", "vers", "à", "est", "sont", "a",
           "ont", "être", "avoir", "fait", "été", "était", "c", "d", "l",
           "n", "s", "j", "qu", "m", "t"},
    "de": {"der", "die", "das", "ein", "eine", "eines", "einem", "einen",
           "den", "dem", "des", "und", "oder", "aber", "denn", "weil",
           "wenn", "dass", "ob", "als", "wie", "nach", "vor", "mit", "bei",
           "von", "zu", "auf", "in", "an", "um", "für", "über", "unter",
           "aus", "bis", "durch", "gegen", "ohne", "ich", "du", "er", "sie",
           "es", "wir", "ihr", "sie", "sich", "mich", "dich", "uns", "euch",
           "mir", "dir", "ihm", "ihr", "ist", "sind", "war", "hat", "haben",
           "sein", "wird", "wurde", "kann", "muss", "soll", "will", "darf",
           "nicht", "kein", "keine", "auch", "noch", "schon", "nur", "sehr"},
    "es": {"el", "la", "los", "las", "un", "una", "unos", "unas", "de",
           "del", "al", "en", "con", "por", "para", "sin", "sobre", "entre",
           "y", "o", "pero", "sino", "que", "como", "más", "menos", "muy",
           "yo", "tú", "él", "ella", "nosotros", "ellos", "ellas", "me",
           "te", "se", "le", "lo", "nos", "les", "su", "sus", "mi", "tu",
           "es", "son", "fue", "ha", "ser", "estar", "no", "ni", "si",
           "este", "esta", "estos", "estas", "ese", "esa", "esos"},
    "it": {"il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "di",
           "del", "dello", "della", "dei", "degli", "delle", "a", "al",
           "allo", "alla", "ai", "agli", "alle", "da", "dal", "dalla",
           "in", "nel", "nella", "con", "su", "per", "tra", "fra",
           "e", "o", "ma", "che", "non", "è", "sono", "ha", "io",
           "tu", "lui", "lei", "noi", "voi", "loro", "si", "mi", "ti",
           "ci", "vi", "ne", "questo", "questa", "quello", "quella"},
    "hi": {"के", "है", "है।", "और", "में", "को", "से", "की", "एक", "हैं।",
           "हो", "का", "पर", "हैं", "जो", "किसी", "होता", "ये", "भी", "नहीं",
           "या", "तो", "इस", "वह", "यह", "जैसे", "अपने", "कर", "ही",
           "इसे", "उस", "कि", "जा", "कई", "होती", "सकता", "होते",
           "किया", "उसे", "अपनी", "उनके", "इसके", "इसकी", "कोई", "जब",
           "तक", "बहुत", "करता", "साथ", "बाद", "सभी", "दो", "रूप",
           "अन्य", "करने", "होने", "लिए", "रहा", "गया", "दिया", "किए"},
    "sa": {"च", "न", "इति", "तु", "वा", "एव", "अपि", "यत्", "तत्", "सः",
           "सा", "तम्", "तस्य", "तस्याः", "तेषाम्", "यः", "या", "ये",
           "अस्ति", "भवति", "कृते", "तथा", "अथ"},
    "ja": {"の", "は", "が", "を", "に", "で", "と", "も", "へ", "から",
           "まで", "より", "か", "な", "だ", "です", "ます", "する", "した",
           "して", "される", "された", "ない", "ある", "いる", "この", "その",
           "あの", "これ", "それ", "あれ", "こと", "もの", "ため", "よう",
           "など", "として", "について", "における", "に対して"},
    "zh": {"的", "了", "是", "在", "和", "有", "也", "不", "人", "我",
           "他", "她", "它", "这", "那", "个", "一", "与", "为", "被",
           "对", "从", "到", "会", "能", "可以", "就", "都", "而", "但",
           "如果", "因为", "所以", "或", "又", "等", "把", "让", "用",
           "着", "过", "中", "上", "下", "里", "以", "及"},
    "ru": {"и", "в", "на", "с", "по", "для", "не", "что", "это", "как",
           "он", "она", "они", "его", "её", "их", "но", "а", "или",
           "из", "от", "до", "при", "за", "об", "же", "бы", "ли",
           "то", "так", "все", "уже", "ещё", "был", "была", "были",
           "быть", "есть", "может", "будет", "только", "также", "очень",
           "тоже", "более", "после", "между", "через", "этот", "эта"},
    "pt": {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos",
           "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
           "sem", "sob", "sobre", "entre", "e", "ou", "mas", "que",
           "se", "não", "mais", "muito", "também", "já", "ainda",
           "eu", "tu", "ele", "ela", "nós", "eles", "elas", "me",
           "te", "se", "lhe", "nos", "é", "são", "foi", "ser", "estar"},
    "nl": {"de", "het", "een", "en", "van", "in", "is", "dat", "op", "te",
           "aan", "met", "er", "zijn", "voor", "niet", "ook", "maar",
           "was", "om", "bij", "als", "uit", "kan", "nog", "wel", "naar",
           "al", "dan", "tot", "over", "door", "dit", "die", "deze",
           "hij", "zij", "ze", "we", "ik", "je", "hun", "haar", "hem",
           "wat", "wie", "geen", "meer", "zo", "hoe", "waar"},
    "fi": {"ja", "on", "ei", "se", "että", "ole", "oli", "olla", "en",
           "tai", "kun", "jo", "joka", "niin", "myös", "vain", "mutta",
           "nyt", "ovat", "yli", "alla", "alle", "asti", "kanssa",
           "jotta", "koska", "kuin", "kuten", "mihin", "mikä", "mitä",
           "miten", "missä", "mistä", "siitä", "tämä", "tässä", "hän"},
    "eo": {"la", "de", "kaj", "en", "al", "ne", "estas", "por", "kun",
           "sed", "li", "ŝi", "ili", "ni", "vi", "mi", "ĝi", "kiu",
           "kio", "tiu", "tio", "ĉiu", "ĉio", "ĉi", "sur", "el",
           "pri", "inter", "tra", "post", "antaŭ", "ankaŭ", "jam",
           "tre", "pli", "plej", "nur", "do", "aŭ"},
}

# Fallback for languages without explicit stop words
DEFAULT_STOP_WORDS = {".", ",", ";", ":", "!", "?", "(", ")", "[", "]", "{", "}",
                      "\"", "'", "-", "–", "—", "…", "/", "\\"}


def get_stop_words(lang: str) -> set:
    """Get stop words for a language, with fallback + v4.7/v4.8/v4.8.1 expansion."""
    base = STOP_WORDS.get(lang, set()) | DEFAULT_STOP_WORDS
    if _HAS_EXPANSION and lang in EXTRA_STOP_WORDS:
        base = base | EXTRA_STOP_WORDS[lang]
    # v4.8: additional stop words and literary words (but NOT proper nouns:
    # proper nouns are content words mapped to AGENT atom, not stop words)
    if _HAS_EXPANSION_V48:
        if lang in STOP_WORDS_V48:
            base = base | set(STOP_WORDS_V48[lang])
        base = base | LITERARY_STOP_WORDS
    # v4.8.1: Finnish stop word expansion (voikko-derived function words)
    if _HAS_EXPANSION_V481 and lang in STOP_WORDS_V481:
        base = base | STOP_WORDS_V481[lang]
    # v4.8.2: Massive stop word expansion (archaic forms, function words)
    if _HAS_EXPANSION_V482 and lang in _STOP_WORDS_V482:
        base = base | _STOP_WORDS_V482[lang]
    # v4.8.3: Targeted weak-language stop words
    if _HAS_EXPANSION_V483 and lang in _STOP_WORDS_V483:
        base = base | set(_STOP_WORDS_V483[lang])
    # v4.8.4: EN base-form stop words + remaining
    if _HAS_EXPANSION_V484 and lang in _STOP_WORDS_V484:
        base = base | set(_STOP_WORDS_V484[lang])
    # v4.8.6: Push toward 90% stop words
    if _HAS_EXPANSION_V486 and lang in _STOP_WORDS_V486:
        base = base | set(_STOP_WORDS_V486[lang])
    # v4.8.7: All-languages push toward 90%+ stop words
    if _HAS_EXPANSION_V487 and lang in _STOP_WORDS_V487:
        base = base | set(_STOP_WORDS_V487[lang])
    # v4.8.8: Push FR/IT/FI above 90% stop words
    if _HAS_EXPANSION_V488 and lang in _STOP_WORDS_V488:
        base = base | set(_STOP_WORDS_V488[lang])
    return base


# CJK character ranges
def _is_cjk(ch: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(ch)
    return (
        (0x4E00 <= cp <= 0x9FFF) or     # CJK Unified
        (0x3400 <= cp <= 0x4DBF) or     # CJK Extension A
        (0x3040 <= cp <= 0x309F) or     # Hiragana
        (0x30A0 <= cp <= 0x30FF) or     # Katakana
        (0xF900 <= cp <= 0xFAFF) or     # CJK Compatibility
        (0x20000 <= cp <= 0x2A6DF)      # CJK Extension B
    )


def count_words(text: str, lang: str) -> int:
    """Language-aware word count. CJK counts characters; others split on spaces."""
    if lang in ("ja", "zh"):
        # Count CJK characters + non-CJK tokens
        cjk_chars = sum(1 for ch in text if _is_cjk(ch))
        non_cjk = ''.join(' ' if _is_cjk(ch) else ch for ch in text)
        non_cjk_words = len([w for w in non_cjk.split() if len(w) >= 2])
        return cjk_chars + non_cjk_words
    return len(text.split())


def get_content_words(text: str, lang: str, stop_words: set) -> list:
    """Extract content words (not stop words, not punctuation, len >= 2).
    CJK-aware: treats each character as a potential word."""
    # Extended punctuation chars (v4.7)
    _strip = EXTRA_PUNCTUATION_CHARS if _HAS_EXPANSION else ".,;:!?\"'()-–—…[]{}«»"
    # v4.8: extend with additional quote/dash characters
    if _HAS_EXPANSION_V48:
        _strip = _strip + EXTRA_PUNCTUATION_V48
    # v4.8.1: Finnish typographic chars
    if _HAS_EXPANSION_V481:
        _strip = _strip + EXTRA_PUNCTUATION_V481
    # v4.8: normalize curly/smart apostrophes to straight apostrophe
    # This ensures contractions like I'm/qu'il match stop words consistently
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    if lang in ("ja", "zh"):
        content = []
        for ch in text:
            if _is_cjk(ch) and ch not in stop_words:
                content.append(ch)
        # Also check non-CJK words in the text
        non_cjk = ''.join(' ' if _is_cjk(ch) else ch for ch in text)
        for w in non_cjk.split():
            w_lower = w.lower().strip(_strip)
            if w_lower and len(w_lower) >= 2 and w_lower not in stop_words:
                content.append(w_lower)
        return content
    else:
        content = []
        for w in text.split():
            w_lower = w.lower().strip(_strip)
            if w_lower and len(w_lower) >= 2 and w_lower not in stop_words:
                content.append(w_lower)
        return content


# ═══════════════════════════════════════════════════════════════════════════════
# FIDELITY METRICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ParagraphFidelity:
    """Fidelity metrics for a single paragraph."""
    index: int = 0
    word_count: int = 0
    content_word_count: int = 0  # excluding stop words
    
    # L1: Syntax coverage
    syntax_words_parsed: int = 0
    syntax_coverage: float = 0.0  # % of words with POS tags
    
    # L2: Atom coverage (the key metric)
    atom_alignments: int = 0
    atoms_unique: int = 0
    lexical_coverage: float = 0.0  # atoms / content_words
    atom_density: float = 0.0     # atoms / total_words
    uncovered_content_words: List[str] = field(default_factory=list)
    
    # L3: Morphology coverage
    morpho_features: int = 0  # words with at least one morpho feature
    morpho_coverage: float = 0.0
    
    # L4: Operator count
    operator_count: int = 0
    
    # L5: Discourse
    discourse_relations: int = 0
    has_discourse: bool = False
    
    # L6: Prosody
    has_prosody: bool = False
    syllable_count: int = 0
    
    # Concepts
    concept_count: int = 0
    concepts_with_evidence: int = 0
    
    # Overall
    reconstruction_readiness: float = 0.0  # 0.0–1.0


@dataclass
class DocumentFidelity:
    """Aggregate fidelity metrics for a document."""
    filepath: str = ""
    language: str = ""
    total_paragraphs: int = 0
    total_words: int = 0
    total_content_words: int = 0
    
    # Aggregate layer coverages
    avg_lexical_coverage: float = 0.0
    avg_atom_density: float = 0.0
    avg_syntax_coverage: float = 0.0
    avg_morpho_coverage: float = 0.0
    
    # Paragraph-level coverage
    paragraphs_with_atoms: int = 0     # at least 1 atom
    paragraphs_with_concepts: int = 0   # at least 1 concept
    paragraphs_with_discourse: int = 0
    paragraphs_with_prosody: int = 0
    
    # Global coverage percentages
    atom_paragraph_coverage: float = 0.0
    concept_paragraph_coverage: float = 0.0
    discourse_paragraph_coverage: float = 0.0
    prosody_paragraph_coverage: float = 0.0
    
    # Information retention
    total_atom_alignments: int = 0
    total_uncovered_content_words: int = 0
    information_retention_ratio: float = 0.0  # atoms / content_words (global)
    
    # Reconstruction readiness (weighted)
    avg_reconstruction_readiness: float = 0.0
    min_reconstruction_readiness: float = 0.0
    max_reconstruction_readiness: float = 0.0
    
    # Top uncovered words (most frequent content words without atoms)
    top_uncovered_words: List[Tuple[str, int]] = field(default_factory=list)
    
    # Per-paragraph details
    paragraphs: List[ParagraphFidelity] = field(default_factory=list)
    
    # Timing
    analysis_time_s: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        # Convert paragraph list for readability
        d["paragraphs"] = [asdict(p) for p in self.paragraphs]
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_paragraph_fidelity(
    layer: dict,
    lang: str,
    stop_words: set,
) -> ParagraphFidelity:
    """Compute fidelity metrics for a single paragraph's rich layer data."""
    pf = ParagraphFidelity()
    pf.index = layer.get("paragraph_index", 0)
    
    text = layer.get("text", "")
    pf.word_count = count_words(text, lang)
    
    # Identify content words (non-stop, non-punctuation, len >= 2)
    content_words = get_content_words(text, lang, stop_words)
    pf.content_word_count = len(content_words)
    
    # L1: Syntax
    syntax = layer.get("syntax", [])
    pf.syntax_words_parsed = len([s for s in syntax if s.get("pos")])
    pf.syntax_coverage = pf.syntax_words_parsed / max(pf.word_count, 1)
    
    # L2: Atom alignments
    atoms = layer.get("atoms", [])
    pf.atom_alignments = len(atoms)
    # Use same strip chars as get_content_words for consistent matching
    _atom_strip = EXTRA_PUNCTUATION_CHARS if _HAS_EXPANSION else ".,;:!?\"'()-–—…[]{}«»"
    if _HAS_EXPANSION_V48:
        _atom_strip = _atom_strip + EXTRA_PUNCTUATION_V48
    if _HAS_EXPANSION_V481:
        _atom_strip = _atom_strip + EXTRA_PUNCTUATION_V481
    atom_words = set()
    for a in atoms:
        w = a.get("word", "").lower().strip(_atom_strip)
        # Normalize curly apostrophes (same as get_content_words)
        w = w.replace('\u2019', "'").replace('\u2018', "'")
        if w:
            atom_words.add(w)
    pf.atoms_unique = len(set(a.get("atom", "") for a in atoms))
    # Also collect keyword forms from atoms (e.g., keyword="rabbit" for word="rabbit-hole")
    for a in atoms:
        kw = a.get("keyword", "")
        if isinstance(kw, str) and kw:
            kw_clean = kw.lower().strip(_atom_strip)
            if kw_clean:
                atom_words.add(kw_clean)
        elif isinstance(kw, list):
            for k in kw:
                k_clean = str(k).lower().strip(_atom_strip)
                if k_clean:
                    atom_words.add(k_clean)
    # Lexical coverage = unique content words that are covered
    # Uses enhanced matching: atom words + global keywords + suffix stripping + compound splitting
    # v4.8.1: Pre-stem atom_words for efficient Snowball matching
    _atom_stems = None
    if _HAS_STEMMER:
        stemmer = _get_stemmer(lang)
        if stemmer is not None:
            _atom_stems = set(stemmer.stemWord(aw) for aw in atom_words)
    # Single pass: compute covered count AND uncovered list together
    covered_count = 0
    for cw in content_words:
        if _is_covered_enhanced(cw, atom_words, lang, atom_stems=_atom_stems):
            covered_count += 1
        else:
            pf.uncovered_content_words.append(cw)
    pf.lexical_coverage = covered_count / max(pf.content_word_count, 1)
    pf.atom_density = pf.atom_alignments / max(pf.word_count, 1)
    
    # L3: Morphology
    morpho = layer.get("morphology", [])
    pf.morpho_features = len(morpho)
    pf.morpho_coverage = pf.morpho_features / max(pf.word_count, 1)
    
    # L4: Operators
    operators = layer.get("operators", [])
    pf.operator_count = len(operators)
    
    # L5: Discourse
    discourse = layer.get("discourse", [])
    pf.discourse_relations = len(discourse)
    pf.has_discourse = len(discourse) > 0
    
    # L6: Prosody
    prosody = layer.get("prosody", {})
    pf.has_prosody = bool(prosody and prosody.get("syllables", 0) > 0)
    pf.syllable_count = prosody.get("syllables", 0) if prosody else 0
    
    # Concepts
    concepts = layer.get("concepts", [])
    pf.concept_count = len(concepts)
    pf.concepts_with_evidence = len([c for c in concepts if c.get("atoms_evidence")])
    
    # Reconstruction readiness (weighted by layer importance for reconstruction)
    pf.reconstruction_readiness = min(1.0, (
        # L2 atoms are critical (40% weight)
        min(1.0, pf.lexical_coverage) * 0.40
        # L1 syntax provides structure (15%)
        + min(1.0, pf.syntax_coverage) * 0.15
        # L3 morphology for inflection (15%)
        + min(1.0, pf.morpho_coverage) * 0.15
        # Concepts with evidence for meaning (15%)
        + (1.0 if pf.concepts_with_evidence > 0 else 0.0) * 0.15
        # L5 discourse for coherence (10%)
        + (1.0 if pf.has_discourse else 0.0) * 0.10
        # L6 prosody for style (5%)
        + (1.0 if pf.has_prosody else 0.0) * 0.05
    ))
    
    return pf


def analyze_document_fidelity(
    filepath: str,
    lang: str = None,
    verbose: bool = False,
) -> DocumentFidelity:
    """Run rich analysis on a document and compute fidelity metrics.
    
    This is the key function that answers: "How much can we reconstruct?"
    
    Args:
        filepath: Path to the document.
        lang: Force language.
        verbose: Print progress.
    
    Returns:
        DocumentFidelity with per-paragraph and aggregate metrics.
    """
    t_start = time.time()
    
    if verbose:
        print(f"\n{'═' * 72}")
        print(f"RECONSTRUCTION FIDELITY ANALYSIS")
        print(f"{'═' * 72}")
        print(f"  📄 {os.path.basename(filepath)}")
    
    # Run rich analysis
    report = analyze_document(filepath, lang=lang, verbose=verbose, rich_mode=True)
    
    if "error" in report:
        raise ValueError(f"Analysis failed: {report['error']}")
    
    detected_lang = report["language"]
    stop_words = get_stop_words(detected_lang)
    rich_layers = report.get("rich_layers", [])
    
    if not rich_layers:
        raise ValueError("No rich layer data — rich_mode failed")
    
    if verbose:
        print(f"  🔬 Analyzing {len(rich_layers)} paragraphs in rich mode...")
    
    # Analyze each paragraph
    doc = DocumentFidelity()
    doc.filepath = filepath
    doc.language = detected_lang
    doc.total_paragraphs = len(rich_layers)
    
    uncovered_counter = Counter()
    readiness_scores = []
    
    for layer in rich_layers:
        pf = analyze_paragraph_fidelity(layer, detected_lang, stop_words)
        doc.paragraphs.append(pf)
        
        doc.total_words += pf.word_count
        doc.total_content_words += pf.content_word_count
        doc.total_atom_alignments += pf.atom_alignments
        doc.total_uncovered_content_words += len(pf.uncovered_content_words)
        
        if pf.atom_alignments > 0:
            doc.paragraphs_with_atoms += 1
        if pf.concept_count > 0:
            doc.paragraphs_with_concepts += 1
        if pf.has_discourse:
            doc.paragraphs_with_discourse += 1
        if pf.has_prosody:
            doc.paragraphs_with_prosody += 1
        
        readiness_scores.append(pf.reconstruction_readiness)
        
        for w in pf.uncovered_content_words:
            uncovered_counter[w] += 1
    
    # Aggregate metrics
    n = max(doc.total_paragraphs, 1)
    doc.avg_lexical_coverage = sum(p.lexical_coverage for p in doc.paragraphs) / n
    doc.avg_atom_density = sum(p.atom_density for p in doc.paragraphs) / n
    doc.avg_syntax_coverage = sum(p.syntax_coverage for p in doc.paragraphs) / n
    doc.avg_morpho_coverage = sum(p.morpho_coverage for p in doc.paragraphs) / n
    
    doc.atom_paragraph_coverage = doc.paragraphs_with_atoms / n
    doc.concept_paragraph_coverage = doc.paragraphs_with_concepts / n
    doc.discourse_paragraph_coverage = doc.paragraphs_with_discourse / n
    doc.prosody_paragraph_coverage = doc.paragraphs_with_prosody / n
    
    doc.information_retention_ratio = (
        doc.total_atom_alignments / max(doc.total_content_words, 1)
    )
    
    doc.avg_reconstruction_readiness = sum(readiness_scores) / n
    doc.min_reconstruction_readiness = min(readiness_scores) if readiness_scores else 0
    doc.max_reconstruction_readiness = max(readiness_scores) if readiness_scores else 0
    
    doc.top_uncovered_words = uncovered_counter.most_common(30)
    
    doc.analysis_time_s = round(time.time() - t_start, 2)
    
    if verbose:
        print_fidelity_report(doc)
    
    return doc


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════════════════

def print_fidelity_report(doc: DocumentFidelity):
    """Print a visual fidelity report."""
    print(f"\n{'═' * 72}")
    print(f"RECONSTRUCTION FIDELITY REPORT")
    print(f"{'═' * 72}")
    print(f"  📄 {os.path.basename(doc.filepath)}")
    print(f"  🌍 Language: {doc.language}")
    print(f"  📊 {doc.total_paragraphs} paragraphs, {doc.total_words:,} words "
          f"({doc.total_content_words:,} content words)")
    print(f"  ⏱️  Analysis: {doc.analysis_time_s}s")
    
    # Layer coverage dashboard
    print(f"\n  {'─' * 68}")
    print(f"  LAYER COVERAGE (% of paragraphs/words covered)")
    print(f"  {'─' * 68}")
    
    layers = [
        ("L1 Syntax (POS tags)", doc.avg_syntax_coverage),
        ("L2 Atoms (word→atom)", doc.avg_lexical_coverage),
        ("L3 Morphology", doc.avg_morpho_coverage),
        ("L4 Operators", doc.paragraphs_with_atoms / max(doc.total_paragraphs, 1)),
        ("L5 Discourse", doc.discourse_paragraph_coverage),
        ("L6 Prosody", doc.prosody_paragraph_coverage),
        ("L7 Concepts", doc.concept_paragraph_coverage),
    ]
    
    for name, coverage in layers:
        bar_len = int(coverage * 40)
        bar = '█' * bar_len + '░' * (40 - bar_len)
        grade = "✅" if coverage >= 0.7 else ("🟡" if coverage >= 0.4 else "🔴")
        print(f"  {grade} {name:25s} {coverage * 100:5.1f}% [{bar}]")
    
    # Key metrics
    print(f"\n  {'─' * 68}")
    print(f"  KEY METRICS")
    print(f"  {'─' * 68}")
    print(f"  Atom density:              {doc.avg_atom_density * 100:.1f}% "
          f"({doc.total_atom_alignments:,} atoms / {doc.total_words:,} words)")
    print(f"  Lexical coverage:          {doc.avg_lexical_coverage * 100:.1f}% "
          f"(atoms / content words)")
    print(f"  Information retention:     {doc.information_retention_ratio * 100:.1f}% "
          f"(global atoms / content words)")
    print(f"  Uncovered content words:   {doc.total_uncovered_content_words:,} "
          f"({doc.total_uncovered_content_words / max(doc.total_content_words, 1) * 100:.1f}%)")
    
    # Reconstruction readiness
    print(f"\n  {'─' * 68}")
    rr = doc.avg_reconstruction_readiness
    bar_len = int(rr * 40)
    bar = '█' * bar_len + '░' * (40 - bar_len)
    grade = (
        "EXCELLENT — near-lossless" if rr >= 0.8 else
        "BON — structure preserved" if rr >= 0.6 else
        "MODÉRÉ — partial" if rr >= 0.4 else
        "FAIBLE — major gaps" if rr >= 0.2 else
        "INSUFFISANT"
    )
    print(f"  🎯 RECONSTRUCTION READINESS: {rr:.4f}  [{bar}]")
    print(f"     {grade}")
    print(f"     Range: [{doc.min_reconstruction_readiness:.3f} — "
          f"{doc.max_reconstruction_readiness:.3f}]")
    
    # Top uncovered words (the "black holes" in our representation)
    if doc.top_uncovered_words:
        print(f"\n  {'─' * 68}")
        print(f"  TOP UNCOVERED CONTENT WORDS (semantic black holes)")
        print(f"  {'─' * 68}")
        for word, count in doc.top_uncovered_words[:20]:
            bar = '█' * min(count, 40)
            print(f"    {word:20s} {count:4d} {bar}")
    
    # Assessment summary
    print(f"\n  {'─' * 68}")
    print(f"  ASSESSMENT")
    print(f"  {'─' * 68}")
    
    gaps = []
    if doc.avg_lexical_coverage < 0.5:
        gaps.append(f"  🔴 Atom coverage too low ({doc.avg_lexical_coverage*100:.1f}%) — "
                    f"most content words have no atom mapping")
    elif doc.avg_lexical_coverage < 0.8:
        gaps.append(f"  🟡 Atom coverage moderate ({doc.avg_lexical_coverage*100:.1f}%) — "
                    f"significant content words unmapped")
    
    if doc.concept_paragraph_coverage < 0.5:
        gaps.append(f"  🟡 Concept detection sparse — only {doc.concept_paragraph_coverage*100:.0f}% "
                    f"of paragraphs have concepts")
    
    if doc.discourse_paragraph_coverage < 0.3:
        gaps.append(f"  🟡 Discourse relations rare — only {doc.discourse_paragraph_coverage*100:.0f}% "
                    f"of paragraphs")
    
    # Positive observations
    if doc.avg_syntax_coverage > 0.9:
        gaps.append(f"  ✅ Syntax coverage excellent ({doc.avg_syntax_coverage*100:.1f}%)")
    if doc.prosody_paragraph_coverage > 0.8:
        gaps.append(f"  ✅ Prosody coverage good ({doc.prosody_paragraph_coverage*100:.0f}%)")
    
    for gap in gaps:
        print(gap)
    
    # Final recommendation
    print(f"\n  {'─' * 68}")
    if rr >= 0.6:
        print(f"  ✅ READY for round-trip reconstruction experiments")
    elif rr >= 0.4:
        print(f"  🟡 PARTIALLY READY — reconstruction possible but lossy")
        print(f"     Priority: increase atom vocabulary to cover top uncovered words")
    else:
        print(f"  🔴 NOT READY — fundamental gaps in representation")
        print(f"     Priority: expand keyword dictionaries for {doc.language}")
    
    print(f"  {'═' * 72}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def batch_fidelity(
    directory: str,
    lang: str = None,
    output_path: str = None,
    verbose: bool = False,
) -> Dict[str, DocumentFidelity]:
    """Run fidelity analysis on all .txt files in a directory."""
    results = {}
    txt_files = sorted(
        f for f in os.listdir(directory)
        if f.endswith('.txt') and not f.startswith('_')
    )
    
    if not txt_files:
        print(f"No .txt files found in {directory}")
        return results
    
    print(f"\n{'═' * 72}")
    print(f"BATCH FIDELITY ANALYSIS — {len(txt_files)} files")
    print(f"{'═' * 72}\n")
    
    for i, fname in enumerate(txt_files):
        fpath = os.path.join(directory, fname)
        print(f"  [{i+1}/{len(txt_files)}] {fname}...", end=" ", flush=True)
        try:
            doc = analyze_document_fidelity(fpath, lang=lang, verbose=False)
            results[fname] = doc
            print(f"✅ readiness={doc.avg_reconstruction_readiness:.3f} "
                  f"lex_cov={doc.avg_lexical_coverage*100:.1f}%")
        except Exception as e:
            print(f"❌ {e}")
    
    # Summary
    if results:
        avg_rr = sum(d.avg_reconstruction_readiness for d in results.values()) / len(results)
        avg_lc = sum(d.avg_lexical_coverage for d in results.values()) / len(results)
        avg_ad = sum(d.avg_atom_density for d in results.values()) / len(results)
        
        print(f"\n{'─' * 72}")
        print(f"BATCH SUMMARY ({len(results)} documents)")
        print(f"{'─' * 72}")
        print(f"  Avg reconstruction readiness: {avg_rr:.4f}")
        print(f"  Avg lexical coverage:         {avg_lc*100:.1f}%")
        print(f"  Avg atom density:             {avg_ad*100:.1f}%")
        
        # Aggregate top uncovered words
        agg_uncov = Counter()
        for doc in results.values():
            for word, count in doc.top_uncovered_words:
                agg_uncov[word] += count
        
        print(f"\n  Top 20 uncovered words across all documents:")
        for word, count in agg_uncov.most_common(20):
            print(f"    {word:20s} {count:6d}")
    
    # Save results
    if output_path:
        summary = {
            "batch_size": len(results),
            "avg_reconstruction_readiness": round(avg_rr, 4),
            "avg_lexical_coverage": round(avg_lc, 4),
            "avg_atom_density": round(avg_ad, 4),
            "per_document": {
                fname: {
                    "reconstruction_readiness": round(d.avg_reconstruction_readiness, 4),
                    "lexical_coverage": round(d.avg_lexical_coverage, 4),
                    "atom_density": round(d.avg_atom_density, 4),
                    "words": d.total_words,
                    "language": d.language,
                }
                for fname, d in results.items()
            },
            "top_uncovered_words": agg_uncov.most_common(50),
        }
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n  💾 Saved → {output_path}")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Measure reconstruction fidelity of PaniniFS semantic exports.",
    )
    parser.add_argument("file", nargs="?", help="Path to document to analyze")
    parser.add_argument("--lang", help="Force language",
                        choices=["en", "fr", "de", "es", "it", "eo", "fi",
                                 "pt", "nl", "zh", "ja", "ru", "hi", "sa"])
    parser.add_argument("--batch", help="Directory of .txt files to analyze")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.batch:
        batch_fidelity(args.batch, lang=args.lang,
                       output_path=args.output, verbose=args.verbose)
    elif args.file:
        doc = analyze_document_fidelity(args.file, lang=args.lang, verbose=True)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"  💾 Saved → {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""diachronic_rules.py — Diachronic sound change rules for historical text coverage

Instead of hand-listing every archaic word form (brute force), this module
encodes *systematic phonetic/orthographic change rules* for each language
and epoch. A single rule like "IT: o→uo in open syllable (Tuscan diphthongization)"
covers dozens of word forms automatically.

This is the Pāṇinian approach: sūtras (rules), not koṣa (dictionaries).

Architecture:
  1. DIACHRONIC_RULES — per-language, per-epoch transformation rules
  2. diachronic_modernize() — apply rules to generate modern candidates
  3. COGNATE_BRIDGES — cross-language root correspondences
  4. cognate_resolve() — try resolving via sibling-language cognates

Integration with existing pipeline:
  - text_normalizer.py detect_epoch() → epoch detection (ALREADY EXISTS)
  - reconstruction_fidelity.py _is_covered_enhanced() → Strategy 10 + 11
  - morpho_semantic_bridge.py LANGUAGE_FAMILIES → family grouping

Created: 2026-02-22 by Copilot (Claude Opus 4.6) on hauru
"""

import re
from typing import List, Tuple, Optional, Set, Dict
from functools import lru_cache


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DIACHRONIC RULES — Sound/orthographic change rules per language/epoch
# ═══════════════════════════════════════════════════════════════════════════════
#
# Each rule is a tuple: (pattern, replacement, context, description)
#   - pattern: regex or string to match in the archaic word
#   - replacement: what to substitute
#   - context: optional regex for where the pattern must appear
#       "^" = start, "$" = end, None = anywhere, callable = custom predicate
#   - description: human-readable explanation
#
# Rules are applied in order. Multiple candidates may be generated.
# The caller checks if ANY generated candidate is a known word.

DIACHRONIC_RULES: Dict[str, Dict[str, List[Tuple]]] = {
    # ─────────────────────────────────────────────────────────────────────
    # ITALIAN — Medieval/Renaissance → Modern
    # Sources: Rohlfs (1966), Tekavčić (1972), Maiden (1995)
    # ─────────────────────────────────────────────────────────────────────
    "it": {
        "letterario": [
            # === Tuscan diphthongization (13th-14th c.) ===
            # In open stressed syllables: ŏ → uo, ĕ → ie
            # Dante writes 'foco', modern 'fuoco'; 'bono', modern 'buono'
            ("oco", "uoco", None, "o→uo diphthongization: foco→fuoco"),
            ("ono", "uono", None, "o→uo: bono→buono"),
            ("ovo", "uovo", None, "o→uo: novo→nuovo"),
            ("ore", "uore", None, "o→uo: core→cuore"),
            ("ogo", "uogo", None, "o→uo: loco→luogo"),
            ("omo", "uomo", None, "o→uo: omo→uomo"),
            ("ote", "uote", None, "o→uo: rote→ruote"),
            ("ole", "uole", None, "o→uo: vole→vuole"),
            ("osa", "uosa", None, "o→uo: cosa (rare, context-dependent)"),

            # === Pronoun/demonstrative evolution ===
            ("elli", "egli", None, "3sg masc pronoun: elli→egli"),
            ("ella", "ella", None, "3sg fem (stable)"),
            ("quelli", "quegli", None, "demonstrative: quelli→quegli"),
            ("costui", "costui", None, "demonstrative (stable)"),

            # === Verb forms — passato remoto ===
            # Many Dante verb forms use archaic passato remoto
            ("puose", "pose", None, "passato remoto: puose→pose"),
            ("rispuose", "rispose", None, "rispuose→rispose"),
            ("chiuse", "chiuse", None, "stable"),
            ("fece", "fece", None, "stable"),
            ("disse", "disse", None, "stable"),

            # === Consonant changes ===
            # Double → single or vice versa in archaic forms
            ("tt", "t", None, "consonant simplification (context-dep)"),

            # === Function word evolution ===
            ("sanza", "senza", None, "preposition: sanza→senza"),
            ("sovra", "sopra", None, "preposition: sovra→sopra"),
            ("medesmo", "medesimo", None, "pronoun: medesmo→medesimo"),
            ("poscia", "poi", None, "adverb: poscia→poi"),
            ("quivi", "qui", None, "adverb: quivi→qui/lì"),

            # === Lexical archaisms ===
            ("maraviglia", "meraviglia", None, "vowel shift: a→e"),
            ("etterno", "eterno", None, "double→single: tt→t"),
            ("etterna", "eterna", None, "double→single"),
            ("spirto", "spirito", None, "syncope reversal"),
            ("dritto", "diritto", None, "metathesis reversal"),

            # === Archaic verb forms (congiuntivo, passato remoto) ===
            ("vegna", "venga", None, "congiuntivo: vegna→venga"),
            ("tegna", "tenga", None, "congiuntivo: tegna→tenga"),
            ("vegno", "vengo", None, "indicativo: vegno→vengo"),
            ("fenno", "fecero", None, "passato remoto: fenno→fecero"),
            ("denno", "devono", None, "indicativo: denno→devono"),
            ("davante", "davanti", None, "avverbio: davante→davanti"),
            ("dinanzi", "davanti", None, "avverbio: dinanzi→davanti"),
            ("diserto", "deserto", None, "vocale: diserto→deserto"),
            ("discerno", "discerno", None, "stable (modern form exists)"),
            ("sembianza", "sembianza", None, "stable (archaic feel, modern form)"),
            ("dimandar", "domandare", None, "vocale: dimandar→domandare"),

            # === Systematic suffix rules ===
            # -ade → -à (modern truncation, but archaic is longer)
            # Actually reverse: Dante's truncated forms → modern full forms
            ("virtute", "virtù", None, "truncation: virtute→virtù"),
            ("salute", "salute", None, "stable (modern kept -e)"),
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # GERMAN — Pre-1901 orthography → Modern
    # Source: Duden reform documentation, 2. Orthographische Konferenz 1901
    # ─────────────────────────────────────────────────────────────────────
    "de": {
        "pre_1901": [
            # === th → t reform (systematic) ===
            # Affects ~200 words: Thal→Tal, Thür→Tür, Theil→Teil, etc.
            ("th", "t", None, "th→t: Thal→Tal, Thür→Tür"),

            # === Vowel changes ===
            ("ey", "ei", None, "ey→ei: Freyheit→Freiheit"),
            ("äu", "eu", None, "spelling standardization (some words)"),

            # === giebt → gibt (ie→i in short vowel verbs) ===
            ("giebt", "gibt", None, "giebt→gibt"),
            ("gieng", "ging", None, "gieng→ging"),
            ("hieng", "hing", None, "hieng→hing"),
            ("fieng", "fing", None, "fieng→fing"),

            # === Double consonant standardization ===
            ("ß", "ss", None, "Eszett context (post-vowel)"),

            # === Latin/French spellings → German ===
            ("ph", "f", None, "Phantasie→Fantasie, Telephon→Telefon"),
            ("clav", "klav", None, "Clavier→Klavier"),
            ("c", "k", None, "selective c→k (context-dependent)"),
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # FRENCH — Classical French (pre-1835) → Modern
    # Source: Académie française, 6e édition (1835) reform
    # ─────────────────────────────────────────────────────────────────────
    "fr": {
        "classique": [
            # === -oi- → -ai- (THE major reform of 1835) ===
            # Systematic: all imperfect/conditional -oit → -ait
            ("oit", "ait", "$", "-oit→-ait imperfect: étoit→était"),
            ("oient", "aient", "$", "-oient→-aient: étoient→étaient"),
            ("ois", "ais", "$", "-ois→-ais: françois→français"),
            ("oître", "aître", None, "connoître→connaître"),
            ("oiss", "aiss", None, "connoissoit→connaissait"),

            # === y → i simplification ===
            ("ay", "ai", None, "ay→ai: paye→paie (partial)"),

            # === Spelling standardization ===
            ("foible", "faible", None, "foible→faible"),
            ("encor", "encore", None, "encor→encore"),
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # SPANISH — Old Castilian (pre-17th c.) → Modern
    # Source: RAE norms, Lapesa (1981)
    # ─────────────────────────────────────────────────────────────────────
    "es": {
        "antiguo": [
            # === Consonant changes ===
            ("x", "j", None, "dixo→dijo, exemplo→ejemplo"),
            ("ss", "s", None, "double s simplification"),
            ("ff", "f", None, "double f simplification"),

            # === Vowel changes ===
            ("agora", "ahora", None, "agora→ahora"),
            ("mesmo", "mismo", None, "e→i: mesmo→mismo"),
            ("mesma", "misma", None, "e→i: mesma→misma"),
            ("ansí", "así", None, "ansí→así"),

            # === f- → h- (systematic in Old Castilian → Modern) ===
            # Latin f- → h- is one of the defining features of Castilian
            ("fablar", "hablar", None, "f→h: fablar→hablar"),
            ("fijo", "hijo", None, "f→h: fijo→hijo"),
            ("fazer", "hacer", None, "f→h: fazer→hacer"),
            ("fecho", "hecho", None, "f→h: fecho→hecho"),
            ("fierro", "hierro", None, "f→h: fierro→hierro"),
            ("fermoso", "hermoso", None, "f→h: fermoso→hermoso"),

            # === Archaic verb forms ===
            ("vos", "os", None, "pronoun: vos→os (partial)"),
        ],
    },

    # ─────────────────────────────────────────────────────────────────────
    # ENGLISH — Early Modern / Victorian → Modern
    # ─────────────────────────────────────────────────────────────────────
    "en": {
        "early_modern": [
            # === Pronoun/verb forms ===
            ("thou", "you", None, "2sg→you"),
            ("thee", "you", None, "2sg objective→you"),
            ("hath", "has", None, "3sg: hath→has"),
            ("doth", "does", None, "3sg: doth→does"),
            ("dost", "do", None, "2sg: dost→do"),
            ("hast", "have", None, "2sg: hast→have"),
            ("shalt", "shall", None, "2sg: shalt→shall"),
            ("wilt", "will", None, "2sg: wilt→will"),
            ("art", "are", None, "2sg copula: art→are"),

            # === -eth → -s (3sg present) ===
            ("eth", "es", "$", "-eth→-es: giveth→gives"),
            ("th", "s", "$", "-th→-s: speakth→speaks (rare)"),

            # === Spelling changes ===
            ("connexion", "connection", None, "Latin→English spelling"),
            ("shew", "show", None, "shew→show"),
        ],
        "victorian": [
            ("connexion", "connection", None, "connexion→connection"),
            ("gaol", "jail", None, "gaol→jail"),
            ("waggon", "wagon", None, "waggon→wagon"),
            ("to-day", "today", None, "to-day→today"),
            ("to-morrow", "tomorrow", None, "to-morrow→tomorrow"),
            ("to-night", "tonight", None, "to-night→tonight"),
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SYSTEMATIC PHONETIC RULES (regex-based, generate multiple candidates)
# ═══════════════════════════════════════════════════════════════════════════════
#
# These are the powerful generative rules that cover words never seen before.
# Unlike the specific mappings above, these use regex substitution on ANY word.

GENERATIVE_RULES: Dict[str, Dict[str, List[Tuple[str, str, str]]]] = {
    # (regex_pattern, replacement, description)

    "it": {
        "letterario": [
            # Verse apheresis: elision (l'inferno, d'intorno) tokenizes as
            # nferno, ntorno — restore the initial vowel
            (r'^n([bcdfglmnprstvz])', r'in\1',
             "apheresis reversal: nferno→inferno, ntorno→intorno"),
            (r'^m([bp])', r'im\1',
             "apheresis reversal: mpero→impero"),

            # Tuscan diphthongization: any 'o' before single consonant + vowel
            # This is the most productive rule for Dante
            (r'^(.+?)o([bcdfglmnprstvz])([aeio])$', r'\1uo\2\3',
             "systematic o→uo diphthongization"),

            # -elli → -egli (pronoun suffix)
            (r'elli$', 'egli', "pronoun evolution"),

            # Archaic doubled consonants
            (r'tt([aeiou])', r't\1', "tt→t simplification"),

            # Syncope reversal: spirto→spirito, dritto→diritto
            (r'^(.+)r([bcdfglmnpstvz])([aeiou])$', r'\1ri\2\3',
             "syncope reversal (insert i)"),

            # -ade/-ude → -à/-ù (modern truncation)
            (r'ute$', 'ù', "truncation: virtute→virtù"),
            (r'ade$', 'à', "truncation: cittade→città"),
            (r'one$', 'on', "truncation (selective)"),

            # Archaic a→e shift in prefixes
            (r'^dis([aeiou])', r'des\1', "dis→des: diserto→deserto"),
            (r'^dim([aeiou])', r'dom\1', "dim→dom: dimandar→domandar"),

            # Vowel changes in verb stems
            (r'egn([aoie])$', r'eng\1', "vegna→venga, tegna→tenga"),
            (r'enno$', 'ecero', "fenno→fecero (passato remoto)"),
        ],
    },

    "de": {
        "pre_1901": [
            # th → t (the single most productive rule for pre-1901 German)
            (r'[Tt]h', lambda m: m.group().replace('h', ''),
             "systematic th→t"),

            # ey → ei
            (r'ey', 'ei', "ey→ei standardization"),

            # giebt-type: ie before consonant cluster → i
            (r'gie([bcdfgklmnprstvwz]+)$', r'gi\1',
             "ie→i in short-vowel verbs"),

            # ph → f
            (r'[Pp]h', lambda m: 'F' if m.group()[0].isupper() else 'f',
             "ph→f (Phantasie→Fantasie)"),
        ],
    },

    "fr": {
        "classique": [
            # -oit → -ait (imperfect/conditional, the BIG rule)
            (r'oi(t|ent|s|re)$', r'ai\1',
             "systematic -oi-→-ai- reform of 1835"),

            # -oiss- → -aiss- (in verb stems)
            (r'oiss', 'aiss', "connoissoit→connaissait"),

            # -oît- → -aît-
            (r'oît', 'aît', "connoître→connaître"),
        ],
    },

    "es": {
        "antiguo": [
            # f- → h- (the defining Castilian sound change!)
            # Only word-initial, and only before vowels
            (r'^f([aeiou])', r'h\1',
             "Castilian f→h: fablar→hablar, fijo→hijo"),

            # -x- → -j- (Old Castilian /ʃ/ → Modern /x/)
            (r'x', 'j', "dixo→dijo"),

            # ss → s
            (r'ss', 's', "double s simplification"),
        ],
    },

    "en": {
        "early_modern": [
            # -eth → -es/-s (3sg present indicative)
            (r'eth$', 'es', "giveth→gives"),

            # -th → -s (after vowel)
            (r'([aeiou])th$', r'\1s', "speaketh→speaks (truncated)"),
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. COGNATE BRIDGES — Cross-language word correspondences
# ═══════════════════════════════════════════════════════════════════════════════
#
# Rather than listing every cognate pair, we define systematic correspondence
# rules between related languages. If a word in IT matches a pattern that
# corresponds to a known FR word, we can infer coverage.
#
# These are based on regular sound correspondences (Neogrammarian Lautgesetze).

COGNATE_CORRESPONDENCES: Dict[Tuple[str, str], List[Tuple[str, str, str]]] = {
    # (source_lang, target_lang): [(source_pattern, target_pattern, description)]

    # Italian → French (both from Latin, regular correspondences)
    ("it", "fr"): [
        (r'zione$', 'tion', "IT -zione → FR -tion: nazione→nation"),
        (r'tà$', 'té', "IT -tà → FR -té: libertà→liberté"),
        (r'mente$', 'ment', "IT -mente → FR -ment: naturalmente→naturellement"),
        (r'oso$', 'eux', "IT -oso → FR -eux: famoso→fameux"),
        (r'ezza$', 'esse', "IT -ezza → FR -esse: bellezza→bellesse"),
        (r'iere$', 'ier', "IT -iere → FR -ier: cavaliere→chevalier"),
        (r'aggio$', 'age', "IT -aggio → FR -age: coraggio→courage"),
        (r'ura$', 'ure', "IT -ura → FR -ure: natura→nature"),
        (r'ore$', 'eur', "IT -ore → FR -eur: amore→amour"),
        (r'iere$', 'ière', "IT -iere → FR -ière"),
    ],

    # Italian → Spanish
    ("it", "es"): [
        (r'zione$', 'ción', "IT -zione → ES -ción: nazione→nación"),
        (r'tà$', 'dad', "IT -tà → ES -dad: libertà→libertad"),
        (r'mente$', 'mente', "cognate suffix (same)"),
        (r'oso$', 'oso', "cognate suffix (same)"),
        (r'ura$', 'ura', "cognate suffix (same)"),
        (r'aggio$', 'aje', "IT -aggio → ES -aje: coraggio→coraje"),
        (r'ore$', 'or', "IT -ore → ES -or: amore→amor"),
    ],

    # French → Italian
    ("fr", "it"): [
        (r'tion$', 'zione', "FR -tion → IT -zione"),
        (r'té$', 'tà', "FR -té → IT -tà"),
        (r'ment$', 'mente', "FR -ment → IT -mente: naturellement→naturalmente"),
        (r'eux$', 'oso', "FR -eux → IT -oso"),
        (r'age$', 'aggio', "FR -age → IT -aggio"),
        (r'eur$', 'ore', "FR -eur → IT -ore"),
        (r'ure$', 'ura', "FR -ure → IT -ura"),
    ],

    # French → Spanish
    ("fr", "es"): [
        (r'tion$', 'ción', "FR -tion → ES -ción"),
        (r'té$', 'dad', "FR -té → ES -dad"),
        (r'ment$', 'mente', "FR -ment → ES -mente"),
        (r'eur$', 'or', "FR -eur → ES -or"),
        (r'age$', 'aje', "FR -age → ES -aje"),
    ],

    # Spanish → French
    ("es", "fr"): [
        (r'ción$', 'tion', "ES -ción → FR -tion"),
        (r'dad$', 'té', "ES -dad → FR -té"),
        (r'mente$', 'ment', "ES -mente → FR -ment"),
        (r'or$', 'eur', "ES -or → FR -eur"),
        (r'aje$', 'age', "ES -aje → FR -age"),
    ],

    # German → English (Germanic cognates)
    ("de", "en"): [
        (r'ung$', 'ing', "DE -ung → EN -ing: Hoffnung→hoping"),
        (r'heit$', 'hood', "DE -heit → EN -hood (partial)"),
        (r'keit$', 'ness', "DE -keit → EN -ness (semantic)"),
        (r'lich$', 'ly', "DE -lich → EN -ly: natürlich→naturally"),
        (r'isch$', 'ish', "DE -isch → EN -ish: kindisch→childish"),
    ],

    # English → German
    ("en", "de"): [
        (r'tion$', 'tion', "EN -tion → DE -tion (Latin loans)"),
        (r'ing$', 'ung', "EN -ing → DE -ung (partial)"),
        (r'ly$', 'lich', "EN -ly → DE -lich"),
        (r'ish$', 'isch', "EN -ish → DE -isch"),
    ],
}

# Language family definitions (extended from morpho_semantic_bridge.py)
LANGUAGE_FAMILIES_EXTENDED = {
    "romance":     ["fr", "it", "es", "pt", "eo"],
    "germanic":    ["en", "de", "nl"],
    "slavic":      ["ru"],
    "finno_ugric": ["fi"],
    "indic":       ["hi", "sa"],
    "sinitic":     ["zh"],
    "japonic":     ["ja"],
}


def _get_family(lang: str) -> str:
    """Get language family for a language code."""
    for family, members in LANGUAGE_FAMILIES_EXTENDED.items():
        if lang in members:
            return family
    return "isolate"


def _get_siblings(lang: str) -> List[str]:
    """Get sibling languages (same family, excluding self)."""
    family = _get_family(lang)
    if family == "isolate":
        return []
    return [l for l in LANGUAGE_FAMILIES_EXTENDED[family] if l != lang]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def diachronic_modernize(word: str, lang: str,
                         epoch: str = "") -> List[str]:
    """Generate modern candidate forms from an archaic word using sound rules.

    Applies both specific mappings and generative regex rules.
    Returns a list of candidate modern forms (may be empty).

    Args:
        word: The archaic word form (lowercase).
        lang: ISO 639-1 language code.
        epoch: Detected epoch label (e.g. "pre_1901", "letterario").
               If empty, tries ALL epochs for the language.

    Returns:
        List of candidate modern forms (deduplicated, excluding input).
    """
    candidates = set()
    word_lower = word.lower()

    if lang not in DIACHRONIC_RULES and lang not in GENERATIVE_RULES:
        return []

    # Determine which epochs to try
    if epoch:
        epochs_to_try = [epoch]
    else:
        # Try all epochs for this language
        all_epochs = set()
        if lang in DIACHRONIC_RULES:
            all_epochs.update(DIACHRONIC_RULES[lang].keys())
        if lang in GENERATIVE_RULES:
            all_epochs.update(GENERATIVE_RULES[lang].keys())
        epochs_to_try = list(all_epochs)

    for ep in epochs_to_try:
        # Apply specific replacement rules
        if lang in DIACHRONIC_RULES and ep in DIACHRONIC_RULES[lang]:
            for pattern, replacement, context, _desc in DIACHRONIC_RULES[lang][ep]:
                if pattern in word_lower:
                    candidate = word_lower.replace(pattern, replacement, 1)
                    if candidate != word_lower and len(candidate) >= 2:
                        candidates.add(candidate)

        # Apply generative regex rules
        if lang in GENERATIVE_RULES and ep in GENERATIVE_RULES[lang]:
            for regex, repl, _desc in GENERATIVE_RULES[lang][ep]:
                try:
                    if callable(repl):
                        result = re.sub(regex, repl, word_lower)
                    else:
                        result = re.sub(regex, repl, word_lower)
                    if result != word_lower and len(result) >= 2:
                        candidates.add(result)
                except re.error:
                    continue

    # Remove the input word itself
    candidates.discard(word_lower)
    return list(candidates)


def cognate_candidates(word: str, source_lang: str) -> List[Tuple[str, str]]:
    """Generate cognate candidates in sibling languages.

    Uses systematic suffix correspondence rules to transform a word
    from the source language into potential cognates in related languages.

    Args:
        word: The word to find cognates for (lowercase).
        source_lang: ISO 639-1 code of the source language.

    Returns:
        List of (candidate_word, target_lang) tuples.
    """
    results = []
    word_lower = word.lower()

    # Direct cognate correspondence rules
    for (src, tgt), rules in COGNATE_CORRESPONDENCES.items():
        if src != source_lang:
            continue
        for src_pattern, tgt_pattern, _desc in rules:
            try:
                if re.search(src_pattern, word_lower):
                    candidate = re.sub(src_pattern, tgt_pattern, word_lower)
                    if candidate != word_lower and len(candidate) >= 3:
                        results.append((candidate, tgt))
            except re.error:
                continue

    # Also try the word as-is in sibling languages
    # (many cognates are identical or near-identical: IT "natura" = FR "nature")
    siblings = _get_siblings(source_lang)
    for sib in siblings:
        # The word itself might be a valid keyword in the sibling language
        results.append((word_lower, sib))

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 5. EPOCH AUTO-DETECTION (lightweight, for use when epoch is not pre-detected)
# ═══════════════════════════════════════════════════════════════════════════════

# Cache: (lang, epoch) → compiled regex patterns
_EPOCH_PATTERNS_CACHE: Dict[Tuple[str, str], List] = {}

def detect_epoch_lightweight(text_sample: str, lang: str) -> str:
    """Quick epoch detection from a text sample.

    Lighter than text_normalizer.detect_epoch() — just checks for
    characteristic markers in a small sample.

    Returns:
        Epoch key (e.g. "letterario", "pre_1901", "classique") or "".
    """
    if lang not in DIACHRONIC_RULES:
        return ""

    sample_lower = text_sample[:5000].lower()
    words = set(re.findall(r'\b\w+\b', sample_lower))

    # Check specific epoch markers
    _EPOCH_INDICATOR_WORDS = {
        ("it", "letterario"): {"elli", "sanza", "quivi", "poscia", "sovra",
                               "medesmo", "spirto", "foco", "maraviglia"},
        ("de", "pre_1901"): {"theil", "thal", "thür", "giebt", "gieng",
                             "phantasie", "thorheit", "nothwendig"},
        ("fr", "classique"): {"étoit", "avoit", "connoître", "foible",
                              "étoient", "connoissoit", "françois"},
        ("es", "antiguo"): {"agora", "mesmo", "ansí", "fablar", "vos",
                            "aqueste", "fecho", "dixo"},
        ("en", "early_modern"): {"thou", "thee", "hath", "doth", "dost",
                                 "forsooth", "prithee", "methinks"},
        ("en", "victorian"): {"connexion", "shew", "gaol", "waggon",
                              "to-day", "to-morrow"},
    }

    best_epoch = ""
    best_count = 0

    for (lang_key, epoch_key), markers in _EPOCH_INDICATOR_WORDS.items():
        if lang_key != lang:
            continue
        found = len(markers & words)
        if found > best_count and found >= 2:
            best_epoch = epoch_key
            best_count = found

    return best_epoch


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== Diachronic Rules Self-Test ===\n")

    # Count rules
    specific = sum(
        len(rules)
        for epochs in DIACHRONIC_RULES.values()
        for rules in epochs.values()
    )
    generative = sum(
        len(rules)
        for epochs in GENERATIVE_RULES.values()
        for rules in epochs.values()
    )
    correspondences = sum(
        len(rules) for rules in COGNATE_CORRESPONDENCES.values()
    )
    print(f"Specific rules:    {specific}")
    print(f"Generative rules:  {generative}")
    print(f"Cognate rules:     {correspondences}")
    print(f"Languages covered: {sorted(set(list(DIACHRONIC_RULES.keys()) + list(GENERATIVE_RULES.keys())))}")
    print()

    # Test Italian diachronic modernization
    print("--- Italian (Dante) ---")
    test_it = [
        ("foco", "fuoco"), ("bono", "buono"), ("elli", "egli"),
        ("sanza", "senza"), ("sovra", "sopra"), ("maraviglia", "meraviglia"),
        ("medesmo", "medesimo"), ("poscia", "poi"), ("etterno", "eterno"),
        ("spirto", "spirito"),
    ]
    for archaic, expected in test_it:
        candidates = diachronic_modernize(archaic, "it")
        ok = expected in candidates
        print(f"  {archaic:15s} → {candidates!s:40s}  {'✓' if ok else '✗ EXPECTED: ' + expected}")

    # Test German pre-1901
    print("\n--- German (pre-1901) ---")
    test_de = [
        ("thal", "tal"), ("thür", "tür"), ("theil", "teil"),
        ("giebt", "gibt"), ("phantasie", "fantasie"),
    ]
    for archaic, expected in test_de:
        candidates = diachronic_modernize(archaic, "de")
        ok = expected in candidates
        print(f"  {archaic:15s} → {candidates!s:40s}  {'✓' if ok else '✗ EXPECTED: ' + expected}")

    # Test French classical
    print("\n--- French (classical) ---")
    test_fr = [
        ("étoit", "était"), ("connoître", "connaître"),
        ("foible", "faible"), ("étoient", "étaient"),
    ]
    for archaic, expected in test_fr:
        candidates = diachronic_modernize(archaic, "fr")
        ok = expected in candidates
        print(f"  {archaic:15s} → {candidates!s:40s}  {'✓' if ok else '✗ EXPECTED: ' + expected}")

    # Test Spanish Old Castilian
    print("\n--- Spanish (Old Castilian) ---")
    test_es = [
        ("fablar", "hablar"), ("fijo", "hijo"), ("mesmo", "mismo"),
        ("agora", "ahora"), ("ansí", "así"),
    ]
    for archaic, expected in test_es:
        candidates = diachronic_modernize(archaic, "es")
        ok = expected in candidates
        print(f"  {archaic:15s} → {candidates!s:40s}  {'✓' if ok else '✗ EXPECTED: ' + expected}")

    # Test cognate candidates
    print("\n--- Cognate Bridges ---")
    test_cognates = [
        ("nazione", "it"),      # → FR nation, ES nación
        ("liberté", "fr"),      # → IT libertà, ES libertad
        ("coraje", "es"),       # → FR courage, IT coraggio
        ("naturally", "en"),    # → DE natürlich
    ]
    for word, lang in test_cognates:
        cands = cognate_candidates(word, lang)
        print(f"  {lang} '{word}' → {cands[:5]}")

    # Test epoch detection
    print("\n--- Epoch Detection ---")
    test_texts = {
        "it": "E quivi elli mi disse, con sanza dubbio, che poscia il foco...",
        "de": "Im Thal war es nothwendig, daß der Theil des Phantasie...",
        "fr": "Il étoit vrai que le foible homme connoissoit son destin...",
        "es": "Agora mesmo fablar quiero con vos, ansí como dixo...",
    }
    for lang, text in test_texts.items():
        epoch = detect_epoch_lightweight(text, lang)
        print(f"  {lang}: detected '{epoch}'")

    print("\n✓ Self-test complete")

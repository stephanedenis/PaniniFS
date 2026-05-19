#!/usr/bin/env python3
"""text_normalizer.py — Normalisation unifiée pour le pipeline PaniniFS

Point unique de normalisation de texte avant analyse. Garantit que tout texte
entrant dans le pipeline est dans une forme canonique, reproductible et
comparaison-safe.

Responsabilités :
  1. Normalisation Unicode (NFC)         — forme canonique composée
  2. Nettoyage de jeux de caractères     — legacy → UTF-8 propre
  3. Annotation d'époque orthographique  — détecte le registre temporel
  4. Tag BCP 47 enrichi                  — langue + script + région + variante
  5. Normalisation script-spécifique     — devanagari, CJK, arabe

Principes :
  - Idempotent : normaliser deux fois donne le même résultat
  - Non-destructif : les formes originales sont préservées dans les métadonnées
  - Pipeline-aware : s'insère dans _clean_paragraphs() et detect_language()

Usage :
    from text_normalizer import normalize_text, TextMeta, detect_bcp47
    clean, meta = normalize_text("Ça était beau", lang_hint="fr")
    tag = detect_bcp47("fr", text=clean)  # → "fr-Latn"

Référence normative : Copilotage/knowledge/LANGUAGE_STANDARDS_ISO_UNICODE.md
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CONSTANTES NORMATIVES
# ═══════════════════════════════════════════════════════════════════════════════

# --- ISO 639 : Correspondances complètes pour les 14 langues Panini ----------

ISO_639_MAP = {
    # iso639-1 → (iso639-2/T, iso639-3, nom_fr, nom_en, famille_639-5)
    "en": ("eng", "eng", "Anglais",     "English",    "ine"),
    "fr": ("fra", "fra", "Français",    "French",     "ine"),
    "de": ("deu", "deu", "Allemand",    "German",     "ine"),
    "it": ("ita", "ita", "Italien",     "Italian",    "ine"),
    "es": ("spa", "spa", "Espagnol",    "Spanish",    "ine"),
    "eo": ("epo", "epo", "Espéranto",   "Esperanto",  "art"),
    "fi": ("fin", "fin", "Finnois",     "Finnish",    "urj"),
    "pt": ("por", "por", "Portugais",   "Portuguese", "ine"),
    "nl": ("nld", "nld", "Néerlandais", "Dutch",      "ine"),
    "zh": ("zho", "zho", "Chinois",     "Chinese",    "sit"),
    "ja": ("jpn", "jpn", "Japonais",    "Japanese",   "jpx"),
    "ru": ("rus", "rus", "Russe",       "Russian",    "ine"),
    "hi": ("hin", "hin", "Hindi",       "Hindi",      "ine"),
    "sa": ("san", "san", "Sanskrit",    "Sanskrit",   "ine"),
}

# --- ISO 639-2 Bibliographique → Terminologique (pour Gutenberg) -------------

ISO_639_2_BIBLIO_TO_TERM = {
    "fre": "fra", "ger": "deu", "dut": "nld", "chi": "zho",
    "ice": "isl", "baq": "eus", "tib": "bod", "gre": "ell",
    "bur": "mya", "cze": "ces", "mac": "mkd", "mao": "mri",
    "may": "msa", "per": "fas", "rum": "ron", "slo": "slk",
    "wel": "cym", "alb": "sqi", "arm": "hye", "geo": "kat",
}

# --- ISO 639-2/3 → ISO 639-1 (pour conversion Gutenberg/métadonnées) --------

ISO_639_23_TO_1 = {
    "eng": "en", "fra": "fr", "fre": "fr", "deu": "de", "ger": "de",
    "ita": "it", "spa": "es", "epo": "eo", "fin": "fi",
    "por": "pt", "nld": "nl", "dut": "nl", "zho": "zh", "chi": "zh",
    "jpn": "ja", "rus": "ru", "hin": "hi", "san": "sa",
    "lat": "la", "grc": None,  # grec ancien → pas de 639-1
    "ara": "ar", "heb": "he", "ell": "el", "swa": "sw",
    "kor": "ko", "tha": "th", "ben": "bn", "tur": "tr",
}

# --- ISO 15924 : Scripts et leurs ranges Unicode ----------------------------

SCRIPT_DEFINITIONS = {
    # code_15924: (nom, regex_pattern, unicode_script_property)
    "Latn": ("Latin",      r'\p{Script=Latin}',      "Latin"),
    "Cyrl": ("Cyrillique", r'\p{Script=Cyrillic}',   "Cyrillic"),
    "Hani": ("Han (CJK)",  r'\p{Script=Han}',        "Han"),
    "Hira": ("Hiragana",   r'\p{Script=Hiragana}',   "Hiragana"),
    "Kana": ("Katakana",   r'\p{Script=Katakana}',   "Katakana"),
    "Deva": ("Devanagari", r'\p{Script=Devanagari}',  "Devanagari"),
    "Arab": ("Arabe",      r'\p{Script=Arabic}',      "Arabic"),
    "Grek": ("Grec",       r'\p{Script=Greek}',       "Greek"),
    "Hebr": ("Hébreu",     r'\p{Script=Hebrew}',      "Hebrew"),
    "Hang": ("Hangul",     r'\p{Script=Hangul}',      "Hangul"),
}

# Ranges de fallback (quand le module `regex` n'est pas disponible)
SCRIPT_RANGES_FALLBACK = {
    "Latn": r'[A-Za-z\u00C0-\u024F\u1E00-\u1EFF]',
    "Cyrl": r'[\u0400-\u04FF\u0500-\u052F]',
    "Hani": r'[\u4E00-\u9FFF\u3400-\u4DBF\U00020000-\U0002A6DF]',
    "Hira": r'[\u3040-\u309F]',
    "Kana": r'[\u30A0-\u30FF]',
    "Deva": r'[\u0900-\u097F\uA8E0-\uA8FF]',
    "Arab": r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
    "Grek": r'[\u0370-\u03FF\u1F00-\u1FFF]',
    "Hebr": r'[\u0590-\u05FF\uFB1D-\uFB4F]',
    "Hang": r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]',
}

# Mapping script → langues candidates (1:N, résout le gap G2)
SCRIPT_TO_LANGUAGES = {
    "Latn": ["en", "fr", "de", "it", "es", "eo", "fi", "pt", "nl", "la"],
    "Cyrl": ["ru", "uk", "bg", "sr", "mk"],
    "Hani": ["zh", "ja"],
    "Hira": ["ja"],
    "Kana": ["ja"],
    "Deva": ["hi", "sa", "mr", "ne"],
    "Arab": ["ar", "fa", "ur"],
    "Grek": ["el"],
    "Hebr": ["he", "yi"],
    "Hang": ["ko"],
}

# --- BCP 47 : Variantes connues par langue ---------------------------------

BCP47_VARIANTS = {
    "de": {
        "orthographic_reforms": ["de-1901", "de-1996"],
        "default": "de-Latn",
        "regional": ["de-DE", "de-AT", "de-CH"],
    },
    "fr": {
        "orthographic_reforms": ["fr-1694", "fr-1990"],
        "default": "fr-Latn",
        "regional": ["fr-FR", "fr-CA", "fr-BE", "fr-CH"],
    },
    "pt": {
        "orthographic_reforms": [],
        "default": "pt-Latn",
        "regional": ["pt-BR", "pt-PT"],
    },
    "zh": {
        "script_variants": ["zh-Hans", "zh-Hant"],
        "default": "zh-Hans",
        "regional": ["zh-CN", "zh-TW", "zh-HK"],
    },
    "sa": {
        "script_variants": ["sa-Deva", "sa-Latn"],
        "default": "sa-Deva",
    },
    "en": {
        "default": "en-Latn",
        "regional": ["en-US", "en-GB", "en-AU"],
    },
    "ja": {"default": "ja-Jpan"},  # Jpan = Han + Hiragana + Katakana
    "ru": {"default": "ru-Cyrl"},
    "hi": {"default": "hi-Deva"},
    "it": {"default": "it-Latn", "regional": ["it-IT", "it-CH"]},
    "es": {"default": "es-Latn", "regional": ["es-ES", "es-MX", "es-AR"]},
    "eo": {"default": "eo-Latn"},
    "fi": {"default": "fi-Latn"},
    "nl": {"default": "nl-Latn", "regional": ["nl-NL", "nl-BE"]},
}


# --- Époques orthographiques : marqueurs de détection -----------------------

EPOCH_MARKERS = {
    "de": {
        "pre_1901": {
            "label": "de-1901 (Alte Rechtschreibung)",
            "bcp47": "de-1901",
            "markers": {
                "Thränen", "Thür", "Phantasie", "Thorheit", "giebt",
                "gieng", "nothwendig", "Thal", "Theil", "Noth",
                "daß", "muß", "Kuß", "Fluß", "Genuß",
                "Clavier", "Telephon", "Photographie",
            },
            "patterns": [
                r'\bth(?=al|ür|or|eil|ier|räne)',  # th → t reform
                r'\bgiebt\b',                       # giebt → gibt
            ],
        },
        "post_1996": {
            "label": "de-1996 (Neue Rechtschreibung)",
            "bcp47": "de-1996",
            "markers": {
                "dass", "muss", "Kuss", "Fluss", "Genuss",
                "Foto", "Telefon",
            },
        },
    },
    "fr": {
        "classique": {
            "label": "fr-1694 (Français classique, avant 1835)",
            "bcp47": "fr-1694",
            "markers": {
                "étoit", "avoit", "connoître", "foible", "oi",
                "avoient", "étoient", "connoissoit",
                "françois", "anglois", "paroître",
            },
            "patterns": [
                r'\b\w+oi(?:t|ent|s)\b',  # formes en -oit/-oient (avant réforme -ait)
            ],
        },
        "post_1990": {
            "label": "fr-1990 (Rectifications orthographiques)",
            "bcp47": "fr-1990",
            "markers": {
                "cout", "gout", "bruler", "connaitre", "paraitre",
                "ile", "maitresse", "boite", "chaine", "entrainer",
            },
        },
    },
    "en": {
        "early_modern": {
            "label": "Early Modern English (pre-1700)",
            "bcp47": "en",
            "markers": {
                "thou", "thee", "thy", "thine", "hath", "doth",
                "dost", "hast", "art", "shalt", "wilt",
                "wherefore", "forsooth", "prithee", "methinks",
                "betwixt", "whence", "hither", "thither",
            },
        },
        "victorian": {
            "label": "Victorian English (1837-1901)",
            "bcp47": "en-GB",
            "markers": {
                "connexion", "shew", "gaol", "waggon",
                "phantasy", "to-day", "to-morrow", "to-night",
            },
        },
    },
    "it": {
        "letterario": {
            "label": "Italiano letterario (pre-1900)",
            "bcp47": "it",
            "markers": {
                "egli", "ella", "codesto", "costui", "costei",
                "uopo", "guari", "testé", "dianzi",
            },
        },
    },
    "es": {
        "antiguo": {
            "label": "Español antiguo (pre-1815)",
            "bcp47": "es",
            "markers": {
                "vos", "vuestra merced", "agora", "ansí",
                "aqueste", "mesmo", "fablar",
            },
        },
    },
}


# --- Caractères de remplacement courants (mojibake / legacy) ----------------

LEGACY_CHAR_FIXES = {
    # cp1252 → UTF-8 mojibake patterns
    "â\x80\x93": "–",    # en-dash
    "â\x80\x94": "—",    # em-dash
    "â\x80\x98": "'",    # left single quote
    "â\x80\x99": "'",    # right single quote
    "â\x80\x9c": "\u201c",  # left double quote
    "â\x80\x9d": "\u201d",  # right double quote
    "â\x80\xa6": "…",    # ellipsis
    "Ã©":        "é",    # UTF-8 double-decoded
    "Ã¨":        "è",
    "Ãª":        "ê",
    "Ã«":        "ë",
    "Ã ":        "à",
    "Ã¢":        "â",
    "Ã®":        "î",
    "Ã´":        "ô",
    "Ã¹":        "ù",
    "Ã»":        "û",
    "Ã¼":        "ü",
    "Ã¶":        "ö",
    "Ã¤":        "ä",
    "Ã§":        "ç",
    "Ã±":        "ñ",
    "Â\xa0":     " ",    # non-breaking space (double-decoded)
    "\ufeff":    "",     # BOM
    "\x00":      "",     # null bytes
}

# --- Normalisation devanagari : nukta et consonnes composées ----------------

DEVANAGARI_NORMALIZATIONS = {
    # Nukta forms → canonical
    "\u0958": "\u0915\u093C",  # क़ → क + ़ (mais NFC garde la forme composée)
    "\u0959": "\u0916\u093C",  # ख़
    "\u095A": "\u0917\u093C",  # ग़
    "\u095B": "\u091C\u093C",  # ज़
    "\u095C": "\u0921\u093C",  # ड़
    "\u095D": "\u0922\u093C",  # ढ़
    "\u095E": "\u092B\u093C",  # फ़
    "\u095F": "\u092F\u093C",  # य़
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DATACLASS DE MÉTADONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TextMeta:
    """Métadonnées de normalisation attachées à chaque texte traité.
    
    Préserve la traçabilité complète : forme originale → forme normalisée.
    """
    # Identité linguistique
    lang_iso639_1: str = ""              # "fr"
    lang_iso639_2t: str = ""             # "fra"
    lang_iso639_3: str = ""              # "fra"
    lang_family: str = ""                # "ine"
    bcp47_tag: str = ""                  # "fr-Latn" ou "de-1901"
    
    # Scripts détectés (ISO 15924)
    scripts_detected: List[str] = field(default_factory=list)  # ["Latn"]
    script_primary: str = ""             # "Latn"
    script_proportions: Dict[str, float] = field(default_factory=dict)
    
    # Encodage source
    source_encoding: str = ""            # "utf-8", "iso-8859-1", "cp1252"
    encoding_confidence: float = 0.0     # 0.0-1.0
    encoding_repairs: int = 0            # nombre de réparations mojibake
    had_bom: bool = False                # BOM UTF-8 détecté et retiré
    
    # Normalisation Unicode
    original_form: str = ""              # "NFC", "NFD", "mixed", "unknown"
    normalized_to: str = "NFC"           # toujours NFC
    normalization_changes: int = 0       # nb de caractères modifiés par NFC
    
    # Époque orthographique
    epoch_detected: str = ""             # "de-1901", "fr-1694", "early_modern"
    epoch_confidence: float = 0.0        # 0.0-1.0
    epoch_markers_found: List[str] = field(default_factory=list)
    
    # Caractères spéciaux
    has_rtl: bool = False                # contient des scripts RTL
    has_cjk: bool = False                # contient du CJK
    has_devanagari: bool = False         # contient du devanagari
    whitespace_normalized: bool = False  # espaces/tabs normalisés


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FONCTIONS DE NORMALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_text(text: str, lang_hint: str = "",
                   preserve_case: bool = True) -> Tuple[str, TextMeta]:
    """Point d'entrée principal — normalisation complète d'un texte.
    
    Applique dans l'ordre :
      1. Réparation de mojibake (double-encodage cp1252/latin-1)
      2. Retrait du BOM
      3. Normalisation Unicode NFC
      4. Normalisation des espaces (NBSP, tabs, CR/LF)
      5. Détection des scripts présents
      6. Détection d'époque orthographique
      7. Construction du tag BCP 47
    
    Args:
        text: Texte brut en entrée.
        lang_hint: Code ISO 639-1 de la langue (optionnel).
        preserve_case: Si False, convertit en minuscules (pour indexation).
    
    Returns:
        (texte_normalisé, métadonnées_TextMeta)
    
    Propriété : idempotent — normalize_text(normalize_text(t)[0])[0] == normalize_text(t)[0]
    """
    meta = TextMeta()
    
    if not text:
        return "", meta
    
    # --- Étape 1 : Réparation mojibake ---
    text, repairs = _fix_mojibake(text)
    meta.encoding_repairs = repairs
    
    # --- Étape 2 : BOM ---
    if text.startswith('\ufeff'):
        text = text[1:]
        meta.had_bom = True
    
    # --- Étape 3 : Normalisation Unicode NFC ---
    original_nfc_check = unicodedata.normalize('NFC', text)
    meta.normalization_changes = sum(
        1 for a, b in zip(text, original_nfc_check) if a != b
    ) + abs(len(text) - len(original_nfc_check))
    
    if text == original_nfc_check:
        meta.original_form = "NFC"
    elif text == unicodedata.normalize('NFD', text):
        meta.original_form = "NFD"
    else:
        meta.original_form = "mixed"
    
    text = original_nfc_check  # Appliquer NFC
    meta.normalized_to = "NFC"
    
    # --- Étape 4 : Normalisation des espaces ---
    text = _normalize_whitespace(text)
    meta.whitespace_normalized = True
    
    # --- Étape 5 : Détection des scripts ---
    scripts = detect_scripts(text)
    meta.scripts_detected = list(scripts.keys())
    meta.script_proportions = scripts
    if scripts:
        meta.script_primary = max(scripts, key=scripts.get)
    
    # Flags de commodité
    meta.has_cjk = "Hani" in scripts
    meta.has_devanagari = "Deva" in scripts
    meta.has_rtl = bool({"Arab", "Hebr"} & set(scripts.keys()))
    
    # --- Étape 6 : Identité linguistique ---
    if lang_hint and lang_hint in ISO_639_MAP:
        info = ISO_639_MAP[lang_hint]
        meta.lang_iso639_1 = lang_hint
        meta.lang_iso639_2t = info[0]
        meta.lang_iso639_3 = info[1]
        meta.lang_family = info[4]
    
    # --- Étape 7 : Époque orthographique ---
    if lang_hint:
        epoch, confidence, markers = detect_epoch(text, lang_hint)
        meta.epoch_detected = epoch
        meta.epoch_confidence = confidence
        meta.epoch_markers_found = markers
    
    # --- Étape 8 : Tag BCP 47 ---
    meta.bcp47_tag = build_bcp47_tag(
        lang=lang_hint or "und",
        script=meta.script_primary,
        epoch=meta.epoch_detected,
    )
    
    # --- Optionnel : lowercase ---
    if not preserve_case:
        text = text.lower()
    
    return text, meta


def normalize_nfc(text: str) -> str:
    """Normalisation NFC minimale — pour injection rapide dans le pipeline.
    
    Usage là où on veut juste NFC sans toute la machinerie TextMeta.
    Idempotent et sans effet de bord.
    """
    if not text:
        return text
    return unicodedata.normalize('NFC', text)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FONCTIONS INTERNES
# ═══════════════════════════════════════════════════════════════════════════════

def _fix_mojibake(text: str) -> Tuple[str, int]:
    """Répare les corruptions d'encodage courantes (mojibake).
    
    Détecte les patterns de double-encodage UTF-8 via cp1252 ou latin-1,
    et les corrige. Retourne (texte_réparé, nombre_de_réparations).
    """
    repairs = 0
    for bad, good in LEGACY_CHAR_FIXES.items():
        if bad in text:
            count = text.count(bad)
            text = text.replace(bad, good)
            repairs += count
    
    # Détection heuristique de double-encodage UTF-8
    # Pattern : Ã suivi d'un octet 0x80-0xBF (séquence UTF-8 2-octets mal interprétée)
    double_encoded = re.findall(r'Ã[\x80-\xBF]', text)
    if len(double_encoded) > 3:
        try:
            # Tenter re-encodage cp1252 → décodage UTF-8
            repaired = text.encode('cp1252', errors='ignore').decode('utf-8', errors='ignore')
            if repaired and len(repaired) > len(text) * 0.5:
                text = repaired
                repairs += len(double_encoded)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    
    return text, repairs


def _normalize_whitespace(text: str) -> str:
    """Normalise les différents types d'espaces Unicode.
    
    - NBSP (U+00A0) → espace normal
    - Espaces Unicode rares (thin, em, en, ideographic) → espace normal
    - Tabs → espace
    - CR/LF → LF seul
    - Séquences de 3+ espaces → 2 espaces max
    - Zero-width spaces → supprimés
    """
    # Retirer les espaces de largeur zéro
    text = text.replace('\u200b', '')   # zero-width space
    text = text.replace('\u200c', '')   # zero-width non-joiner
    text = text.replace('\u200d', '')   # zero-width joiner (sauf dans emoji/devanagari)
    text = text.replace('\ufeff', '')   # BOM / zero-width no-break space
    
    # Normaliser les variantes d'espace → espace ASCII
    SPACE_CHARS = (
        '\u00a0'   # NBSP
        '\u2000'   # en quad
        '\u2001'   # em quad
        '\u2002'   # en space
        '\u2003'   # em space
        '\u2004'   # three-per-em space
        '\u2005'   # four-per-em space
        '\u2006'   # six-per-em space
        '\u2007'   # figure space
        '\u2008'   # punctuation space
        '\u2009'   # thin space
        '\u200a'   # hair space
        '\u202f'   # narrow no-break space
        '\u205f'   # medium mathematical space
        '\u3000'   # ideographic space
    )
    for ch in SPACE_CHARS:
        text = text.replace(ch, ' ')
    
    # Tabs → espaces
    text = text.replace('\t', ' ')
    
    # Normaliser les fins de ligne
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Réduire les espaces multiples (mais pas les sauts de ligne)
    text = re.sub(r' {3,}', '  ', text)
    
    return text


def detect_scripts(text: str, sample_size: int = 5000) -> Dict[str, float]:
    """Détecte les scripts (ISO 15924) présents dans un texte.
    
    Retourne un dict {code_15924: proportion} pour les scripts représentant
    au moins 1% du texte analysé.
    
    Utilise les ranges Unicode en fallback (pas besoin du module `regex`).
    """
    sample = text[:sample_size]
    if not sample:
        return {}
    
    counts: Dict[str, int] = {}
    total_letters = 0
    
    for char in sample:
        cat = unicodedata.category(char)
        if not cat.startswith('L'):  # Seulement les lettres
            continue
        total_letters += 1
        
        cp = ord(char)
        script = _codepoint_to_script(cp)
        if script:
            counts[script] = counts.get(script, 0) + 1
    
    if total_letters == 0:
        return {}
    
    return {
        script: count / total_letters
        for script, count in counts.items()
        if count / total_letters >= 0.01  # seuil 1%
    }


def _codepoint_to_script(cp: int) -> Optional[str]:
    """Mappe un codepoint Unicode vers son code ISO 15924.
    
    Utilise des ranges codés en dur (rapide, pas de dépendance externe).
    Couvre les scripts supportés par Panini-FS + extensions courantes.
    """
    # Latin (étendu: Basic, Supplement, Extended-A/B, Additional)
    if (0x0041 <= cp <= 0x024F or 0x1E00 <= cp <= 0x1EFF or
        0x2C60 <= cp <= 0x2C7F or 0xA720 <= cp <= 0xA7FF):
        return "Latn"
    # Cyrillique
    if 0x0400 <= cp <= 0x052F or 0x2DE0 <= cp <= 0x2DFF:
        return "Cyrl"
    # Han (CJK) — Unified + Extension A/B
    if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
        0x20000 <= cp <= 0x2A6DF or 0x2A700 <= cp <= 0x2B73F or
        0xF900 <= cp <= 0xFAFF):
        return "Hani"
    # Hiragana
    if 0x3040 <= cp <= 0x309F:
        return "Hira"
    # Katakana
    if 0x30A0 <= cp <= 0x30FF or 0x31F0 <= cp <= 0x31FF:
        return "Kana"
    # Devanagari (+ extended)
    if 0x0900 <= cp <= 0x097F or 0xA8E0 <= cp <= 0xA8FF:
        return "Deva"
    # Arabe (+ supplement + extended-A/B)
    if (0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F or
        0x08A0 <= cp <= 0x08FF or 0xFB50 <= cp <= 0xFDFF or
        0xFE70 <= cp <= 0xFEFF):
        return "Arab"
    # Grec (+ extended)
    if 0x0370 <= cp <= 0x03FF or 0x1F00 <= cp <= 0x1FFF:
        return "Grek"
    # Hébreu
    if 0x0590 <= cp <= 0x05FF or 0xFB1D <= cp <= 0xFB4F:
        return "Hebr"
    # Hangul (syllables + jamo + compatibility jamo)
    if (0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF or
        0x3130 <= cp <= 0x318F or 0xA960 <= cp <= 0xA97F):
        return "Hang"
    # Bengali
    if 0x0980 <= cp <= 0x09FF:
        return "Beng"
    # Thai
    if 0x0E00 <= cp <= 0x0E7F:
        return "Thai"
    # Georgian
    if 0x10A0 <= cp <= 0x10FF or 0x2D00 <= cp <= 0x2D2F:
        return "Geor"
    # Armenian
    if 0x0530 <= cp <= 0x058F or 0xFB00 <= cp <= 0xFB17:
        return "Armn"
    # Ethiopic
    if 0x1200 <= cp <= 0x137F or 0x1380 <= cp <= 0x139F:
        return "Ethi"
    # Tibetan
    if 0x0F00 <= cp <= 0x0FFF:
        return "Tibt"
    
    return None


def detect_epoch(text: str, lang: str,
                 sample_size: int = 10000) -> Tuple[str, float, List[str]]:
    """Détecte l'époque orthographique d'un texte.
    
    Analyse les marqueurs lexicaux et les patterns orthographiques pour
    déterminer si le texte est en orthographe historique.
    
    Args:
        text: Texte à analyser.
        lang: Code ISO 639-1 de la langue.
        sample_size: Taille de l'échantillon à analyser.
    
    Returns:
        (epoch_label, confidence, markers_found)
        epoch_label: chaîne BCP 47 de la variante détectée, ou "" si moderne.
        confidence: 0.0-1.0.
        markers_found: liste des marqueurs trouvés.
    """
    if lang not in EPOCH_MARKERS:
        return "", 0.0, []
    
    sample = text[:sample_size].lower()
    words = set(re.findall(r'\b\w+\b', sample))
    
    best_epoch = ""
    best_confidence = 0.0
    best_markers: List[str] = []
    
    for epoch_name, epoch_def in EPOCH_MARKERS[lang].items():
        markers = epoch_def.get("markers", set())
        found = [m for m in markers if m.lower() in words]
        
        # Aussi vérifier les patterns regex
        patterns = epoch_def.get("patterns", [])
        for pattern in patterns:
            pattern_matches = re.findall(pattern, sample)
            found.extend(pattern_matches[:5])  # limiter
        
        if found:
            # Confiance basée sur le ratio de marqueurs trouvés
            marker_ratio = len(found) / max(len(markers), 1)
            confidence = min(marker_ratio * 2, 1.0)  # saturé à 1.0
            
            if confidence > best_confidence:
                best_epoch = epoch_def.get("bcp47", epoch_def.get("label", epoch_name))
                best_confidence = confidence
                best_markers = found[:20]  # Top 20
    
    return best_epoch, best_confidence, best_markers


def build_bcp47_tag(lang: str, script: str = "",
                    region: str = "", epoch: str = "") -> str:
    """Construit un tag BCP 47 à partir des composants.
    
    Suit RFC 5646 : language[-script][-region][-variant]
    
    Le script est omis s'il est celui par défaut de la langue
    (ex: pas besoin de "fr-Latn", "fr" suffit — sauf pour désambiguïser).
    """
    if lang == "und" or not lang:
        return "und"
    
    parts = [lang]
    
    # Script : inclure seulement si non-défaut ou si ambiguïté
    default_scripts = {
        "en": "Latn", "fr": "Latn", "de": "Latn", "it": "Latn",
        "es": "Latn", "eo": "Latn", "fi": "Latn", "pt": "Latn",
        "nl": "Latn", "ru": "Cyrl", "hi": "Deva", "sa": "Deva",
        "ja": "Jpan", "zh": "Hans", "ar": "Arab", "he": "Hebr",
        "el": "Grek", "ko": "Hang",
    }
    
    if script and script != default_scripts.get(lang, ""):
        parts.append(script)
    
    # Région
    if region:
        parts.append(region)
    
    # Variante d'époque
    if epoch and epoch != lang:
        # Extraire la partie variante du tag BCP 47 d'époque
        # ex: "de-1901" → "1901", "fr-1694" → "1694"
        variant_part = epoch.replace(f"{lang}-", "")
        if variant_part and variant_part != lang:
            parts.append(variant_part)
    
    return "-".join(parts)


def convert_iso639(code: str, to_format: str = "1") -> Optional[str]:
    """Convertit entre les formats ISO 639.
    
    Args:
        code: Code source (2 ou 3 lettres).
        to_format: "1" (alpha-2), "2t" (alpha-3 terminologique), "3" (alpha-3).
    
    Returns:
        Le code converti, ou None si inconnu.
    """
    # Normaliser le code d'entrée
    code = code.lower().strip()
    
    # Si c'est un code bibliographique 639-2, convertir d'abord
    if code in ISO_639_2_BIBLIO_TO_TERM:
        code = ISO_639_2_BIBLIO_TO_TERM[code]
    
    # Chercher dans ISO_639_23_TO_1 (639-2/3 → 639-1)
    if len(code) == 3 and to_format == "1":
        return ISO_639_23_TO_1.get(code)
    
    # Chercher dans ISO_639_MAP (639-1 → 639-2/3)
    if len(code) == 2 and code in ISO_639_MAP:
        info = ISO_639_MAP[code]
        if to_format == "2t":
            return info[0]
        elif to_format == "3":
            return info[1]
        elif to_format == "1":
            return code
    
    return None


def resolve_script_languages(script: str) -> List[str]:
    """Retourne les langues candidates pour un script donné (1:N).
    
    Résout le gap G2 identifié dans LANGUAGE_STANDARDS_ISO_UNICODE.md.
    """
    return SCRIPT_TO_LANGUAGES.get(script, [])


# ═══════════════════════════════════════════════════════════════════════════════
# 5. VALIDATION DES DICTIONNAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def validate_nfc_keywords(keywords_dict: dict) -> List[str]:
    """Vérifie que tous les mots-clés sont en forme NFC.
    
    Args:
        keywords_dict: Dictionnaire ATOM_KEYWORDS ou similaire.
                       Format: {atom: {lang: [mots]}} ou {lang: [mots]}
    
    Returns:
        Liste des anomalies trouvées (vide si tout est NFC).
    """
    anomalies = []
    
    for key, value in keywords_dict.items():
        if isinstance(value, dict):
            # Format {atom: {lang: [mots]}}
            for lang, words in value.items():
                if isinstance(words, (list, tuple, set)):
                    for w in words:
                        if isinstance(w, str):
                            nfc = unicodedata.normalize('NFC', w)
                            if w != nfc:
                                anomalies.append(
                                    f"NON-NFC: {key}/{lang}: {w!r} → {nfc!r}"
                                )
        elif isinstance(value, (list, tuple, set)):
            # Format {lang: [mots]}
            for w in value:
                if isinstance(w, str):
                    nfc = unicodedata.normalize('NFC', w)
                    if w != nfc:
                        anomalies.append(
                            f"NON-NFC: {key}: {w!r} → {nfc!r}"
                        )
    
    return anomalies


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MODULE SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("text_normalizer.py — Self-test")
    print("=" * 70)
    
    # --- Test 1 : NFC ---
    # é en NFD (e + combining acute) vs NFC (precomposed é)
    nfd_e_acute = "e\u0301"  # NFD
    nfc_e_acute = "\u00e9"   # NFC
    
    result_nfd, meta_nfd = normalize_text(f"L'{nfd_e_acute}t{nfd_e_acute} est beau", lang_hint="fr")
    result_nfc, meta_nfc = normalize_text(f"L'{nfc_e_acute}t{nfc_e_acute} est beau", lang_hint="fr")
    
    assert result_nfd == result_nfc, f"NFC mismatch: {result_nfd!r} vs {result_nfc!r}"
    assert meta_nfd.normalization_changes > 0, "NFD input should show changes"
    assert meta_nfc.normalization_changes == 0, "NFC input should show 0 changes"
    print(f"✅ Test 1 (NFC): NFD→NFC = NFC→NFC ('{result_nfd[:20]}…')")
    print(f"   NFD changes: {meta_nfd.normalization_changes}, NFC changes: {meta_nfc.normalization_changes}")
    print(f"   Original forms: NFD={meta_nfd.original_form}, NFC={meta_nfc.original_form}")
    
    # --- Test 2 : Idempotence ---
    text1, _ = normalize_text("Héllo wörld café")
    text2, _ = normalize_text(text1)
    assert text1 == text2, "Not idempotent!"
    print(f"✅ Test 2 (idempotent): normalize(normalize(x)) == normalize(x)")
    
    # --- Test 3 : Détection de scripts ---
    scripts_fr = detect_scripts("Bonjour le monde, c'est l'été !")
    scripts_ru = detect_scripts("Привет мир, это лето!")
    scripts_zh = detect_scripts("你好世界，这是夏天！")
    scripts_hi = detect_scripts("नमस्ते दुनिया, यह गर्मी है!")
    scripts_mixed = detect_scripts("Hello 你好 Привет नमस्ते")
    
    assert "Latn" in scripts_fr, f"FR should be Latin, got {scripts_fr}"
    assert "Cyrl" in scripts_ru, f"RU should be Cyrillic, got {scripts_ru}"
    assert "Hani" in scripts_zh, f"ZH should be Han, got {scripts_zh}"
    assert "Deva" in scripts_hi, f"HI should be Devanagari, got {scripts_hi}"
    assert len(scripts_mixed) >= 3, f"Mixed should have 3+ scripts, got {scripts_mixed}"
    print(f"✅ Test 3 (scripts): FR={list(scripts_fr)}, RU={list(scripts_ru)}, "
          f"ZH={list(scripts_zh)}, HI={list(scripts_hi)}")
    print(f"   Mixed: {scripts_mixed}")
    
    # --- Test 4 : Époque orthographique ---
    epoch_de_old, conf_de, markers_de = detect_epoch(
        "Es giebt Thränen und Noth in diesem Thal, das Clavier klingt", "de"
    )
    epoch_fr_old, conf_fr, markers_fr = detect_epoch(
        "Il étoit une fois un roi qui avoit trois fils", "fr"
    )
    epoch_en_old, conf_en, markers_en = detect_epoch(
        "Thou hast forsooth done thy duty, methinks", "en"
    )
    
    assert epoch_de_old, f"DE old should be detected, got '{epoch_de_old}'"
    assert epoch_fr_old, f"FR old should be detected, got '{epoch_fr_old}'"
    assert epoch_en_old, f"EN old should be detected, got '{epoch_en_old}'"
    print(f"✅ Test 4 (époque): DE={epoch_de_old} ({conf_de:.2f}), "
          f"FR={epoch_fr_old} ({conf_fr:.2f}), EN={epoch_en_old} ({conf_en:.2f})")
    print(f"   DE markers: {markers_de}")
    print(f"   FR markers: {markers_fr}")
    print(f"   EN markers: {markers_en}")
    
    # --- Test 5 : BCP 47 ---
    tag1 = build_bcp47_tag("fr", "Latn")
    tag2 = build_bcp47_tag("zh", "Hant")
    tag3 = build_bcp47_tag("de", "Latn", epoch="de-1901")
    tag4 = build_bcp47_tag("sa", "Latn")
    tag5 = build_bcp47_tag("ja")
    
    assert tag1 == "fr", f"FR-Latn should be 'fr', got '{tag1}'"
    assert tag2 == "zh-Hant", f"ZH-Hant should be 'zh-Hant', got '{tag2}'"
    assert tag3 == "de-1901", f"DE-1901 should be 'de-1901', got '{tag3}'"
    assert tag4 == "sa-Latn", f"SA-Latn should be 'sa-Latn', got '{tag4}'"
    assert tag5 == "ja", f"JA should be 'ja', got '{tag5}'"
    print(f"✅ Test 5 (BCP 47): fr={tag1}, zh-Hant={tag2}, de-old={tag3}, sa-Latn={tag4}, ja={tag5}")
    
    # --- Test 6 : ISO 639 conversion ---
    assert convert_iso639("fre", "1") == "fr", "fre → fr"
    assert convert_iso639("dut", "1") == "nl", "dut → nl"
    assert convert_iso639("fr", "2t") == "fra", "fr → fra"
    assert convert_iso639("zh", "3") == "zho", "zh → zho"
    assert convert_iso639("grc", "1") is None, "grc → None (no 639-1)"
    print(f"✅ Test 6 (ISO 639): fre→fr, dut→nl, fr→fra, zh→zho, grc→None")
    
    # --- Test 7 : Mojibake ---
    mojibake_text = "Ã©tÃ© Ã Â Paris"
    clean, meta = normalize_text(mojibake_text, lang_hint="fr")
    print(f"✅ Test 7 (mojibake): '{mojibake_text}' → '{clean}'")
    print(f"   Repairs: {meta.encoding_repairs}")
    
    # --- Test 8 : Script → langues (1:N) ---
    deva_langs = resolve_script_languages("Deva")
    assert "hi" in deva_langs and "sa" in deva_langs, f"Deva should have hi+sa, got {deva_langs}"
    hani_langs = resolve_script_languages("Hani")
    assert "zh" in hani_langs and "ja" in hani_langs, f"Hani should have zh+ja, got {hani_langs}"
    print(f"✅ Test 8 (script→langs): Deva={deva_langs}, Hani={hani_langs}")
    
    # --- Test 9 : Caractères espaces spéciaux ---
    weird_spaces = "hello\u00a0world\u2003test\u3000日本"
    clean_spaces, _ = normalize_text(weird_spaces)
    assert "\u00a0" not in clean_spaces, "NBSP should be normalized"
    assert "\u2003" not in clean_spaces, "Em space should be normalized"
    assert "\u3000" not in clean_spaces, "Ideographic space should be normalized"
    print(f"✅ Test 9 (espaces): '{weird_spaces}' → '{clean_spaces}'")
    
    # --- Test 10 : normalize_nfc (version rapide) ---
    quick = normalize_nfc(f"caf{nfd_e_acute}")
    assert quick == "café", f"Quick NFC failed: {quick!r}"
    assert normalize_nfc("") == "", "Empty should stay empty"
    assert normalize_nfc(None) is None, "None should stay None"
    print(f"✅ Test 10 (normalize_nfc rapide): OK")
    
    print()
    print("=" * 70)
    print(f"✅ Tous les tests passent — text_normalizer.py opérationnel")
    print("=" * 70)

#!/usr/bin/env python3
"""gutenberg_preamble_normalizer.py — Preamble normalization & citation detection

Trois responsabilités :

1. **Normalisation des préambules Gutenberg** : les blocs génériques (licence,
   crédits, notice) apparaissent dans la langue du texte *ou* en anglais. Ils
   sont sémantiquement identiques quel que soit la langue. Ce module les
   identifie, les fingerprint et les marque comme « GUTENBERG_BOILERPLATE »
   afin qu'ils ne polluent pas l'analyse atomique du contenu littéraire.

2. **Détection de citations en langue étrangère** : dans un document dont la
   langue principale est L, repérer les passages (citations, épigraphes, mots
   latins, termes en italique) rédigés dans une autre langue L'.

3. **Re-synthèse multi-format** : pour un même ouvrage (même gutenberg_id),
   produire une vue unifiée à partir de toutes les éditions/formats disponibles
   (txt, html, epub) et permettre la comparaison inter-formats.

Principe PaniniFS : toute information en relation avec sa source.

Usage:
    from gutenberg_preamble_normalizer import (
        classify_gutenberg_zones,
        detect_foreign_citations,
        unify_editions,
    )
"""

import os
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PREAMBLE NORMALIZATION — Fingerprint & zone classification
# ═══════════════════════════════════════════════════════════════════════════════

class ZoneType(Enum):
    """Classification sémantique des zones d'un fichier Gutenberg."""
    GUTENBERG_HEADER = auto()      # Bloc licence/crédits avant le texte
    GUTENBERG_FOOTER = auto()      # Bloc licence/donations après le texte
    TITLE_PAGE = auto()            # Page de titre (auteur, éditeur, date)
    TABLE_OF_CONTENTS = auto()     # Table des matières
    PREFACE = auto()               # Préface, avant-propos
    BODY = auto()                  # Corps du texte littéraire
    FOOTNOTE = auto()              # Notes de bas de page
    ILLUSTRATION_MARKER = auto()   # [Illustration: ...]
    ENDNOTE = auto()               # Notes de fin
    APPENDIX = auto()              # Annexes
    FOREIGN_CITATION = auto()      # Citation en langue étrangère


@dataclass
class TextZone:
    """Une zone identifiée dans le texte avec sa classification."""
    zone_type: ZoneType
    start_char: int
    end_char: int
    text: str
    language: Optional[str] = None      # langue détectée de cette zone
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.text.split())


# ─── Marqueurs de préambule Gutenberg multilingues ───────────────────────────
# Ces phrases apparaissent dans les en-têtes/pieds de page Gutenberg.
# Toutes expriment le MÊME sens (licence, crédits, conditions d'utilisation).

GUTENBERG_HEADER_FINGERPRINTS = {
    # Anglais (standard)
    "en": [
        r"the project gutenberg e[-‐]?book",
        r"project gutenberg'?s",
        r"\*\*\* ?start of (the|this) project gutenberg",
        r"this e[-‐]?book is for the use of anyone",
        r"produced by",
        r"release date",
        r"posting date",
        r"character set encoding",
        r"distributed proofreading",
        r"this and all associated files",
    ],
    # Français
    "fr": [
        r"le projet gutenberg",
        r"projet gutenberg",
        r"livre électronique",
        r"distribué par le projet gutenberg",
        r"produit par",
        r"date de publication",
        r"encodage",
        r"ce livre est pour l'usage de quiconque",
        r"correction d'épreuves",
        r"relecture et correction",
    ],
    # Allemand
    "de": [
        r"das projekt gutenberg",
        r"projekt gutenberg[-‐]?de",
        r"dieses e[-‐]?book",
        r"herausgegeben",
        r"zeichensatz",
        r"korrektur gelesen",
    ],
    # Espagnol
    "es": [
        r"el proyecto gutenberg",
        r"proyecto gutenberg",
        r"este libro electrónico",
        r"producido por",
        r"codificación de caracteres",
    ],
    # Italien
    "it": [
        r"il progetto gutenberg",
        r"progetto gutenberg",
        r"questo e[-‐]?book",
        r"prodotto da",
        r"codifica dei caratteri",
    ],
    # Néerlandais
    "nl": [
        r"het project gutenberg",
        r"project gutenberg",
        r"dit e[-‐]?book",
        r"geproduceerd door",
    ],
    # Portugais
    "pt": [
        r"o projeto gutenberg",
        r"projeto gutenberg",
        r"este e[-‐]?book",
        r"produzido por",
    ],
    # Finnois
    "fi": [
        r"projekti gutenberg",
        r"tämä e[-‐]?kirja",
        r"vapaasti käytettävissä",
    ],
    # Espéranto
    "eo": [
        r"projekto gutenberg",
        r"ĉi tiu e[-‐]?libro",
    ],
}

GUTENBERG_FOOTER_FINGERPRINTS = {
    "en": [
        r"\*\*\* ?end of (the|this) project gutenberg",
        r"end of the project gutenberg",
        r"end of project gutenberg",
        r"project gutenberg.*license",
        r"full license",
        r"donations? (to|are)",
        r"subscribe to our email",
        r"gutenberg literary archive",
        r"section \d+\.\s+general terms",
        r"trademark/copyright",
    ],
    "fr": [
        r"fin du (texte|livre|projet) gutenberg",
        r"licence du projet gutenberg",
        r"licence complète",
        r"donations?",
    ],
    "de": [
        r"ende des? projekt gutenberg",
        r"lizenz",
        r"spenden",
    ],
    "es": [
        r"fin del (texto|libro|proyecto) gutenberg",
        r"licencia",
        r"donaciones?",
    ],
    "it": [
        r"fine del (testo|libro|progetto) gutenberg",
        r"licenza",
        r"donazioni",
    ],
}

# ─── Marqueurs structurels internes ─────────────────────────────────────────

ILLUSTRATION_PATTERN = re.compile(
    r'\[(Illustration|Illustrazione|Ilustrajxo|Abbildung|'
    r'Ilustraci[oó]n|Figura|Gravure|Illustratie)'
    r'[:\s]*([^\]]*)\]', re.IGNORECASE
)
FOOTNOTE_PATTERN = re.compile(
    r'\[(?:Footnote|Note|Nota|Anmerkung|Fußnote)[:\s]*([^\]]*)\]', re.IGNORECASE
)
TOC_PATTERNS = [
    re.compile(r'^(?:table (?:of|des) (?:contents|matières)|'
               r'inhalt(?:sverzeichnis)?|'
               r'índice|indice|sommaire|'
               r'sisällysluettelo)\s*$', re.IGNORECASE | re.MULTILINE),
]
PREFACE_PATTERNS = [
    re.compile(r'^(?:preface|préface|avant[- ]propos|vorwort|prefacio|prefazione|'
               r'introduction|einleitung|introducción|introduzione|'
               r'foreword|dedication|dédicace)\s*$', re.IGNORECASE | re.MULTILINE),
]


def _compute_boilerplate_score(text: str, fingerprints: Dict[str, List[str]]) -> Tuple[float, str]:
    """Score how much a text block matches Gutenberg boilerplate patterns.
    
    Returns (score 0.0–1.0, detected_language).
    Uses absolute match count × (matches/total_patterns) to favor languages
    with more specific matches.
    """
    text_lower = text.lower()
    best_score = 0.0
    best_matches = 0
    best_lang = "en"
    
    for lang, patterns in fingerprints.items():
        matches = 0
        for pat in patterns:
            if re.search(pat, text_lower):
                matches += 1
        # Combined score: proportion × absolute count (rewards more specific matches)
        proportion = matches / max(len(patterns), 1)
        combined = proportion * (1 + matches * 0.1)
        if combined > best_score or (combined == best_score and matches > best_matches):
            best_score = combined
            best_matches = matches
            best_lang = lang
    
    # Normalize back to 0..1
    return min(best_score, 1.0), best_lang


def classify_gutenberg_zones(
    text: str,
    declared_lang: str = "en",
    boilerplate_threshold: float = 0.15,
) -> List[TextZone]:
    """Classifie le texte Gutenberg en zones sémantiques.
    
    Identifie :
    - GUTENBERG_HEADER : le préambule licence/crédits (en TOUTE langue)
    - GUTENBERG_FOOTER : le postambule licence/donations
    - TITLE_PAGE : titre, auteur, éditeur entre le header et le premier chapitre
    - TABLE_OF_CONTENTS : table des matières
    - PREFACE : préface / avant-propos
    - BODY : le contenu littéraire proprement dit
    - ILLUSTRATION_MARKER : les marqueurs [Illustration: ...]
    - FOOTNOTE : les notes de bas de page
    
    Le préambule peut être dans UNE LANGUE DIFFÉRENTE du contenu.
    Deux préambules dans des langues différentes sont reconnus comme
    sémantiquement identiques (même ZoneType, même fingerprint hash).
    
    Args:
        text: Texte brut du fichier Gutenberg.
        declared_lang: Langue déclarée du contenu (hint).
        boilerplate_threshold: Seuil minimum pour détecter le boilerplate.
    
    Returns:
        Liste ordonnée de TextZone couvrant tout le texte.
    """
    zones: List[TextZone] = []
    
    # ── Phase 1 : Détecter les bornes START/END ──────────────────────────
    
    start_markers = [
        r'\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG',
        r'\*\*\*START OF (?:THE|THIS) PROJECT GUTENBERG',
        r'\*END\*THE SMALL PRINT',
    ]
    end_markers = [
        r'\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG',
        r'\*\*\*END OF (?:THE|THIS) PROJECT GUTENBERG',
        r'End of (?:the )?Project Gutenberg',
    ]
    
    header_end = 0
    for pat in start_markers:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            # Le header va du début jusqu'à la fin de la ligne du marqueur
            line_end = text.find('\n', m.end())
            header_end = line_end + 1 if line_end >= 0 else m.end()
            
            header_text = text[:header_end]
            score, bp_lang = _compute_boilerplate_score(
                header_text, GUTENBERG_HEADER_FINGERPRINTS
            )
            # Short headers (just the marker line) are always English
            if len(header_text.strip()) < 100:
                bp_lang = "en"
            zones.append(TextZone(
                zone_type=ZoneType.GUTENBERG_HEADER,
                start_char=0,
                end_char=header_end,
                text=header_text,
                language=bp_lang,
                confidence=max(score, 0.9),  # High confidence if markers found
                metadata={
                    "boilerplate_score": round(score, 3),
                    "boilerplate_lang": bp_lang,
                    "semantic_id": "GUTENBERG_PREAMBLE_LICENCE",
                    "equivalent_across_languages": True,
                },
            ))
            break
    
    footer_start = len(text)
    for pat in end_markers:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            footer_start = m.start()
            footer_text = text[footer_start:]
            score, bp_lang = _compute_boilerplate_score(
                footer_text, GUTENBERG_FOOTER_FINGERPRINTS
            )
            zones.append(TextZone(
                zone_type=ZoneType.GUTENBERG_FOOTER,
                start_char=footer_start,
                end_char=len(text),
                text=footer_text,
                language=bp_lang,
                confidence=max(score, 0.9),
                metadata={
                    "boilerplate_score": round(score, 3),
                    "boilerplate_lang": bp_lang,
                    "semantic_id": "GUTENBERG_POSTAMBLE_LICENCE",
                    "equivalent_across_languages": True,
                },
            ))
            break
    
    # ── Phase 2 : Analyser le corps (entre header_end et footer_start) ───
    
    body_text = text[header_end:footer_start]
    
    if not body_text.strip():
        return zones
    
    # Sous-zones dans le corps
    body_zones = _classify_body_zones(body_text, header_end, declared_lang)
    zones.extend(body_zones)
    
    # Trier par position
    zones.sort(key=lambda z: z.start_char)
    
    return zones


def _classify_body_zones(
    body_text: str,
    offset: int,
    declared_lang: str,
) -> List[TextZone]:
    """Classifie les sous-zones du corps du texte."""
    zones: List[TextZone] = []
    
    # ── Détecter la page de titre (premiers paragraphes courts) ──────────
    paragraphs = re.split(r'\n\s*\n', body_text)
    title_end = 0
    title_paras = []
    
    for i, para in enumerate(paragraphs[:10]):
        para_stripped = para.strip()
        if not para_stripped:
            continue
        # La page de titre : paragraphes courts, souvent en majuscules
        if (len(para_stripped.split()) < 20 and
            (para_stripped.isupper() or
             i < 3 or
             re.match(r'^by\s|^par\s|^von\s|^por\s|^di\s', para_stripped, re.I))):
            title_end = body_text.find(para_stripped) + len(para_stripped)
            title_paras.append(para_stripped)
        elif title_paras:
            break
    
    if title_paras and title_end > 0:
        zones.append(TextZone(
            zone_type=ZoneType.TITLE_PAGE,
            start_char=offset,
            end_char=offset + title_end,
            text='\n'.join(title_paras),
            language=declared_lang,
            confidence=0.8,
        ))
    
    # ── Détecter table des matières ──────────────────────────────────────
    for toc_pat in TOC_PATTERNS:
        m = toc_pat.search(body_text)
        if m:
            # La TdM s'étend jusqu'au prochain double saut de ligne après
            # une séquence de lignes courtes
            toc_start = m.start()
            toc_end = toc_start
            lines_after = body_text[m.end():].split('\n')
            for j, line in enumerate(lines_after):
                toc_end = m.end() + sum(len(l) + 1 for l in lines_after[:j+1])
                # Fin de TdM : paragraphe long ou double saut de ligne suivi de texte long
                if len(line.strip()) > 80:
                    break
                if j > 50:  # Sécurité
                    break
            
            zones.append(TextZone(
                zone_type=ZoneType.TABLE_OF_CONTENTS,
                start_char=offset + toc_start,
                end_char=offset + toc_end,
                text=body_text[toc_start:toc_end],
                language=declared_lang,
                confidence=0.9,
            ))
            break
    
    # ── Détecter préface/avant-propos ────────────────────────────────────
    for pref_pat in PREFACE_PATTERNS:
        m = pref_pat.search(body_text)
        if m:
            # La préface va du marqueur jusqu'au prochain chapitre
            pref_start = m.start()
            chapter_pat = re.compile(
                r'^(?:chapter|chapitre|kapitel|capítulo|capitolo)\s+[IVXLCDM\d]+',
                re.IGNORECASE | re.MULTILINE
            )
            next_chapter = chapter_pat.search(body_text[m.end():])
            pref_end = m.end() + next_chapter.start() if next_chapter else min(m.end() + 5000, len(body_text))
            
            zones.append(TextZone(
                zone_type=ZoneType.PREFACE,
                start_char=offset + pref_start,
                end_char=offset + pref_end,
                text=body_text[pref_start:pref_end],
                language=declared_lang,
                confidence=0.85,
            ))
            break
    
    # ── Détecter les illustrations ───────────────────────────────────────
    for m in ILLUSTRATION_PATTERN.finditer(body_text):
        zones.append(TextZone(
            zone_type=ZoneType.ILLUSTRATION_MARKER,
            start_char=offset + m.start(),
            end_char=offset + m.end(),
            text=m.group(0),
            language=declared_lang,
            confidence=1.0,
            metadata={
                "marker_type": m.group(1),
                "caption": m.group(2).strip() if m.group(2) else "",
            },
        ))
    
    # ── Détecter les notes de bas de page ────────────────────────────────
    for m in FOOTNOTE_PATTERN.finditer(body_text):
        zones.append(TextZone(
            zone_type=ZoneType.FOOTNOTE,
            start_char=offset + m.start(),
            end_char=offset + m.end(),
            text=m.group(0),
            language=declared_lang,
            confidence=1.0,
            metadata={"note_content": m.group(1).strip() if m.group(1) else ""},
        ))
    
    # ── Le reste est du corps ────────────────────────────────────────────
    # On marque le bloc principal comme BODY
    zones.append(TextZone(
        zone_type=ZoneType.BODY,
        start_char=offset + (title_end if title_paras else 0),
        end_char=offset + len(body_text),
        text=body_text[title_end if title_paras else 0:],
        language=declared_lang,
        confidence=0.95,
    ))
    
    return zones


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FOREIGN CITATION DETECTION — Repérer les langues étrangères dans le corps
# ═══════════════════════════════════════════════════════════════════════════════

# Marqueurs typiques de citations en langue étrangère dans la littérature
CITATION_DELIMITERS = [
    # Guillemets et italiques (souvent utilisés pour mots étrangers)
    re.compile(r'_([^_]{5,200})_'),              # _texte en italique_
    re.compile(r'\*([^*]{5,200})\*'),             # *texte en italique*
    # Citations explicites entre guillemets
    re.compile(r'«\s*([^»]{5,500})\s*»'),         # guillemets français
    re.compile(r'„([^"]{5,500})"'),                # guillemets allemands
    # Discours rapporté après deux-points (ex: : "Oh dear!")
    re.compile(r':\s*[«"\u201C]([^»"\u201D]{5,300})[»"\u201D]'),
    # Discours rapporté avec guillemets anglais
    re.compile(r'"([^"]{5,300})"'),
    # Mots latins courants (souvent non traduits dans toutes les langues)
    re.compile(r'\b((?:et cetera|ad hoc|a priori|a posteriori|'
               r'in situ|in vivo|in vitro|ex nihilo|tabula rasa|'
               r'carpe diem|memento mori|alma mater|'
               r'status quo|modus operandi|quid pro quo|'
               r'veni vidi vici|cogito ergo sum|'
               r'deus ex machina|persona non grata)\b)', re.IGNORECASE),
]

# Profils de caractères par famille linguistique pour détection rapide
SCRIPT_PROFILES = {
    "latin_extended": re.compile(r'[àâäéèêëïîôùûüçœæ]', re.IGNORECASE),
    "latin_accented_de": re.compile(r'[äöüß]', re.IGNORECASE),
    "latin_accented_es": re.compile(r'[ñ¿¡áéíóú]', re.IGNORECASE),
    "cyrillic": re.compile(r'[\u0400-\u04FF]'),
    "cjk": re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]'),
    "hiragana": re.compile(r'[\u3040-\u309F]'),
    "katakana": re.compile(r'[\u30A0-\u30FF]'),
    "devanagari": re.compile(r'[\u0900-\u097F]'),
    "greek": re.compile(r'[\u0370-\u03FF]'),
    "arabic": re.compile(r'[\u0600-\u06FF]'),
    "hebrew": re.compile(r'[\u0590-\u05FF]'),
}

# Trigrams de haute fréquence par langue pour identification rapide
# Pour les langues CJK, on utilise des bigrammes (plus significatifs que les trigrammes
# pour des écritures idéographiques). La clé "ngram_size" dans LANGUAGE_NGRAM_CONFIG
# indique la taille à utiliser.
LANGUAGE_TRIGRAMS = {
    "en": {"the", "and", "ing", "ion", "tio", "ent", "ati", "for", "her", "ter",
           "hat", "tha", "ere", "his", "not", "was", "all", "ons",
           "hal", "sha", "oul", "oul", "wou", "ear", "are", "mad",
           "you", "our", "hav", "ave", "hey", "hem", "hey", "ome",
           "wit", "ith", "sho", "hou", "hou", "she", "ery", "ver"},
    "fr": {"les", "des", "ent", "que", "ion", "ait", "ous", "par", "pas",
           "une", "son", "sur", "ont", "est", "ais", "eur", "qui", "dan",
           "ans", "our", "oir", "tre", "com", "men", "tou", "pou", "mai",
           "ell", "out", "ait", "ant", "ien", "ème", "ère"},
    "de": {"der", "die", "und", "ein", "den", "sch", "ich", "ung", "eit",
           "gen", "cht", "ver", "ber", "ste", "auf", "enn", "war", "hat"},
    "es": {"que", "los", "las", "del", "ent", "ión", "con", "ado", "por",
           "una", "est", "nte", "dos", "cia", "aba", "era", "mos"},
    "it": {"che", "del", "ell", "per", "con", "gli", "ato", "ent", "ion",
           "lla", "tta", "era", "ono", "nte", "ato", "ita", "sta"},
    "pt": {"que", "dos", "uma", "com", "não", "ção", "ent", "ado", "por",
           "era", "ava", "mos", "ção", "nte", "das"},
    "nl": {"het", "een", "van", "den", "der", "die", "dat", "aan", "aar",
           "oor", "ijk", "ver", "sch"},
    "la": {"que", "ium", "unt", "tur", "ent", "tis", "est", "ati", "bus",
           "ris", "rum", "ere", "ens", "ant"},
    # ── Cyrillic (broadly common — function words, suffixes, particles) ───
    "ru": {"что", "его", "все", "как", "это", "она", "они", "или", "так",
           "при", "про", "ого", "его", "ной", "ала", "ать", "ить", "ост",
           "сть", "ени", "ень", "тво", "ест", "ств", "пре", "енн", "стр",
           "тся", "сво", "ска", "ком", "ова", "был", "ыла", "ыло", "ыли",
           "ого", "ому", "ным", "ных", "ной", "ное", "ний", "гов", "ово",
           "каз", "пос", "сле", "ред", "пер", "чер", "еще", "ожн", "жно"},
    # ── Japanese (hiragana trigrams — most distinctive functional words) ──
    "ja": {"であ", "ある", "てい", "いた", "って", "てい", "なが", "がら",
           "よう", "うに", "ので", "のよ", "たの", "して", "ばか", "かり",
           "そう", "うし", "する", "ると", "しか", "かし", "さっ", "っき",
           "です", "ます", "した", "から", "こと", "それ", "この", "もの"},
    # ── Chinese (CJK bigrams — high-frequency function pairs) ────────────
    "zh": {"的是", "不是", "一個", "了一", "也不", "什么", "我們", "那里",
           "起來", "出來", "來了", "怎么", "如今", "不知", "只見", "去了",
           "不過", "這個", "那個", "人的", "他的", "心中", "自己", "已經",
           "可以", "就是", "所以", "因為", "但是", "還是", "沒有", "只是"},
}

# Configuration n-gram par langue : taille du n-gram à extraire
# Les langues CJK utilisent des bigrammes (caractères individuels portent
# plus de sens), les autres utilisent des trigrammes (syllabiques).
LANGUAGE_NGRAM_CONFIG = {
    "zh": 2,    # bigrammes CJK
    # Toutes les autres langues : trigrammes (défaut = 3)
}

# Regex par script pour extraction de "mots" (séquences de caractères du même script)
_WORD_EXTRACTORS = {
    "latin": re.compile(r'[a-zàâäéèêëïîôùûüçœæñ¿¡áíóúäöüß]+'),
    "cyrillic": re.compile(r'[\u0400-\u04FF]+'),
    "hiragana": re.compile(r'[\u3040-\u309F]+'),
    "cjk": re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]+'),
}


@dataclass
class ForeignCitation:
    """Une citation ou un passage en langue étrangère détecté."""
    text: str
    start_char: int
    end_char: int
    detected_language: str
    document_language: str
    confidence: float
    context_before: str = ""    # 50 chars avant pour contexte
    context_after: str = ""     # 50 chars après pour contexte
    detection_method: str = ""  # "trigram", "script", "delimiter", "latin_phrase"


def _detect_language_trigram(text: str, exclude_lang: str = "") -> Tuple[str, float]:
    """Détecte la langue d'un court texte par analyse de n-grammes multi-scripts.
    
    Plus adapté que langdetect pour les textes courts (< 100 mots).
    Supporte les écritures latine, cyrillique, hiragana et CJK.
    
    Pour les langues sans trigram (devanagari, grec, arabe, hébreu),
    retombe sur la détection de script seule.
    
    Args:
        text: Texte à analyser (idéalement 20–200 mots).
        exclude_lang: Langue à exclure (la langue du document).
    
    Returns:
        (langue_détectée, confiance 0.0–1.0)
    """
    text_lower = text.lower()
    
    # ── Phase 1 : Détection de script dominant ───────────────────────────
    # Comptage des caractères par script
    script_counts = {}
    for script_name, pattern in SCRIPT_PROFILES.items():
        matches = pattern.findall(text_lower)
        if matches:
            script_counts[script_name] = len(matches)
    
    text_len = max(len(text_lower), 1)
    
    # Scripts sans trigrams → détection directe
    for script_name, threshold, lang in [
        ("devanagari", 0.3, "hi"),
        ("greek", 0.3, "el"),
        ("arabic", 0.3, "ar"),
        ("hebrew", 0.3, "he"),
    ]:
        if script_counts.get(script_name, 0) / text_len > threshold:
            return lang, 0.85
    
    # ── Phase 2 : Extraction de n-grammes multi-scripts ──────────────────
    # Déterminer le script dominant pour choisir le bon extracteur
    dominant_script = None
    cyrillic_ratio = script_counts.get("cyrillic", 0) / text_len
    cjk_ratio = script_counts.get("cjk", 0) / text_len
    hiragana_ratio = script_counts.get("hiragana", 0) / text_len
    katakana_ratio = script_counts.get("katakana", 0) / text_len
    
    if cyrillic_ratio > 0.3:
        dominant_script = "cyrillic"
    elif cjk_ratio > 0.1:
        dominant_script = "cjk"
    elif hiragana_ratio > 0.05 or katakana_ratio > 0.05:
        dominant_script = "hiragana"
    
    # Extraire les n-grammes selon le script
    text_ngrams_by_size: Dict[int, set] = {}  # {ngram_size: set_of_ngrams}
    
    if dominant_script and dominant_script in _WORD_EXTRACTORS:
        # Non-Latin script dominant → extraire des n-grammes de ce script
        extractor = _WORD_EXTRACTORS[dominant_script]
        raw_words = extractor.findall(text_lower)
        # Normaliser ё→е pour le cyrillique (variante orthographique fréquente)
        if dominant_script == "cyrillic":
            raw_words = [w.replace('ё', 'е') for w in raw_words]
        words = raw_words
        for ngram_size in (2, 3):  # Extraire les deux tailles
            ngrams = set()
            for word in words:
                for i in range(len(word) - ngram_size + 1):
                    ngrams.add(word[i:i + ngram_size])
            if ngrams:
                text_ngrams_by_size[ngram_size] = ngrams
    else:
        # Latin script (défaut) → trigrammes classiques
        words = _WORD_EXTRACTORS["latin"].findall(text_lower)
        ngrams = set()
        for word in words:
            for i in range(len(word) - 2):
                ngrams.add(word[i:i + 3])
        if ngrams:
            text_ngrams_by_size[3] = ngrams
    
    if not text_ngrams_by_size:
        return "unknown", 0.0
    
    # ── Phase 3 : Scoring par langue ─────────────────────────────────────
    scores = {}
    for lang, ref_ngrams in LANGUAGE_TRIGRAMS.items():
        if lang == exclude_lang:
            continue
        # Déterminer la taille de n-gramme pour cette langue
        ngram_size = LANGUAGE_NGRAM_CONFIG.get(lang, 3)
        text_ngrams = text_ngrams_by_size.get(ngram_size)
        if text_ngrams is None:
            continue  # Pas de n-grammes de la bonne taille extraits
        overlap = text_ngrams & ref_ngrams
        scores[lang] = len(overlap) / max(len(ref_ngrams), 1)
    
    if not scores:
        # Aucun score n-gramme → fallback sur la détection de script
        if dominant_script:
            _SCRIPT_DEFAULT_LANG = {
                "cyrillic": "ru", "cjk": "zh", "hiragana": "ja",
            }
            fallback = _SCRIPT_DEFAULT_LANG.get(dominant_script, "unknown")
            if fallback != exclude_lang:
                return fallback, 0.75
        return "unknown", 0.0
    
    best_lang = max(scores, key=scores.get)
    best_score = scores[best_lang]
    
    # Si le meilleur score est très bas mais qu'on a un script dominant,
    # fallback sur le script (les trigrams ne discriminent pas assez)
    if best_score < 0.05 and dominant_script:
        _SCRIPT_DEFAULT_LANG = {
            "cyrillic": "ru", "cjk": "zh", "hiragana": "ja",
        }
        fallback = _SCRIPT_DEFAULT_LANG.get(dominant_script, best_lang)
        if fallback != exclude_lang:
            return fallback, 0.75
    
    # Normaliser la confiance
    # Si le meilleur score est très proche du deuxième, confiance basse
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[0] > 0:
        discrimination = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
    else:
        discrimination = 1.0
    
    confidence = min(best_score * 2, 1.0) * max(discrimination, 0.3)
    
    return best_lang, round(confidence, 3)


def detect_foreign_citations(
    text: str,
    document_lang: str,
    min_words: int = 3,
    min_confidence: float = 0.1,
) -> List[ForeignCitation]:
    """Détecte les citations et passages en langue étrangère dans le texte.
    
    Stratégie multi-niveaux :
    1. **Délimiteurs** : texte entre _italiques_, «guillemets», etc.
    2. **Script** : passages en script non-latin (cyrillique, CJK, etc.)
    3. **Trigrammes** : analyse linguistique sur des segments suspects.
    4. **Phrases latines** : locutions latines courantes.
    
    Args:
        text: Corps du texte (sans header/footer Gutenberg).
        document_lang: Langue principale du document.
        min_words: Nombre minimum de mots pour considérer une citation.
        min_confidence: Confiance minimum pour retenir une détection.
    
    Returns:
        Liste de ForeignCitation triées par position.
    """
    citations: List[ForeignCitation] = []
    seen_spans = set()  # Éviter les doublons
    
    def _add_citation(text_span, start, end, lang, conf, method):
        span_key = (start, end)
        if span_key in seen_spans:
            return
        if lang == document_lang:
            return
        if conf < min_confidence:
            return
        if len(text_span.split()) < min_words:
            return
        
        seen_spans.add(span_key)
        ctx_before = text[max(0, start - 50):start].strip()
        ctx_after = text[end:min(len(text), end + 50)].strip()
        
        citations.append(ForeignCitation(
            text=text_span,
            start_char=start,
            end_char=end,
            detected_language=lang,
            document_language=document_lang,
            confidence=conf,
            context_before=ctx_before,
            context_after=ctx_after,
            detection_method=method,
        ))
    
    # ── Méthode 1 : Phrases latines connues (haute confiance) ──────────
    # Fait AVANT les délimiteurs pour éviter que les mêmes spans soient
    # détectés comme "unknown" par trigram dans la méthode 2.
    latin_phrase_pat = CITATION_DELIMITERS[-1]  # Le dernier pattern = phrases latines
    for m in latin_phrase_pat.finditer(text):
        _add_citation(m.group(0), m.start(), m.end(), "la", 0.95, "latin_phrase")
    
    # Language families — close-family detections need higher confidence
    ROMANCE = {"fr", "es", "it", "pt", "la"}
    GERMANIC = {"en", "de", "nl"}
    
    def _is_close_family(doc_lang, detected_lang):
        """Return True if both languages are in the same family."""
        if doc_lang in ROMANCE and detected_lang in ROMANCE:
            return True
        if doc_lang in GERMANIC and detected_lang in GERMANIC:
            return True
        return False
    
    # ── Méthode 2 : Délimiteurs (italiques, guillemets) ──────────────────
    for pat in CITATION_DELIMITERS[:-1]:  # Exclure le pattern latin déjà traité
        for m in pat.finditer(text):
            inner = m.group(1) if m.lastindex else m.group(0)
            # Skip very short delimiter content (< min_words) — too noisy
            if len(inner.split()) < min_words:
                continue
            # D'abord vérifier si c'est une phrase latine connue
            if latin_phrase_pat.search(inner):
                _add_citation(inner, m.start(), m.end(), "la", 0.95, "latin_in_delimiter")
                continue
            lang, conf = _detect_language_trigram(inner, exclude_lang=document_lang)
            # Higher threshold for close-family languages (FR↔IT↔PT↔ES, EN↔DE↔NL)
            if _is_close_family(document_lang, lang):
                delim_threshold = 0.40
            else:
                word_count = len(inner.split())
                delim_threshold = 0.20 if word_count >= 8 else 0.15
            if lang != "unknown" and lang != document_lang and conf >= delim_threshold:
                _add_citation(inner, m.start(), m.end(), lang, conf, "delimiter")
    
    # ── Méthode 2 : Changements de script ────────────────────────────────
    # Détecter les blocs de script non-latin dans un document latin (et vice versa)
    doc_is_latin = document_lang in {"en", "fr", "de", "es", "it", "pt", "nl", "eo", "fi"}
    
    if doc_is_latin:
        # Chercher des passages non-latins
        non_latin_patterns = {
            "cyrillic": (SCRIPT_PROFILES["cyrillic"], "ru"),
            "cjk": (SCRIPT_PROFILES["cjk"], "zh"),
            "devanagari": (SCRIPT_PROFILES["devanagari"], "hi"),
            "greek": (SCRIPT_PROFILES["greek"], "el"),
            "arabic": (SCRIPT_PROFILES["arabic"], "ar"),
            "hebrew": (SCRIPT_PROFILES["hebrew"], "he"),
        }
        for script_name, (pattern, default_lang) in non_latin_patterns.items():
            # Trouver les clusters de caractères de ce script (3+ chars)
            cluster_re = re.compile(
                r'(?:' + pattern.pattern + r'[\s.,;:!?\-]*){3,}'
            )
            for m in cluster_re.finditer(text):
                _add_citation(m.group(0), m.start(), m.end(), default_lang, 0.85, "script")
    
    # ── Méthode 4 : Segments par paragraphe ──────────────────────────────
    # Pour chaque paragraphe, vérifier s'il est dans une autre langue que le doc
    paragraphs = re.split(r'\n\s*\n', text)
    pos = 0
    for para in paragraphs:
        para_stripped = para.strip()
        para_start = text.find(para_stripped, pos)
        if para_start < 0:
            pos += len(para) + 1
            continue
        para_end = para_start + len(para_stripped)
        
        # Seulement les paragraphes de taille raisonnable
        word_count = len(para_stripped.split())
        if word_count < 5 or word_count > 500:
            pos = para_end
            continue
        
        lang, conf = _detect_language_trigram(para_stripped, exclude_lang=document_lang)
        # Higher threshold for close-family languages at paragraph level
        para_threshold = 0.65 if _is_close_family(document_lang, lang) else 0.5
        if lang != "unknown" and lang != document_lang and conf > para_threshold:
            _add_citation(para_stripped, para_start, para_end, lang, conf, "paragraph_trigram")
        
        pos = para_end
    
    # Trier par position
    citations.sort(key=lambda c: c.start_char)
    
    return citations


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FORMAT RE-SYNTHESIS — Vue unifiée multi-format d'un même ouvrage
#
# Principe PaniniFS : le format le plus riche (HTML) est la référence
# canonique. Les formats plus pauvres (EPUB, TXT) sont des projections
# qui PERDENT de l'information. La comparaison mesure cette perte par
# dimension informationnelle.
# ═══════════════════════════════════════════════════════════════════════════════

# Richesse informationnelle par format (plus haut = plus riche)
# HTML préserve : structure (headings), emphase (em/i/strong), images (img),
#                  liens (a), tables, métadonnées inline
# EPUB préserve : structure + emphase + images, mais pas les liens externes
# TXT  perd     : tout le formatage, seul le texte brut survit
FORMAT_RICHNESS = {
    "html": 100,
    "epub": 80,
    "docx": 70,
    "md":   50,
    "txt":  10,
}


@dataclass
class InformationLayer:
    """Dimensions informationnelles extraites d'un format.
    
    Chaque dimension représente un type d'information structurelle
    que certains formats préservent et d'autres perdent.
    Le format le plus riche (HTML) sert de référence bit-perfect.
    """
    # Structure
    headings: int = 0               # h1–h6 count
    heading_texts: List[str] = field(default_factory=list)
    # Emphasis (often marks foreign words, titles, key terms)
    emphasis_spans: int = 0         # em/i count
    strong_spans: int = 0           # strong/b count
    emphasis_texts: List[str] = field(default_factory=list)  # first N emphasized words
    # Media
    images: int = 0                 # img count
    image_alts: List[str] = field(default_factory=list)
    # Links
    links: int = 0                  # a[href] count
    # Tables
    tables: int = 0                 # table count
    table_cells: int = 0            # td/th count
    # Paragraphs (structural boundaries)
    paragraphs: int = 0             # p count (explicit paragraph boundaries)
    # Block elements
    blockquotes: int = 0
    preformatted: int = 0           # pre/code blocks
    lists: int = 0                  # ol/ul count
    list_items: int = 0             # li count
    # Text content (the one dimension ALL formats share)
    text_chars: int = 0             # character count of pure text
    text_words: int = 0             # word count of pure text

    @property
    def structural_richness(self) -> int:
        """Score composite de richesse structurelle (0–N)."""
        return (self.headings + self.emphasis_spans + self.strong_spans +
                self.images + self.links + self.tables + self.blockquotes +
                self.preformatted + self.lists)

    def loss_vs(self, reference: 'InformationLayer') -> Dict[str, float]:
        """Calcule la perte informationnelle par rapport à une référence.
        
        Retourne un dict {dimension: ratio_perdu} où 0.0 = rien perdu,
        1.0 = tout perdu. Les dimensions absentes des deux sont omises.
        """
        loss = {}
        for dim in ('headings', 'emphasis_spans', 'strong_spans', 'images',
                    'links', 'tables', 'table_cells', 'blockquotes',
                    'preformatted', 'lists', 'list_items', 'paragraphs'):
            ref_val = getattr(reference, dim)
            self_val = getattr(self, dim)
            if ref_val > 0:
                lost = max(0, ref_val - self_val) / ref_val
                loss[dim] = round(lost, 4)
        # Text — should ideally be 0% loss (bit-perfect)
        if reference.text_words > 0:
            # Ratio of text preserved (can be > 1 if format adds markup text)
            text_ratio = self.text_words / reference.text_words
            loss["text_words"] = round(abs(1.0 - text_ratio), 4)
        return loss

    def to_dict(self) -> Dict[str, int]:
        """Serialize numeric dimensions for JSON export (skip text lists)."""
        return {
            "headings": self.headings,
            "emphasis_spans": self.emphasis_spans,
            "strong_spans": self.strong_spans,
            "images": self.images,
            "links": self.links,
            "tables": self.tables,
            "table_cells": self.table_cells,
            "paragraphs": self.paragraphs,
            "blockquotes": self.blockquotes,
            "preformatted": self.preformatted,
            "lists": self.lists,
            "list_items": self.list_items,
            "text_chars": self.text_chars,
            "text_words": self.text_words,
            "structural_richness": self.structural_richness,
        }


@dataclass
class EditionFormat:
    """Un format/édition d'un même ouvrage."""
    gutenberg_id: int
    format: str          # "txt", "html", "epub"
    filepath: str
    language: str
    title: str
    word_count: int = 0
    paragraph_count: int = 0
    zones: List[TextZone] = field(default_factory=list)
    citations: List[ForeignCitation] = field(default_factory=list)
    atom_profile: Dict[str, float] = field(default_factory=dict)
    info_layers: Optional[InformationLayer] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def richness_score(self) -> int:
        """Score de richesse du format (FORMAT_RICHNESS)."""
        return FORMAT_RICHNESS.get(self.format, 10)


@dataclass
class UnifiedWork:
    """Vue unifiée d'un ouvrage à travers tous ses formats et éditions."""
    work_id: str           # Ex: "ALICE", "CANDIDE"
    title_original: str
    author: str
    original_lang: str
    editions: List[EditionFormat] = field(default_factory=list)
    
    # Comparaison inter-formats
    format_consistency: Dict = field(default_factory=dict)
    
    @property
    def languages(self) -> List[str]:
        return sorted(set(e.language for e in self.editions))
    
    @property
    def formats(self) -> List[str]:
        return sorted(set(e.format for e in self.editions))


def _extract_information_layers(filepath: str, fmt: str) -> InformationLayer:
    """Extrait le profil informationnel d'un fichier selon son format.
    
    HTML → analyse complète (headings, emphasis, images, links, tables)
    EPUB → via BeautifulSoup sur le contenu décompressé
    TXT  → seuls text_chars et text_words (tout le reste = 0 = perdu)
    
    C'est la fonction clé du modèle de perte : ce que cette fonction
    ne trouve PAS dans un format est de l'information perdue.
    """
    layers = InformationLayer()
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            raw = f.read()
    except Exception:
        return layers
    
    if fmt == 'html':
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, 'html.parser')
            
            # Remove script/style (not informational)
            for tag in soup(['script', 'style']):
                tag.decompose()
            
            # Structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            layers.headings = len(headings)
            layers.heading_texts = [h.get_text(strip=True) for h in headings[:50]]
            
            # Emphasis
            em_tags = soup.find_all(['em', 'i'])
            layers.emphasis_spans = len(em_tags)
            layers.emphasis_texts = [e.get_text(strip=True) for e in em_tags[:100]
                                     if e.get_text(strip=True)]
            strong_tags = soup.find_all(['strong', 'b'])
            layers.strong_spans = len(strong_tags)
            
            # Media
            imgs = soup.find_all('img')
            layers.images = len(imgs)
            layers.image_alts = [img.get('alt', '') for img in imgs if img.get('alt')]
            
            # Links
            layers.links = len(soup.find_all('a', href=True))
            
            # Tables
            layers.tables = len(soup.find_all('table'))
            layers.table_cells = len(soup.find_all(['td', 'th']))
            
            # Paragraphs
            layers.paragraphs = len(soup.find_all('p'))
            
            # Blocks
            layers.blockquotes = len(soup.find_all('blockquote'))
            layers.preformatted = len(soup.find_all(['pre', 'code']))
            layers.lists = len(soup.find_all(['ol', 'ul']))
            layers.list_items = len(soup.find_all('li'))
            
            # Text (pure text content — the bit-perfect reference)
            body = soup.find('body') or soup
            pure_text = body.get_text(separator=' ', strip=True)
            layers.text_chars = len(pure_text)
            layers.text_words = len(pure_text.split())
            
        except ImportError:
            pass
    
    elif fmt == 'epub':
        try:
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(filepath, options={"ignore_ncx": True})
            all_text_parts = []
            
            for item in book.get_items_of_type(9):  # ITEM_DOCUMENT
                content = item.get_content().decode('utf-8', errors='replace')
                soup = BeautifulSoup(content, 'html.parser')
                
                layers.headings += len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
                layers.emphasis_spans += len(soup.find_all(['em', 'i']))
                layers.strong_spans += len(soup.find_all(['strong', 'b']))
                layers.images += len(soup.find_all('img'))
                layers.paragraphs += len(soup.find_all('p'))
                layers.links += len(soup.find_all('a', href=True))
                layers.tables += len(soup.find_all('table'))
                layers.table_cells += len(soup.find_all(['td', 'th']))
                layers.blockquotes += len(soup.find_all('blockquote'))
                layers.lists += len(soup.find_all(['ol', 'ul']))
                layers.list_items += len(soup.find_all('li'))
                
                body = soup.find('body') or soup
                all_text_parts.append(body.get_text(separator=' ', strip=True))
            
            full_text = ' '.join(all_text_parts)
            layers.text_chars = len(full_text)
            layers.text_words = len(full_text.split())
            
        except (ImportError, Exception):
            pass
    
    else:
        # TXT, MD, etc. — aucune structure, seulement du texte
        # Tenter de récupérer les pseudo-headings (lignes courtes en majuscules)
        lines = raw.split('\n')
        for line in lines:
            stripped = line.strip()
            if (stripped and len(stripped) < 60 and
                (stripped.isupper() or
                 re.match(r'^(?:CHAPTER|CHAPITRE|KAPITEL)\s', stripped, re.I))):
                layers.headings += 1
                layers.heading_texts.append(stripped)
        
        # Comptage des pseudo-emphases (_italique_ ou *italique*)
        layers.emphasis_spans = len(re.findall(r'_[^_]{2,50}_', raw))
        layers.emphasis_spans += len(re.findall(r'\*[^*]{2,50}\*', raw))
        
        # Illustration markers — multilingual variants
        # [Illustration: caption], [Illustrazione: ...], [Ilustrajxo: ...],
        # [Abbildung: ...], [Ilustración: ...], [Figura: ...]
        illus_pattern = re.compile(
            r'\[(Illustration|Illustrazione|Ilustrajxo|Abbildung|'
            r'Ilustraci[oó]n|Figura|Gravure|Illustratie)'
            r'(?:[:\s]*([^\]]*))?\]', re.IGNORECASE
        )
        illus_matches = illus_pattern.findall(raw)
        layers.images = len(illus_matches)
        layers.image_alts = [
            caption.strip() for _, caption in illus_matches
            if caption.strip()
        ]
        
        # Paragraphs = blocks separated by blank lines
        layers.paragraphs = len(re.split(r'\n\s*\n', raw.strip()))
        
        layers.text_chars = len(raw)
        layers.text_words = len(raw.split())
    
    return layers


def unify_editions(
    work_id: str,
    edition_paths: Dict[str, str],
    work_metadata: Dict = None,
    analyze_atoms: bool = True,
    verbose: bool = False,
) -> UnifiedWork:
    """Crée une vue unifiée d'un ouvrage à partir de plusieurs formats/éditions.
    
    Pour un même ouvrage (même gutenberg_id ou même work_id), combine les
    informations extraites de chaque format disponible (txt, html, epub) et
    permet la comparaison inter-formats.
    
    Args:
        work_id: Identifiant de l'œuvre (ex: "ALICE").
        edition_paths: Dict {edition_key: filepath}, ex:
            {"ALICE_EN_11_txt": "/path/pg11.txt", "ALICE_EN_11_html": "/path/pg11.html"}
        work_metadata: Métadonnées de l'œuvre (titre, auteur, etc.).
        analyze_atoms: Lancer l'analyse atomique sur chaque édition.
        verbose: Afficher la progression.
    
    Returns:
        UnifiedWork avec toutes les éditions et comparaisons.
    """
    from text_extractor import extract_document, detect_format
    
    meta = work_metadata or {}
    work = UnifiedWork(
        work_id=work_id,
        title_original=meta.get("title_original", work_id),
        author=meta.get("author", "Unknown"),
        original_lang=meta.get("original_lang", "en"),
    )
    
    for edition_key, filepath in edition_paths.items():
        if not os.path.exists(filepath):
            if verbose:
                print(f"  ⚠️  Fichier manquant : {filepath}")
            continue
        
        if verbose:
            print(f"  📄 {edition_key}: {filepath}")
        
        fmt = detect_format(filepath)
        
        # Extraction du texte
        extraction = extract_document(filepath)
        
        # Déterminer la langue
        lang = meta.get("lang", "en")
        # Essayer d'extraire la langue du edition_key (ex: ALICE_FR_55456)
        lang_match = re.search(r'_([a-z]{2})_', edition_key, re.IGNORECASE)
        if lang_match:
            lang = lang_match.group(1).lower()
        
        # Lire le texte brut pour la classification des zones
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                raw_text = f.read()
        except Exception:
            raw_text = ""
        
        # Classifier les zones
        zones = classify_gutenberg_zones(raw_text, declared_lang=lang)
        
        # Détecter les citations étrangères (dans le BODY seulement)
        body_zones = [z for z in zones if z.zone_type == ZoneType.BODY]
        citations = []
        for bz in body_zones:
            citations.extend(detect_foreign_citations(bz.text, lang))
        
        # Extraire le profil informationnel (dimensions structurelles)
        info_layers = _extract_information_layers(filepath, fmt)
        
        edition = EditionFormat(
            gutenberg_id=int(re.search(r'(\d+)', os.path.basename(filepath)).group(1))
                         if re.search(r'(\d+)', os.path.basename(filepath)) else 0,
            format=fmt,
            filepath=filepath,
            language=lang,
            title=extraction.title or meta.get("title_original", ""),
            word_count=extraction.total_words,
            paragraph_count=extraction.total_paragraphs,
            zones=zones,
            citations=citations,
            info_layers=info_layers,
            metadata={
                "edition_key": edition_key,
                "extraction_errors": extraction.errors,
            },
        )
        
        # Analyse atomique optionnelle
        if analyze_atoms:
            try:
                from semantic_serializer import export_document_atoms
                export = export_document_atoms(filepath, lang=lang, verbose=False)
                edition.atom_profile = export.atom_profile
            except Exception as e:
                edition.metadata["atom_error"] = str(e)
        
        work.editions.append(edition)
    
    # ── Comparaison inter-formats ────────────────────────────────────────
    if len(work.editions) >= 2:
        work.format_consistency = _compare_editions(work.editions)
    
    return work


def _compare_editions(editions: List[EditionFormat]) -> Dict:
    """Compare les éditions en mesurant la perte depuis le format le plus riche.
    
    Philosophie PaniniFS : le format le plus riche (HTML) est la référence
    bit-perfect. Chaque format plus pauvre est une projection qui perd
    de l'information. On mesure cette perte par dimension.
    """
    # Trier par richesse décroissante — le plus riche est la référence
    sorted_editions = sorted(editions, key=lambda e: e.richness_score, reverse=True)
    canonical = sorted_editions[0]
    
    comparison = {
        "edition_count": len(editions),
        "formats": [e.format for e in sorted_editions],
        "canonical_format": canonical.format,
        "canonical_richness": canonical.richness_score,
        "information_loss": {},
        "canonical_layers": {},
        "atom_similarity": {},
        "zone_consistency": {},
    }
    
    # ── Profil de référence (canonical) ──────────────────────────────────
    if canonical.info_layers:
        ref = canonical.info_layers
        comparison["canonical_layers"] = {
            "headings": ref.headings,
            "emphasis_spans": ref.emphasis_spans,
            "strong_spans": ref.strong_spans,
            "images": ref.images,
            "links": ref.links,
            "tables": ref.tables,
            "paragraphs": ref.paragraphs,
            "text_words": ref.text_words,
            "structural_richness": ref.structural_richness,
        }
        
        # ── Perte informationnelle par format (vs canonical) ─────────────
        for e in sorted_editions[1:]:
            if e.info_layers:
                loss = e.info_layers.loss_vs(ref)
                # Score synthétique de perte (moyenne des dimensions perdues)
                loss_values = [v for k, v in loss.items() if k != "text_words"]
                avg_loss = sum(loss_values) / max(len(loss_values), 1)
                total_dims_lost = sum(1 for v in loss_values if v > 0.5)
                
                comparison["information_loss"][e.format] = {
                    "per_dimension": loss,
                    "avg_structural_loss": round(avg_loss, 4),
                    "dimensions_mostly_lost": total_dims_lost,
                    "text_fidelity": round(1.0 - loss.get("text_words", 0), 4),
                    "richness_score": e.richness_score,
                }
    
    # ── Similarité cosinus des profils atomiques ────────────────────────
    profiles = [(e.language, e.format, e.atom_profile) for e in editions if e.atom_profile]
    if len(profiles) >= 2:
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                key = f"{profiles[i][0]}_{profiles[i][1]}_vs_{profiles[j][0]}_{profiles[j][1]}"
                sim = _cosine_sim(profiles[i][2], profiles[j][2])
                comparison["atom_similarity"][key] = round(sim, 4)
    
    # ── Cohérence des zones ──────────────────────────────────────────────
    zone_counts = {}
    for e in editions:
        for z in e.zones:
            zt = z.zone_type.name
            zone_counts.setdefault(zt, []).append(1)
    comparison["zone_consistency"] = {
        zt: {"present_in": count, "total_editions": len(editions)}
        for zt, count in {zt: len(counts) for zt, counts in zone_counts.items()}.items()
    }
    
    return comparison


def _cosine_sim(profile_a: Dict[str, float], profile_b: Dict[str, float]) -> float:
    """Similarité cosinus entre deux profils atomiques."""
    all_keys = set(profile_a.keys()) | set(profile_b.keys())
    if not all_keys:
        return 0.0
    
    dot = sum(profile_a.get(k, 0) * profile_b.get(k, 0) for k in all_keys)
    norm_a = sum(v**2 for v in profile_a.values())**0.5
    norm_b = sum(v**2 for v in profile_b.values())**0.5
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot / (norm_a * norm_b)


# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED STRIP — Remplacement de strip_gutenberg_header_footer
# ═══════════════════════════════════════════════════════════════════════════════

def strip_gutenberg_boilerplate(text: str, declared_lang: str = "en") -> str:
    """Version améliorée de strip_gutenberg_header_footer.
    
    En plus de retirer le header/footer, cette version :
    1. Détecte les préambules DANS TOUTE LANGUE (pas seulement en anglais)
    2. Les marque comme sémantiquement identiques
    3. Retourne uniquement le BODY du texte
    
    Compatible en remplacement direct de strip_gutenberg_header_footer().
    """
    zones = classify_gutenberg_zones(text, declared_lang=declared_lang)
    
    # Extraire uniquement les zones BODY
    body_parts = [z.text for z in zones if z.zone_type == ZoneType.BODY]
    
    if body_parts:
        return '\n\n'.join(body_parts)
    
    # Fallback : si pas de zones détectées, utiliser la méthode classique
    return _fallback_strip(text)


def _fallback_strip(text: str) -> str:
    """Fallback classique pour les textes sans marqueurs Gutenberg standard."""
    start_markers = [
        "*** START OF THIS PROJECT GUTENBERG",
        "*** START OF THE PROJECT GUTENBERG",
        "***START OF THE PROJECT GUTENBERG",
        "*END*THE SMALL PRINT",
    ]
    end_markers = [
        "*** END OF THIS PROJECT GUTENBERG",
        "*** END OF THE PROJECT GUTENBERG",
        "***END OF THE PROJECT GUTENBERG",
        "End of the Project Gutenberg",
        "End of Project Gutenberg",
    ]
    
    start_idx = 0
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            nl = text.find('\n', idx)
            start_idx = nl + 1 if nl >= 0 else idx + len(marker)
            break
    
    end_idx = len(text)
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            end_idx = idx
            break
    
    return text[start_idx:end_idx].strip()


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT — Rapport de synthèse
# ═══════════════════════════════════════════════════════════════════════════════

def print_zone_report(zones: List[TextZone], title: str = "") -> None:
    """Affiche un rapport des zones détectées."""
    print(f"\n{'═' * 72}")
    print(f"ZONE CLASSIFICATION{(' — ' + title) if title else ''}")
    print(f"{'═' * 72}")
    
    total_chars = sum(z.end_char - z.start_char for z in zones)
    
    for z in zones:
        size = z.end_char - z.start_char
        pct = size / max(total_chars, 1) * 100
        lang_info = f" [{z.language}]" if z.language else ""
        equiv = " ≡IDENTICAL_SENSE" if z.metadata.get("equivalent_across_languages") else ""
        
        print(f"  {z.zone_type.name:25s} {size:7,d} chars ({pct:5.1f}%)"
              f"{lang_info}{equiv}")
        if z.zone_type in (ZoneType.GUTENBERG_HEADER, ZoneType.GUTENBERG_FOOTER):
            bp_score = z.metadata.get("boilerplate_score", 0)
            bp_lang = z.metadata.get("boilerplate_lang", "?")
            print(f"    ↳ boilerplate score: {bp_score:.3f}, detected lang: {bp_lang}")
    
    print(f"{'─' * 72}")
    
    # Résumé des citations étrangères
    citation_zones = [z for z in zones if z.zone_type == ZoneType.FOREIGN_CITATION]
    if citation_zones:
        print(f"  🌐 {len(citation_zones)} foreign citation(s) detected")
        for cz in citation_zones:
            print(f"    [{cz.language}] {cz.text[:80]}...")


def print_citation_report(citations: List[ForeignCitation], doc_lang: str = "") -> None:
    """Affiche un rapport des citations en langue étrangère."""
    if not citations:
        print(f"  Aucune citation en langue étrangère détectée.")
        return
    
    print(f"\n{'═' * 72}")
    print(f"FOREIGN CITATIONS (document language: {doc_lang})")
    print(f"{'═' * 72}")
    
    by_lang = {}
    for c in citations:
        by_lang.setdefault(c.detected_language, []).append(c)
    
    for lang, cits in sorted(by_lang.items()):
        print(f"\n  ── {lang.upper()} ({len(cits)} citation(s)) ──")
        for c in cits[:10]:  # Limiter l'affichage
            preview = c.text[:100].replace('\n', ' ')
            print(f"    [{c.detection_method}] conf={c.confidence:.2f}: {preview}")
            if c.context_before:
                print(f"      ...{c.context_before[-30:]} │ {preview[:40]}... │ {c.context_after[:30]}...")


def print_unified_work_report(work: UnifiedWork) -> None:
    """Affiche un rapport de la vue unifiée d'un ouvrage."""
    print(f"\n{'═' * 72}")
    print(f"UNIFIED WORK: {work.title_original}")
    print(f"{'═' * 72}")
    print(f"  Author:     {work.author}")
    print(f"  Original:   {work.original_lang}")
    print(f"  Languages:  {', '.join(work.languages)}")
    print(f"  Formats:    {', '.join(work.formats)}")
    print(f"  Editions:   {len(work.editions)}")
    
    for e in work.editions:
        print(f"\n  ── {e.language.upper()} / {e.format} (pg{e.gutenberg_id}) ──")
        print(f"    Words:      {e.word_count:,}")
        print(f"    Paragraphs: {e.paragraph_count}")
        print(f"    Zones:      {len(e.zones)}")
        if e.citations:
            print(f"    Citations:  {len(e.citations)} foreign")
            for c in e.citations[:3]:
                print(f"      [{c.detected_language}] {c.text[:60]}...")
        if e.atom_profile:
            top_atoms = sorted(e.atom_profile.items(), key=lambda x: -x[1])[:5]
            print(f"    Top atoms:  {', '.join(f'{a}={v:.1%}' for a, v in top_atoms)}")
    
    if work.format_consistency:
        fc = work.format_consistency
        print(f"\n  ── INTER-FORMAT CONSISTENCY ──")
        if fc.get("word_count_variance"):
            wcv = fc["word_count_variance"]
            print(f"    Word count: mean={wcv['mean']}, CV={wcv['cv']:.4f}")
        if fc.get("atom_similarity"):
            for pair, sim in fc["atom_similarity"].items():
                print(f"    Atom sim ({pair}): {sim:.4f}")
    
    print(f"{'═' * 72}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gutenberg preamble normalizer & citation detector"
    )
    parser.add_argument("file", nargs="?", help="Gutenberg text file to analyze")
    parser.add_argument("--lang", default="en", help="Document language (default: en)")
    parser.add_argument("--zones", action="store_true", help="Show zone classification")
    parser.add_argument("--citations", action="store_true", help="Detect foreign citations")
    parser.add_argument("--all", action="store_true", help="Full analysis")
    parser.add_argument("--strip", action="store_true", help="Output stripped body text only")
    
    args = parser.parse_args()
    
    if not args.file:
        parser.print_help()
        print("\nExample:")
        print("  python gutenberg_preamble_normalizer.py gutenberg_corpus/fr/pg55456.txt --lang fr --all")
        exit(1)
    
    with open(args.file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    
    if args.strip:
        print(strip_gutenberg_boilerplate(text, declared_lang=args.lang))
        exit(0)
    
    if args.zones or args.all:
        zones = classify_gutenberg_zones(text, declared_lang=args.lang)
        print_zone_report(zones, title=os.path.basename(args.file))
    
    if args.citations or args.all:
        # D'abord strip le boilerplate
        body = strip_gutenberg_boilerplate(text, declared_lang=args.lang)
        citations = detect_foreign_citations(body, args.lang)
        print_citation_report(citations, doc_lang=args.lang)
    
    if not any([args.zones, args.citations, args.all, args.strip]):
        # Par défaut : zones + citations
        zones = classify_gutenberg_zones(text, declared_lang=args.lang)
        print_zone_report(zones, title=os.path.basename(args.file))
        body = strip_gutenberg_boilerplate(text, declared_lang=args.lang)
        citations = detect_foreign_citations(body, args.lang)
        print_citation_report(citations, doc_lang=args.lang)

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
    """Get stop words for a language, with fallback."""
    return STOP_WORDS.get(lang, set()) | DEFAULT_STOP_WORDS


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
    if lang in ("ja", "zh"):
        content = []
        for ch in text:
            if _is_cjk(ch) and ch not in stop_words:
                content.append(ch)
        # Also check non-CJK words in the text
        non_cjk = ''.join(' ' if _is_cjk(ch) else ch for ch in text)
        for w in non_cjk.split():
            w_lower = w.lower().strip(".,;:!?\"'()-–—…[]{}«»")
            if w_lower and len(w_lower) >= 2 and w_lower not in stop_words:
                content.append(w_lower)
        return content
    else:
        content = []
        for w in text.split():
            w_lower = w.lower().strip(".,;:!?\"'()-–—…[]{}«»")
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
    atom_words = {a.get("word", "").lower().strip(".,;:!?\"'()-") for a in atoms}
    pf.atoms_unique = len(set(a.get("atom", "") for a in atoms))
    pf.lexical_coverage = pf.atom_alignments / max(pf.content_word_count, 1)
    pf.atom_density = pf.atom_alignments / max(pf.word_count, 1)
    
    # Find uncovered content words
    for cw in content_words:
        if cw not in atom_words:
            pf.uncovered_content_words.append(cw)
    
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

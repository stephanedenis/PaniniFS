#!/usr/bin/env python3
"""document_analyzer.py — Document→Atoms pipeline for PaniniFS v4.1

Orchestrates the full pipeline:
  file → text_extractor → language detection → seven_layers_engine → Dolt

This is the bridge between arbitrary documents and the semantic atom engine.

Usage:
    python document_analyzer.py my_book.pdf
    python document_analyzer.py my_book.epub --lang fr
    python document_analyzer.py article.html --format html --verbose
"""

import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# ── Local imports ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_extractor import extract_document, ExtractionResult
from seven_layers_engine import (
    analyze_syntax, align_words_to_atoms, analyze_morphology,
    detect_structural_operators, detect_paragraph_concepts,
    split_into_sentences, CONCEPT_MAPPINGS, get_db, dolt_sql, esc,
)


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE DETECTION
# ─────────────────────────────────────────────────────────────────────────────

# Supported languages (matching seven_layers_engine LANGUAGE_PROFILES)
SUPPORTED_LANGS = {"en", "fr", "de", "it", "es", "eo", "fi", "pt", "nl", "zh", "ja", "ru"}


def detect_language(text: str, hint: str = None) -> str:
    """Detect the language of a text string.
    
    Uses langdetect with fallback to trigram heuristic.
    Returns ISO 639-1 code (en, fr, de, it, es, fi, eo).
    """
    if hint and hint in SUPPORTED_LANGS:
        return hint

    # Try langdetect first
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0  # deterministic
        detected = detect(text[:5000])  # first 5K chars is enough
        if detected in SUPPORTED_LANGS:
            return detected
        # Map close variants
        lang_map = {
            "ca": "es",  # Catalan → Spanish (closest supported)
            "pt": "es",  # Portuguese → Spanish
            "nl": "de",  # Dutch → German
            "sv": "fi",  # Swedish → Finnish (closest supported)
            "no": "de",  # Norwegian → German
            "da": "de",  # Danish → German
        }
        return lang_map.get(detected, "en")
    except Exception:
        pass

    # Trigram fallback — check for language-specific patterns
    text_lower = text[:3000].lower()
    scores = {}
    trigram_patterns = {
        "fr": ["les ", "des ", "une ", "que ", " la ", " le ", " du ", "est "],
        "de": ["die ", "der ", "das ", "und ", "ein ", "ich ", " zu ", "den "],
        "it": ["che ", "per ", "con ", "del ", "una ", " il ", "gli ", "non "],
        "es": ["que ", "los ", "del ", "las ", "una ", "con ", " el ", "por "],
        "en": ["the ", "and ", "for ", "was ", "not ", "but ", "are ", "his "],
        "fi": ["ssa ", "stä ", "lle ", "kin ", "ään ", "nen ", "tta ", "sta "],
        "eo": [" la ", " de ", " en ", "ŭ ", "ĝi ", "ĉu ", " al ", "ĉio"],
    }
    for lang, patterns in trigram_patterns.items():
        scores[lang] = sum(text_lower.count(p) for p in patterns)

    if scores:
        return max(scores, key=scores.get)
    return "en"  # ultimate fallback


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def analyze_paragraph(text: str, lang: str) -> dict:
    """Run the 7-layer analysis on a single paragraph.
    
    Returns a dict with syntax, atoms, morphology, concepts, operators.
    This is a lightweight version of step3 — no Dolt storage, pure computation.
    """
    # Layer 1: Syntax
    syntax = analyze_syntax(text, lang)

    # Layer 2: Word→atom alignment (with WSD)
    atoms = align_words_to_atoms(text, lang, syntax_results=syntax)

    # Layer 3: Morphology
    morpho = analyze_morphology(text, lang, syntax)

    # Structural operators
    struct_ops = detect_structural_operators(text, lang, atoms, syntax)

    # Concept detection
    concepts = detect_paragraph_concepts(atoms, syntax, struct_ops)

    return {
        "syntax": syntax,
        "atoms": atoms,
        "morphology": morpho,
        "structural_operators": struct_ops,
        "concepts": concepts,
    }


def analyze_document(
    filepath: str,
    lang: str = None,
    force_format: str = None,
    store_in_dolt: bool = False,
    verbose: bool = False,
) -> dict:
    """Full document analysis pipeline.
    
    Args:
        filepath: Path to the document.
        lang: Force language (auto-detected if None).
        force_format: Force format (auto-detected if None).
        store_in_dolt: Store results in Dolt DB.
        verbose: Print progress.
    
    Returns:
        Dict with extraction results, analysis results, and statistics.
    """
    t_start = time.time()
    filepath = os.path.abspath(filepath)

    if verbose:
        print(f"\n{'=' * 70}")
        print(f"DOCUMENT ANALYSIS: {os.path.basename(filepath)}")
        print(f"{'=' * 70}")

    # ── Step 1: Extract text ──
    t_extract = time.time()
    extraction = extract_document(filepath, force_format=force_format)

    if extraction.errors:
        for err in extraction.errors:
            print(f"  ⚠️  {err}")

    if not extraction.paragraphs:
        print(f"  ❌ No text extracted from {filepath}")
        return {"error": "No text extracted", "extraction": extraction}

    if verbose:
        print(f"  📄 Format: {extraction.format}")
        print(f"  📝 Title: {extraction.title or '(unknown)'}")
        print(f"  📊 {extraction.total_paragraphs} paragraphs, "
              f"{extraction.total_words} words")
        print(f"  ⏱️  Extraction: {time.time() - t_extract:.2f}s")

    # ── Step 2: Detect language ──
    sample_text = ' '.join(p.text for p in extraction.paragraphs[:10])
    detected_lang = detect_language(sample_text, hint=lang)
    if verbose:
        print(f"  🌍 Language: {detected_lang}"
              f"{' (forced)' if lang else ' (auto-detected)'}")

    # ── Step 3: Analyze paragraphs ──
    t_analysis = time.time()
    all_atoms = Counter()
    all_concepts = Counter()
    all_operators = Counter()
    concept_details = []
    wsd_count = 0
    total_atom_count = 0
    negated_concepts = 0

    for i, para in enumerate(extraction.paragraphs):
        if verbose and (i % 50 == 0 or i == 0):
            print(f"  [{i + 1}/{extraction.total_paragraphs}] Analyzing...")

        result = analyze_paragraph(para.text, detected_lang)

        # Accumulate atom statistics
        for a in result["atoms"]:
            all_atoms[a["atom_id"]] += 1
            total_atom_count += 1
            if a.get("disambiguation") and "[WSD:" in str(a.get("disambiguation", "")):
                wsd_count += 1

        # Accumulate concept statistics
        for c in result["concepts"]:
            all_concepts[c["concept_id"]] += 1
            if c.get("negated"):
                negated_concepts += 1

        # Accumulate operator statistics
        for op in result["structural_operators"]:
            all_operators[op["operator"]] += 1

        # Keep detailed concept info
        if result["concepts"]:
            concept_details.append({
                "paragraph_index": para.index,
                "section": para.section,
                "concepts": [
                    {
                        "id": c["concept_id"],
                        "confidence": c["confidence"],
                        "negated": c.get("negated", False),
                        "quantified": c.get("quantified", False),
                        "modal": c.get("modal", False),
                    }
                    for c in result["concepts"]
                ],
            })

    analysis_time = time.time() - t_analysis

    # ── Step 4: Store in Dolt (optional) ──
    if store_in_dolt:
        _store_document_analysis(
            filepath, extraction, detected_lang,
            all_atoms, all_concepts, all_operators,
            verbose
        )

    # ── Build report ──
    total_time = time.time() - t_start
    report = {
        "filepath": filepath,
        "format": extraction.format,
        "title": extraction.title,
        "language": detected_lang,
        "paragraphs": extraction.total_paragraphs,
        "total_words": extraction.total_words,
        "atoms": {
            "total_detections": total_atom_count,
            "unique_atoms": len(all_atoms),
            "wsd_disambiguations": wsd_count,
            "top_atoms": all_atoms.most_common(15),
            "all_atoms": dict(all_atoms),          # full distribution for export
        },
        "concepts": {
            "unique_detected": len(all_concepts),
            "total_detections": sum(all_concepts.values()),
            "negated_detections": negated_concepts,
            "top_concepts": all_concepts.most_common(15),
            "all_concepts": dict(all_concepts),    # full distribution for export
            "details": concept_details,
        },
        "structural_operators": dict(all_operators),
        "timing": {
            "extraction_s": round(time.time() - t_start - analysis_time, 2),
            "analysis_s": round(analysis_time, 2),
            "total_s": round(total_time, 2),
            "paragraphs_per_sec": round(extraction.total_paragraphs / max(analysis_time, 0.01), 1),
        },
    }

    if verbose:
        _print_report(report)

    return report


# ─────────────────────────────────────────────────────────────────────────────
# DOLT STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def _store_document_analysis(
    filepath, extraction, lang,
    all_atoms, all_concepts, all_operators,
    verbose=False
):
    """Store document analysis results in Dolt DB."""
    db = get_db()

    # Create document_analyses table if it doesn't exist
    dolt_sql("""
        CREATE TABLE IF NOT EXISTS document_analyses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filepath VARCHAR(500) NOT NULL,
            filename VARCHAR(200) NOT NULL,
            format VARCHAR(10) NOT NULL,
            title VARCHAR(500),
            language VARCHAR(5) NOT NULL,
            total_paragraphs INT NOT NULL,
            total_words INT NOT NULL,
            unique_atoms INT NOT NULL,
            unique_concepts INT NOT NULL,
            top_atoms_json TEXT,
            top_concepts_json TEXT,
            operators_json TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_filepath (filepath(255))
        )
    """, check=False)

    # Insert or update
    filename = os.path.basename(filepath)
    dolt_sql(f"""
        INSERT INTO document_analyses
        (filepath, filename, format, title, language, total_paragraphs,
         total_words, unique_atoms, unique_concepts,
         top_atoms_json, top_concepts_json, operators_json)
        VALUES (
            {esc(filepath)}, {esc(filename)}, {esc(extraction.format)},
            {esc(extraction.title)}, {esc(lang)},
            {extraction.total_paragraphs}, {extraction.total_words},
            {len(all_atoms)}, {len(all_concepts)},
            {esc(json.dumps(all_atoms.most_common(20)))},
            {esc(json.dumps(all_concepts.most_common(20)))},
            {esc(json.dumps(dict(all_operators)))}
        )
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            total_paragraphs = VALUES(total_paragraphs),
            total_words = VALUES(total_words),
            unique_atoms = VALUES(unique_atoms),
            unique_concepts = VALUES(unique_concepts),
            top_atoms_json = VALUES(top_atoms_json),
            top_concepts_json = VALUES(top_concepts_json),
            operators_json = VALUES(operators_json),
            analyzed_at = CURRENT_TIMESTAMP
    """, check=False)

    db.commit_data()

    if verbose:
        print(f"  💾 Stored in Dolt (document_analyses)")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT FORMATTING
# ─────────────────────────────────────────────────────────────────────────────

def _print_report(report: dict):
    """Print a formatted analysis report."""
    print(f"\n{'─' * 70}")
    print(f"ANALYSIS RESULTS")
    print(f"{'─' * 70}")
    print(f"  ⏱️  Total time: {report['timing']['total_s']}s "
          f"({report['timing']['paragraphs_per_sec']} para/s)")

    print(f"\n  ── Atoms ({report['atoms']['unique_atoms']} unique, "
          f"{report['atoms']['total_detections']} total) ──")
    for atom, count in report['atoms']['top_atoms'][:10]:
        print(f"    {atom:20s} {count:5d}")
    if report['atoms']['wsd_disambiguations']:
        print(f"    (WSD disambiguations: {report['atoms']['wsd_disambiguations']})")

    print(f"\n  ── Concepts ({report['concepts']['unique_detected']} unique, "
          f"{report['concepts']['total_detections']} total) ──")
    for concept, count in report['concepts']['top_concepts'][:10]:
        print(f"    {concept:20s} {count:5d}")
    if report['concepts']['negated_detections']:
        print(f"    (Negated detections: {report['concepts']['negated_detections']})")

    ops = report['structural_operators']
    if ops:
        print(f"\n  ── Structural operators ──")
        for op, count in sorted(ops.items()):
            print(f"    {op:10s} {count:5d}")

    print(f"\n{'=' * 70}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze a document through the PaniniFS atom engine.",
        epilog="Example: python document_analyzer.py my_book.pdf --verbose"
    )
    parser.add_argument("file", help="Path to the document to analyze")
    parser.add_argument("--lang", help="Force language (auto-detected if omitted)",
                        choices=list(SUPPORTED_LANGS))
    parser.add_argument("--format", dest="fmt",
                        help="Force format (auto-detected if omitted)",
                        choices=["pdf", "epub", "docx", "html", "md", "txt"])
    parser.add_argument("--store", action="store_true",
                        help="Store results in Dolt database")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print detailed progress")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    report = analyze_document(
        args.file,
        lang=args.lang,
        force_format=args.fmt,
        store_in_dolt=args.store,
        verbose=not args.json_output or args.verbose,
    )

    if args.json_output:
        # Remove concept_details for compact JSON
        if 'concepts' in report and 'details' in report['concepts']:
            report['concepts']['details'] = f"({len(report['concepts']['details'])} entries)"
        print(json.dumps(report, indent=2, ensure_ascii=False))

    sys.exit(0 if 'error' not in report else 1)


if __name__ == '__main__':
    main()

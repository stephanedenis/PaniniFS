#!/usr/bin/env python3
"""semantic_serializer.py — v4.2a: Serialize document atoms to portable JSON.

Exports the complete semantic analysis of a document (atoms, concepts,
structural operators, metadata) to a portable JSON format that can be
compared across languages, stored, and used for reconstruction (E2).

Usage:
    python semantic_serializer.py <file> [--output <path.json>] [--lang <code>]
    python semantic_serializer.py --compare <file1.json> <file2.json> [--report]
    python semantic_serializer.py --batch <dir> [--output-dir <dir>] [--lang <code>]

Part of PaniniFS concept store — NA-004 roadmap v4.2.
"""
import argparse
import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

# ─── Add parent paths ───
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_analyzer import analyze_document, detect_language
from text_extractor import extract_document


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

SCHEMA_VERSION = "1.1"

@dataclass
class SemanticExport:
    """Portable semantic analysis of a document."""
    schema_version: str = SCHEMA_VERSION
    source_path: str = ""
    source_filename: str = ""
    format: str = ""
    title: str = ""
    language: str = ""
    total_paragraphs: int = 0
    total_words: int = 0

    # Atom profile
    unique_atoms: int = 0
    total_atom_detections: int = 0
    atom_distribution: Dict[str, int] = field(default_factory=dict)
    # Normalized atom distribution (proportions 0.0–1.0)
    atom_profile: Dict[str, float] = field(default_factory=dict)

    # Concept profile
    unique_concepts: int = 0
    total_concept_detections: int = 0
    concept_distribution: Dict[str, int] = field(default_factory=dict)
    concept_profile: Dict[str, float] = field(default_factory=dict)

    # Structural operators
    operators: Dict[str, int] = field(default_factory=dict)

    # WSD statistics
    wsd_disambiguations: int = 0

    # Negation/modality statistics
    negated_concepts: int = 0
    modal_concepts: int = 0
    quantified_concepts: int = 0

    # Per-paragraph details (optional, for deep analysis)
    paragraph_atoms: List[Dict] = field(default_factory=list)

    # Rich 7-layer data per paragraph (v1.1 — for reconstruction fidelity)
    # Contains: text, syntax, word→atom, morphology, operators, discourse,
    # prosody, concepts with atom evidence — the full "spectrogramme"
    rich_layers: List[Dict] = field(default_factory=list)

    # Timing
    analysis_time_s: float = 0.0
    exported_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def export_document_atoms(
    filepath: str,
    lang: str = None,
    include_paragraphs: bool = False,
    include_rich: bool = False,
    verbose: bool = False,
) -> SemanticExport:
    """Analyze a document and export its semantic profile.
    
    Args:
        filepath: Path to the document to analyze.
        lang: Force language (auto-detected if None).
        include_paragraphs: Include per-paragraph concept summaries.
        include_rich: Include full 7-layer data per paragraph
            (word→atom alignments, morphology, discourse, prosody,
            concepts with atom evidence). ~10× larger output but
            enables reconstruction fidelity analysis.
        verbose: Print progress.
    
    Returns:
        SemanticExport with complete semantic profile.
    """
    t_start = time.time()

    # Run full analysis (with rich mode if requested)
    report = analyze_document(
        filepath, lang=lang, verbose=verbose,
        rich_mode=include_rich,
    )

    if "error" in report:
        raise ValueError(f"Analysis failed: {report['error']}")

    # Build export
    export = SemanticExport()
    export.source_path = report["filepath"]
    export.source_filename = os.path.basename(report["filepath"])
    export.format = report["format"]
    export.title = report.get("title", "")
    export.language = report["language"]
    export.total_paragraphs = report["paragraphs"]
    export.total_words = report["total_words"]

    # Atom distribution — use full distribution if available, fallback to top_atoms
    atom_counts = report["atoms"].get("all_atoms", dict(report["atoms"]["top_atoms"]))
    export.atom_distribution = atom_counts
    export.unique_atoms = report["atoms"]["unique_atoms"]
    export.total_atom_detections = report["atoms"]["total_detections"]
    export.wsd_disambiguations = report["atoms"]["wsd_disambiguations"]

    # Normalize atom distribution to proportions
    total = max(export.total_atom_detections, 1)
    export.atom_profile = {
        atom: round(count / total, 4)
        for atom, count in atom_counts.items()
    }

    # Concept distribution — use full distribution if available
    concept_counts = report["concepts"].get("all_concepts", dict(report["concepts"]["top_concepts"]))
    export.concept_distribution = concept_counts
    export.unique_concepts = report["concepts"]["unique_detected"]
    export.total_concept_detections = report["concepts"]["total_detections"]
    export.negated_concepts = report["concepts"]["negated_detections"]

    # Normalize concept distribution
    total_c = max(export.total_concept_detections, 1)
    export.concept_profile = {
        concept: round(count / total_c, 4)
        for concept, count in concept_counts.items()
    }

    # Count modal/quantified from concept details
    for detail in report["concepts"]["details"]:
        for c in detail["concepts"]:
            if c.get("modal"):
                export.modal_concepts += 1
            if c.get("quantified"):
                export.quantified_concepts += 1

    # Structural operators
    export.operators = report["structural_operators"]

    # Per-paragraph details (optional)
    if include_paragraphs:
        export.paragraph_atoms = report["concepts"]["details"]

    # Rich 7-layer data (v1.1 — for reconstruction fidelity)
    if include_rich and "rich_layers" in report:
        export.rich_layers = report["rich_layers"]

    export.analysis_time_s = round(time.time() - t_start, 2)
    export.exported_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    return export


def save_export(export: SemanticExport, output_path: str) -> str:
    """Save a SemanticExport to a JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export.to_dict(), f, indent=2, ensure_ascii=False)
    return output_path


def load_export(path: str) -> SemanticExport:
    """Load a SemanticExport from a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    export = SemanticExport()
    for key, value in data.items():
        if hasattr(export, key):
            setattr(export, key, value)
    return export


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-LANGUAGE COMPARISON (v4.2b)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ComparisonResult:
    """Result of comparing two semantic exports."""
    doc_a: str = ""  # filename
    doc_b: str = ""
    lang_a: str = ""
    lang_b: str = ""

    # Atom comparison
    shared_atoms: List[str] = field(default_factory=list)
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    atom_jaccard: float = 0.0  # |intersection| / |union|
    atom_cosine: float = 0.0   # cosine similarity of atom profiles
    atom_rank_correlation: float = 0.0  # Spearman rank correlation

    # Concept comparison
    shared_concepts: List[str] = field(default_factory=list)
    concepts_only_a: List[str] = field(default_factory=list)
    concepts_only_b: List[str] = field(default_factory=list)
    concept_jaccard: float = 0.0
    concept_cosine: float = 0.0

    # Operator comparison
    operator_similarity: float = 0.0  # cosine of operator vectors

    # Overall universality score
    universality_score: float = 0.0  # weighted average

    def to_dict(self) -> dict:
        return asdict(self)


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors (dicts)."""
    all_keys = set(vec_a) | set(vec_b)
    if not all_keys:
        return 0.0

    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in all_keys)
    mag_a = sum(v ** 2 for v in vec_a.values()) ** 0.5
    mag_b = sum(v ** 2 for v in vec_b.values()) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return round(dot / (mag_a * mag_b), 4)


def _spearman_rank(dist_a: Dict[str, int], dist_b: Dict[str, int]) -> float:
    """Spearman rank correlation between two distributions.
    
    Only considers atoms/concepts present in both.
    """
    common = sorted(set(dist_a) & set(dist_b))
    if len(common) < 2:
        return 0.0

    # Rank by count (descending)
    sorted_a = sorted(dist_a.items(), key=lambda x: -x[1])
    sorted_b = sorted(dist_b.items(), key=lambda x: -x[1])

    rank_a = {item: i + 1 for i, (item, _) in enumerate(sorted_a)}
    rank_b = {item: i + 1 for i, (item, _) in enumerate(sorted_b)}

    n = len(common)
    d_sq = sum((rank_a[k] - rank_b[k]) ** 2 for k in common)

    # Spearman formula: 1 - (6 * Σd²) / (n * (n²-1))
    return round(1 - (6 * d_sq) / (n * (n ** 2 - 1)), 4)


def compare_documents(
    export_a: SemanticExport,
    export_b: SemanticExport,
) -> ComparisonResult:
    """Compare two semantic exports and compute universality metrics.
    
    The core question: when the same text is expressed in two languages,
    do the detected atoms and concepts converge?
    
    Returns:
        ComparisonResult with Jaccard, cosine, rank correlation metrics.
    """
    result = ComparisonResult()
    result.doc_a = export_a.source_filename
    result.doc_b = export_b.source_filename
    result.lang_a = export_a.language
    result.lang_b = export_b.language

    # ── Atom comparison ──
    atoms_a = set(export_a.atom_distribution.keys())
    atoms_b = set(export_b.atom_distribution.keys())

    result.shared_atoms = sorted(atoms_a & atoms_b)
    result.only_in_a = sorted(atoms_a - atoms_b)
    result.only_in_b = sorted(atoms_b - atoms_a)

    union = atoms_a | atoms_b
    result.atom_jaccard = round(len(atoms_a & atoms_b) / max(len(union), 1), 4)
    result.atom_cosine = _cosine_similarity(
        export_a.atom_profile, export_b.atom_profile
    )
    result.atom_rank_correlation = _spearman_rank(
        export_a.atom_distribution, export_b.atom_distribution
    )

    # ── Concept comparison ──
    concepts_a = set(export_a.concept_distribution.keys())
    concepts_b = set(export_b.concept_distribution.keys())

    result.shared_concepts = sorted(concepts_a & concepts_b)
    result.concepts_only_a = sorted(concepts_a - concepts_b)
    result.concepts_only_b = sorted(concepts_b - concepts_a)

    union_c = concepts_a | concepts_b
    result.concept_jaccard = round(
        len(concepts_a & concepts_b) / max(len(union_c), 1), 4
    )
    result.concept_cosine = _cosine_similarity(
        export_a.concept_profile, export_b.concept_profile
    )

    # ── Operator comparison ──
    # Normalize operators to proportions
    total_ops_a = max(sum(export_a.operators.values()), 1)
    total_ops_b = max(sum(export_b.operators.values()), 1)
    ops_a_norm = {k: v / total_ops_a for k, v in export_a.operators.items()}
    ops_b_norm = {k: v / total_ops_b for k, v in export_b.operators.items()}
    result.operator_similarity = _cosine_similarity(ops_a_norm, ops_b_norm)

    # ── Universality score ──
    # Weighted average: atoms are most important (they're the universal
    # building blocks), then concepts (language-mapped), then operators
    result.universality_score = round(
        0.40 * result.atom_cosine
        + 0.25 * result.concept_cosine
        + 0.20 * result.atom_rank_correlation
        + 0.10 * result.atom_jaccard
        + 0.05 * result.operator_similarity,
        4
    )

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD (v4.2c)
# ═══════════════════════════════════════════════════════════════════════════════

def print_comparison_dashboard(
    comparison: ComparisonResult,
    export_a: SemanticExport,
    export_b: SemanticExport,
):
    """Print a visual dashboard of the cross-language comparison."""
    print(f"\n{'═' * 72}")
    print("CROSS-LANGUAGE UNIVERSALITY ANALYSIS")
    print(f"{'═' * 72}")
    print(f"  📄 A: {comparison.doc_a} ({comparison.lang_a})")
    print(f"  📄 B: {comparison.doc_b} ({comparison.lang_b})")

    # Overview
    print(f"\n  {'─' * 68}")
    print(f"  OVERVIEW")
    print(f"  {'─' * 68}")
    print(f"  {'':30s} {'A (' + comparison.lang_a + ')':>15s} {'B (' + comparison.lang_b + ')':>15s}")
    print(f"  {'Paragraphs':30s} {export_a.total_paragraphs:>15d} {export_b.total_paragraphs:>15d}")
    print(f"  {'Words':30s} {export_a.total_words:>15d} {export_b.total_words:>15d}")
    print(f"  {'Unique atoms':30s} {export_a.unique_atoms:>15d} {export_b.unique_atoms:>15d}")
    print(f"  {'Atom detections':30s} {export_a.total_atom_detections:>15d} {export_b.total_atom_detections:>15d}")
    print(f"  {'Unique concepts':30s} {export_a.unique_concepts:>15d} {export_b.unique_concepts:>15d}")
    print(f"  {'Concept detections':30s} {export_a.total_concept_detections:>15d} {export_b.total_concept_detections:>15d}")
    print(f"  {'WSD disambiguations':30s} {export_a.wsd_disambiguations:>15d} {export_b.wsd_disambiguations:>15d}")

    # Universality score
    print(f"\n  {'─' * 68}")
    score = comparison.universality_score
    bar_len = int(score * 40)
    bar = '█' * bar_len + '░' * (40 - bar_len)
    grade = (
        "EXCELLENT" if score >= 0.85 else
        "BON" if score >= 0.70 else
        "MODÉRÉ" if score >= 0.50 else
        "FAIBLE" if score >= 0.30 else
        "TRÈS FAIBLE"
    )
    print(f"  🌍 UNIVERSALITY SCORE: {score:.4f}  [{bar}]  {grade}")
    print(f"  {'─' * 68}")

    # Atom analysis
    print(f"\n  ── Atoms ──")
    print(f"    Shared:  {len(comparison.shared_atoms):>3d}  {comparison.shared_atoms}")
    if comparison.only_in_a:
        print(f"    Only A:  {len(comparison.only_in_a):>3d}  {comparison.only_in_a}")
    if comparison.only_in_b:
        print(f"    Only B:  {len(comparison.only_in_b):>3d}  {comparison.only_in_b}")
    print(f"    Jaccard similarity:    {comparison.atom_jaccard:.4f}")
    print(f"    Cosine similarity:     {comparison.atom_cosine:.4f}")
    print(f"    Rank correlation:      {comparison.atom_rank_correlation:.4f}")

    # Top atoms side by side
    print(f"\n    Top atoms (by proportion):")
    top_a = sorted(export_a.atom_profile.items(), key=lambda x: -x[1])[:10]
    top_b = sorted(export_b.atom_profile.items(), key=lambda x: -x[1])[:10]

    print(f"    {'A (' + comparison.lang_a + ')':>25s}  {'B (' + comparison.lang_b + ')':>25s}")
    for i in range(max(len(top_a), len(top_b))):
        a_str = f"{top_a[i][0]:>15s} {top_a[i][1]:5.1%}" if i < len(top_a) else " " * 21
        b_str = f"{top_b[i][0]:>15s} {top_b[i][1]:5.1%}" if i < len(top_b) else " " * 21
        print(f"    {a_str}  {b_str}")

    # Concept analysis
    print(f"\n  ── Concepts ──")
    print(f"    Shared:  {len(comparison.shared_concepts):>3d}")
    if comparison.concepts_only_a:
        print(f"    Only A:  {len(comparison.concepts_only_a):>3d}  {comparison.concepts_only_a[:10]}{'...' if len(comparison.concepts_only_a) > 10 else ''}")
    if comparison.concepts_only_b:
        print(f"    Only B:  {len(comparison.concepts_only_b):>3d}  {comparison.concepts_only_b[:10]}{'...' if len(comparison.concepts_only_b) > 10 else ''}")
    print(f"    Jaccard similarity:    {comparison.concept_jaccard:.4f}")
    print(f"    Cosine similarity:     {comparison.concept_cosine:.4f}")

    # Operator analysis
    print(f"\n  ── Structural operators ──")
    all_ops = sorted(set(export_a.operators) | set(export_b.operators))
    for op in all_ops:
        a_val = export_a.operators.get(op, 0)
        b_val = export_b.operators.get(op, 0)
        print(f"    {op:>8s}  A={a_val:>5d}  B={b_val:>5d}")
    print(f"    Similarity:            {comparison.operator_similarity:.4f}")

    # Metric breakdown
    print(f"\n  ── Score breakdown ──")
    print(f"    Atom cosine (×0.40):       {comparison.atom_cosine:.4f} → {0.40 * comparison.atom_cosine:.4f}")
    print(f"    Concept cosine (×0.25):    {comparison.concept_cosine:.4f} → {0.25 * comparison.concept_cosine:.4f}")
    print(f"    Atom rank corr (×0.20):    {comparison.atom_rank_correlation:.4f} → {0.20 * comparison.atom_rank_correlation:.4f}")
    print(f"    Atom Jaccard (×0.10):      {comparison.atom_jaccard:.4f} → {0.10 * comparison.atom_jaccard:.4f}")
    print(f"    Operator sim (×0.05):      {comparison.operator_similarity:.4f} → {0.05 * comparison.operator_similarity:.4f}")
    print(f"    {'─' * 40}")
    print(f"    TOTAL:                     {comparison.universality_score:.4f}")

    print(f"\n{'═' * 72}")


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def batch_export(
    input_dir: str,
    output_dir: str = None,
    lang: str = None,
    verbose: bool = False,
) -> List[str]:
    """Export semantic profiles for all supported files in a directory.
    
    Returns list of output JSON paths.
    """
    supported_exts = {'.txt', '.md', '.html', '.htm', '.pdf', '.epub', '.docx'}
    output_dir = output_dir or os.path.join(input_dir, "semantic_exports")
    os.makedirs(output_dir, exist_ok=True)

    output_paths = []
    files = sorted(
        f for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported_exts
    )

    for i, filename in enumerate(files):
        filepath = os.path.join(input_dir, filename)
        if not os.path.isfile(filepath):
            continue

        if verbose:
            print(f"\n[{i + 1}/{len(files)}] Processing {filename}...")

        try:
            export = export_document_atoms(filepath, lang=lang, verbose=False)
            out_name = os.path.splitext(filename)[0] + ".semantic.json"
            out_path = os.path.join(output_dir, out_name)
            save_export(export, out_path)
            output_paths.append(out_path)

            if verbose:
                print(f"  ✅ {export.unique_atoms} atoms, "
                      f"{export.unique_concepts} concepts → {out_name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    return output_paths


# ═══════════════════════════════════════════════════════════════════════════════
# E2 PREPARATION (v4.2d)
# ═══════════════════════════════════════════════════════════════════════════════

def prepare_e2_experiment(
    exports: List[SemanticExport],
    output_path: str = None,
) -> dict:
    """Prepare E2 experiment data: aggregate universality metrics across
    multiple document pairs.
    
    This generates the baseline data needed for E2 (reconstruction):
    - Which atoms are truly universal (appear in all analyzed documents)?
    - What's the minimum atom set for reconstruction?
    - What's the concept convergence rate?
    
    Args:
        exports: List of semantic exports to analyze.
        output_path: Optional path to save E2 preparation data.
    
    Returns:
        Dict with E2 preparation data.
    """
    if len(exports) < 2:
        return {"error": "Need at least 2 exports for E2 preparation"}

    # Find atoms present in ALL exports
    all_atom_sets = [set(e.atom_distribution.keys()) for e in exports]
    universal_atoms = set.intersection(*all_atom_sets) if all_atom_sets else set()
    all_atoms_union = set.union(*all_atom_sets) if all_atom_sets else set()

    # Find concepts present in ALL exports
    all_concept_sets = [set(e.concept_distribution.keys()) for e in exports]
    universal_concepts = set.intersection(*all_concept_sets) if all_concept_sets else set()
    all_concepts_union = set.union(*all_concept_sets) if all_concept_sets else set()

    # Atom frequency stability: for universal atoms, how stable is their
    # relative frequency across documents?
    atom_stability = {}
    for atom in universal_atoms:
        proportions = [e.atom_profile.get(atom, 0) for e in exports]
        mean_p = sum(proportions) / len(proportions)
        variance = sum((p - mean_p) ** 2 for p in proportions) / len(proportions)
        cv = (variance ** 0.5) / max(mean_p, 1e-10)  # coefficient of variation
        atom_stability[atom] = {
            "mean_proportion": round(mean_p, 4),
            "std_dev": round(variance ** 0.5, 4),
            "cv": round(cv, 4),  # lower = more stable
            "proportions": [round(p, 4) for p in proportions],
        }

    # Sort by stability (lowest CV = most stable)
    stable_atoms = sorted(atom_stability.items(), key=lambda x: x[1]["cv"])

    e2_data = {
        "experiment": "E2 — RECONSTRUCTION PREPARATION",
        "documents_analyzed": len(exports),
        "languages": list(set(e.language for e in exports)),
        "documents": [
            {
                "filename": e.source_filename,
                "language": e.language,
                "words": e.total_words,
                "unique_atoms": e.unique_atoms,
                "unique_concepts": e.unique_concepts,
            }
            for e in exports
        ],
        "universal_atoms": {
            "count": len(universal_atoms),
            "total_atoms_seen": len(all_atoms_union),
            "universality_rate": round(len(universal_atoms) / max(len(all_atoms_union), 1), 4),
            "atoms": sorted(universal_atoms),
        },
        "universal_concepts": {
            "count": len(universal_concepts),
            "total_concepts_seen": len(all_concepts_union),
            "universality_rate": round(len(universal_concepts) / max(len(all_concepts_union), 1), 4),
            "concepts": sorted(universal_concepts),
        },
        "atom_stability": {
            "most_stable": [(a, s["cv"]) for a, s in stable_atoms[:10]],
            "least_stable": [(a, s["cv"]) for a, s in stable_atoms[-5:]],
            "details": dict(stable_atoms),
        },
        "e2_readiness": {
            "minimum_atom_set_for_reconstruction": sorted(universal_atoms),
            "coverage_with_universal_only": round(
                sum(
                    sum(e.atom_distribution.get(a, 0) for a in universal_atoms) /
                    max(e.total_atom_detections, 1)
                    for e in exports
                ) / len(exports),
                4
            ),
            "recommendation": (
                "READY for E2" if len(universal_atoms) >= 15
                else "NEED MORE ATOMS — universal set too small for reconstruction"
            ),
        },
    }

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(e2_data, f, indent=2, ensure_ascii=False)

    return e2_data


def print_e2_report(e2_data: dict):
    """Print the E2 preparation report."""
    print(f"\n{'═' * 72}")
    print("E2 RECONSTRUCTION PREPARATION REPORT")
    print(f"{'═' * 72}")

    print(f"\n  Documents analyzed: {e2_data['documents_analyzed']}")
    print(f"  Languages: {', '.join(e2_data['languages'])}")

    for doc in e2_data["documents"]:
        print(f"    • {doc['filename']} ({doc['language']}): "
              f"{doc['words']} words, {doc['unique_atoms']} atoms, "
              f"{doc['unique_concepts']} concepts")

    ua = e2_data["universal_atoms"]
    print(f"\n  ── Universal Atoms ──")
    print(f"    Universal: {ua['count']} / {ua['total_atoms_seen']} "
          f"({ua['universality_rate']:.1%})")
    print(f"    Atoms: {ua['atoms']}")

    uc = e2_data["universal_concepts"]
    print(f"\n  ── Universal Concepts ──")
    print(f"    Universal: {uc['count']} / {uc['total_concepts_seen']} "
          f"({uc['universality_rate']:.1%})")
    print(f"    Concepts: {uc['concepts']}")

    stab = e2_data["atom_stability"]
    print(f"\n  ── Atom Stability (CV = coefficient of variation, lower = more stable) ──")
    print(f"    Most stable:")
    for atom, cv in stab["most_stable"]:
        print(f"      {atom:>20s}  CV={cv:.4f}")
    print(f"    Least stable:")
    for atom, cv in stab["least_stable"]:
        print(f"      {atom:>20s}  CV={cv:.4f}")

    e2r = e2_data["e2_readiness"]
    print(f"\n  ── E2 Readiness ──")
    print(f"    Minimum atom set: {len(e2r['minimum_atom_set_for_reconstruction'])} atoms")
    print(f"    Coverage with universal only: {e2r['coverage_with_universal_only']:.1%}")
    print(f"    📋 {e2r['recommendation']}")

    print(f"\n{'═' * 72}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Semantic serializer — export and compare document atoms"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # export
    p_export = subparsers.add_parser("export", help="Export document atoms to JSON")
    p_export.add_argument("file", help="File to analyze")
    p_export.add_argument("--output", "-o", help="Output JSON path")
    p_export.add_argument("--lang", help="Force language")
    p_export.add_argument("--paragraphs", action="store_true",
                         help="Include per-paragraph details")
    p_export.add_argument("--verbose", "-v", action="store_true")

    # compare
    p_compare = subparsers.add_parser("compare", help="Compare two semantic exports")
    p_compare.add_argument("file_a", help="First JSON export or document")
    p_compare.add_argument("file_b", help="Second JSON export or document")
    p_compare.add_argument("--json", action="store_true",
                          help="Output comparison as JSON")
    p_compare.add_argument("--output", "-o", help="Save comparison JSON to file")
    p_compare.add_argument("--verbose", "-v", action="store_true")

    # batch
    p_batch = subparsers.add_parser("batch", help="Export all files in a directory")
    p_batch.add_argument("dir", help="Input directory")
    p_batch.add_argument("--output-dir", help="Output directory for JSON exports")
    p_batch.add_argument("--lang", help="Force language")
    p_batch.add_argument("--verbose", "-v", action="store_true")

    # e2-prep
    p_e2 = subparsers.add_parser("e2-prep",
                                 help="Prepare E2 experiment from multiple exports")
    p_e2.add_argument("files", nargs="+", help="Semantic export JSON files")
    p_e2.add_argument("--output", "-o", help="Save E2 preparation data to file")
    p_e2.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "export":
        export = export_document_atoms(
            args.file,
            lang=args.lang,
            include_paragraphs=args.paragraphs,
            verbose=args.verbose,
        )
        output = args.output or os.path.splitext(args.file)[0] + ".semantic.json"
        save_export(export, output)
        print(f"\n✅ Exported to {output}")
        print(f"   {export.unique_atoms} atoms, {export.unique_concepts} concepts, "
              f"{export.total_words} words")

    elif args.command == "compare":
        # Load or analyze
        def load_or_analyze(path, verbose=False):
            if path.endswith(".semantic.json") or path.endswith(".json"):
                return load_export(path)
            else:
                return export_document_atoms(path, verbose=verbose)

        export_a = load_or_analyze(args.file_a, args.verbose)
        export_b = load_or_analyze(args.file_b, args.verbose)

        comparison = compare_documents(export_a, export_b)

        if args.json:
            print(json.dumps(comparison.to_dict(), indent=2, ensure_ascii=False))
        else:
            print_comparison_dashboard(comparison, export_a, export_b)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(comparison.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"\n💾 Comparison saved to {args.output}")

    elif args.command == "batch":
        paths = batch_export(
            args.dir,
            output_dir=args.output_dir,
            lang=args.lang,
            verbose=args.verbose,
        )
        print(f"\n✅ Exported {len(paths)} files")

    elif args.command == "e2-prep":
        exports = [load_export(f) for f in args.files]
        e2_data = prepare_e2_experiment(
            exports,
            output_path=args.output,
        )
        print_e2_report(e2_data)
        if args.output:
            print(f"\n💾 E2 preparation saved to {args.output}")


if __name__ == "__main__":
    main()

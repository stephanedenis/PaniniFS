#!/usr/bin/env python3
"""round_trip_reconstruction.py — v4.6: Attempt to reconstruct text from atoms

This is the E2 experiment: given a rich semantic export produced by PaniniFS,
attempt to reconstruct an approximate version of the original text.

The reconstruction uses:
  - L2 word→atom alignments (primary: exact word forms preserved)
  - L1 syntax (word order, POS tags, dependencies)
  - L3 morphology (tense, gender, number for inflection)
  - L4 operators (negation, modality, quantification)
  - L5 discourse (conjunctions, connectors)
  - L6 prosody (rhythm hints for word choice)
  - L7 concepts (high-level meaning verification)

Strategy:
  1. SKELETON: Use syntax layer to establish word positions
  2. FILL: Place known atom-aligned words at their positions
  3. CONNECT: Insert function words and operators
  4. VERIFY: Check concept coverage of reconstruction

This is NOT expected to produce identical text — it measures how much
semantic information survives the atom decomposition.

Part of PaniniFS concept store — E2 reconstruction experiment.
"""

import json
import os
import sys
import time
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════════════════════════
# RECONSTRUCTION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ParagraphReconstruction:
    """Result of reconstructing one paragraph."""
    index: int = 0
    original: str = ""
    reconstructed: str = ""
    
    # Token-level metrics
    original_tokens: int = 0
    reconstructed_tokens: int = 0
    shared_tokens: int = 0        # tokens appearing in both
    
    # Word overlap (Jaccard-like)
    word_overlap: float = 0.0     # |intersection| / |union|
    word_precision: float = 0.0   # |intersection| / |reconstructed|
    word_recall: float = 0.0      # |intersection| / |original|
    
    # Atom preservation
    atoms_in_original: int = 0
    atoms_in_reconstruction: int = 0
    atom_preservation: float = 0.0
    
    # Positional accuracy
    position_accuracy: float = 0.0  # % of words in correct relative order


@dataclass
class DocumentReconstruction:
    """Result of reconstructing a full document."""
    filepath: str = ""
    language: str = ""
    total_paragraphs: int = 0
    
    # Aggregate metrics
    avg_word_overlap: float = 0.0
    avg_word_precision: float = 0.0
    avg_word_recall: float = 0.0
    avg_atom_preservation: float = 0.0
    
    # F1-like score
    reconstruction_f1: float = 0.0
    
    # Per-paragraph
    paragraphs: List[ParagraphReconstruction] = field(default_factory=list)
    
    analysis_time_s: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION WORD TEMPLATES (for connecting content words)
# ═══════════════════════════════════════════════════════════════════════════════

CONNECTORS = {
    "en": {
        "NOUN_NOUN": ["of", "and", "the"],
        "VERB_NOUN": ["the", "a"],
        "ADJ_NOUN": [],
        "NOUN_VERB": [],
        "default_article": "the",
        "conjunction": "and",
    },
    "fr": {
        "NOUN_NOUN": ["de", "et", "le", "la"],
        "VERB_NOUN": ["le", "la", "un", "une"],
        "ADJ_NOUN": [],
        "NOUN_VERB": [],
        "default_article": "le",
        "conjunction": "et",
    },
    "de": {
        "NOUN_NOUN": ["der", "und", "des"],
        "VERB_NOUN": ["der", "die", "das", "ein"],
        "ADJ_NOUN": [],
        "NOUN_VERB": [],
        "default_article": "der",
        "conjunction": "und",
    },
    "es": {
        "NOUN_NOUN": ["de", "y", "el", "la"],
        "VERB_NOUN": ["el", "la", "un", "una"],
        "ADJ_NOUN": [],
        "NOUN_VERB": [],
        "default_article": "el",
        "conjunction": "y",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# RECONSTRUCTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def reconstruct_paragraph(
    layer: dict,
    lang: str,
    mode: str = "full",
) -> ParagraphReconstruction:
    """Reconstruct a paragraph from its rich layer data.
    
    Modes:
      "full"   — Use all layers (syntax gives all words → trivial 100%)
      "atoms"  — Use only L2 atoms + L4 operators + L5 discourse (true E2 test)
      "semantic" — Use L2 atoms + L4 operators + L5 discourse + L7 concept keywords
    
    The "atoms" mode answers: "What survives if we only keep the semantic atoms?"
    """
    pr = ParagraphReconstruction()
    pr.index = layer.get("paragraph_index", 0)
    pr.original = layer.get("text", "")
    
    original_words = pr.original.split()
    pr.original_tokens = len(original_words)
    
    if not original_words:
        return pr
    
    # ─── Build reconstruction based on mode ───
    
    slots = {}  # position → word
    
    if mode == "full":
        # Use ALL layers — trivially recovers everything
        for s in layer.get("syntax", []):
            pos = s.get("position", -1)
            word = s.get("word", "")
            if word and pos >= 0:
                slots[pos] = word
        
        # L2 atoms override syntax (exact original forms)
        for a in layer.get("atoms", []):
            pos = a.get("position", -1)
            word = a.get("word", "")
            if word and pos >= 0:
                slots[pos] = word
        
        # L4 operators
        for op in layer.get("operators", []):
            pos = op.get("position")
            word = op.get("word", "")
            if word and pos is not None and pos >= 0:
                if pos not in slots:
                    slots[pos] = word
        
        # L5 discourse connectors
        for d in layer.get("discourse", []):
            connector = d.get("connector", "")
            pos = d.get("source_pos")
            if connector and pos is not None and pos >= 0:
                if pos not in slots:
                    slots[pos] = connector
    
    elif mode in ("atoms", "semantic"):
        # ONLY L2 atom-aligned words (the true E2 test)
        for a in layer.get("atoms", []):
            pos = a.get("position", -1)
            word = a.get("word", "")
            if word and pos >= 0:
                slots[pos] = word
        
        # L4 operators (negation, modality — critical for meaning)
        for op in layer.get("operators", []):
            pos = op.get("position")
            word = op.get("word", "")
            if word and pos is not None and pos >= 0:
                slots[pos] = word
        
        # L5 discourse connectors (conjunctions, anaphora)
        for d in layer.get("discourse", []):
            connector = d.get("connector", "")
            pos = d.get("source_pos")
            if connector and pos is not None and pos >= 0:
                slots[pos] = connector
        
        if mode == "semantic":
            # Also use concept evidence to fill gaps
            for c in layer.get("concepts", []):
                evidence = c.get("atoms_evidence", {})
                for atom_id, keyword in evidence.items():
                    if isinstance(keyword, dict):
                        keyword = keyword.get("keyword", keyword.get("word", ""))
                    if not isinstance(keyword, str) or not keyword:
                        continue
                    # Find the position of this keyword in the text
                    for i, w in enumerate(original_words):
                        wl = w.lower().strip(".,;:!?\"'()-–—…")
                        if wl == keyword.lower() and i not in slots:
                            slots[i] = w
                            break
    
    # ─── Step 2: Assemble reconstruction ───
    
    if not slots:
        pr.reconstructed = ""
        return pr
    
    max_pos = max(slots.keys())
    reconstructed_words = []
    
    for i in range(max_pos + 1):
        if i in slots:
            reconstructed_words.append(slots[i])
    
    pr.reconstructed = " ".join(reconstructed_words)
    pr.reconstructed_tokens = len(reconstructed_words)
    
    # ─── Step 3: Compute metrics ───
    
    # Normalize for comparison
    def normalize(word):
        return word.lower().strip(".,;:!?\"'()-–—…[]{}«»")
    
    orig_set = Counter(normalize(w) for w in original_words if normalize(w))
    recon_set = Counter(normalize(w) for w in reconstructed_words if normalize(w))
    
    # Intersection (min count for each word)
    intersection = sum((orig_set & recon_set).values())
    union = sum((orig_set | recon_set).values())
    
    pr.shared_tokens = intersection
    pr.word_overlap = intersection / max(union, 1)
    pr.word_precision = intersection / max(sum(recon_set.values()), 1)
    pr.word_recall = intersection / max(sum(orig_set.values()), 1)
    
    # Atom preservation: check if atoms from original appear in reconstruction
    layer_atoms = layer.get("atoms", [])
    pr.atoms_in_original = len(layer_atoms)
    atom_words_in_recon = sum(
        1 for a in layer_atoms
        if normalize(a.get("word", "")) in recon_set
    )
    pr.atoms_in_reconstruction = atom_words_in_recon
    pr.atom_preservation = atom_words_in_recon / max(len(layer_atoms), 1)
    
    # Positional accuracy: % of shared words in correct relative order
    if intersection > 0:
        orig_order = [normalize(w) for w in original_words if normalize(w)]
        recon_order = [normalize(w) for w in reconstructed_words if normalize(w)]
        
        # Find common words and check order preservation
        common = set(orig_set.keys()) & set(recon_set.keys())
        if len(common) >= 2:
            # Simplified: check pairwise ordering of common words
            orig_positions = {}
            for i, w in enumerate(orig_order):
                if w in common and w not in orig_positions:
                    orig_positions[w] = i
            
            recon_positions = {}
            for i, w in enumerate(recon_order):
                if w in common and w not in recon_positions:
                    recon_positions[w] = i
            
            shared_words = list(set(orig_positions.keys()) & set(recon_positions.keys()))
            if len(shared_words) >= 2:
                correct = 0
                total = 0
                for i in range(len(shared_words)):
                    for j in range(i + 1, len(shared_words)):
                        w1, w2 = shared_words[i], shared_words[j]
                        orig_cmp = orig_positions[w1] < orig_positions[w2]
                        recon_cmp = recon_positions[w1] < recon_positions[w2]
                        if orig_cmp == recon_cmp:
                            correct += 1
                        total += 1
                pr.position_accuracy = correct / max(total, 1)
            else:
                pr.position_accuracy = 1.0
        else:
            pr.position_accuracy = 1.0
    
    return pr


def reconstruct_document(
    filepath: str,
    lang: str = None,
    verbose: bool = False,
    mode: str = "atoms",
) -> DocumentReconstruction:
    """Reconstruct a document from its rich semantic analysis.
    
    This is the E2 experiment: analyze → enrich → reconstruct → compare.
    
    Args:
        filepath: Path to original document.
        lang: Force language detection.
        verbose: Print report.
        mode: "full" (all layers), "atoms" (L2+L4+L5 only), "semantic" (L2+L4+L5+L7).
    """
    from document_analyzer import analyze_document, detect_language
    
    t_start = time.time()
    
    if verbose:
        print(f"\n{'═' * 72}")
        print(f"ROUND-TRIP RECONSTRUCTION EXPERIMENT")
        print(f"{'═' * 72}")
        print(f"  📄 {os.path.basename(filepath)}")
    
    # Step 1: Rich analysis
    report = analyze_document(filepath, lang=lang, verbose=False, rich_mode=True)
    
    if "error" in report:
        raise ValueError(f"Analysis failed: {report['error']}")
    
    detected_lang = report["language"]
    rich_layers = report.get("rich_layers", [])
    
    if not rich_layers:
        raise ValueError("No rich layer data")
    
    if verbose:
        print(f"  🌍 Language: {detected_lang}")
        print(f"  📊 {len(rich_layers)} paragraphs analyzed in rich mode")
        print(f"  🔄 Reconstructing (mode={mode})...")
    
    # Step 2: Reconstruct each paragraph
    dr = DocumentReconstruction()
    dr.filepath = filepath
    dr.language = detected_lang
    dr.total_paragraphs = len(rich_layers)
    
    for layer in rich_layers:
        pr = reconstruct_paragraph(layer, detected_lang, mode=mode)
        dr.paragraphs.append(pr)
    
    # Step 3: Aggregate metrics
    n = max(dr.total_paragraphs, 1)
    valid = [p for p in dr.paragraphs if p.original_tokens > 0]
    nv = max(len(valid), 1)
    
    dr.avg_word_overlap = sum(p.word_overlap for p in valid) / nv
    dr.avg_word_precision = sum(p.word_precision for p in valid) / nv
    dr.avg_word_recall = sum(p.word_recall for p in valid) / nv
    dr.avg_atom_preservation = sum(p.atom_preservation for p in valid) / nv
    
    # F1 = 2 * P * R / (P + R)
    if dr.avg_word_precision + dr.avg_word_recall > 0:
        dr.reconstruction_f1 = (
            2 * dr.avg_word_precision * dr.avg_word_recall /
            (dr.avg_word_precision + dr.avg_word_recall)
        )
    
    dr.analysis_time_s = round(time.time() - t_start, 2)
    
    if verbose:
        print_reconstruction_report(dr)
    
    return dr


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════════════════

def print_reconstruction_report(dr: DocumentReconstruction):
    """Print the round-trip reconstruction report."""
    print(f"\n{'═' * 72}")
    print(f"ROUND-TRIP RECONSTRUCTION REPORT")
    print(f"{'═' * 72}")
    print(f"  📄 {os.path.basename(dr.filepath)}")
    print(f"  🌍 Language: {dr.language}")
    print(f"  📊 {dr.total_paragraphs} paragraphs")
    print(f"  ⏱️  Time: {dr.analysis_time_s}s")
    
    # Metrics dashboard
    print(f"\n  {'─' * 68}")
    print(f"  RECONSTRUCTION QUALITY METRICS")
    print(f"  {'─' * 68}")
    
    metrics = [
        ("Word Recall", dr.avg_word_recall, "% of original words recovered"),
        ("Word Precision", dr.avg_word_precision, "% of recon words that are correct"),
        ("Word F1", dr.reconstruction_f1, "harmonic mean of P and R"),
        ("Word Overlap (Jaccard)", dr.avg_word_overlap, "|∩| / |∪|"),
        ("Atom Preservation", dr.avg_atom_preservation, "% of atom-aligned words kept"),
    ]
    
    for name, value, desc in metrics:
        bar_len = int(value * 40)
        bar = '█' * bar_len + '░' * (40 - bar_len)
        grade = "✅" if value >= 0.7 else ("🟡" if value >= 0.4 else "🔴")
        print(f"  {grade} {name:25s} {value * 100:5.1f}% [{bar}]")
        print(f"       {desc}")
    
    # Show sample reconstructions
    print(f"\n  {'─' * 68}")
    print(f"  SAMPLE RECONSTRUCTIONS (first 3 paragraphs)")
    print(f"  {'─' * 68}")
    
    for pr in dr.paragraphs[:3]:
        if not pr.original.strip():
            continue
        print(f"\n  ¶{pr.index}:")
        # Truncate for display
        orig_disp = pr.original[:120] + ("..." if len(pr.original) > 120 else "")
        recon_disp = pr.reconstructed[:120] + ("..." if len(pr.reconstructed) > 120 else "")
        print(f"  ORIG:  {orig_disp}")
        print(f"  RECON: {recon_disp}")
        print(f"  → overlap={pr.word_overlap:.3f} recall={pr.word_recall:.3f} "
              f"precision={pr.word_precision:.3f} atoms={pr.atom_preservation:.3f} "
              f"order={pr.position_accuracy:.3f}")
    
    # Assessment
    print(f"\n  {'─' * 68}")
    print(f"  ASSESSMENT")
    print(f"  {'─' * 68}")
    
    f1 = dr.reconstruction_f1
    if f1 >= 0.7:
        print(f"  ✅ HIGH FIDELITY — {f1*100:.1f}% F1 — structure largely preserved")
        print(f"     The atom representation captures most of the original text.")
    elif f1 >= 0.5:
        print(f"  🟡 MODERATE FIDELITY — {f1*100:.1f}% F1 — core meaning preserved")
        print(f"     Content words recoverable, but function words and word order partially lost.")
    elif f1 >= 0.3:
        print(f"  🟡 PARTIAL FIDELITY — {f1*100:.1f}% F1 — key words preserved")
        print(f"     Main topics identifiable, but significant structural loss.")
    else:
        print(f"  🔴 LOW FIDELITY — {f1*100:.1f}% F1 — significant information loss")
        print(f"     Reconstruction very distant from original.")
    
    print(f"\n  E2 CONCLUSION:")
    recall = dr.avg_word_recall
    if recall >= 0.5:
        pct = recall * 100
        print(f"  The PaniniFS atom system recovers {pct:.0f}% of original word tokens.")
        print(f"  This is {pct:.0f}/100 on the E2 scale: decompose(text) → atoms → reconstruct(atoms) ≈ text")
    else:
        print(f"  Current atom vocabulary covers {recall*100:.0f}% of word tokens.")
        print(f"  More keyword coverage needed for faithful reconstruction.")
    
    print(f"  {'═' * 72}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Round-trip reconstruction experiment for PaniniFS",
    )
    parser.add_argument("file", help="Path to document")
    parser.add_argument("--lang", help="Force language")
    parser.add_argument("--mode", choices=["full", "atoms", "semantic"],
                        default="atoms", help="Reconstruction mode")
    parser.add_argument("--verbose", "-v", action="store_true", default=True)
    
    args = parser.parse_args()
    reconstruct_document(args.file, lang=args.lang, verbose=args.verbose,
                        mode=args.mode)


if __name__ == "__main__":
    main()

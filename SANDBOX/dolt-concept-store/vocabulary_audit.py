#!/usr/bin/env python3
"""vocabulary_audit.py — v4.7: Deep audit of uncovered vocabulary per language.

Runs fidelity analysis on the Gutenberg corpus with FORCED language codes
(extracted from filenames) to avoid misdetection. Produces a detailed report
of uncovered content words per language, suitable for vocabulary expansion.

Usage:
    python vocabulary_audit.py [--top N] [--output PATH]

Part of PaniniFS concept store — vocabulary expansion support.
"""

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reconstruction_fidelity import (
    analyze_document_fidelity,
    get_stop_words,
    get_content_words,
    DocumentFidelity,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CORPUS FILE → LANGUAGE MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

# Pattern: pg<id>_<lang>.txt
FILENAME_LANG_RE = re.compile(r"pg\d+_(\w+)\.txt$")

# Manual overrides for files whose names follow the pattern
LANG_MAP = {
    "pg11_en.txt": "en",
    "pg17482_eo.txt": "eo",
    "pg19778_de.txt": "de",
    "pg19942_en.txt": "en",
    "pg28371_it.txt": "it",
    "pg4650_fr.txt": "fr",
    "pg46569_fi.txt": "fi",
    "pg52336_fi.txt": "fi",
    "pg55456_fr.txt": "fr",
    "pg7109_es.txt": "es",
    "pg9000_sa.txt": "sa",
}


def detect_lang_from_filename(fname: str) -> str:
    """Extract language code from filename, fallback to regex."""
    if fname in LANG_MAP:
        return LANG_MAP[fname]
    m = FILENAME_LANG_RE.search(fname)
    if m:
        return m.group(1)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# DEEP AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

def audit_corpus(
    corpus_dir: str = "gutenberg_corpus",
    top_n: int = 100,
    output_path: str = None,
) -> dict:
    """Run deep vocabulary audit on the Gutenberg corpus.
    
    Returns per-language uncovered word inventories and recommendations
    for atom mapping.
    """
    t_start = time.time()
    
    txt_files = sorted(
        f for f in os.listdir(corpus_dir)
        if f.endswith('.txt') and not f.startswith('_')
    )
    
    print(f"\n{'═' * 72}")
    print(f"VOCABULARY AUDIT — v4.7")
    print(f"{'═' * 72}")
    print(f"  📂 Corpus: {corpus_dir}")
    print(f"  📚 {len(txt_files)} files")
    print()
    
    # Per-language aggregates
    per_lang = defaultdict(lambda: {
        "files": [],
        "total_words": 0,
        "total_content_words": 0,
        "total_atom_alignments": 0,
        "total_uncovered": 0,
        "uncovered_counter": Counter(),
        "readiness_sum": 0.0,
        "lex_cov_sum": 0.0,
        "n_docs": 0,
    })
    
    results = {}
    
    for i, fname in enumerate(txt_files):
        fpath = os.path.join(corpus_dir, fname)
        lang = detect_lang_from_filename(fname)
        
        print(f"  [{i+1}/{len(txt_files)}] {fname} (lang={lang})...", end=" ", flush=True)
        
        try:
            doc = analyze_document_fidelity(fpath, lang=lang, verbose=False)
            results[fname] = doc
            
            info = per_lang[lang]
            info["files"].append(fname)
            info["total_words"] += doc.total_words
            info["total_content_words"] += doc.total_content_words
            info["total_atom_alignments"] += doc.total_atom_alignments
            info["total_uncovered"] += doc.total_uncovered_content_words
            info["readiness_sum"] += doc.avg_reconstruction_readiness
            info["lex_cov_sum"] += doc.avg_lexical_coverage
            info["n_docs"] += 1
            
            for word, count in doc.top_uncovered_words:
                info["uncovered_counter"][word] += count
            
            # Also collect ALL uncovered words (not just top 30)
            for p in doc.paragraphs:
                for w in p.uncovered_content_words:
                    info["uncovered_counter"][w] += 1
            
            print(f"✅ readiness={doc.avg_reconstruction_readiness:.3f} "
                  f"lex_cov={doc.avg_lexical_coverage*100:.1f}% "
                  f"(detected={doc.language})")
            
        except Exception as e:
            print(f"❌ {e}")
    
    # ── Per-language reports ──
    print(f"\n{'═' * 72}")
    print(f"PER-LANGUAGE VOCABULARY GAPS")
    print(f"{'═' * 72}")
    
    audit_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "corpus_dir": corpus_dir,
        "total_files": len(txt_files),
        "languages": {},
    }
    
    for lang in sorted(per_lang.keys()):
        info = per_lang[lang]
        n = info["n_docs"]
        avg_rr = info["readiness_sum"] / n
        avg_lc = info["lex_cov_sum"] / n
        gap_pct = 100 - avg_lc * 100
        
        print(f"\n  {'─' * 68}")
        print(f"  🌍 {lang.upper()} — {n} doc(s), {info['total_words']:,} words")
        print(f"     Files: {', '.join(info['files'])}")
        print(f"     Avg readiness:     {avg_rr:.4f}")
        print(f"     Avg lex coverage:  {avg_lc*100:.1f}%  (gap: {gap_pct:.1f}%)")
        print(f"     Atom alignments:   {info['total_atom_alignments']:,} / "
              f"{info['total_content_words']:,} content words")
        print(f"     Unique uncovered:  {len(info['uncovered_counter']):,}")
        
        # Top uncovered words for this language
        top = info["uncovered_counter"].most_common(top_n)
        print(f"\n     Top {min(top_n, len(top))} uncovered content words:")
        
        for rank, (word, count) in enumerate(top[:50], 1):
            bar = '█' * min(count // 2, 30)
            print(f"       {rank:3d}. {word:20s} ×{count:5d} {bar}")
        
        if len(top) > 50:
            print(f"       ... ({len(top) - 50} more)")
        
        # Store for JSON
        audit_data["languages"][lang] = {
            "files": info["files"],
            "total_words": info["total_words"],
            "total_content_words": info["total_content_words"],
            "total_atom_alignments": info["total_atom_alignments"],
            "avg_readiness": round(avg_rr, 4),
            "avg_lexical_coverage": round(avg_lc, 4),
            "unique_uncovered_count": len(info["uncovered_counter"]),
            "top_uncovered_words": top,
        }
    
    # ── Global summary ──
    total_unique_uncov = sum(
        len(info["uncovered_counter"]) for info in per_lang.values()
    )
    total_words = sum(info["total_words"] for info in per_lang.values())
    total_content = sum(info["total_content_words"] for info in per_lang.values())
    total_atoms = sum(info["total_atom_alignments"] for info in per_lang.values())
    
    print(f"\n{'═' * 72}")
    print(f"GLOBAL SUMMARY")
    print(f"{'═' * 72}")
    print(f"  Total words:           {total_words:,}")
    print(f"  Total content words:   {total_content:,}")
    print(f"  Total atom alignments: {total_atoms:,}")
    print(f"  Global lex coverage:   {total_atoms / max(total_content, 1) * 100:.1f}%")
    print(f"  Unique uncov words:    {total_unique_uncov:,} across {len(per_lang)} languages")
    print(f"  Analysis time:         {time.time() - t_start:.1f}s")
    
    audit_data["global"] = {
        "total_words": total_words,
        "total_content_words": total_content,
        "total_atom_alignments": total_atoms,
        "global_lexical_coverage": round(total_atoms / max(total_content, 1), 4),
        "total_unique_uncovered": total_unique_uncov,
        "analysis_time_s": round(time.time() - t_start, 1),
    }
    
    # Save
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        print(f"\n  💾 Saved → {output_path}")
    
    print(f"{'═' * 72}\n")
    
    return audit_data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deep vocabulary audit for PaniniFS")
    parser.add_argument("--top", type=int, default=100, help="Top N uncovered per lang")
    parser.add_argument("--output", "-o", default="vocabulary_audit_results.json",
                        help="Output JSON path")
    parser.add_argument("--corpus", default="gutenberg_corpus", help="Corpus directory")
    args = parser.parse_args()
    
    audit_corpus(args.corpus, top_n=args.top, output_path=args.output)

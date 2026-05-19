#!/usr/bin/env python3
"""vocabulary_audit.py — v4.8.12: Deep audit of uncovered vocabulary per language.

Runs fidelity analysis on the Gutenberg corpus with FORCED language codes
(extracted from filenames) to avoid misdetection. Produces a detailed report
of uncovered content words per language, suitable for vocabulary expansion.

v4.8.12: Scans subdirectories (zh/, ja/, ru/, etc.) to include all corpus files.

Usage:
    python vocabulary_audit.py [--top N] [--output PATH]

Part of PaniniFS concept store — vocabulary expansion support.
"""

import json
import os
import pathlib
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


def detect_lang_from_filename(fname: str, subdir: str = None) -> str:
    """Extract language code from filename or subdirectory name."""
    # Check top-level LANG_MAP first (basename only)
    basename = os.path.basename(fname)
    if basename in LANG_MAP:
        return LANG_MAP[basename]
    # If file is in a language subdirectory (e.g., zh/pg23839.txt), use dir name
    if subdir:
        return subdir
    # Fallback to regex pattern pg<id>_<lang>.txt
    m = FILENAME_LANG_RE.search(basename)
    if m:
        return m.group(1)
    return None


# v4.8.12: Gutenberg metadata language detection (safety net)
_GUTENBERG_LANG_MAP = {
    "english": "en", "french": "fr", "german": "de", "spanish": "es",
    "italian": "it", "portuguese": "pt", "dutch": "nl", "russian": "ru",
    "japanese": "ja", "chinese": "zh", "finnish": "fi", "esperanto": "eo",
    "sanskrit": "sa", "latin": "la", "greek": "el", "swedish": "sv",
    "norwegian": "no", "danish": "da", "polish": "pl", "czech": "cs",
    "hungarian": "hu", "korean": "ko", "arabic": "ar", "hebrew": "he",
    "tagalog": "tl", "catalan": "ca", "romanian": "ro",
}

def detect_lang_from_gutenberg_metadata(filepath: str, hint_lang: str = None) -> str | None:
    """Read 'Language:' field from Gutenberg header (first 40 lines).
    
    If the file lists multiple languages (e.g. "English, Spanish") and
    hint_lang matches one of them, returns hint_lang to keep the file
    in its directory.  Otherwise returns the first listed language.
    
    Returns 2-letter code or None if not found.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for _ in range(40):
                line = f.readline()
                if not line:
                    break
                if line.strip().lower().startswith("language:"):
                    lang_str = line.strip().split(":", 1)[1].strip().lower()
                    parts = [p.strip() for p in lang_str.split(",")]
                    codes = [_GUTENBERG_LANG_MAP.get(p) for p in parts]
                    codes = [c for c in codes if c]  # filter None
                    if not codes:
                        return None
                    # If hint matches any listed language, keep it
                    if hint_lang and hint_lang in codes:
                        return hint_lang
                    return codes[0]
    except OSError:
        pass
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
    
    # ── Collect all .txt files: top-level AND subdirectories ──
    file_entries = []  # list of (relative_path, subdir_or_None)
    corpus_root = pathlib.Path(corpus_dir)
    for path in sorted(corpus_root.rglob("*.txt")):
        if path.name.startswith("_"):
            continue
        rel = path.relative_to(corpus_root)
        parts = rel.parts
        subdir = parts[0] if len(parts) > 1 else None
        file_entries.append((str(rel), subdir))
    
    print(f"\n{'═' * 72}")
    print(f"VOCABULARY AUDIT — v4.8.12")
    print(f"{'═' * 72}")
    print(f"  📂 Corpus: {corpus_dir}")
    print(f"  📚 {len(file_entries)} files (top-level + subdirectories)")
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
    
    for i, (rel_path, subdir) in enumerate(file_entries):
        fpath = os.path.join(corpus_dir, rel_path)
        fname = os.path.basename(rel_path)
        lang = detect_lang_from_filename(fname, subdir=subdir)
        
        # v4.8.12: Validate against Gutenberg metadata (safety net)
        meta_lang = detect_lang_from_gutenberg_metadata(fpath, hint_lang=lang)
        if meta_lang and lang and meta_lang != lang:
            print(f"\n  ⚠️  LANG MISMATCH: {rel_path} — dir={lang}, metadata={meta_lang}. Using metadata.")
            lang = meta_lang
        
        display_name = rel_path if subdir else fname
        print(f"  [{i+1}/{len(file_entries)}] {display_name} (lang={lang})...", end=" ", flush=True)
        
        try:
            doc = analyze_document_fidelity(fpath, lang=lang, verbose=False, strip_boilerplate=True)
            results[rel_path] = doc
            
            info = per_lang[lang]
            info["files"].append(display_name)
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
        "total_files": len(file_entries),
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
    total_uncov = sum(info["total_uncovered"] for info in per_lang.values())
    # Weighted lex coverage: (total_content - total_uncov) / total_content
    global_weighted_lex = (total_content - total_uncov) / max(total_content, 1)
    # Simple average (legacy)
    total_n_docs = sum(info["n_docs"] for info in per_lang.values())
    global_lex_sum = sum(info["lex_cov_sum"] for info in per_lang.values())
    global_avg_lex = global_lex_sum / max(total_n_docs, 1)
    
    print(f"\n{'═' * 72}")
    print(f"GLOBAL SUMMARY")
    print(f"{'═' * 72}")
    print(f"  Total words:           {total_words:,}")
    print(f"  Total content words:   {total_content:,}")
    print(f"  Total covered:         {total_content - total_uncov:,}")
    print(f"  Total uncovered:       {total_uncov:,}")
    print(f"  Total atom alignments: {total_atoms:,}")
    print(f"  Lex coverage (weighted): {global_weighted_lex * 100:.1f}%")
    print(f"  Lex coverage (avg/doc):  {global_avg_lex * 100:.1f}%")
    print(f"  Atom density:          {total_atoms / max(total_content, 1) * 100:.1f}% (atoms/content)")
    print(f"  Unique uncov words:    {total_unique_uncov:,} across {len(per_lang)} languages")
    print(f"  Analysis time:         {time.time() - t_start:.1f}s")
    
    audit_data["global"] = {
        "total_words": total_words,
        "total_content_words": total_content,
        "total_covered": total_content - total_uncov,
        "total_uncovered": total_uncov,
        "total_atom_alignments": total_atoms,
        "lexical_coverage_weighted": round(global_weighted_lex, 4),
        "lexical_coverage_avg_doc": round(global_avg_lex, 4),
        "atom_density": round(total_atoms / max(total_content, 1), 4),
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

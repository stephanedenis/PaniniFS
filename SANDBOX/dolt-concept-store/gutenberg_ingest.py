#!/usr/bin/env python3
"""gutenberg_ingest.py — Download and analyze Gutenberg texts in batch.

Downloads a curated list of Project Gutenberg books (multiple languages),
analyzes them through the PaniniFS 7-layer engine, and stores results in Dolt.

Usage:
    python gutenberg_ingest.py --download          # Download all texts
    python gutenberg_ingest.py --analyze            # Analyze all downloaded texts
    python gutenberg_ingest.py --all                # Download + analyze + compare
    python gutenberg_ingest.py --status             # Show progress

Part of PaniniFS concept store — Gutenberg corpus ingestion.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_analyzer import analyze_document
from semantic_serializer import (
    export_document_atoms, save_export, load_export,
    compare_documents, print_comparison_dashboard,
    prepare_e2_experiment, print_e2_report,
)

# ═══════════════════════════════════════════════════════════════════════════════
# GUTENBERG CATALOG — curated multilingual corpus
# ═══════════════════════════════════════════════════════════════════════════════

# Format: (gutenberg_id, language, title, author)
# Selected for: diversity of language, genre, era, and length
CATALOG = [
    # ── English ──
    (11,    "en", "Alice's Adventures in Wonderland", "Lewis Carroll"),
    (1342,  "en", "Pride and Prejudice", "Jane Austen"),
    (74,    "en", "The Adventures of Tom Sawyer", "Mark Twain"),
    (84,    "en", "Frankenstein", "Mary Shelley"),
    (174,   "en", "The Picture of Dorian Gray", "Oscar Wilde"),
    (35,    "en", "The Time Machine", "H.G. Wells"),
    (46,    "en", "A Christmas Carol", "Charles Dickens"),
    (1661,  "en", "The Adventures of Sherlock Holmes", "Arthur Conan Doyle"),
    (219,   "en", "Heart of Darkness", "Joseph Conrad"),
    (1232,  "en", "The Prince", "Niccolò Machiavelli"),
    (98,    "en", "A Tale of Two Cities", "Charles Dickens"),
    (345,   "en", "Dracula", "Bram Stoker"),
    (2701,  "en", "Moby Dick", "Herman Melville"),
    (1080,  "en", "A Modest Proposal", "Jonathan Swift"),
    (16328, "en", "Beowulf", "Anonymous"),

    # ── French ──
    (55456, "fr", "Aventures d'Alice au pays des merveilles", "Lewis Carroll (tr. Bué)"),
    (13846, "fr", "Le Petit Prince", "Antoine de Saint-Exupéry"),
    (17989, "fr", "Les Misérables — Tome 1: Fantine", "Victor Hugo"),
    (4650,  "fr", "Les Fleurs du Mal", "Charles Baudelaire"),
    (5185,  "fr", "Candide", "Voltaire"),
    (799,   "fr", "Les Trois Mousquetaires — Tome 1", "Alexandre Dumas"),
    (14287, "fr", "Le Tour du Monde en 80 Jours", "Jules Verne"),
    (19942, "fr", "Germinal", "Émile Zola"),
    (17396, "fr", "Cyrano de Bergerac", "Edmond Rostand"),
    (22966, "fr", "L'Étranger (domaine public)", "Placeholder"),  # may not exist

    # ── German ──
    (2229,  "de", "Die Verwandlung (The Metamorphosis)", "Franz Kafka"),
    (7205,  "de", "Also sprach Zarathustra", "Friedrich Nietzsche"),
    (2407,  "de", "Faust — Der Tragödie erster Teil", "J.W. von Goethe"),
    (6498,  "de", "Siddhartha", "Hermann Hesse"),
    (29220, "de", "Der Prozess (The Trial)", "Franz Kafka"),

    # ── Spanish ──
    (2000,  "es", "Don Quijote — Primera Parte", "Miguel de Cervantes"),
    (15532, "es", "La Regenta — Tomo 1", "Leopoldo Alas (Clarín)"),

    # ── Italian ──
    (1012,  "it", "La Divina Commedia — Inferno", "Dante Alighieri"),
    (3601,  "it", "I Promessi Sposi", "Alessandro Manzoni"),

    # ── Portuguese ──
    (17525, "pt", "Dom Casmurro", "Machado de Assis"),
    (29668, "pt", "Os Lusíadas", "Luís de Camões"),

    # ── Dutch ──
    (18066, "nl", "Max Havelaar", "Multatuli (Eduard Douwes Dekker)"),

    # ── v4.3: Exotic languages (CJK + Cyrillic) ──

    # ── Chinese (zh) — classical and modern ──
    (24264, "zh", "紅樓夢 (Dream of the Red Chamber)", "曹雪芹 (Cao Xueqin)"),
    (23962, "zh", "西遊記 (Journey to the West)", "吳承恩 (Wu Cheng'en)"),
    (23950, "zh", "三國志演義 (Romance of Three Kingdoms)", "羅貫中 (Luo Guanzhong)"),
    (23863, "zh", "水滸傳 (Water Margin)", "施耐庵 (Shi Nai'an)"),
    (7337,  "zh", "道德經 (Tao Te Ching)", "老子 (Laozi)"),
    (23864, "zh", "孫子兵法 (The Art of War)", "孫子 (Sunzi)"),
    (27166, "zh", "吶喊 (Call to Arms)", "魯迅 (Lu Xun)"),
    (23839, "zh", "論語 (Analects of Confucius)", "孔子 (Confucius)"),

    # ── Japanese (ja) ──
    (1982,  "ja", "羅生門 (Rashōmon)", "芥川龍之介 (Akutagawa Ryūnosuke)"),
    (20683, "ja", "奥の細道 (Narrow Road to the Deep North)", "松尾芭蕉 (Matsuo Bashō)"),
    (31617, "ja", "刺靑 (The Tattooer)", "谷崎潤一郎 (Tanizaki Jun'ichirō)"),
    (31757, "ja", "お目出たき人 (A Happy Man)", "武者小路実篤 (Mushanokōji Saneatsu)"),

    # ── Russian (ru) ──
    (16527, "ru", "1001 задача для умственного счёта (1001 Mental Arithmetic Problems)", "С.А. Рачинский (Rachinskii)"),
    (14741, "ru", "Духовные оды (Spiritual Odes)", "Г.Р. Державин (Derzhavin)"),
    (30774, "ru", "Московия в представлении иностранцев XVI-XVII в.", "П.Н. Апостол (Apostol)"),

    # ── v4.4: Indic languages (Sanskrit ITRANS) ──
    (9000,  "sa", "विष्णुसहस्रनाम (Vishnu Sahasranaamam — ITRANS)", "Anonymous (Vedic hymn)"),
]

CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gutenberg_corpus")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gutenberg_exports")


# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════

def get_gutenberg_url(gid: int) -> str:
    """Get the plain text URL for a Gutenberg ID."""
    return f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"


def download_text(gid: int, lang: str, title: str, author: str) -> Optional[str]:
    """Download a Gutenberg text. Returns the local path or None on failure."""
    outdir = os.path.join(CORPUS_DIR, lang)
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"pg{gid}.txt")

    if os.path.exists(outpath) and os.path.getsize(outpath) > 100:
        return outpath  # Already downloaded

    url = get_gutenberg_url(gid)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'PaniniFS-Research/1.0 (https://github.com/stephanedenis/Panini-FS)'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 100:
                return None
            with open(outpath, 'wb') as f:
                f.write(data)
        return outpath
    except Exception as e:
        print(f"  ⚠️  Failed to download {gid} ({title}): {e}")
        return None


def download_all(verbose=True) -> Dict[str, List[str]]:
    """Download all catalog texts. Returns {lang: [paths]}."""
    if verbose:
        print(f"\n{'═' * 72}")
        print(f"DOWNLOADING GUTENBERG CORPUS ({len(CATALOG)} texts)")
        print(f"{'═' * 72}")

    results = defaultdict(list)
    downloaded = 0
    skipped = 0
    failed = 0

    for i, (gid, lang, title, author) in enumerate(CATALOG):
        outpath = os.path.join(CORPUS_DIR, lang, f"pg{gid}.txt")
        already = os.path.exists(outpath) and os.path.getsize(outpath) > 100

        if verbose:
            status = "✓ cached" if already else "↓ downloading..."
            print(f"  [{i+1}/{len(CATALOG)}] {status:16s} {lang} | {title[:45]}")

        if already:
            results[lang].append(outpath)
            skipped += 1
            continue

        path = download_text(gid, lang, title, author)
        if path:
            results[lang].append(path)
            downloaded += 1
        else:
            failed += 1

    if verbose:
        print(f"\n  ✅ Downloaded: {downloaded}, Cached: {skipped}, Failed: {failed}")
        total_size = sum(
            os.path.getsize(p)
            for paths in results.values()
            for p in paths
        )
        print(f"  📦 Total corpus size: {total_size / 1024 / 1024:.1f} MB")

    return dict(results)


# ═══════════════════════════════════════════════════════════════════════════════
# COPY LOCAL TEXTS (use existing corpus if already downloaded)
# ═══════════════════════════════════════════════════════════════════════════════

def copy_local_texts():
    """Copy locally available Gutenberg texts into the corpus dir."""
    local_base = "/home/stephane/GitHub/Panini/data/gutenberg_corpus_large"
    if not os.path.isdir(local_base):
        return

    mapping = {
        "11": ("en", 11),
        "1342": ("en", 1342),
        "74": ("en", 74),
        "84": ("en", 84),
        "174": ("en", 174),
        "35": ("en", 35),
        "46": ("en", 46),
    }

    for dirname, (lang, gid) in mapping.items():
        src = os.path.join(local_base, dirname, f"{dirname}.txt")
        dst = os.path.join(CORPUS_DIR, lang, f"pg{gid}.txt")
        if os.path.exists(src) and not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            import shutil
            shutil.copy2(src, dst)

    # Alice FR from /tmp
    alice_fr_src = "/tmp/alice_fr.txt"
    alice_fr_dst = os.path.join(CORPUS_DIR, "fr", "pg55456.txt")
    if os.path.exists(alice_fr_src) and not os.path.exists(alice_fr_dst):
        os.makedirs(os.path.dirname(alice_fr_dst), exist_ok=True)
        import shutil
        shutil.copy2(alice_fr_src, alice_fr_dst)


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZE
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_all(store_in_dolt=True, verbose=True) -> List[str]:
    """Analyze all downloaded texts and export semantic JSON.
    
    Returns list of export JSON paths.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    # Find all downloaded texts
    texts = []
    for lang_dir in sorted(os.listdir(CORPUS_DIR)):
        lang_path = os.path.join(CORPUS_DIR, lang_dir)
        if not os.path.isdir(lang_path):
            continue
        for fname in sorted(os.listdir(lang_path)):
            if fname.endswith(".txt"):
                texts.append((os.path.join(lang_path, fname), lang_dir))

    if verbose:
        print(f"\n{'═' * 72}")
        print(f"ANALYZING GUTENBERG CORPUS ({len(texts)} texts)")
        print(f"{'═' * 72}")

    export_paths = []
    total_words = 0
    total_atoms = 0
    total_concepts = 0
    total_time = 0
    results_summary = []

    for i, (filepath, lang) in enumerate(texts):
        fname = os.path.basename(filepath)
        export_name = os.path.splitext(fname)[0] + ".semantic.json"
        export_path = os.path.join(EXPORTS_DIR, export_name)

        # Skip if already analyzed
        if os.path.exists(export_path):
            if verbose:
                print(f"  [{i+1}/{len(texts)}] ✓ cached  {lang} | {fname}")
            export_paths.append(export_path)
            try:
                existing = load_export(export_path)
                total_words += existing.total_words
                total_atoms += existing.unique_atoms
                total_concepts += existing.unique_concepts
                results_summary.append({
                    "file": fname, "lang": lang,
                    "words": existing.total_words,
                    "atoms": existing.unique_atoms,
                    "concepts": existing.unique_concepts,
                })
            except Exception:
                pass
            continue

        if verbose:
            sys.stdout.write(f"  [{i+1}/{len(texts)}] ⚙ analyzing  {lang} | {fname}...")
            sys.stdout.flush()

        t0 = time.time()
        try:
            export = export_document_atoms(filepath, lang=lang, verbose=False)
            save_export(export, export_path)
            export_paths.append(export_path)

            dt = time.time() - t0
            total_time += dt
            total_words += export.total_words
            total_atoms += export.unique_atoms
            total_concepts += export.unique_concepts

            results_summary.append({
                "file": fname, "lang": lang,
                "words": export.total_words,
                "atoms": export.unique_atoms,
                "concepts": export.unique_concepts,
                "time_s": round(dt, 1),
            })

            if verbose:
                sys.stdout.write(f"  {dt:.1f}s | {export.total_words:,} words | "
                      f"{export.unique_atoms} atoms | {export.unique_concepts} concepts\n")
                sys.stdout.flush()

            # Also store in Dolt
            if store_in_dolt:
                try:
                    analyze_document(filepath, lang=lang, store_in_dolt=True, verbose=False)
                except Exception as e:
                    print(f"  ⚠️  Dolt storage failed: {e}")

        except Exception as e:
            dt = time.time() - t0
            total_time += dt
            if verbose:
                print(f"  ❌ {e} ({dt:.1f}s)")
            results_summary.append({
                "file": fname, "lang": lang, "error": str(e),
            })

    if verbose:
        print(f"\n{'─' * 72}")
        print(f"  📊 SUMMARY")
        print(f"  {'─' * 68}")
        print(f"  Texts analyzed:    {len(export_paths)}")
        print(f"  Total words:       {total_words:,}")
        print(f"  Avg atoms/text:    {total_atoms / max(len(export_paths), 1):.1f}")
        print(f"  Avg concepts/text: {total_concepts / max(len(export_paths), 1):.1f}")
        print(f"  Total time:        {total_time:.1f}s ({total_time/60:.1f} min)")
        if total_time > 0:
            print(f"  Throughput:        {total_words / total_time:.0f} words/s")
        print(f"{'═' * 72}")

    # Save summary
    summary_path = os.path.join(EXPORTS_DIR, "_analysis_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "analyzed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "texts": len(export_paths),
            "total_words": total_words,
            "total_time_s": round(total_time, 1),
            "results": results_summary,
        }, f, indent=2, ensure_ascii=False)

    return export_paths


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-LANGUAGE MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

def build_universality_matrix(export_paths: List[str], verbose=True) -> dict:
    """Build a cross-language universality matrix from all exports.
    
    Compares documents within and across languages.
    """
    exports = []
    for p in export_paths:
        try:
            exports.append(load_export(p))
        except Exception:
            continue

    if len(exports) < 2:
        print("Need at least 2 exports for comparison")
        return {}

    # Group by language
    by_lang = defaultdict(list)
    for e in exports:
        by_lang[e.language].append(e)

    if verbose:
        print(f"\n{'═' * 72}")
        print(f"CROSS-LANGUAGE UNIVERSALITY MATRIX")
        print(f"{'═' * 72}")
        print(f"  Languages: {', '.join(sorted(by_lang.keys()))}")
        for lang, docs in sorted(by_lang.items()):
            print(f"    {lang}: {len(docs)} documents, "
                  f"{sum(d.total_words for d in docs):,} words")

    # ── Aggregate atom profiles by language ──
    lang_profiles = {}
    for lang, docs in by_lang.items():
        merged = Counter()
        total = 0
        for doc in docs:
            for atom, count in doc.atom_distribution.items():
                merged[atom] += count
                total += count
        lang_profiles[lang] = {
            atom: count / max(total, 1)
            for atom, count in merged.items()
        }

    # ── Pairwise language comparison ──
    from semantic_serializer import _cosine_similarity, _spearman_rank
    languages = sorted(by_lang.keys())
    matrix = {}

    if verbose:
        print(f"\n  ── Pairwise cosine similarity (atom profiles) ──")
        header = "         " + "  ".join(f"{l:>7s}" for l in languages)
        print(f"  {header}")

    for la in languages:
        row = {}
        for lb in languages:
            sim = _cosine_similarity(lang_profiles[la], lang_profiles[lb])
            row[lb] = sim
        matrix[la] = row

        if verbose:
            values = "  ".join(f"{row[lb]:7.4f}" for lb in languages)
            print(f"    {la:>5s}  {values}")

    # ── Universal atoms across ALL languages ──
    all_atom_sets = [set(p.keys()) for p in lang_profiles.values()]
    universal = set.intersection(*all_atom_sets) if all_atom_sets else set()
    union = set.union(*all_atom_sets) if all_atom_sets else set()

    if verbose:
        print(f"\n  ── Universal atoms (present in ALL {len(languages)} languages) ──")
        print(f"    {len(universal)} / {len(union)} ({len(universal)/max(len(union),1):.1%})")
        print(f"    {sorted(universal)}")

        # Per-atom cross-language stability
        print(f"\n  ── Atom stability across languages (CV) ──")
        stabilities = []
        for atom in sorted(universal):
            proportions = [lang_profiles[l].get(atom, 0) for l in languages]
            mean_p = sum(proportions) / len(proportions)
            var = sum((p - mean_p)**2 for p in proportions) / len(proportions)
            cv = (var**0.5) / max(mean_p, 1e-10)
            stabilities.append((atom, cv, mean_p))

        stabilities.sort(key=lambda x: x[1])
        for atom, cv, mean_p in stabilities:
            bar = "█" * int(mean_p * 200)
            print(f"    {atom:>20s}  CV={cv:.3f}  mean={mean_p:.3%}  {bar}")

    result = {
        "languages": languages,
        "matrix": matrix,
        "universal_atoms": sorted(universal),
        "universal_count": len(universal),
        "total_atoms": len(union),
        "universality_rate": round(len(universal) / max(len(union), 1), 4),
        "lang_profiles": {
            lang: {k: round(v, 4) for k, v in sorted(profile.items(), key=lambda x: -x[1])}
            for lang, profile in lang_profiles.items()
        },
    }

    # Save matrix
    matrix_path = os.path.join(EXPORTS_DIR, "_universality_matrix.json")
    with open(matrix_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n  💾 Matrix saved to {matrix_path}")
        print(f"{'═' * 72}")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════════════════════

def show_status():
    """Show current progress of Gutenberg ingestion."""
    print(f"\n{'═' * 72}")
    print(f"GUTENBERG INGESTION STATUS")
    print(f"{'═' * 72}")

    # Check downloads
    downloaded = 0
    missing = 0
    for gid, lang, title, author in CATALOG:
        path = os.path.join(CORPUS_DIR, lang, f"pg{gid}.txt")
        if os.path.exists(path) and os.path.getsize(path) > 100:
            downloaded += 1
        else:
            missing += 1
            print(f"  ❌ Missing: pg{gid} ({lang}) — {title}")

    print(f"\n  Downloaded: {downloaded}/{len(CATALOG)}")

    # Check exports
    exported = 0
    if os.path.isdir(EXPORTS_DIR):
        exported = len([f for f in os.listdir(EXPORTS_DIR) if f.endswith(".semantic.json")])
    print(f"  Analyzed:   {exported}/{downloaded}")

    # Summary if available
    summary_path = os.path.join(EXPORTS_DIR, "_analysis_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)
        print(f"  Last run:   {summary.get('analyzed_at', '?')}")
        print(f"  Total words: {summary.get('total_words', 0):,}")
        print(f"  Time:       {summary.get('total_time_s', 0):.1f}s")

    print(f"{'═' * 72}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Gutenberg corpus ingestion for PaniniFS"
    )
    parser.add_argument("--download", action="store_true", help="Download all texts")
    parser.add_argument("--analyze", action="store_true", help="Analyze all texts")
    parser.add_argument("--compare", action="store_true", help="Build universality matrix")
    parser.add_argument("--all", action="store_true", help="Download + analyze + compare")
    parser.add_argument("--status", action="store_true", help="Show progress")
    parser.add_argument("--e2", action="store_true", help="Run E2 preparation")
    parser.add_argument("--no-dolt", action="store_true", help="Skip Dolt storage")
    parser.add_argument("--verbose", "-v", action="store_true", default=True)
    parser.add_argument("--quiet", "-q", action="store_true")

    args = parser.parse_args()
    verbose = not args.quiet

    if args.status:
        show_status()
        return

    if args.all or args.download:
        copy_local_texts()
        download_all(verbose=verbose)

    if args.all or args.analyze:
        export_paths = analyze_all(
            store_in_dolt=not args.no_dolt,
            verbose=verbose,
        )

    if args.all or args.compare:
        # Find all exports
        if not os.path.isdir(EXPORTS_DIR):
            print("No exports found. Run --analyze first.")
            return
        export_paths = [
            os.path.join(EXPORTS_DIR, f)
            for f in sorted(os.listdir(EXPORTS_DIR))
            if f.endswith(".semantic.json")
        ]
        build_universality_matrix(export_paths, verbose=verbose)

    if args.e2:
        if not os.path.isdir(EXPORTS_DIR):
            print("No exports found. Run --analyze first.")
            return
        export_paths = [
            os.path.join(EXPORTS_DIR, f)
            for f in sorted(os.listdir(EXPORTS_DIR))
            if f.endswith(".semantic.json")
        ]
        exports = [load_export(p) for p in export_paths]
        e2_data = prepare_e2_experiment(
            exports,
            output_path=os.path.join(EXPORTS_DIR, "_e2_preparation.json"),
        )
        print_e2_report(e2_data)

    if not any([args.download, args.analyze, args.compare, args.all,
                args.status, args.e2]):
        parser.print_help()


if __name__ == "__main__":
    main()

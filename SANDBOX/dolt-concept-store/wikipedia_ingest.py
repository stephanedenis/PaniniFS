#!/usr/bin/env python3
"""wikipedia_ingest.py — Wikipedia corpus ingestion for PaniniFS (14 languages).

Downloads curated + random Wikipedia articles across all 14 supported languages,
analyzes them through the PaniniFS 7-layer semantic engine, and builds a
cross-language universality matrix.

Strategy:
  1. 30 curated parallel articles (same topic in all languages via Wikidata)
  2. Optional random articles for breadth (--random N per language)
  3. Full PaniniFS analysis pipeline (document_analyzer → semantic_serializer)
  4. Cross-language universality matrix

Usage:
    python3 wikipedia_ingest.py --all                # Full pipeline (curated only)
    python3 wikipedia_ingest.py --all --random 50    # + 50 random articles/lang
    python3 wikipedia_ingest.py --download           # Download only
    python3 wikipedia_ingest.py --analyze            # Analyze downloaded
    python3 wikipedia_ingest.py --compare            # Build matrix
    python3 wikipedia_ingest.py --status             # Show progress

Part of PaniniFS v4.4 — Wikipedia corpus ingestion.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter, defaultdict
from html import unescape
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_analyzer import analyze_document
from semantic_serializer import (
    export_document_atoms, save_export, load_export,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SUPPORTED_LANGS = [
    "de", "en", "eo", "es", "fi", "fr", "hi", "it",
    "ja", "nl", "pt", "ru", "sa", "zh",
]

USER_AGENT = (
    "PaniniFS-Research/1.0 "
    "(https://github.com/stephanedenis/Panini-FS; semantic-universality-research)"
)

CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wikipedia_corpus")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wikipedia_exports")

# Rate limiting — be respectful to Wikimedia
API_DELAY = 0.5   # seconds between requests
API_RETRIES = 3   # max retries on failure
API_TIMEOUT = 30  # seconds

# Minimum article length (words) to keep
MIN_ARTICLE_WORDS = 200


# ═══════════════════════════════════════════════════════════════════════════════
# CURATED TOPICS — 30 Wikidata items covering all 34 semantic atoms
# ═══════════════════════════════════════════════════════════════════════════════

# Format: (topic_key, wikidata_qid, en_fallback_title, target_atoms)
CURATED_TOPICS = [
    # ── PROC atoms (actions, events) ──
    ("sun",          "Q525",    "Sun",              "EXISTENCE, MATIÈRE, GRAND"),
    ("war",          "Q198",    "War",              "DESTRUCTION, DOMINATION, RAGE"),
    ("love",         "Q316",    "Love",             "CARE, SEEKING, RELATION"),
    ("death",        "Q4",      "Death",            "EXISTENCE, GRIEF, FEAR"),
    ("music",        "Q638",    "Music",            "CREATION, PLAY, PERCEPTION"),
    ("dance",        "Q11639",  "Dance",            "MOUVEMENT, PLAY, CORPS"),
    ("agriculture",  "Q11451",  "Agriculture",      "CREATION, POSSESSION, MATIÈRE"),
    ("cooking",      "Q13442",  "Cooking",          "CREATION, MATIÈRE, CHOSE"),
    ("migration",    "Q180684", "Human migration",  "MOUVEMENT, LIEU, AGENT"),

    # ── EMOT atoms (emotions) ──
    ("fear_emotion",  "Q544",    "Fear",            "FEAR, COGNITION"),
    ("anger",         "Q170494", "Anger",           "RAGE, INTENSE"),
    ("happiness",     "Q8",      "Happiness",       "BON, PLAY, CARE"),
    ("disgust",       "Q160232", "Disgust",         "DISGUST"),
    ("boredom",       "Q131123", "Boredom",         "TEDIUM"),
    ("grief_emotion", "Q169251", "Grief",           "GRIEF, CARE"),

    # ── ENT atoms (entities) ──
    ("human",    "Q5",      "Human",        "AGENT, CORPS, EXISTENCE"),
    ("earth",    "Q2",      "Earth",        "LIEU, MATIÈRE, EXISTENCE"),
    ("food",     "Q2095",   "Food",         "CHOSE, MATIÈRE, POSSESSION"),
    ("mountain", "Q8502",   "Mountain",     "LIEU, GRAND, MATIÈRE"),
    ("fire",     "Q3196",   "Fire",         "MATIÈRE, DESTRUCTION, INTENSE"),
    ("ocean",    "Q9430",   "Ocean",        "LIEU, MATIÈRE, GRAND, MOUVEMENT"),

    # ── ABS atoms (abstract structures) ──
    ("time",         "Q11471",  "Time",          "MESURE, RÉCURRENCE, ANCIEN"),
    ("mathematics",  "Q395",    "Mathematics",   "MESURE, STRUCTURE, ORDRE"),
    ("philosophy",   "Q5891",   "Philosophy",    "COGNITION, VRAI, STRUCTURE"),
    ("language_art", "Q315",    "Language",      "COMMUNICATION, COGNITION"),
    ("symmetry",     "Q165474", "Symmetry",      "INVARIANCE, STRUCTURE, DUALITÉ"),

    # ── QUAL atoms (qualities) ──
    ("color",   "Q1075",   "Color",    "PERCEPTION, BON"),
    ("beauty",  "Q7242",   "Beauty",   "BON, PERCEPTION, VRAI"),

    # ── Literary/cultural (broad atom coverage) ──
    ("mahabharata", "Q8276",  "Mahabharata",  "ALL — epic narrative, hi/sa"),
    ("odyssey",     "Q35160",  "Odyssey",      "MOUVEMENT, SEEKING, DESTRUCTION"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

_last_request_time = 0.0


def api_get(url: str, retries: int = API_RETRIES) -> Optional[dict]:
    """HTTP GET with rate limiting, retries, and JSON parsing."""
    global _last_request_time

    for attempt in range(retries):
        # Rate limiting
        elapsed = time.time() - _last_request_time
        if elapsed < API_DELAY:
            time.sleep(API_DELAY - elapsed)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
                _last_request_time = time.time()
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait = int(e.headers.get("Retry-After", 5))
                print(f"    ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                print(f"    ⚠️  HTTP {e.code} (attempt {attempt+1}/{retries})")
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"    ⚠️  {type(e).__name__}: {e} (attempt {attempt+1}/{retries})")
            time.sleep(2 ** attempt)

    return None


def html_to_plaintext(html: str) -> str:
    """Convert Wikipedia HTML to clean plaintext."""
    # Remove infoboxes, navboxes, sidebars, metadata tables
    html = re.sub(
        r'<table[^>]*class="[^"]*(?:infobox|navbox|sidebar|metadata|wikitable|'
        r'ambox|mbox|tmbox|ombox|cmbox|fmbox|imbox)[^"]*"[^>]*>.*?</table>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove reference superscripts and ref lists
    html = re.sub(r'<sup[^>]*class="[^"]*reference[^"]*"[^>]*>.*?</sup>', '',
                  html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="[^"]*reflist[^"]*"[^>]*>.*?</div>', '',
                  html, flags=re.DOTALL)
    html = re.sub(r'<ol[^>]*class="[^"]*references[^"]*"[^>]*>.*?</ol>', '',
                  html, flags=re.DOTALL)
    # Remove edit sections
    html = re.sub(r'<span[^>]*class="[^"]*mw-editsection[^"]*"[^>]*>.*?</span>',
                  '', html, flags=re.DOTALL)
    # Remove scripts, styles, comments
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # Remove navigation divs (toc, catlinks, etc.)
    html = re.sub(r'<div[^>]*(?:id|class)="[^"]*(?:toc|catlinks|printfooter|'
                  r'mw-jump-link|bandeau|hatnote)[^"]*"[^>]*>.*?</div>',
                  '', html, flags=re.DOTALL)

    # Convert headings to text with newlines
    html = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\n\1\n\n',
                  html, flags=re.DOTALL)
    # Convert paragraphs and line breaks
    html = re.sub(r'</p>', '\n\n', html)
    html = re.sub(r'<p[^>]*>', '', html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</li>', '\n', html)
    html = re.sub(r'<li[^>]*>', '• ', html)

    # Remove all remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)

    # Unescape HTML entities
    text = unescape(html)

    # Remove reference brackets [1], [2], [note 1], [citation needed]
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[(?:citation needed|note \d+|quoting|verification needed)\]',
                  '', text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def slugify(title: str) -> str:
    """Convert an article title to a safe filename slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '_', slug)
    slug = slug.strip('_')
    return slug[:80] or "untitled"


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE RESOLUTION — Wikidata QID → article titles in all languages
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_curated_titles() -> Dict[str, Dict[str, str]]:
    """Resolve all curated topics to article titles via Wikidata.

    Returns: {topic_key: {lang: article_title}}
    """
    print(f"\n{'═' * 72}")
    print(f"RESOLVING WIKIDATA → ARTICLE TITLES ({len(CURATED_TOPICS)} topics)")
    print(f"{'═' * 72}")

    # Collect all QIDs
    qid_to_topic = {qid: (key, en_title) for key, qid, en_title, _ in CURATED_TOPICS}
    all_qids = list(qid_to_topic.keys())

    # Batch API call (max 50 per request)
    result = {}
    for batch_start in range(0, len(all_qids), 50):
        batch = all_qids[batch_start:batch_start + 50]
        ids_param = "|".join(batch)
        url = (
            f"https://www.wikidata.org/w/api.php?"
            f"action=wbgetentities&ids={ids_param}"
            f"&props=sitelinks&format=json"
        )
        data = api_get(url)
        if not data or "entities" not in data:
            print(f"  ⚠️  Wikidata API failed for batch starting at {batch_start}")
            continue

        for qid, entity in data["entities"].items():
            if qid not in qid_to_topic:
                continue
            topic_key, en_fallback = qid_to_topic[qid]
            sitelinks = entity.get("sitelinks", {})

            titles = {}
            for lang in SUPPORTED_LANGS:
                wiki_key = f"{lang}wiki"
                if wiki_key in sitelinks:
                    titles[lang] = sitelinks[wiki_key]["title"]

            # Ensure English fallback
            if "en" not in titles:
                titles["en"] = en_fallback

            result[topic_key] = titles

    # Report coverage
    total_articles = sum(len(t) for t in result.values())
    max_possible = len(CURATED_TOPICS) * len(SUPPORTED_LANGS)
    print(f"\n  Resolved: {total_articles}/{max_possible} articles "
          f"({total_articles/max_possible:.0%})")

    for lang in SUPPORTED_LANGS:
        count = sum(1 for t in result.values() if lang in t)
        bar = "█" * count + "░" * (len(CURATED_TOPICS) - count)
        print(f"    {lang}: {count:>2}/{len(CURATED_TOPICS)} {bar}")

    # Cache the resolution
    os.makedirs(CORPUS_DIR, exist_ok=True)
    cache_path = os.path.join(CORPUS_DIR, "_title_resolution.json")
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n  💾 Cached → {cache_path}")

    return result


def load_cached_titles() -> Optional[Dict[str, Dict[str, str]]]:
    """Load cached title resolution if available."""
    cache_path = os.path.join(CORPUS_DIR, "_title_resolution.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════

def download_article(lang: str, title: str) -> Optional[str]:
    """Download full article text from Wikipedia.

    Uses action=parse for complete HTML, then converts to plaintext.
    Returns the plaintext or None on failure.
    """
    encoded_title = urllib.parse.quote(title.replace(" ", "_"), safe="/:@")
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?"
        f"action=parse&page={encoded_title}&prop=text"
        f"&format=json&disableeditsection=1&disabletoc=1"
        f"&maxlag=5&redirects=1"
    )

    data = api_get(url)
    if not data:
        return None

    if "error" in data:
        return None

    try:
        html = data["parse"]["text"]["*"]
    except (KeyError, TypeError):
        return None

    text = html_to_plaintext(html)

    # Check minimum length
    word_count = len(text.split())
    if word_count < MIN_ARTICLE_WORDS:
        return None

    return text


def save_article(lang: str, category: str, slug: str, text: str) -> str:
    """Save article text to disk. Returns the filepath."""
    outdir = os.path.join(CORPUS_DIR, lang, category)
    os.makedirs(outdir, exist_ok=True)
    filepath = os.path.join(outdir, f"{slug}.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    return filepath


def download_curated(title_map: Dict[str, Dict[str, str]], verbose=True) -> int:
    """Download all curated articles. Returns count of downloaded articles."""
    if verbose:
        print(f"\n{'═' * 72}")
        print(f"DOWNLOADING CURATED WIKIPEDIA ARTICLES")
        print(f"{'═' * 72}")

    total = sum(len(titles) for titles in title_map.values())
    downloaded = 0
    cached = 0
    failed = 0
    idx = 0

    for topic_key, lang_titles in title_map.items():
        for lang, title in sorted(lang_titles.items()):
            idx += 1
            slug = slugify(topic_key)
            filepath = os.path.join(CORPUS_DIR, lang, "curated", f"{slug}.txt")

            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                cached += 1
                if verbose:
                    print(f"  [{idx:>4}/{total}] ✓ cached    {lang} | {title[:50]}")
                continue

            if verbose:
                sys.stdout.write(
                    f"  [{idx:>4}/{total}] ↓ download  {lang} | {title[:50]}..."
                )
                sys.stdout.flush()

            text = download_article(lang, title)
            if text:
                save_article(lang, "curated", slug, text)
                words = len(text.split())
                downloaded += 1
                if verbose:
                    print(f"  {words:,} words")
            else:
                failed += 1
                if verbose:
                    print(f"  ❌ failed")

    if verbose:
        print(f"\n  ✅ Downloaded: {downloaded}, Cached: {cached}, "
              f"Failed: {failed}, Total: {total}")

    return downloaded + cached


def download_random_articles(n_per_lang: int, verbose=True) -> int:
    """Download N random articles per language. Returns count downloaded."""
    if verbose:
        print(f"\n{'═' * 72}")
        print(f"DOWNLOADING RANDOM ARTICLES ({n_per_lang}/language × "
              f"{len(SUPPORTED_LANGS)} languages)")
        print(f"{'═' * 72}")

    total_downloaded = 0

    for lang in SUPPORTED_LANGS:
        if verbose:
            print(f"\n  ── {lang.upper()} ──")

        # Get random article titles
        url = (
            f"https://{lang}.wikipedia.org/w/api.php?"
            f"action=query&list=random&rnnamespace=0"
            f"&rnlimit={min(n_per_lang * 2, 500)}"  # request extra to filter stubs
            f"&format=json&maxlag=5"
        )
        data = api_get(url)
        if not data or "query" not in data:
            print(f"    ⚠️  Failed to get random titles for {lang}")
            continue

        random_pages = data["query"]["random"]
        lang_downloaded = 0

        for page in random_pages:
            if lang_downloaded >= n_per_lang:
                break

            title = page["title"]
            slug = slugify(title)
            filepath = os.path.join(CORPUS_DIR, lang, "random", f"{slug}.txt")

            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                lang_downloaded += 1
                continue

            text = download_article(lang, title)
            if text:
                save_article(lang, "random", slug, text)
                lang_downloaded += 1
                words = len(text.split())
                if verbose and lang_downloaded % 10 == 0:
                    print(f"    {lang_downloaded}/{n_per_lang} downloaded...")
            # else: article too short, skip it silently

        total_downloaded += lang_downloaded
        if verbose:
            print(f"    ✅ {lang}: {lang_downloaded}/{n_per_lang} articles")

    if verbose:
        print(f"\n  ✅ Total random articles: {total_downloaded}")

    return total_downloaded


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS — process all downloaded articles through PaniniFS
# ═══════════════════════════════════════════════════════════════════════════════

def find_all_articles() -> List[Tuple[str, str, str]]:
    """Find all downloaded Wikipedia articles.

    Returns: [(filepath, lang, category)]
    """
    articles = []
    if not os.path.isdir(CORPUS_DIR):
        return articles

    for lang in sorted(os.listdir(CORPUS_DIR)):
        lang_dir = os.path.join(CORPUS_DIR, lang)
        if not os.path.isdir(lang_dir) or lang.startswith("_"):
            continue
        for category in ["curated", "random"]:
            cat_dir = os.path.join(lang_dir, category)
            if not os.path.isdir(cat_dir):
                continue
            for fname in sorted(os.listdir(cat_dir)):
                if fname.endswith(".txt") and not fname.startswith("_"):
                    filepath = os.path.join(cat_dir, fname)
                    if os.path.getsize(filepath) > 100:
                        articles.append((filepath, lang, category))

    return articles


def analyze_all(verbose=True) -> List[str]:
    """Analyze all downloaded Wikipedia articles.

    Returns list of export JSON paths.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    articles = find_all_articles()

    if not articles:
        print("  No articles found. Run --download first.")
        return []

    if verbose:
        print(f"\n{'═' * 72}")
        print(f"ANALYZING WIKIPEDIA CORPUS ({len(articles)} articles)")
        print(f"{'═' * 72}")

    export_paths = []
    total_words = 0
    total_atoms = 0
    total_concepts = 0
    total_time = 0
    errors = 0
    cached = 0

    for i, (filepath, lang, category) in enumerate(articles):
        fname = os.path.basename(filepath)
        export_name = f"wiki_{lang}_{category}_{os.path.splitext(fname)[0]}.semantic.json"
        export_path = os.path.join(EXPORTS_DIR, export_name)

        # Skip if already analyzed
        if os.path.exists(export_path):
            cached += 1
            export_paths.append(export_path)
            try:
                existing = load_export(export_path)
                total_words += existing.total_words
                total_atoms += existing.unique_atoms
                total_concepts += existing.unique_concepts
            except Exception:
                pass
            if verbose and (cached % 50 == 0 or i == len(articles) - 1):
                print(f"  [{i+1:>4}/{len(articles)}] ✓ {cached} cached...")
            continue

        if verbose:
            sys.stdout.write(
                f"  [{i+1:>4}/{len(articles)}] ⚙ {lang}/{category}/{fname[:30]}..."
            )
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

            if verbose:
                wps = export.total_words / max(dt, 0.01)
                eta = (len(articles) - i - 1) * (total_time / max(i - cached + 1, 1))
                print(f"  {dt:.1f}s | {export.total_words:,}w | "
                      f"{export.unique_atoms}a | ETA {eta/60:.0f}min")

        except Exception as e:
            dt = time.time() - t0
            total_time += dt
            errors += 1
            if verbose:
                print(f"  ❌ {e}")

    if verbose:
        analyzed = len(export_paths) - cached
        print(f"\n{'─' * 72}")
        print(f"  📊 ANALYSIS SUMMARY")
        print(f"  {'─' * 68}")
        print(f"  Articles:      {len(export_paths)} ({cached} cached, "
              f"{analyzed} new, {errors} errors)")
        print(f"  Total words:   {total_words:,}")
        if analyzed > 0:
            print(f"  Avg atoms:     {total_atoms / max(len(export_paths), 1):.1f}/text")
            print(f"  Analysis time: {total_time:.1f}s ({total_time/60:.1f} min)")
            if total_time > 0:
                print(f"  Throughput:    {total_words / total_time:.0f} words/s")
        print(f"{'═' * 72}")

    # Save summary
    summary_path = os.path.join(EXPORTS_DIR, "_wiki_analysis_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "analyzed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "articles": len(export_paths),
            "total_words": total_words,
            "total_time_s": round(total_time, 1),
            "errors": errors,
        }, f, indent=2, ensure_ascii=False)

    return export_paths


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-LANGUAGE UNIVERSALITY MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

def build_universality_matrix(export_paths: List[str], verbose=True) -> dict:
    """Build cross-language universality matrix from all Wikipedia exports."""
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
        print(f"WIKIPEDIA CROSS-LANGUAGE UNIVERSALITY MATRIX")
        print(f"{'═' * 72}")
        print(f"  Languages: {len(by_lang)} — {', '.join(sorted(by_lang.keys()))}")
        for lang, docs in sorted(by_lang.items()):
            total_w = sum(d.total_words for d in docs)
            print(f"    {lang}: {len(docs):>3} articles, {total_w:>10,} words")

    # Aggregate atom profiles by language
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

    # Pairwise cosine similarity
    from semantic_serializer import _cosine_similarity
    languages = sorted(by_lang.keys())
    matrix = {}

    if verbose:
        print(f"\n  ── Pairwise cosine similarity ──")
        header = "         " + "  ".join(f"{l:>5s}" for l in languages)
        print(f"  {header}")

    for la in languages:
        row = {}
        for lb in languages:
            sim = _cosine_similarity(lang_profiles[la], lang_profiles[lb])
            row[lb] = round(sim, 4)
        matrix[la] = row

        if verbose:
            values = "  ".join(f"{row[lb]:5.3f}" for lb in languages)
            print(f"    {la:>5s}  {values}")

    # Universal atoms
    all_atom_sets = [set(p.keys()) for p in lang_profiles.values()]
    universal = set.intersection(*all_atom_sets) if all_atom_sets else set()
    union = set.union(*all_atom_sets) if all_atom_sets else set()

    if verbose:
        print(f"\n  ── Universal atoms ({len(languages)} languages) ──")
        print(f"    {len(universal)} / {len(union)} "
              f"({len(universal)/max(len(union),1):.1%})")
        print(f"    {sorted(universal)}")

        # Per-atom stability (CV)
        print(f"\n  ── Atom stability (coefficient of variation) ──")
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

    # Average cross-language similarity
    sims = []
    for la in languages:
        for lb in languages:
            if la < lb:
                sims.append(matrix[la][lb])
    avg_sim = sum(sims) / len(sims) if sims else 0

    if verbose:
        print(f"\n  ── Summary ──")
        print(f"    Avg cross-language cosine: {avg_sim:.4f}")
        print(f"    Min: {min(sims):.4f}  Max: {max(sims):.4f}")

    result = {
        "source": "wikipedia",
        "languages": languages,
        "language_article_counts": {l: len(by_lang[l]) for l in languages},
        "language_word_counts": {
            l: sum(d.total_words for d in by_lang[l]) for l in languages
        },
        "matrix": matrix,
        "universal_atoms": sorted(universal),
        "universal_count": len(universal),
        "total_atoms": len(union),
        "universality_rate": round(len(universal) / max(len(union), 1), 4),
        "avg_cosine_similarity": round(avg_sim, 4),
        "lang_profiles": {
            lang: {k: round(v, 4) for k, v in
                   sorted(profile.items(), key=lambda x: -x[1])}
            for lang, profile in lang_profiles.items()
        },
    }

    # Save matrix
    matrix_path = os.path.join(EXPORTS_DIR, "_wiki_universality_matrix.json")
    with open(matrix_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n  💾 Matrix saved → {matrix_path}")
        print(f"{'═' * 72}")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════════════════════

def show_status():
    """Show current progress of Wikipedia ingestion."""
    print(f"\n{'═' * 72}")
    print(f"WIKIPEDIA INGESTION STATUS")
    print(f"{'═' * 72}")

    articles = find_all_articles()
    by_lang = defaultdict(lambda: {"curated": 0, "random": 0, "words": 0})
    total_size = 0

    for filepath, lang, category in articles:
        by_lang[lang][category] += 1
        size = os.path.getsize(filepath)
        by_lang[lang]["words"] += size // 6  # rough estimate
        total_size += size

    print(f"\n  Downloaded articles: {len(articles)}")
    print(f"  Total corpus size:  {total_size / 1024 / 1024:.1f} MB")
    print(f"\n  {'Lang':<6} {'Curated':>8} {'Random':>8} {'Total':>8} {'~Words':>10}")
    print(f"  {'─'*46}")

    for lang in SUPPORTED_LANGS:
        info = by_lang.get(lang, {"curated": 0, "random": 0, "words": 0})
        total = info["curated"] + info["random"]
        if total > 0:
            print(f"  {lang:<6} {info['curated']:>8} {info['random']:>8} "
                  f"{total:>8} {info['words']:>10,}")
        else:
            print(f"  {lang:<6} {'—':>8} {'—':>8} {'—':>8} {'—':>10}")

    # Check exports
    exported = 0
    if os.path.isdir(EXPORTS_DIR):
        exported = len([f for f in os.listdir(EXPORTS_DIR)
                        if f.startswith("wiki_") and f.endswith(".semantic.json")])
    print(f"\n  Analyzed exports: {exported}/{len(articles)}")

    # Check matrix
    matrix_path = os.path.join(EXPORTS_DIR, "_wiki_universality_matrix.json")
    if os.path.exists(matrix_path):
        with open(matrix_path) as f:
            m = json.load(f)
        print(f"  Languages in matrix: {len(m.get('languages', []))}")
        print(f"  Universal atoms: {m.get('universal_count', '?')}/{m.get('total_atoms', '?')}")
        print(f"  Avg cosine: {m.get('avg_cosine_similarity', '?')}")

    print(f"{'═' * 72}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Wikipedia corpus ingestion for PaniniFS (14 languages)"
    )
    parser.add_argument("--download", action="store_true",
                        help="Download curated articles")
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze all downloaded articles")
    parser.add_argument("--compare", action="store_true",
                        help="Build universality matrix")
    parser.add_argument("--all", action="store_true",
                        help="Download + analyze + compare")
    parser.add_argument("--random", type=int, default=0, metavar="N",
                        help="Also download N random articles per language")
    parser.add_argument("--status", action="store_true",
                        help="Show progress")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Less verbose output")

    args = parser.parse_args()
    verbose = not args.quiet

    if args.status:
        show_status()
        return

    t_global = time.time()

    if args.all or args.download:
        # 1. Resolve titles
        title_map = load_cached_titles()
        if not title_map:
            title_map = resolve_curated_titles()

        # 2. Download curated
        download_curated(title_map, verbose=verbose)

        # 3. Download random (optional)
        if args.random > 0:
            download_random_articles(args.random, verbose=verbose)

    if args.all or args.analyze:
        export_paths = analyze_all(verbose=verbose)

    if args.all or args.compare:
        if not os.path.isdir(EXPORTS_DIR):
            print("No exports found. Run --analyze first.")
            return
        export_paths = [
            os.path.join(EXPORTS_DIR, f)
            for f in sorted(os.listdir(EXPORTS_DIR))
            if f.startswith("wiki_") and f.endswith(".semantic.json")
        ]
        build_universality_matrix(export_paths, verbose=verbose)

    elapsed = time.time() - t_global
    if args.all or args.download or args.analyze or args.compare:
        print(f"\n⏱️  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")

    if not any([args.download, args.analyze, args.compare, args.all, args.status]):
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""interpretation_ingest.py — v4.7: Hierarchical ingestion pipeline

Parses document structure (chapters, paragraphs), runs 7-layer analysis on each
unit, and stores the hierarchical interpretation in panini-interpretations-db.

Usage:
    python interpretation_ingest.py                        # all gutenberg_corpus/
    python interpretation_ingest.py gutenberg_corpus/pg11_en.txt  # single file
    python interpretation_ingest.py --verbose              # detailed progress

Part of PaniniFS concept store — E2 total reconstruction pipeline.
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seven_layers_engine import (
    analyze_syntax, align_words_to_atoms, analyze_morphology,
    detect_structural_operators, detect_paragraph_concepts,
    analyze_discourse, analyze_prosody,
)
from reconstruction_fidelity import (
    get_stop_words, get_content_words, count_words,
)


# ═══════════════════════════════════════════════════════════════════════════════
# WORK METADATA
# ═══════════════════════════════════════════════════════════════════════════════

WORK_METADATA = {
    "pg11_en.txt":    {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "lang": "en"},
    "pg17482_eo.txt": {"title": "La Aventuroj de Alicio en Mirlando", "author": "Lewis Carroll (trad.)", "lang": "eo"},
    "pg19778_de.txt": {"title": "Alice im Wunderland", "author": "Lewis Carroll (übers.)", "lang": "de"},
    "pg19942_en.txt": {"title": "Candide", "author": "Voltaire (trans.)", "lang": "en"},
    "pg28371_it.txt": {"title": "Le avventure di Alice nel Paese delle Meraviglie", "author": "Lewis Carroll (trad.)", "lang": "it"},
    "pg4650_fr.txt":  {"title": "Candide, ou l'Optimisme", "author": "Voltaire", "lang": "fr"},
    "pg46569_fi.txt": {"title": "Liisan seikkailut ihmemaassa", "author": "Lewis Carroll (suom.)", "lang": "fi"},
    "pg52336_fi.txt": {"title": "Candide eli optimismi", "author": "Voltaire (suom.)", "lang": "fi"},
    "pg55456_fr.txt": {"title": "Les Aventures d'Alice au pays des merveilles", "author": "Lewis Carroll (trad.)", "lang": "fr"},
    "pg7109_es.txt":  {"title": "Cándido, ó El Optimismo", "author": "Voltaire (trad.)", "lang": "es"},
    "pg9000_sa.txt":  {"title": "Viṣṇusahasranāma", "author": "Traditional", "lang": "sa"},
}

# Chapter patterns per language
CHAPTER_PATTERNS = {
    "en": [re.compile(r'^CHAPTER\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE),
           re.compile(r'^Chapter\s+(\d+)\s*(.*)', re.IGNORECASE)],
    "fr": [re.compile(r'^CHAPITRE\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE)],
    "de": [re.compile(r'^(?:KAPITEL|Kapitel|Erstes|Zweites|Drittes|Viertes|Fünftes|Sechstes|Siebentes|Achtes|Neuntes|Zehntes|Elftes|Zwölftes)\s*(.*)', re.IGNORECASE)],
    "es": [re.compile(r'^CAP[IÍ]TULO\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE)],
    "it": [re.compile(r'^CAPITOLO\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE),
           re.compile(r'^Capitolo\s+(\d+)\s*(.*)', re.IGNORECASE)],
    "eo": [re.compile(r'^(?:ĈAPITRO|CXAPITRO|Ĉapitro|Cxapitro)\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE)],
    "fi": [re.compile(r'^(?:LUKU|Luku)\s+([IVXLC\d]+)\.?\s*(.*)', re.IGNORECASE)],
}


def detect_chapters(text: str, lang: str) -> List[Dict]:
    """Split text into chapters. Returns list of {title, ordinal, text, offset}."""
    lines = text.split('\n')
    patterns = CHAPTER_PATTERNS.get(lang, CHAPTER_PATTERNS["en"])
    chapters = []
    cur_title = None
    cur_lines = []
    cur_offset = 0
    ch_offset = 0

    for line in lines:
        matched = False
        for pat in patterns:
            if pat.match(line.strip()):
                if cur_lines or cur_title:
                    ct = '\n'.join(cur_lines).strip()
                    if ct:
                        chapters.append({"title": cur_title or "(Preamble)",
                                         "ordinal": len(chapters) + 1,
                                         "text": ct, "offset": ch_offset})
                cur_title = line.strip()
                cur_lines = []
                ch_offset = cur_offset
                matched = True
                break
        if not matched:
            cur_lines.append(line)
        cur_offset += len(line) + 1

    if cur_lines:
        ct = '\n'.join(cur_lines).strip()
        if ct:
            chapters.append({"title": cur_title or "(Full Text)",
                             "ordinal": len(chapters) + 1,
                             "text": ct, "offset": ch_offset})

    if not chapters:
        chapters.append({"title": "(Full Text)", "ordinal": 1,
                         "text": text.strip(), "offset": 0})
    return chapters


def split_paragraphs(text: str) -> List[str]:
    """Split into paragraphs (double newline separated)."""
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def compute_atom_profile(atoms: List[Dict]) -> Dict:
    """Normalized atom distribution from alignment list."""
    counts = Counter(a["atom_id"] for a in atoms)
    total = sum(counts.values()) or 1

    COL = {
        "MOUVEMENT": "mouvement", "COGNITION": "cognition",
        "PERCEPTION": "perception", "COMMUNICATION": "communication",
        "CREATION": "creation", "EXISTENCE": "existence",
        "DESTRUCTION": "destruction", "POSSESSION": "possession",
        "DOMINATION": "domination",
        "SEEKING": "seeking", "FEAR": "fear", "CARE": "care",
        "GRIEF": "grief", "RAGE": "rage", "DISGUST": "disgust",
        "PLAY": "play", "TEDIUM": "tedium",
        "RELATION": "relation_", "STRUCTURE": "structure_",
        "INVARIANCE": "invariance", "RÉCURRENCE": "recurrence",
        "DUALITÉ": "dualite", "MESURE": "mesure", "ORDRE": "ordre",
        "CHOSE": "chose", "AGENT": "agent", "CORPS": "corps",
        "LIEU": "lieu", "MATIÈRE": "matiere",
        "BON": "bon", "GRAND": "grand", "VRAI": "vrai",
        "INTENSE": "intense", "ANCIEN": "ancien",
    }

    profile = {c: 0.0 for c in COL.values()}
    dominant = None
    mx = 0
    for atom, cnt in counts.items():
        col = COL.get(atom)
        if col:
            profile[col] = cnt / total
            if cnt > mx:
                mx = cnt
                dominant = atom

    probs = [c / total for c in counts.values() if c > 0]
    entropy = -sum(p * math.log2(p) for p in probs) if probs else 0.0

    profile["total_alignments"] = total
    profile["dominant_atom"] = dominant
    profile["atom_entropy"] = round(entropy, 4)
    return profile


def analyze_para(text: str, lang: str) -> Dict:
    """Full 7-layer analysis on a paragraph."""
    syn = analyze_syntax(text, lang)
    atoms = align_words_to_atoms(text, lang, syntax_results=syn)
    morph = analyze_morphology(text, lang, syntax_results=syn)
    struct = detect_structural_operators(text, lang, atom_results=atoms, syntax_results=syn)
    try:
        disc = analyze_discourse(text, lang)
    except Exception:
        disc = {}
    try:
        pros = analyze_prosody(text, lang)
    except Exception:
        pros = {}
    concepts = detect_paragraph_concepts(atoms, syn, struct_ops=struct)
    return {"syntax": syn, "atoms": atoms, "morphology": morph,
            "structural": struct, "discourse": disc, "prosody": pros,
            "concepts": concepts}


def compute_fidelity(text: str, lang: str, analysis: Dict) -> Dict:
    stop = get_stop_words(lang)
    content = get_content_words(text, lang, stop)
    nc = len(content)
    na = len(analysis["atoms"])
    wc = count_words(text, lang)
    lc = na / nc if nc else 0.0
    ad = na / wc if wc else 0.0
    sc = len(analysis["syntax"]) / wc if wc else 0.0
    mc = 1.0 if analysis["morphology"] else 0.0
    cc = 1.0 if analysis["concepts"] else 0.0
    dc = 1.0 if analysis["discourse"] else 0.0
    pc = 1.0 if analysis["prosody"] else 0.0
    rr = 0.40*min(lc,1) + 0.15*min(sc,1) + 0.15*mc + 0.15*cc + 0.10*dc + 0.05*pc
    return {"lexical_coverage": round(lc,4), "atom_density": round(ad,4),
            "syntax_coverage": round(sc,4), "morpho_coverage": round(mc,4),
            "concept_coverage": round(cc,4), "discourse_coverage": round(dc,4),
            "prosody_coverage": round(pc,4), "reconstruction_readiness": round(rr,4),
            "content_word_count": nc, "atom_alignment_count": na}


# ═══════════════════════════════════════════════════════════════════════════════
# DOLT INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class DoltCLI:
    """Thin wrapper around dolt sql CLI for the interpretations DB.
    Uses a persistent subprocess for speed (pipe mode)."""

    def __init__(self, db_path: str):
        self.db = os.path.abspath(db_path)
        self._pipe = None
        self._buf = []     # accumulated statements for batch execution
        self._next_su = 1  # manual ID counter for structural_units
        self._next_ap = 1  # atom_profiles
        self._next_co = 1  # concepts
        self._next_fi = 1  # fidelity_metrics
        self._init_counters()

    def _init_counters(self):
        """Read current max IDs to seed counters."""
        for tbl, col, attr in [
            ("structural_units", "unit_id", "_next_su"),
            ("atom_profiles", "profile_id", "_next_ap"),
            ("concepts", "concept_id", "_next_co"),
            ("fidelity_metrics", "metric_id", "_next_fi"),
        ]:
            rows = self._sql_direct(f"SELECT COALESCE(MAX({col}),0) as mx FROM {tbl};")
            try:
                d = json.loads(rows)
                setattr(self, attr, (d.get("rows", d) if isinstance(d, dict) else d)[0]["mx"] + 1)
            except Exception:
                pass

    def _sql_direct(self, q: str) -> str:
        r = subprocess.run(["dolt", "sql", "-q", q, "-r", "json"],
                           cwd=self.db, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"SQL error: {r.stderr.strip()[:300]}")
        return r.stdout.strip()

    def sql(self, q: str) -> str:
        return self._sql_direct(q)

    def sql_rows(self, q: str) -> List[Dict]:
        raw = self._sql_direct(q)
        if not raw:
            return []
        try:
            d = json.loads(raw)
            return d.get("rows", d) if isinstance(d, dict) else d
        except json.JSONDecodeError:
            return []

    def insert_id(self, q: str) -> int:
        """INSERT + LAST_INSERT_ID in one session (Dolt CLI multi-statement)."""
        combined = q.rstrip(';') + "; SELECT LAST_INSERT_ID() as id;"
        r = subprocess.run(["dolt", "sql", "-q", combined, "-r", "json"],
                           cwd=self.db, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(f"SQL error: {r.stderr.strip()[:300]}")
        try:
            d = json.loads(r.stdout.strip())
            rows = d.get("rows", d) if isinstance(d, dict) else d
            return rows[0]["id"] if rows else 0
        except (json.JSONDecodeError, IndexError, KeyError):
            return 0

    def batch_add(self, stmt: str):
        """Queue a statement for batch execution."""
        self._buf.append(stmt.rstrip(';'))

    def batch_flush(self):
        """Execute all queued statements in one subprocess call."""
        if not self._buf:
            return
        combined = "; ".join(self._buf) + ";"
        r = subprocess.run(["dolt", "sql", "-q", combined],
                           cwd=self.db, capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            # Try statements one by one for better error reporting
            for stmt in self._buf:
                try:
                    subprocess.run(["dolt", "sql", "-q", stmt + ";"],
                                   cwd=self.db, capture_output=True, text=True, timeout=60,
                                   check=True)
                except subprocess.CalledProcessError as e:
                    sys.stderr.write(f"  ⚠ SQL: {stmt[:80]}... → {e.stderr.strip()[:100]}\n")
        self._buf.clear()

    def alloc_unit_id(self) -> int:
        v = self._next_su; self._next_su += 1; return v

    def alloc_profile_id(self) -> int:
        v = self._next_ap; self._next_ap += 1; return v

    def alloc_concept_id(self) -> int:
        v = self._next_co; self._next_co += 1; return v

    def alloc_fidelity_id(self) -> int:
        v = self._next_fi; self._next_fi += 1; return v

    def esc(self, s) -> str:
        if s is None:
            return "NULL"
        return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"

    def commit(self, msg: str):
        subprocess.run(["dolt", "add", "."], cwd=self.db, capture_output=True)
        subprocess.run(["dolt", "commit", "-m", msg], cwd=self.db, capture_output=True)


def ingest_file(fp: str, db: DoltCLI, corpus_id: int, verbose: bool = False) -> Dict:
    """Ingest one Gutenberg file."""
    fn = os.path.basename(fp)
    meta = WORK_METADATA.get(fn, {})
    lang = meta.get("lang", "en")
    title = meta.get("title", fn)
    author = meta.get("author", "Unknown")

    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    wc = count_words(text, lang)
    work_id = db.insert_id(
        f"INSERT INTO works (corpus_id,title,author,language,source_file,word_count) "
        f"VALUES ({corpus_id},{db.esc(title)},{db.esc(author)},{db.esc(lang)},{db.esc(fn)},{wc});")

    if verbose:
        print(f"\n  📖 {title} ({lang}) — {wc:,} words → work #{work_id}")

    chapters = detect_chapters(text, lang)
    total_paras = 0
    total_atoms = 0
    all_atoms = Counter()
    all_concepts = Counter()

    for ch in chapters:
        ch_wc = count_words(ch["text"], lang)
        ch_id = db.alloc_unit_id()
        db.batch_add(
            f"INSERT INTO structural_units (unit_id,work_id,parent_id,unit_type,ordinal,title,text_hash,word_count,"
            f"char_offset_start,char_offset_end) VALUES "
            f"({ch_id},{work_id},NULL,'chapter',{ch['ordinal']},{db.esc(ch['title'])},"
            f"{db.esc(sha16(ch['text']))},{ch_wc},{ch['offset']},{ch['offset']+len(ch['text'])})")

        paragraphs = split_paragraphs(ch["text"])
        ch_atoms_all = []

        for pi, pt in enumerate(paragraphs):
            if len(pt.strip()) < 10:
                continue
            total_paras += 1
            pwc = count_words(pt, lang)
            para_id = db.alloc_unit_id()
            db.batch_add(
                f"INSERT INTO structural_units (unit_id,work_id,parent_id,unit_type,ordinal,text_hash,word_count) "
                f"VALUES ({para_id},{work_id},{ch_id},'paragraph',{pi+1},{db.esc(sha16(pt))},{pwc})")

            analysis = analyze_para(pt, lang)
            na = len(analysis["atoms"])
            total_atoms += na

            for a in analysis["atoms"]:
                all_atoms[a["atom_id"]] += 1
                ch_atoms_all.append(a)
            for c in analysis["concepts"]:
                all_concepts[c["concept_id"]] += 1

            # Atom profile
            prof = compute_atom_profile(analysis["atoms"])
            cols = ["mouvement","cognition","perception","communication","creation",
                    "existence","destruction","possession","domination",
                    "seeking","fear","care","grief","rage","disgust","play","tedium",
                    "relation_","structure_","invariance","recurrence","dualite","mesure","ordre",
                    "chose","agent","corps","lieu","matiere","bon","grand","vrai","intense","ancien",
                    "total_alignments","dominant_atom","atom_entropy"]
            vals = []
            for c in cols:
                v = prof.get(c, 0)
                vals.append(db.esc(v) if isinstance(v, str) else ("NULL" if v is None else str(round(v, 6) if isinstance(v, float) else v)))
            pid = db.alloc_profile_id()
            db.batch_add(f"INSERT INTO atom_profiles (profile_id,unit_id,{','.join(cols)}) VALUES ({pid},{para_id},{','.join(vals)})")

            # Concepts
            for c in analysis["concepts"][:10]:
                cid_val = c.get("concept_id", "?")
                atoms_str = ','.join(c.get("atoms_evidence", {}).keys())
                conf = c.get('confidence', 1.0)
                coid = db.alloc_concept_id()
                db.batch_add(f"INSERT INTO concepts (concept_id,unit_id,concept_name,atoms_involved,confidence) "
                       f"VALUES ({coid},{para_id},{db.esc(cid_val)},{db.esc(atoms_str)},{conf})")

            # Fidelity
            fid = compute_fidelity(pt, lang, analysis)
            fcols = ["lexical_coverage","atom_density","syntax_coverage","morpho_coverage",
                     "concept_coverage","discourse_coverage","prosody_coverage",
                     "reconstruction_readiness","content_word_count","atom_alignment_count"]
            fvals = [str(fid.get(c,0)) for c in fcols]
            fmid = db.alloc_fidelity_id()
            db.batch_add(f"INSERT INTO fidelity_metrics (metric_id,unit_id,{','.join(fcols)}) VALUES ({fmid},{para_id},{','.join(fvals)})")

            # Flush batch every 20 paragraphs
            if total_paras % 20 == 0:
                db.batch_flush()

        # Chapter aggregate profile
        if ch_atoms_all:
            chp = compute_atom_profile(ch_atoms_all)
            chv = []
            for c in cols:
                v = chp.get(c, 0)
                chv.append(db.esc(v) if isinstance(v, str) else ("NULL" if v is None else str(round(v, 6) if isinstance(v, float) else v)))
            cpid = db.alloc_profile_id()
            db.batch_add(f"INSERT INTO atom_profiles (profile_id,unit_id,{','.join(cols)}) VALUES ({cpid},{ch_id},{','.join(chv)})")

        db.batch_flush()  # Flush at end of each chapter
        if verbose:
            print(f"    Ch {ch['ordinal']:2d}: {len(paragraphs):3d} paras, {ch_wc:6,} words, {len(ch_atoms_all):5d} atoms")

    if verbose:
        print(f"  ✅ {total_paras} paragraphs, {total_atoms:,} atoms, {len(all_concepts)} concepts")

    return {"work_id": work_id, "filename": fn, "title": title, "language": lang,
            "word_count": wc, "chapters": len(chapters), "paragraphs": total_paras,
            "atoms": total_atoms, "concepts": sum(all_concepts.values())}


def main():
    parser = argparse.ArgumentParser(description="Hierarchical Gutenberg ingestion")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("--corpus-dir", default="gutenberg_corpus")
    parser.add_argument("--db-path", default="panini-interpretations-db")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    db = DoltCLI(args.db_path)

    # Ensure corpus
    rows = db.sql_rows("SELECT corpus_id FROM corpora WHERE name='gutenberg';")
    if rows:
        corpus_id = rows[0]["corpus_id"]
    else:
        corpus_id = db.insert_id(
            "INSERT INTO corpora (name,description,source_url) VALUES "
            "('gutenberg','Project Gutenberg literary works','https://www.gutenberg.org');")

    # Gather files
    if args.files:
        files = args.files
    else:
        files = sorted(os.path.join(args.corpus_dir, f)
                       for f in os.listdir(args.corpus_dir) if f.endswith('.txt'))

    print(f"🔄 Ingesting {len(files)} file(s) into panini-interpretations-db")
    t0 = time.time()
    results = []

    for fp in files:
        try:
            r = ingest_file(fp, db, corpus_id, verbose=args.verbose)
            results.append(r)
            print(f"  ✅ {r['filename']}: {r['word_count']:,}w, {r['atoms']:,}a, {r['concepts']}c")
        except Exception as e:
            print(f"  ❌ {os.path.basename(fp)}: {e}")
            import traceback; traceback.print_exc()

    elapsed = time.time() - t0
    tw = sum(r["word_count"] for r in results)
    ta = sum(r["atoms"] for r in results)
    tp = sum(r["paragraphs"] for r in results)

    print(f"\n{'═' * 60}")
    print(f"DONE: {len(results)} works, {tw:,} words, {tp:,} paragraphs, {ta:,} atoms")
    print(f"Time: {elapsed:.0f}s ({elapsed/60:.1f}min)")

    db.commit(f"v4.7: Ingest {len(results)} Gutenberg works ({tw:,} words)")
    print(f"💾 Committed to Dolt")

    summary = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "files": len(results), "total_words": tw,
               "total_paragraphs": tp, "total_atoms": ta,
               "elapsed_s": round(elapsed, 1), "works": results}
    with open("interpretation_ingestion_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"📊 Summary → interpretation_ingestion_summary.json")


if __name__ == "__main__":
    main()

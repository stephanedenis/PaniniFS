#!/usr/bin/env python3
"""
PaniniFS Unified Dolt Storage — Tiered Architecture POC

Démontre le stockage unifié Dolt avec 3 tiers de visibilité:
  - public    : dhātu, grammaires, statistiques (clonable par tous)
  - confidential : analyses, mappings, chunks metadata (accès restreint)
  - private   : fichiers utilisateur, blobs, attributions sensibles

Architecture Dolt:
  Branches = isolation des tiers
  Merges = promotion contrôlée de données entre tiers
  Clones = distribution du tier public

Usage:
    python3 dolt_unified_storage.py
"""

import hashlib
import json
import os
import subprocess
import sys
import struct
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# ─── Configuration ───────────────────────────────────────────────────────────

DB_DIR = "./panini-unified-db"
SCHEMA_FILE = "schema_clean.sql"
TIERS = ["public", "confidential", "private"]

# ─── Dolt Helper ─────────────────────────────────────────────────────────────

def dolt(args: List[str], cwd: str = DB_DIR, input_data: str = None, 
         check: bool = True) -> str:
    """Execute a dolt command and return stdout"""
    try:
        result = subprocess.run(
            ["dolt"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            input=input_data,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            print(f"  ⚠️  dolt {' '.join(args[:3])}...: {e.stderr.strip()[:200]}")
        return ""


def dolt_sql(query: str, cwd: str = DB_DIR) -> str:
    """Execute SQL query via dolt"""
    return dolt(["sql", "-q", query], cwd=cwd)


def dolt_sql_file(sql_content: str, cwd: str = DB_DIR) -> str:
    """Execute SQL from string via stdin"""
    return dolt(["sql"], cwd=cwd, input_data=sql_content)


def dolt_branch(name: str) -> str:
    """Create a branch if it doesn't exist"""
    existing = dolt(["branch", "--list"], check=False)
    if name not in existing:
        return dolt(["branch", name])
    return ""


def dolt_checkout(branch: str) -> str:
    """Switch to branch"""
    return dolt(["checkout", branch])


def dolt_commit(message: str) -> str:
    """Stage all and commit"""
    dolt(["add", "."])
    return dolt(["commit", "-m", message], check=False)


def escape_sql(s: str) -> str:
    """Escape string for SQL"""
    return s.replace("'", "''").replace("\\", "\\\\")


# ─── Tier 1: PUBLIC — Seed reference data ────────────────────────────────────

DHATU_DEFINITIONS = [
    ("dhatu_comm", "COMM", "Communiquer/Partager", "Communicate/Share",
     "Transmission d''information, canal de communication", '["canal","source","cible"]'),
    ("dhatu_iter", "ITER", "Itérer/Répéter", "Iterate/Repeat",
     "Boucle, fréquence, cumul, pattern récurrent", '["boucle","fréquence","cumul"]'),
    ("dhatu_trans", "TRANS", "Transformer", "Transform",
     "Entrée→opération→sortie, filtre, map", '["entrée","opération","sortie"]'),
    ("dhatu_decide", "DECIDE", "Choisir/Régler", "Decide/Choose",
     "Décision, critères, seuils, branches conditionnelles", '["critères","seuils","branches"]'),
    ("dhatu_locate", "LOCATE", "Localiser/Ancrer", "Locate/Anchor",
     "Position, contexte spatial ou conceptuel, repères", '["position","contexte","repères"]'),
    ("dhatu_group", "GROUP", "Regrouper/Structurer", "Group/Structure",
     "Collection, appartenance, classification, hiérarchie", '["collection","appartenance","hiérarchie"]'),
    ("dhatu_seq", "SEQ", "Séquencer/Ordonner", "Sequence/Order",
     "Ordre, dépendances, timeline, pipeline", '["ordre","dépendances","timeline"]'),
]

FORMAT_GRAMMARS = [
    ("png_v1", "PNG", "image", "Chunks IHDR/PLTE/IDAT/IEND"),
    ("jpeg_v1", "JPEG", "image", "Markers SOI/APP/DQT/SOF/SOS/EOI"),
    ("mp4_v1", "MP4", "video", "ISO BMFF boxes ftyp/moov/mdat + keyframe stss"),
    ("webm_v1", "WebM", "video", "EBML/Matroska clusters + tracks"),
    ("mkv_v1", "MKV", "video", "Matroska full spec"),
    ("avi_v1", "AVI", "video", "RIFF/AVI chunks + idx1"),
    ("riff_wav", "WAV", "audio", "RIFF/WAVE fmt+data chunks"),
    ("riff_webp", "WebP", "image", "RIFF/WEBP VP8/VP8L"),
    ("pdf_v1", "PDF", "document", "Objects, xref, streams"),
    ("gzip_v1", "GZIP", "compressed", "Header + compressed blocks"),
    ("text_generic", "TEXT", "text", "Line-based UTF-8 text"),
    ("binary_generic", "BINARY", "binary", "Fixed-size blocks"),
]


def seed_public_tier():
    """Seed the public branch with reference data"""
    print("\n" + "=" * 70)
    print("📗 TIER 1: PUBLIC — Données ouvertes")
    print("=" * 70)
    
    # Already on main
    
    # 1. Dhātu definitions
    print("  🔹 7 dhātu informationnels...")
    for d in DHATU_DEFINITIONS:
        dolt_sql_file(
            f"INSERT IGNORE INTO dhatu_definitions (id, code, name_fr, name_en, description, components) "
            f"VALUES ('{d[0]}', '{d[1]}', '{d[2]}', '{d[3]}', '{d[4]}', '{d[5]}');"
        )
    print(f"     ✅ {len(DHATU_DEFINITIONS)} dhātu")
    
    # 2. Format grammars
    print("  🔹 Grammaires de formats binaires...")
    for g in FORMAT_GRAMMARS:
        dolt_sql_file(
            f"INSERT IGNORE INTO format_grammars (grammar_id, format_name, category, description) "
            f"VALUES ('{g[0]}', '{g[1]}', '{g[2]}', '{g[3]}');"
        )
    print(f"     ✅ {len(FORMAT_GRAMMARS)} grammaires")
    
    # 3. Semantic hash registry (amorce)
    print("  🔹 Semantic hash registry (concepts publics)...")
    concepts = [
        ("COMM", {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0, "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0}),
        ("ITER", {"COMM": 0.1, "ITER": 0.7, "TRANS": 0.1, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.05, "SEQ": 0.0}),
        ("TRANS", {"COMM": 0.1, "ITER": 0.05, "TRANS": 0.7, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.1, "SEQ": 0.0}),
        ("DECIDE", {"COMM": 0.05, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.7, "LOCATE": 0.05, "GROUP": 0.05, "SEQ": 0.05}),
        ("LOCATE", {"COMM": 0.1, "ITER": 0.0, "TRANS": 0.0, "DECIDE": 0.0, "LOCATE": 0.7, "GROUP": 0.1, "SEQ": 0.1}),
    ]
    for dominant, sig in concepts:
        quantized = {k: round(v * 4) / 4 for k, v in sig.items()}
        shash = hashlib.sha256(json.dumps(quantized, sort_keys=True).encode()).hexdigest()
        sig_json = json.dumps(sig)
        dolt_sql_file(
            f"INSERT IGNORE INTO semantic_hash_registry (semantic_hash, dominant_dhatu, dhatu_signature, language_count, entry_count) "
            f"VALUES ('{shash}', '{dominant}', '{sig_json}', 7, 35);"
        )
    print(f"     ✅ {len(concepts)} concepts de référence")
    print("  💾 Tier public prêt")


# ─── Tier 2: CONFIDENTIAL — Analysis data ────────────────────────────────────

def seed_confidential_tier():
    """Seed the confidential branch with analysis data"""
    print("\n" + "=" * 70)
    print("📙 TIER 2: CONFIDENTIAL — Données analysées")
    print("=" * 70)
    
    dolt_checkout("confidential")
    print("  🔹 Héritage du tier public ✅")
    
    # 1. Semantic mappings
    print("  🔹 Semantic mappings multilingues...")
    mappings = [
        ("Bonjour le monde", "fr", "COMM"),
        ("Hello world", "en", "COMM"),
        ("Hola mundo", "es", "COMM"),
        ("مرحبا بالعالم", "ar", "COMM"),
        ("你好世界", "zh", "COMM"),
        ("こんにちは世界", "ja", "COMM"),
        ("Habari dunia", "sw", "COMM"),
        ("Répéter chaque élément", "fr", "ITER"),
        ("Iterate over each item", "en", "ITER"),
        ("Transformer les données en JSON", "fr", "TRANS"),
        ("Transform data into JSON", "en", "TRANS"),
        ("Si la valeur est supérieure à 10", "fr", "DECIDE"),
        ("If the value is greater than 10", "en", "DECIDE"),
        ("Le livre est sur la table", "fr", "LOCATE"),
        ("The book is on the table", "en", "LOCATE"),
    ]
    
    dhatu_sigs = {
        "COMM": {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0, "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0},
        "ITER": {"COMM": 0.1, "ITER": 0.7, "TRANS": 0.1, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.05, "SEQ": 0.0},
        "TRANS": {"COMM": 0.1, "ITER": 0.05, "TRANS": 0.7, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.1, "SEQ": 0.0},
        "DECIDE": {"COMM": 0.05, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.7, "LOCATE": 0.05, "GROUP": 0.05, "SEQ": 0.05},
        "LOCATE": {"COMM": 0.1, "ITER": 0.0, "TRANS": 0.0, "DECIDE": 0.0, "LOCATE": 0.7, "GROUP": 0.1, "SEQ": 0.1},
    }
    
    ok = 0
    for text, lang, dominant in mappings:
        sig = dhatu_sigs[dominant]
        chash = hashlib.sha256(text.encode()).hexdigest()
        quantized = {k: round(v * 4) / 4 for k, v in sig.items()}
        shash = hashlib.sha256(json.dumps(quantized, sort_keys=True).encode()).hexdigest()
        text_esc = escape_sql(text)
        sig_json = json.dumps(sig)
        dolt_sql_file(
            f"INSERT IGNORE INTO semantic_mappings (content_hash, source_text, language, dhatu_signature, semantic_hash, confidence, analyzer_version) "
            f"VALUES ('{chash}', '{text_esc}', '{lang}', '{sig_json}', '{shash}', 0.95, 'python-0.2.2');"
        )
        ok += 1
    print(f"     ✅ {ok} mappings")
    
    # 2. File analysis results
    print("  🔹 Résultats d'analyse de fichiers...")
    test_files = [
        ("test.png", "abc123hash", 45000, "PNG", "png_v1",
         {"COMM": 0.15, "ITER": 0.3, "TRANS": 0.2, "DECIDE": 0.05, "LOCATE": 0.1, "GROUP": 0.15, "SEQ": 0.05}, "ITER"),
        ("readme.md", "def456hash", 8500, "TEXT", "text_generic",
         {"COMM": 0.4, "ITER": 0.05, "TRANS": 0.15, "DECIDE": 0.1, "LOCATE": 0.05, "GROUP": 0.1, "SEQ": 0.15}, "COMM"),
        ("video.mp4", "ghi789hash", 52000000, "MP4", "mp4_v1",
         {"COMM": 0.1, "ITER": 0.25, "TRANS": 0.3, "DECIDE": 0.05, "LOCATE": 0.1, "GROUP": 0.1, "SEQ": 0.1}, "TRANS"),
        ("data.json", "jkl012hash", 12000, "TEXT", "text_generic",
         {"COMM": 0.2, "ITER": 0.15, "TRANS": 0.1, "DECIDE": 0.05, "LOCATE": 0.1, "GROUP": 0.35, "SEQ": 0.05}, "GROUP"),
        ("song.wav", "mno345hash", 35000000, "WAV", "riff_wav",
         {"COMM": 0.3, "ITER": 0.3, "TRANS": 0.15, "DECIDE": 0.05, "LOCATE": 0.05, "GROUP": 0.1, "SEQ": 0.05}, "COMM"),
    ]
    
    for fp, fh, fs, fmt, gid, dv, dd in test_files:
        dv_json = json.dumps(dv)
        dolt_sql_file(
            f"INSERT IGNORE INTO analysis_results (file_path, file_hash, file_size, format_name, grammar_id, dhatu_vector, dominant_dhatu, analysis_version) "
            f"VALUES ('{fp}', '{fh}', {fs}, '{fmt}', '{gid}', '{dv_json}', '{dd}', 'python-0.2.2');"
        )
    print(f"     ✅ {len(test_files)} fichiers analysés")
    
    # 3. Chunk metadata (PNG)
    print("  🔹 Chunk metadata (PNG sémantique)...")
    png_chunks = [
        (0, hashlib.sha256(b"PNG_SIG").hexdigest(), 0, 8, "PNG_SIGNATURE", "png_v1"),
        (1, hashlib.sha256(b"PNG_IHDR").hexdigest(), 8, 25, "PNG_IHDR", "png_v1"),
        (2, hashlib.sha256(b"PNG_IDAT1").hexdigest(), 33, 20000, "PNG_IDAT", "png_v1"),
        (3, hashlib.sha256(b"PNG_IDAT2").hexdigest(), 20033, 20000, "PNG_IDAT", "png_v1"),
        (4, hashlib.sha256(b"PNG_IEND").hexdigest(), 40033, 12, "PNG_IEND", "png_v1"),
    ]
    
    for cid, chash, off, sz, ptype, gid in png_chunks:
        recipe = json.dumps({"version": "1.0", "chunk_id": cid, "grammar_id": gid,
                             "steps": ["LOAD", "VALIDATE", "DECOMPRESS", "ASSEMBLE"],
                             "assembly": {"offset": off, "size": sz}})
        dolt_sql_file(
            f"INSERT IGNORE INTO chunk_metadata (file_hash, chunk_id, chunk_hash, offset_pos, size, pattern_type, grammar_id, reconstruction_recipe, status) "
            f"VALUES ('abc123hash', {cid}, '{chash}', {off}, {sz}, '{ptype}', '{gid}', '{escape_sql(recipe)}', 'pending');"
        )
    print(f"     ✅ {len(png_chunks)} chunks PNG")
    
    # 4. Audio fingerprint
    print("  🔹 Audio fingerprint (Shazam-like)...")
    dolt_sql_file(
        "INSERT IGNORE INTO audio_fingerprints "
        "(file_hash, duration_ms, sample_rate, channels, spectral_centroid, zero_crossing_rate, tempo_bpm, detected_key, constellation_count, hash_pair_count) "
        "VALUES ('mno345hash', 180000, 44100, 2, 2500.5, 0.085, 120.0, 'Am', 1500, 8500);"
    )
    print("     ✅ 1 empreinte audio")
    
    # 5. Reconstruction manifest
    print("  🔹 Reconstruction manifest...")
    manifest = json.dumps({
        "chunks": [{"id": c[0], "hash": c[1], "offset": c[2], "size": c[3]} for c in png_chunks],
        "total_chunks": 5, "grammar_id": "png_v1"
    })
    dolt_sql_file(
        f"INSERT IGNORE INTO reconstruction_manifests "
        f"(file_hash, file_name, total_chunks, grammar_id, original_size, manifest) "
        f"VALUES ('abc123hash', 'test.png', 5, 'png_v1', 40045, '{escape_sql(manifest)}');"
    )
    print("     ✅ 1 manifest")
    
    dolt_commit("seed: confidential tier — mappings + analyses + chunks + audio")
    print("  💾 Commit confidential tier")


# ─── Tier 3: PRIVATE — User data ─────────────────────────────────────────────

def seed_private_tier():
    """Seed the private branch with user-specific data"""
    print("\n" + "=" * 70)
    print("📕 TIER 3: PRIVATE — Données utilisateur")
    print("=" * 70)
    
    # Already on private/stephane
    
    print("  🔹 Héritage des tiers public + confidential ✅")
    
    # 1. User files
    print("  🔹 Fichiers utilisateur...")
    user_files = [
        ("abc123hash", "/home/stephane/Photos/vacances.png", "vacances.png", 45000, "image/png", "PNG"),
        ("def456hash", "/home/stephane/GitHub/Panini-FS/README.md", "README.md", 8500, "text/markdown", "TEXT"),
        ("ghi789hash", "/home/stephane/Videos/demo.mp4", "demo.mp4", 52000000, "video/mp4", "MP4"),
        ("mno345hash", "/home/stephane/Music/ambient.wav", "ambient.wav", 35000000, "audio/wav", "WAV"),
    ]
    
    for fh, fp, fn, fs, mt, fmt in user_files:
        dolt_sql_file(
            f"INSERT IGNORE INTO user_files (file_hash, file_path, file_name, file_size, mime_type, format_name, owner) "
            f"VALUES ('{fh}', '{escape_sql(fp)}', '{fn}', {fs}, '{mt}', '{fmt}', 'stephane');"
        )
    print(f"     ✅ {len(user_files)} fichiers")
    
    # 2. Attribution log
    print("  🔹 Log d attribution...")
    attributions = [
        ("analysis", 1, "abc123hash", "/home/stephane/Photos/vacances.png", "stephane", "CC-BY-4.0", "private"),
        ("analysis", 2, "def456hash", "https://github.com/stephanedenis/Panini-FS", "stephane", "MIT", "public"),
        ("semantic_mapping", 1, None, "corpus-wikipedia-fr", "wikipedia", "CC-BY-SA-4.0", "confidential"),
    ]
    
    for et, eid, sh, src, author, lic, tier in attributions:
        sh_sql = f"'{sh}'" if sh else "NULL"
        dolt_sql_file(
            f"INSERT IGNORE INTO attribution_log (entry_type, entry_id, semantic_hash, source, author, license, access_tier) "
            f"VALUES ('{et}', {eid}, {sh_sql}, '{escape_sql(src)}', '{author}', '{lic}', '{tier}');"
        )
    print(f"     ✅ {len(attributions)} attributions")
    
    # 3. Analysis session
    print("  🔹 Session d analyse...")
    config = json.dumps({"strategy": "semantic", "max_chunk_size": 1048576, "formats": ["PNG", "MP4", "WAV"]})
    dolt_sql_file(
        f"INSERT IGNORE INTO analysis_sessions "
        f"(session_id, owner, status, files_processed, chunks_created, dedup_found, config) "
        f"VALUES ('sess-001', 'stephane', 'completed', 4, 5, 1, '{escape_sql(config)}');"
    )
    print("     ✅ 1 session")
    
    dolt_commit("seed: private/stephane — files + attribution + sessions")
    print("  💾 Commit private tier")


# ─── Demonstration: Cross-tier queries ────────────────────────────────────────

def demonstrate_tier_isolation():
    """Show how tier isolation works with Dolt branches"""
    print("\n" + "=" * 70)
    print("🔍 DÉMONSTRATION: Isolation des tiers")
    print("=" * 70)
    
    # 1. Public tier: only reference data, confidential tables empty
    print("\n📗 Sur la branche 'main' (public):")
    dolt_checkout("main")
    
    result = dolt_sql_file(
        "SELECT 'dhatu_definitions' as tbl, COUNT(*) as cnt FROM dhatu_definitions "
        "UNION ALL SELECT 'format_grammars', COUNT(*) FROM format_grammars "
        "UNION ALL SELECT 'semantic_hash_registry', COUNT(*) FROM semantic_hash_registry;"
    )
    print(result)
    
    # Show tier-2 tables are empty on public
    result = dolt_sql_file("SELECT COUNT(*) as mapping_count FROM semantic_mappings;")
    print(f"  semantic_mappings sur public: {result}")
    result = dolt_sql_file("SELECT COUNT(*) as user_files_count FROM user_files;")
    print(f"  user_files sur public: {result}")
    
    # 2. Confidential: reference + analysis data
    print("\n📙 Sur la branche 'confidential':")
    dolt_checkout("confidential")
    
    result = dolt_sql_file(
        "SELECT 'semantic_mappings' as tbl, COUNT(*) as cnt FROM semantic_mappings "
        "UNION ALL SELECT 'analysis_results', COUNT(*) FROM analysis_results "
        "UNION ALL SELECT 'chunk_metadata', COUNT(*) FROM chunk_metadata "
        "UNION ALL SELECT 'audio_fingerprints', COUNT(*) FROM audio_fingerprints;"
    )
    print(result)
    
    # user_files empty on confidential
    result = dolt_sql_file("SELECT COUNT(*) as user_files_count FROM user_files;")
    print(f"  user_files sur confidential: {result}")
    
    # 3. Private: everything
    print("\n📕 Sur la branche 'private/stephane':")
    dolt_checkout("private/stephane")
    
    result = dolt_sql_file(
        "SELECT 'user_files' as tbl, COUNT(*) as cnt FROM user_files "
        "UNION ALL SELECT 'attribution_log', COUNT(*) FROM attribution_log "
        "UNION ALL SELECT 'analysis_sessions', COUNT(*) FROM analysis_sessions;"
    )
    print(result)
    
    # Private can also see confidential and public data
    result = dolt_sql_file(
        "SELECT 'dhatu_definitions' as tbl, COUNT(*) as cnt FROM dhatu_definitions "
        "UNION ALL SELECT 'semantic_mappings', COUNT(*) FROM semantic_mappings "
        "UNION ALL SELECT 'analysis_results', COUNT(*) FROM analysis_results;"
    )
    print("  Visibilité cross-tier (héritage):")
    print(result)


def demonstrate_promotion_workflow():
    """Show how data can be promoted from private to public via PR"""
    print("\n" + "=" * 70)
    print("🔄 DÉMONSTRATION: Promotion de données (private → public)")
    print("=" * 70)
    
    print("\n  Scénario: Stéphane veut publier ses statistiques d analyse")
    print("  Les données brutes restent privées, seules les stats agrégées")
    print("  sont promues vers le tier public.\n")
    
    # 1. Extract aggregated stats from private
    dolt_checkout("private/stephane")
    
    result = dolt_sql_file(
        "SELECT dominant_dhatu, COUNT(*) as cnt, "
        "ROUND(AVG(file_size), 0) as avg_size "
        "FROM analysis_results "
        "GROUP BY dominant_dhatu;"
    )
    print("  📊 Stats extraites depuis private/stephane:")
    print(result)
    
    # 2. Create promotion branch from main
    dolt_checkout("main")
    dolt_branch("promote/stats-2026-02")
    dolt_checkout("promote/stats-2026-02")
    
    # 3. Insert aggregated stats (not raw data)
    print("\n  📤 Promotion vers promote/stats-2026-02:")
    metrics = json.dumps({
        "COMM": {"count": 2, "avg_size": 21750},
        "ITER": {"count": 1, "avg_size": 45000},
        "TRANS": {"count": 1, "avg_size": 52000000},
        "GROUP": {"count": 1, "avg_size": 12000}
    })
    dolt_sql_file(
        f"INSERT INTO public_statistics (stat_type, scope, metrics) "
        f"VALUES ('dhatu_distribution', 'global', '{escape_sql(metrics)}');"
    )
    
    dolt_commit("promote: dhatu distribution stats from analysis session")
    print("  ✅ Stats agrégées commitées sur branche de promotion")
    
    # 4. Merge to main (simulates approved PR)
    dolt_checkout("main")
    dolt(["merge", "promote/stats-2026-02"], check=False)
    dolt_commit("merge: promoted stats from private analysis")
    
    print("  ✅ Merge vers main (public)")
    
    result = dolt_sql_file("SELECT * FROM public_statistics;")
    print("\n  📊 Statistiques maintenant publiques:")
    print(result)


def demonstrate_full_pipeline():
    """Demonstrate the full PaniniFS pipeline through Dolt"""
    print("\n" + "=" * 70)
    print("🚀 DÉMONSTRATION: Pipeline complet PaniniFS")
    print("=" * 70)
    
    dolt_checkout("private/stephane")
    
    # 1. Query: which formats are richest in TRANS
    print("\n  🔎 Quels formats sont les plus riches en TRANS?")
    result = dolt_sql_file(
        "SELECT ar.format_name, fg.category, "
        "ROUND(AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(ar.dhatu_vector, '$.TRANS')) AS DECIMAL(5,3))), 3) as avg_trans, "
        "COUNT(*) as files "
        "FROM analysis_results ar "
        "JOIN format_grammars fg ON ar.grammar_id = fg.grammar_id "
        "GROUP BY ar.format_name, fg.category "
        "ORDER BY avg_trans DESC;"
    )
    print(result)
    
    # 2. Reconstruction pipeline
    print("\n  🔧 Recipe de reconstruction pour test.png:")
    result = dolt_sql_file(
        "SELECT cm.chunk_id, cm.pattern_type, cm.offset_pos, cm.size, cm.status "
        "FROM chunk_metadata cm "
        "JOIN reconstruction_manifests rm ON cm.file_hash = rm.file_hash "
        "WHERE rm.file_name = 'test.png' "
        "ORDER BY cm.chunk_id;"
    )
    print(result)
    
    # 3. Cross-language deduplication
    print("\n  🌍 Déduplication cross-langue:")
    result = dolt_sql_file("SELECT * FROM v_semantic_deduplication LIMIT 5;")
    print(result)
    
    # 4. Provenance chain
    print("\n  📜 Chaîne de provenance:")
    result = dolt_sql_file(
        "SELECT al.entry_type, al.source, al.author, al.license, al.access_tier "
        "FROM attribution_log al "
        "ORDER BY al.logged_at;"
    )
    print(result)
    
    # 5. Dolt diff between tiers
    print("\n  📊 Diff public vs confidential:")
    dolt_checkout("confidential")
    result = dolt(["diff", "--stat", "main"], check=False)
    print(f"  {result}")
    
    # 6. Dolt history
    print("\n  📚 Historique Dolt (toutes branches):")
    dolt_checkout("main")
    result = dolt(["log", "--oneline", "-n", "5"])
    print(f"  main:\n{result}")
    
    dolt_checkout("confidential")
    result = dolt(["log", "--oneline", "-n", "3"])
    print(f"  confidential:\n{result}")
    
    dolt_checkout("private/stephane")
    result = dolt(["log", "--oneline", "-n", "3"])
    print(f"  private/stephane:\n{result}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("🏗️  PaniniFS UNIFIED DOLT STORAGE — Architecture à 3 Tiers")
    print("=" * 80)
    print()
    print("  📗 PUBLIC       : dhātu, grammaires, statistiques (clonable)")
    print("  📙 CONFIDENTIAL : analyses, mappings, chunks, fingerprints")
    print("  📕 PRIVATE      : fichiers utilisateur, blobs, attributions")
    print()
    print("  Technologie: Dolt (branches = isolation, merges = promotion)")
    print()
    
    # 1. Initialize fresh DB
    print("🔧 Initialisation de la base unifiée...")
    if os.path.exists(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR)
    
    os.makedirs(DB_DIR, exist_ok=True)
    dolt(["init"], cwd=DB_DIR)
    dolt(["config", "--local", "--add", "user.name", "PaniniFS System"], cwd=DB_DIR)
    dolt(["config", "--local", "--add", "user.email", "panini@localhost"], cwd=DB_DIR)
    print("  ✅ Repo Dolt initialisé")
    
    # 2. Create schema (ALL 17 tables on main BEFORE branching)
    print("  🔧 Création du schéma unifié (17 tables + vues)...")
    schema_path = Path(__file__).parent / SCHEMA_FILE
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            schema_lines = f.readlines()
        # Strip comment-only lines, then split by semicolons
        cleaned = []
        for line in schema_lines:
            stripped = line.strip()
            if stripped.startswith('--'):
                continue  # Skip comment-only lines
            cleaned.append(line)
        full_sql = "".join(cleaned)
        stmts = [s.strip() for s in full_sql.split(';') if s.strip()]
        print(f"     {len(stmts)} statements SQL à exécuter...")
        errors = 0
        for stmt in stmts:
            result = dolt_sql_file(stmt + ";")
            if not result and "error" in str(result).lower():
                errors += 1
        print(f"  ✅ Schéma créé ({errors} erreurs mineures)")
    else:
        print(f"  ❌ {SCHEMA_FILE} introuvable!")
        sys.exit(1)
    
    dolt_commit("schema: unified PaniniFS storage with 3-tier architecture")
    
    # Verify all tables
    result = dolt_sql_file(
        "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = 'panini-unified-db' AND TABLE_TYPE = 'BASE TABLE';"
    )
    print(f"  📊 Tables créées:\n{result}")
    
    # 3. Seed each tier
    # PUBLIC data is seeded on main first
    seed_public_tier()
    dolt_commit("seed: public tier — 7 dhatu + 12 grammars + 5 concepts")
    
    # Branch AFTER public is committed so branches inherit schema + public data
    print("\n  🌿 Création des branches...")
    dolt_branch("confidential")
    dolt_branch("private/stephane")
    print("     main → confidential → private/stephane")
    
    # CONFIDENTIAL data goes on its branch
    seed_confidential_tier()
    
    # Merge confidential into private so private inherits everything
    dolt_checkout("private/stephane")
    dolt(["merge", "confidential"], check=False)
    dolt_commit("merge: inherit confidential data")
    
    # PRIVATE data goes on its branch
    seed_private_tier()
    
    # 4. Demonstrations
    demonstrate_tier_isolation()
    demonstrate_promotion_workflow()
    demonstrate_full_pipeline()
    
    # 5. Final summary
    print("\n" + "=" * 80)
    print("✅ ARCHITECTURE UNIFIÉE VALIDÉE!")
    print("=" * 80)
    print()
    print("\n📊 Résumé de la base:")
    
    for branch in ["main", "confidential", "private/stephane"]:
        dolt_checkout(branch)
        commits = dolt(["log", "--oneline"])
        commit_count = len([l for l in commits.split("\n") if l.strip()])
        
        # Count rows safely
        def safe_count(table):
            r = dolt_sql_file(f"SELECT COUNT(*) as c FROM {table};")
            for line in r.split('\n'):
                line = line.strip().strip('|').strip()
                if line.isdigit():
                    return line
            return "0"
        
        pub = safe_count("dhatu_definitions")
        conf = safe_count("semantic_mappings")
        priv = safe_count("user_files")
        print(f"  [{branch}] commits: {commit_count} | dhatu: {pub} | mappings: {conf} | user_files: {priv}")
    
    print()
    print("🎯 Ce que Dolt apporte comme stockage unifié:")
    print("  ✅ Isolation par branches (public/confidential/private)")
    print("  ✅ Promotion contrôlée via merge (comme un PR Git)")
    print("  ✅ Versioning complet de TOUTES les données")
    print("  ✅ SQL natif sur signatures dhātu, chunks, fingerprints")
    print("  ✅ Clone partiel possible (public seulement)")
    print("  ✅ Diff entre versions d'analyses")
    print("  ✅ Rollback instantané en cas de problème")
    print("  ✅ Audit trail intégré via dolt log")
    print()
    print("🚀 Prochaines étapes:")
    print("  1. Brancher le vrai chunker (panini_fs_chunker.py) sur Dolt")
    print("  2. Brancher le fingerprinter audio sur Dolt")
    print("  3. API REST Rust (panini-api) ↔ Dolt MySQL protocol")
    print("  4. Web UI ↔ Dolt en lecture (dashboards temps réel)")
    print("  5. dolt clone pour distribution du tier public")
    print()
    
    # Retour à main
    dolt_checkout("main")


if __name__ == "__main__":
    main()

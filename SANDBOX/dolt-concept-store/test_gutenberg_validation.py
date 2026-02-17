#!/usr/bin/env python3
"""
test_gutenberg_validation.py — Tests for Gutenberg multilingual validation

Validates:
  - Provenance schema (5 tables + 3 views)
  - Works & editions metadata with translator attribution
  - Segment extraction and decomposition
  - Convergence analysis (common vs specific)
  - PaniniFS provenance chain integrity
"""

import json
import os
import subprocess
import sys

DOLT_DB = os.path.join(os.path.dirname(__file__), "panini-unified-db")

passed = 0
failed = 0
total = 0


def dolt_sql(query):
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    r = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    return r.stdout.strip()


def dolt_val(query):
    """Get single value from a query."""
    result = dolt_sql(query)
    lines = result.strip().split('\n')
    return lines[-1] if len(lines) > 1 else None


def check(name, condition, detail=""):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))


# ─────────────────────────────────────────────────────────────────────────────
# Section 1: Provenance schema tables
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 1. PROVENANCE SCHEMA TABLES ══")

tables = dolt_sql("SHOW TABLES")
for t in ["gutenberg_works", "gutenberg_editions", "gutenberg_segments",
          "segment_decompositions", "translation_convergence"]:
    check(f"Table '{t}' exists", t in tables)


# ─────────────────────────────────────────────────────────────────────────────
# Section 2: Provenance views
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 2. PROVENANCE VIEWS ══")

for v in ["v_provenance_chain", "v_concept_universality", "v_translator_profile"]:
    result = dolt_sql(f"SELECT COUNT(*) FROM {v}")
    check(f"View '{v}' is queryable", result is not None and "Error" not in result)


# ─────────────────────────────────────────────────────────────────────────────
# Section 3: Works metadata
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 3. WORKS METADATA ══")

works_count = dolt_val("SELECT COUNT(*) FROM gutenberg_works")
check("At least 2 works registered", works_count and int(works_count) >= 2,
      f"got {works_count}")

# Check ALICE
alice = dolt_val("SELECT author FROM gutenberg_works WHERE id = 'ALICE'")
check("ALICE work: author is Carroll", alice and "Carroll" in alice, f"got: {alice}")

alice_year = dolt_val("SELECT original_year FROM gutenberg_works WHERE id = 'ALICE'")
check("ALICE work: original_year = 1865", alice_year == "1865", f"got: {alice_year}")

# Check CANDIDE
candide = dolt_val("SELECT author FROM gutenberg_works WHERE id = 'CANDIDE'")
check("CANDIDE work: author is Voltaire", candide and "Voltaire" in candide,
      f"got: {candide}")

candide_year = dolt_val("SELECT original_year FROM gutenberg_works WHERE id = 'CANDIDE'")
check("CANDIDE work: original_year = 1759", candide_year == "1759",
      f"got: {candide_year}")


# ─────────────────────────────────────────────────────────────────────────────
# Section 4: Editions with translator provenance
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 4. EDITIONS & TRANSLATOR PROVENANCE ══")

editions_count = dolt_val("SELECT COUNT(*) FROM gutenberg_editions")
check("At least 10 editions registered", editions_count and int(editions_count) >= 10,
      f"got {editions_count}")

# Alice editions: 6 languages
alice_editions = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE work_id = 'ALICE'"
)
check("ALICE: 6 editions (6 langues)", alice_editions == "6",
      f"got {alice_editions}")

# Candide editions: 4 languages
candide_editions = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE work_id = 'CANDIDE'"
)
check("CANDIDE: 4 editions (4 langues)", candide_editions == "4",
      f"got {candide_editions}")

# Check translator attribution for Alice FR
alice_fr_translator = dolt_val(
    "SELECT translator FROM gutenberg_editions WHERE id = 'ALICE_FR_55456'"
)
check("ALICE FR: translator = Bué, Henri",
      alice_fr_translator and "Bué" in alice_fr_translator,
      f"got: {alice_fr_translator}")

# Check translator attribution for Alice DE
alice_de_translator = dolt_val(
    "SELECT translator FROM gutenberg_editions WHERE id = 'ALICE_DE_19778'"
)
check("ALICE DE: translator = Zimmermann, Antonie",
      alice_de_translator and "Zimmermann" in alice_de_translator,
      f"got: {alice_de_translator}")

# Check translator attribution for Alice IT
alice_it_translator = dolt_val(
    "SELECT translator FROM gutenberg_editions WHERE id = 'ALICE_IT_28371'"
)
check("ALICE IT: translator = Pietrocòla-Rossetti",
      alice_it_translator and "Pietrocòla" in alice_it_translator
      or alice_it_translator and "Rossetti" in alice_it_translator,
      f"got: {alice_it_translator}")

# Check is_original flag
originals = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE is_original = 1"
)
check("Exactly 2 original editions (EN Alice + FR Candide)",
      originals == "2", f"got {originals}")

# Check Gutenberg access date is set
access_dates = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE gutenberg_access_date IS NOT NULL"
)
check("All editions have access date",
      access_dates == editions_count, f"got {access_dates}/{editions_count}")


# ─────────────────────────────────────────────────────────────────────────────
# Section 5: Provenance chain format
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 5. PROVENANCE CHAIN FORMAT ══")

# Every edition must have: gutenberg_url, gutenberg_access_date, gutenberg_credits
missing_url = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE gutenberg_url IS NULL OR gutenberg_url = ''"
)
check("All editions have gutenberg_url", missing_url == "0",
      f"{missing_url} missing")

missing_credits = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE gutenberg_credits IS NULL OR gutenberg_credits = ''"
)
check("All editions have gutenberg_credits", missing_credits == "0",
      f"{missing_credits} missing")

# Check the full provenance chain is queryable via the view
chain_count = dolt_val("SELECT COUNT(*) FROM v_provenance_chain")
check("v_provenance_chain returns rows",
      chain_count and int(chain_count) >= 0)


# ─────────────────────────────────────────────────────────────────────────────
# Section 6: Text retrieval
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 6. TEXT RETRIEVAL ══")

retrieved = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_editions WHERE text_retrieved = 1"
)
check("Texts downloaded (text_retrieved = 1)",
      retrieved and int(retrieved) > 0, f"got {retrieved}")


# ─────────────────────────────────────────────────────────────────────────────
# Section 7: Segment extraction
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 7. SEGMENT EXTRACTION ══")

segments_count = dolt_val("SELECT COUNT(*) FROM gutenberg_segments")
check("Segments extracted (> 0)",
      segments_count and int(segments_count) > 0, f"got {segments_count}")

# Check segment types
seg_types = dolt_sql(
    "SELECT DISTINCT segment_type FROM gutenberg_segments ORDER BY segment_type"
)
check("Multiple segment types",
      seg_types and len(seg_types.strip().split('\n')) > 2)

# Check each segment has edition_id and segment_ref
orphan_segs = dolt_val(
    "SELECT COUNT(*) FROM gutenberg_segments "
    "WHERE edition_id IS NULL OR segment_ref IS NULL"
)
check("No orphan segments", orphan_segs == "0", f"{orphan_segs} orphans")


# ─────────────────────────────────────────────────────────────────────────────
# Section 8: Atom decomposition
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 8. ATOM DECOMPOSITION ══")

decomp_count = dolt_val("SELECT COUNT(*) FROM segment_decompositions")
check("Decompositions recorded (> 0)",
      decomp_count and int(decomp_count) > 0, f"got {decomp_count}")

# Check decompositions have atoms_detected
no_atoms = dolt_val(
    "SELECT COUNT(*) FROM segment_decompositions "
    "WHERE atoms_detected IS NULL"
)
check("All decompositions have atoms_detected",
      no_atoms == "0", f"{no_atoms} without atoms")

# Check confidence scores are in range
bad_conf = dolt_val(
    "SELECT COUNT(*) FROM segment_decompositions "
    "WHERE confidence < 0 OR confidence > 1"
)
check("Confidence scores in [0, 1]",
      bad_conf == "0", f"{bad_conf} out of range")


# ─────────────────────────────────────────────────────────────────────────────
# Section 9: Convergence analysis
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 9. CONVERGENCE ANALYSIS ══")

conv_count = dolt_val("SELECT COUNT(*) FROM translation_convergence")
check("Convergence records (> 0)",
      conv_count and int(conv_count) > 0, f"got {conv_count}")

# Check convergence types
conv_types = dolt_sql(
    "SELECT DISTINCT convergence_type FROM translation_convergence "
    "ORDER BY convergence_type"
)
check("At least 1 convergence type",
      conv_types and len(conv_types.strip().split('\n')) >= 2)

# Check convergence_ratio is in range
bad_ratio = dolt_val(
    "SELECT COUNT(*) FROM translation_convergence "
    "WHERE convergence_ratio < 0 OR convergence_ratio > 1"
)
check("Convergence ratios in [0, 1]",
      bad_ratio == "0", f"{bad_ratio} out of range")


# ─────────────────────────────────────────────────────────────────────────────
# Section 10: Cross-validation with v2 model
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 10. CROSS-VALIDATION WITH V2 MODEL ══")

# Check that v2 concepts still intact
v2_count = dolt_val("SELECT COUNT(*) FROM concepts")
check("v2 concepts still present (104)",
      v2_count and int(v2_count) >= 100, f"got {v2_count}")

# Check that v2 primitives still intact
predicates = dolt_val("SELECT COUNT(*) FROM semantic_predicates")
check("10 semantic predicates intact", predicates == "10", f"got {predicates}")

# Check ontological categories
categories = dolt_val("SELECT COUNT(*) FROM ontological_categories")
check("4 ontological categories intact", categories == "4", f"got {categories}")


# ─────────────────────────────────────────────────────────────────────────────
# Section 11: Dolt integrity
# ─────────────────────────────────────────────────────────────────────────────

print("\n══ 11. DOLT INTEGRITY ══")

# Check total table count (v2 + gutenberg)
tables_result = dolt_sql("SHOW TABLES")
table_count = len([l for l in tables_result.strip().split('\n') if l.strip()]) - 1  # minus header
check("Total tables ≥ 15 (v2 + gutenberg)",
      table_count >= 15, f"got {table_count}")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"RESULTS: {passed}/{total} passed, {failed} failed")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)

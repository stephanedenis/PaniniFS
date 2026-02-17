#!/usr/bin/env python3
"""
test_v2_validation.py — Tests de validation pour le schéma v2 et l'import PanLang
Vérifie l'intégrité structurelle, la cohérence des données, et la couverture dimensionnelle.
"""
import subprocess
import json
import sys
import os

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panini-unified-db")
PASSED = 0
FAILED = 0
TOTAL = 0


def dolt_sql(query: str) -> str:
    """Exécute une requête Dolt et renvoie le résultat CSV."""
    result = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        cwd=DB_DIR,
        capture_output=True, text=True,
        env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
    )
    if result.returncode != 0:
        raise RuntimeError(f"Dolt SQL error: {result.stderr.strip()}")
    return result.stdout.strip()


def dolt_sql_value(query: str):
    """Exécute une requête Dolt et renvoie la première valeur."""
    out = dolt_sql(query)
    lines = out.strip().split("\n")
    if len(lines) < 2:
        return None
    return lines[1].strip().strip('"')


def test(name: str, condition: bool, detail: str = ""):
    """Enregistre un résultat de test."""
    global PASSED, FAILED, TOTAL
    TOTAL += 1
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name} — {detail}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 1 : Tables existence & row counts
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 1 : Tables et comptages")
print("=" * 70)

# Ontological categories
n_onto = int(dolt_sql_value("SELECT COUNT(*) FROM ontological_categories"))
test("ontological_categories = 4 rows", n_onto == 4, f"got {n_onto}")

# Structural operations
n_struct = int(dolt_sql_value("SELECT COUNT(*) FROM structural_operations"))
test("structural_operations = 5 rows", n_struct == 5, f"got {n_struct}")

# Semantic predicates
n_pred = int(dolt_sql_value("SELECT COUNT(*) FROM semantic_predicates"))
test("semantic_predicates = 10 rows", n_pred == 10, f"got {n_pred}")

# Nonverbal extensions
n_ext = int(dolt_sql_value("SELECT COUNT(*) FROM nonverbal_extensions"))
test("nonverbal_extensions = 4 rows", n_ext == 4, f"got {n_ext}")

# Concepts — should be 107
n_concepts = int(dolt_sql_value("SELECT COUNT(*) FROM concepts"))
test("concepts = 107 rows", n_concepts == 107, f"got {n_concepts}")

# Composition rules — at least 1 per concept
n_rules = int(dolt_sql_value("SELECT COUNT(*) FROM composition_rules"))
test("composition_rules >= 107", n_rules >= 107, f"got {n_rules}")

# Dimension coverage — at least 1 per concept
n_dim = int(dolt_sql_value("SELECT COUNT(*) FROM dimension_coverage"))
test("dimension_coverage >= 107", n_dim >= 107, f"got {n_dim}")

# Quality audit
n_audit = int(dolt_sql_value("SELECT COUNT(*) FROM quality_audit"))
test("quality_audit has entries", n_audit > 0, f"got {n_audit}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 2 : 23 Primitives — Layer coverage
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 2 : 23 primitifs en 3 couches")
print("=" * 70)

# Layer 1: Ontological (4)
onto_ids = dolt_sql_value("SELECT GROUP_CONCAT(id ORDER BY id) FROM ontological_categories")
test("Layer 1 ontological IDs = ABS,ENT,PROC,QUAL",
     onto_ids == "ABS,ENT,PROC,QUAL",
     f"got {onto_ids}")

# Layer 2: Structural (5)
struct_ids = dolt_sql_value("SELECT GROUP_CONCAT(id ORDER BY id) FROM structural_operations")
test("Layer 2 structural IDs = COMP,ID,MOD,NEG,QUANT",
     struct_ids == "COMP,ID,MOD,NEG,QUANT",
     f"got {struct_ids}")

# Layer 3a: Semantic predicates (10)
pred_ids = dolt_sql_value("SELECT GROUP_CONCAT(id ORDER BY id) FROM semantic_predicates")
expected_preds = "COGNITION,COMMUNICATION,CREATION,DESTRUCTION,DOMINATION,EMOTION,EXISTENCE,MOUVEMENT,PERCEPTION,POSSESSION"
test("Layer 3a semantic predicate IDs correct",
     pred_ids == expected_preds,
     f"got {pred_ids}")

# Layer 3b: Nonverbal extensions (4)
ext_ids = dolt_sql_value("SELECT GROUP_CONCAT(id ORDER BY id) FROM nonverbal_extensions")
test("Layer 3b nonverbal IDs = ESPACE,EVAL,TAXO,TEMPS",
     ext_ids == "ESPACE,EVAL,TAXO,TEMPS",
     f"got {ext_ids}")

# Total primitives = 4 + 5 + 10 + 4 = 23
total_prims = n_onto + n_struct + n_pred + n_ext
test("Total primitives = 23", total_prims == 23, f"got {total_prims}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 3 : Quality tiers distribution
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 3 : Distribution des tiers de qualité")
print("=" * 70)

n_a = int(dolt_sql_value("SELECT COUNT(*) FROM concepts WHERE quality_tier = 'A'"))
n_b = int(dolt_sql_value("SELECT COUNT(*) FROM concepts WHERE quality_tier = 'B'"))
n_c = int(dolt_sql_value("SELECT COUNT(*) FROM concepts WHERE quality_tier = 'C'"))

test("Tier A ≥ 40", n_a >= 40, f"got {n_a}")
test("Tier B ≥ 30", n_b >= 30, f"got {n_b}")
test("Tier C ≤ 20 (problematic)", n_c <= 20, f"got {n_c}")
test("A + B + C = 107", n_a + n_b + n_c == 107, f"got {n_a + n_b + n_c}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 4 : Composition rules integrity
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 4 : Intégrité des règles de composition")
print("=" * 70)

# Every concept must have at least 1 composition rule
concepts_without_rules = int(dolt_sql_value("""
    SELECT COUNT(*) FROM concepts c
    LEFT JOIN composition_rules cr ON c.id = cr.concept_id
    WHERE cr.concept_id IS NULL
"""))
test("All concepts have composition rules",
     concepts_without_rules == 0,
     f"{concepts_without_rules} concepts sans règles")

# Every atom in composition_rules must reference a valid semantic predicate
invalid_atoms = int(dolt_sql_value("""
    SELECT COUNT(*) FROM composition_rules cr
    LEFT JOIN semantic_predicates sp ON cr.atom_id = sp.id
    WHERE sp.id IS NULL
"""))
test("All composition rule atoms are valid predicates",
     invalid_atoms == 0,
     f"{invalid_atoms} invalid atom references")

# Atom count in concepts matches actual composition rules count
mismatched = dolt_sql_value("""
    SELECT COUNT(*) FROM (
        SELECT c.id, c.atom_count, COUNT(cr.atom_id) as actual
        FROM concepts c
        JOIN composition_rules cr ON c.id = cr.concept_id
        GROUP BY c.id, c.atom_count
        HAVING c.atom_count != actual
    ) t
""")
test("atom_count matches actual composition rules",
     int(mismatched) == 0,
     f"{mismatched} mismatches")


# ═══════════════════════════════════════════════════════════════════
# SECTION 5 : Dimension coverage
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 5 : Couverture dimensionnelle")
print("=" * 70)

# All 7 irreducible dimensions should appear
dims_present = dolt_sql_value("""
    SELECT COUNT(DISTINCT dimension) FROM dimension_coverage
""")
test("Dimensions covered (expecting at least 3)",
     int(dims_present) >= 3,
     f"got {dims_present}")

# PanLang covers mainly PROCESSUS — check it's the largest
processus_count = int(dolt_sql_value("""
    SELECT COUNT(*) FROM dimension_coverage WHERE dimension = 'PROCESSUS'
"""))
test("PROCESSUS is dominant dimension",
     processus_count > 50,
     f"got {processus_count}")

# STRUCTURE and SITUATION should be absent (gap = PanLang limitation)
structure_count = int(dolt_sql_value("""
    SELECT COUNT(*) FROM dimension_coverage WHERE dimension = 'STRUCTURE'
"""))
situation_count = int(dolt_sql_value("""
    SELECT COUNT(*) FROM dimension_coverage WHERE dimension = 'SITUATION'
"""))
test("STRUCTURE dimension = 0 (known gap)",
     structure_count == 0,
     f"got {structure_count}")
test("SITUATION dimension = 0 (known gap)",
     situation_count == 0,
     f"got {situation_count}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 6 : Audit trail
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 6 : Piste d'audit")
print("=" * 70)

# Known problematic concepts must be flagged
etoile_audit = int(dolt_sql_value("""
    SELECT COUNT(*) FROM quality_audit
    WHERE concept_id = 'ÉTOILE' AND issue_type = 'tautology'
"""))
test("ÉTOILE flagged as tautology", etoile_audit > 0, "not found in audit")

musique_audit = int(dolt_sql_value("""
    SELECT COUNT(*) FROM quality_audit
    WHERE concept_id = 'MUSIQUE' AND issue_type = 'absurd_formula'
"""))
test("MUSIQUE flagged as absurd", musique_audit > 0, "not found in audit")

recit_audit = int(dolt_sql_value("""
    SELECT COUNT(*) FROM quality_audit
    WHERE concept_id = 'RÉCIT' AND issue_type IN ('tautology', 'absurd_formula')
"""))
test("RÉCIT flagged as problematic", recit_audit > 0, "not found in audit")

# Low validity concepts should be in audit
low_validity_count = int(dolt_sql_value("""
    SELECT COUNT(*) FROM quality_audit WHERE issue_type = 'low_validity'
"""))
test("Low validity issues logged", low_validity_count >= 10, f"got {low_validity_count}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 7 : Exclusion correctness
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 7 : Exclusion des métadonnées")
print("=" * 70)

# Metadata concepts must NOT be in the database
metadata_leaks = dolt_sql("""
    SELECT id FROM concepts
    WHERE id IN (
        'TITRE', 'DESCRIPTION', 'METHODOLOGIE', 'CONCLUSION',
        'TIMESTAMP', 'STATUS', 'BASE_DONNEES',
        'ARCHITECTURE_SEMANTIQUE', 'STATISTIQUES_INTEGRATION',
        'GUIDE_UTILISATION', 'REPRODUCTIBILITE',
        'CONCEPTS_ECHANTILLON', 'DICTIONNAIRE_UNIFIE'
    )
""")
lines = metadata_leaks.strip().split("\n")
has_leaks = len(lines) > 1  # header only = no leaks
test("No metadata concepts leaked into DB",
     not has_leaks,
     f"leaked: {lines[1:]}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 8 : Dolt-specific checks
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 8 : Vérifications Dolt")
print("=" * 70)

# Check Dolt log has v2 commit
dolt_log = subprocess.run(
    ["dolt", "log", "--oneline", "-n", "5"],
    cwd=DB_DIR, capture_output=True, text=True,
    env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
)
has_v2_commit = "v2" in dolt_log.stdout.lower() or "3-layer" in dolt_log.stdout.lower()
test("Dolt log contains v2 commit", has_v2_commit, f"log: {dolt_log.stdout[:200]}")

# Check no uncommitted changes
dolt_status = subprocess.run(
    ["dolt", "status"],
    cwd=DB_DIR, capture_output=True, text=True,
    env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
)
is_clean = "clean" in dolt_status.stdout.lower() or "nothing to commit" in dolt_status.stdout.lower()
test("Dolt working tree is clean", is_clean, f"status: {dolt_status.stdout[:200]}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 9 : Semantic predicates metadata
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 9 : Métadonnées des prédicats sémantiques")
print("=" * 70)

# MOUVEMENT must have dhatu √gam
mouv_dhatu = dolt_sql_value("SELECT dhatu_sa FROM semantic_predicates WHERE id = 'MOUVEMENT'")
test("MOUVEMENT.dhatu_sa = √gam", mouv_dhatu == "√gam", f"got {mouv_dhatu}")

# COGNITION must have dhatu √jñā
cog_dhatu = dolt_sql_value("SELECT dhatu_sa FROM semantic_predicates WHERE id = 'COGNITION'")
test("COGNITION.dhatu_sa = √jñā", cog_dhatu == "√jñā", f"got {cog_dhatu}")

# CREATION must have vendler aspect accomplishment
cre_vendler = dolt_sql_value("SELECT vendler_aspect FROM semantic_predicates WHERE id = 'CREATION'")
test("CREATION.vendler = accomplishment", cre_vendler == "accomplishment", f"got {cre_vendler}")

# MOUVEMENT must have ontological_category = PROC
mouv_onto = dolt_sql_value("SELECT ontological_category FROM semantic_predicates WHERE id = 'MOUVEMENT'")
test("MOUVEMENT.ontological_category = PROC", mouv_onto == "PROC", f"got {mouv_onto}")


# ═══════════════════════════════════════════════════════════════════
# SECTION 10 : Views functionality
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SECTION 10 : Vues fonctionnelles")
print("=" * 70)

# v_atom_distribution
atom_dist = dolt_sql("SELECT * FROM v_atom_distribution ORDER BY usage_count DESC LIMIT 3")
test("v_atom_distribution returns data", len(atom_dist.split("\n")) > 1, "empty")

# v_quality_summary
qual_sum = dolt_sql("SELECT * FROM v_quality_summary")
test("v_quality_summary returns data", len(qual_sum.split("\n")) > 1, "empty")

# v_problematic_concepts
prob = dolt_sql("SELECT * FROM v_problematic_concepts LIMIT 5")
test("v_problematic_concepts returns data", len(prob.split("\n")) > 1, "empty")


# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print(f"  RÉSULTAT : {PASSED}/{TOTAL} tests passés", end="")
if FAILED > 0:
    print(f" ({FAILED} échecs)")
else:
    print(" — 🎉 TOUS PASSÉS")
print("═" * 70)

sys.exit(0 if FAILED == 0 else 1)

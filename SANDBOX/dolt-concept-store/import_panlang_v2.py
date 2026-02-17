#!/usr/bin/env python3
"""
import_panlang_v2.py — Import PanLang ULTIME → Dolt with v2 schema (3-layer universals)

Based on:
  - UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md (72 references)
  - Quality audit (Phase 17): 107 real concepts, 48 fake/metadata excluded
  - schema_v2_universals.sql: 3-layer architecture

Workflow:
  1. Seed ontological categories (4: ENT, PROC, QUAL, ABS)
  2. Seed structural operations (5: COMP, ID, NEG, QUANT, MOD)
  3. Seed semantic predicates (10 dhātu PanLang)
  4. Seed nonverbal extensions (4: ESPACE, TEMPS, EVAL, TAXO)
  5. Load PanLang ULTIME JSON → clean → classify → import 107 concepts
  6. Compute dimension coverage for each concept
  7. Log quality audit issues
  8. Commit to Dolt
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

PANLANG_JSON = os.path.expanduser(
    "~/GitHub/Panini-Research/panlang/current/"
    "dictionnaire_panlang_ULTIME/dictionnaire_panlang_ULTIME_complet.json"
)
DOLT_DB = os.path.join(os.path.dirname(__file__), "panini-unified-db")
SCHEMA_SQL = os.path.join(os.path.dirname(__file__), "schema_v2_universals.sql")

# 48 metadata/fake concept keys to exclude
EXCLUDED_CONCEPTS = {
    # 7 plain-string metadata
    "TITRE", "DESCRIPTION", "METHODOLOGIE", "CONCLUSION",
    "TIMESTAMP", "STATUS", "BASE_DONNEES",
    # 13 mega-containers
    "CONCEPTS_ECHANTILLON", "DICTIONNAIRE_UNIFIE", "DICTIONNAIRE_RECURSIF",
    "NARRATIF_GENERAL", "ACTION_DURATIVE", "EVALUATION_QUALITATIVE",
    "CONTEXTE_TEMPOREL", "RELATION_CAUSALE", "OUVERTURE_CONTE",
    "CONTEXTE_OUVERTURE", "CONTEXTE_NARRATIF", "CONTEXTE_ACTION",
    "CONTEXTE_TRANSFORMATION",
    # 28 metadata dicts without formule_simple
    "ARCHITECTURE_SEMANTIQUE", "STATISTIQUES_INTEGRATION",
    "GUIDE_UTILISATION", "REPRODUCTIBILITE", "ATOMES_UNIVERSELS",
    "RECONSTRUCTIONS_VALIDEES", "COMPLETUDE_UNIVERSELLE",
    "IMPLICATIONS_MAJEURES", "METRIQUES_CONVERGENCE",
    "CONCEPTS_NON_DEFINIS_ANALYSE", "IMPLICATIONS_PANLANG",
    "CONTEXTE_QUALITE", "CONTEXTE_JUGEMENT", "CONTEXTE_DIALOGUE",
    "CONTEXTE_NARRATION", "CONTEXTE_SPATIAL",
    "TEST_1_FR", "TEST_2_EN", "TEST_3_DE",
    "PERFORMANCE", "QUALITE_RESOLUTION", "IMPACT_DICTIONNAIRE",
    "CONCEPTS_INTEGRES", "INTEGRATION_SUMMARY", "DETAILED_RESULTS",
    "TRIPARTITE_PERFORMANCE", "DOMAINES", "LANGUES",
}

# The 10 atoms
ATOMS = {
    "MOUVEMENT", "COGNITION", "PERCEPTION", "COMMUNICATION",
    "CREATION", "EMOTION", "EXISTENCE", "DESTRUCTION",
    "POSSESSION", "DOMINATION",
}

# Atom → dimension mapping (from the literature review § 11.3)
ATOM_DIMENSIONS = {
    "MOUVEMENT":      {"PROCESSUS": 1.0},
    "COGNITION":      {"PROCESSUS": 0.7, "QUALITÉ": 0.3},
    "PERCEPTION":     {"PROCESSUS": 0.5, "QUALITÉ": 0.5},
    "COMMUNICATION":  {"PROCESSUS": 0.6, "RELATION": 0.4},
    "CREATION":       {"PROCESSUS": 1.0},
    "EMOTION":        {"QUALITÉ": 0.7, "PROCESSUS": 0.3},
    "EXISTENCE":      {"ENTITÉ": 0.6, "PROCESSUS": 0.4},
    "DESTRUCTION":    {"PROCESSUS": 1.0},
    "POSSESSION":     {"RELATION": 0.7, "PROCESSUS": 0.3},
    "DOMINATION":     {"MODALITÉ": 0.6, "RELATION": 0.4},
}

# Atom → NSM prime mapping
ATOM_NSM = {
    "MOUVEMENT":      ["MOVE"],
    "COGNITION":      ["THINK", "KNOW"],
    "PERCEPTION":     ["SEE", "HEAR"],
    "COMMUNICATION":  ["SAY"],
    "CREATION":       ["DO", "HAPPEN"],
    "EMOTION":        ["FEEL"],
    "EXISTENCE":      ["EXIST", "THERE IS"],
    "DESTRUCTION":    ["DIE"],
    "POSSESSION":     ["HAVE"],
    "DOMINATION":     ["WANT", "CAN"],
}

# Atom → Jackendoff mapping
ATOM_JACKENDOFF = {
    "MOUVEMENT":      "GO",
    "COGNITION":      None,
    "PERCEPTION":     None,
    "COMMUNICATION":  None,
    "CREATION":       "CAUSE",
    "EMOTION":        None,
    "EXISTENCE":      "BE",
    "DESTRUCTION":    None,
    "POSSESSION":     None,
    "DOMINATION":     None,
}

# Atom → Pustejovsky quale
ATOM_PUSTEJOVSKY = {
    "MOUVEMENT":      "AGENTIVE",
    "COGNITION":      "FORMAL",
    "PERCEPTION":     "FORMAL",
    "COMMUNICATION":  "TELIC",
    "CREATION":       "AGENTIVE",
    "EMOTION":        "FORMAL",
    "EXISTENCE":      "FORMAL",
    "DESTRUCTION":    "AGENTIVE",
    "POSSESSION":     "CONSTITUTIVE",
    "DOMINATION":     "TELIC",
}

# Atom → Dhātu sanskrit
ATOM_DHATU = {
    "MOUVEMENT":      "√gam",
    "COGNITION":      "√jñā",
    "PERCEPTION":     "√dṛś",
    "COMMUNICATION":  "√vac",
    "CREATION":       "√kṛ",
    "EMOTION":        "√hṛd",
    "EXISTENCE":      "√as",
    "DESTRUCTION":    None,
    "POSSESSION":     "√labh",
    "DOMINATION":     "√īś",
}

# Duplicate formulas (same formule_simple for different concepts)
KNOWN_DUPLICATES = {
    # These map to the same simple formula — flagged as issues
    "ÉTOILE":       "COMMUNICATION",        # ÉTOILE = COMMUNICATION (tautology)
    "FENÊTRE":      "EXISTENCE",            # FENÊTRE = EXISTENCE (tautology)
    "LIEU":         "MOUVEMENT",            # LIEU = MOUVEMENT (tautology)
    "ARBRE":        "MOUVEMENT",            # ARBRE = MOUVEMENT (tautology)
    "DÉGOÛT":       "EXISTENCE",            # DÉGOÛT = EXISTENCE (tautology)
    "BEAU":         "EXISTENCE",            # BEAU = EXISTENCE (tautology)
    "GOÛTER":       "MOUVEMENT",            # GOÛTER = MOUVEMENT (tautology)
    "SATISFACTION": "MOUVEMENT",            # SATISFACTION = MOUVEMENT (tautology)
    "IMAGINER":     "POSSESSION",           # IMAGINER = POSSESSION (tautology)
    "RÉCIT":        "DESTRUCTION",          # RÉCIT = DESTRUCTION (tautology)
    "SENTIR":       "PERCEPTION",           # SENTIR = PERCEPTION (tautology)
}


# ─────────────────────────────────────────────────────────────────────────────
# Dolt helpers
# ─────────────────────────────────────────────────────────────────────────────

def dolt(*args, check=True):
    """Run a dolt CLI command in the DB directory."""
    cmd = ["dolt"] + list(args)
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    result = subprocess.run(
        cmd, cwd=DOLT_DB, capture_output=True, text=True, env=env
    )
    if check and result.returncode != 0:
        print(f"  ❌ dolt {' '.join(args[:3])}... failed:")
        print(f"     {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def dolt_sql(query, check=True):
    """Execute a SQL query via dolt sql."""
    return dolt("sql", "-r", "csv", "-q", query, check=check)


def dolt_sql_batch(queries):
    """Execute multiple SQL statements via dolt sql."""
    combined = "\n".join(queries)
    cmd = ["dolt", "sql"]
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    result = subprocess.run(
        cmd, cwd=DOLT_DB, input=combined, capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"  ❌ SQL batch failed: {result.stderr.strip()[:300]}")
        return False
    return True


def escape_sql(s):
    """Escape single quotes for SQL."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''").replace("\\", "\\\\") + "'"


def json_sql(obj):
    """Convert a Python object to a SQL JSON string."""
    if obj is None:
        return "NULL"
    return escape_sql(json.dumps(obj, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────────────────────
# Step 0: Init Dolt DB
# ─────────────────────────────────────────────────────────────────────────────

def init_dolt_db():
    """Ensure Dolt DB exists, create branch if needed."""
    print("=" * 70)
    print("STEP 0: Initialize Dolt DB")
    print("=" * 70)

    if not os.path.isdir(os.path.join(DOLT_DB, ".dolt")):
        print(f"  Creating Dolt DB at {DOLT_DB}")
        os.makedirs(DOLT_DB, exist_ok=True)
        subprocess.run(["dolt", "init"], cwd=DOLT_DB, check=True,
                        capture_output=True, text=True)

    # Apply schema
    print("  Applying schema_v2_universals.sql...")
    with open(SCHEMA_SQL) as f:
        schema = f.read()

    # Split on CREATE and execute each separately (Dolt doesn't handle
    # all statements in one batch well with views)
    stmts = []
    current = []
    for line in schema.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--") or stripped == "":
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmts.append("\n".join(current))
            current = []

    success = 0
    for stmt in stmts:
        result = dolt_sql(stmt, check=False)
        if result is not None:
            success += 1
        # Views may fail on first creation due to Dolt quirks, that's ok

    print(f"  ✅ Applied {success}/{len(stmts)} SQL statements")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Seed ontological categories
# ─────────────────────────────────────────────────────────────────────────────

def seed_ontological_categories():
    """Insert the 4 meta-categories from DOLCE/BFO/SUMO convergence."""
    print("\n" + "=" * 70)
    print("STEP 1: Seed ontological categories (4)")
    print("=" * 70)

    categories = [
        ("ENT", "Entité", "Entity", "dravya",
         "Ce qui persiste dans le temps — substances, objets, lieux",
         "Endurant", "Continuant", "Object",
         ["personne", "arbre", "pierre", "lieu", "outil"]),
        ("PROC", "Processus", "Process", "kriyā",
         "Ce qui se déploie dans le temps — événements, actions, changements",
         "Perdurant", "Occurrent", "Process",
         ["marcher", "penser", "brûler", "naître", "mourir"]),
        ("QUAL", "Qualité", "Quality", "guṇa",
         "Ce qui caractérise — propriétés, attributs, intensités",
         "Quality", "Specifically Dependent Continuant", "Attribute",
         ["rouge", "grand", "rapide", "doux", "bon"]),
        ("ABS", "Abstraction", "Abstract", "sāmānya",
         "Ce qui n'a pas de localisation spatio-temporelle — nombres, propositions, relations",
         "Abstract", "Generically Dependent Continuant", "Abstract",
         ["nombre", "relation", "catégorie", "proposition", "ensemble"]),
    ]

    queries = []
    for cat_id, fr, en, sa, desc, dolce, bfo, sumo, examples in categories:
        queries.append(
            f"REPLACE INTO ontological_categories "
            f"(id, name_fr, name_en, name_sa, description, dolce_equiv, bfo_equiv, sumo_equiv, examples) "
            f"VALUES ({escape_sql(cat_id)}, {escape_sql(fr)}, {escape_sql(en)}, {escape_sql(sa)}, "
            f"{escape_sql(desc)}, {escape_sql(dolce)}, {escape_sql(bfo)}, {escape_sql(sumo)}, "
            f"{json_sql(examples)});"
        )

    if dolt_sql_batch(queries):
        print(f"  ✅ Inserted 4 ontological categories: ENT, PROC, QUAL, ABS")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Seed structural operations
# ─────────────────────────────────────────────────────────────────────────────

def seed_structural_operations():
    """Insert the 5 structural operations from category theory/logic/computation."""
    print("\n" + "=" * 70)
    print("STEP 2: Seed structural operations (5)")
    print("=" * 70)

    ops = [
        ("COMP", "Composition", "Composition",
         "Combiner deux éléments en un tout structuré",
         "composition ∘", "conjunction ∧", "S combinator / λ-abstraction", None,
         2, "(concept, concept, mode) → concept"),
        ("ID", "Identité", "Identity",
         "Reconnaître la mêmeté — ce qui ne change pas",
         "identity morphism id", "tautology ⊤", "I combinator", "SAME",
         1, "(concept) → concept"),
        ("NEG", "Négation", "Negation",
         "Nier, exclure, marquer l'absence",
         "initial object ∅", "negation ¬", "bottom ⊥ / Nothing", "NOT",
         1, "(concept) → concept"),
        ("QUANT", "Quantification", "Quantification",
         "Dénombrer, mesurer — un, tous, quelques, beaucoup",
         "limits / colimits", "∀ / ∃", "recursion / fold", "ONE, TWO, SOME, ALL, MUCH~MANY",
         2, "(quantifier, concept) → concept"),
        ("MOD", "Modalité", "Modality",
         "Possibilité, nécessité, volonté, permission",
         "subobject classifier Ω", "□ / ◇ (modal logic)", "Maybe / Option type", "CAN, MAYBE",
         2, "(mode, concept) → concept"),
    ]

    queries = []
    for op_id, fr, en, desc, cat, logic, comp, nsm, arity, sig in ops:
        queries.append(
            f"REPLACE INTO structural_operations "
            f"(id, name_fr, name_en, description, category_theory_equiv, logic_equiv, "
            f"computation_equiv, nsm_equiv, arity, signature) "
            f"VALUES ({escape_sql(op_id)}, {escape_sql(fr)}, {escape_sql(en)}, "
            f"{escape_sql(desc)}, {escape_sql(cat)}, {escape_sql(logic)}, "
            f"{escape_sql(comp)}, {escape_sql(nsm)}, {arity}, {escape_sql(sig)});"
        )

    if dolt_sql_batch(queries):
        print(f"  ✅ Inserted 5 structural operations: COMP, ID, NEG, QUANT, MOD")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Seed semantic predicates (10 dhātu)
# ─────────────────────────────────────────────────────────────────────────────

def seed_semantic_predicates():
    """Insert the 10 dhātu-based semantic predicates."""
    print("\n" + "=" * 70)
    print("STEP 3: Seed semantic predicates — 10 dhātu (layer 3)")
    print("=" * 70)

    predicates = [
        ("MOUVEMENT", "MOV", "Mouvement", "Movement", "√gam",
         "Déplacement, changement de lieu, transition, flux",
         "PROC", ["MOVE"], "GO", None, "activity"),
        ("COGNITION", "COG", "Cognition", "Cognition", "√jñā",
         "Pensée, raisonnement, compréhension, décision",
         "PROC", ["THINK", "KNOW"], None, None, "state"),
        ("PERCEPTION", "PER", "Perception", "Perception", "√dṛś",
         "Observation, évaluation sensorielle, détection",
         "PROC", ["SEE", "HEAR"], None, None, "achievement"),
        ("COMMUNICATION", "COM", "Communication", "Communication", "√vac",
         "Parole, échange, transmission de sens",
         "PROC", ["SAY"], None, ["Verbs of Communication"], "activity"),
        ("CREATION", "CRE", "Création", "Creation", "√kṛ",
         "Fabrication, causation, mise en existence",
         "PROC", ["DO", "HAPPEN"], "CAUSE", ["Verbs of Creation"], "accomplishment"),
        ("EMOTION", "EMO", "Émotion", "Emotion", "√hṛd",
         "Affect, sentiment, réaction émotionnelle",
         "PROC", ["FEEL"], None, ["Psych-verbs (Experiencer)"], "state"),
        ("EXISTENCE", "EXI", "Existence", "Existence", "√as",
         "Être, présence, subsistance, identité",
         "PROC", ["EXIST", "THERE IS"], "BE", None, "state"),
        ("DESTRUCTION", "DES", "Destruction", "Destruction", None,
         "Fin, annihilation, dissolution, disparition",
         "PROC", ["DIE"], None, ["Verbs of Killing", "Verbs of Breaking"], "achievement"),
        ("POSSESSION", "POS", "Possession", "Possession", "√labh",
         "Avoir, détenir, relation d'appartenance",
         "PROC", ["HAVE"], None, ["Verbs of Obtaining"], "state"),
        ("DOMINATION", "VOL", "Volition/Domination", "Volition/Domination", "√īś",
         "Pouvoir, vouloir, contrôle, modalité déontique — renommé pour mieux couvrir WANT",
         "PROC", ["WANT", "CAN"], None, None, "state"),
    ]

    queries = []
    for pid, code, fr, en, dhatu, desc, cat, nsm, jack, levin, vendler in predicates:
        queries.append(
            f"REPLACE INTO semantic_predicates "
            f"(id, code, name_fr, name_en, dhatu_sa, description, "
            f"ontological_category, nsm_mapping, jackendoff_mapping, "
            f"levin_classes, pustejovsky_quale, vendler_aspect) "
            f"VALUES ({escape_sql(pid)}, {escape_sql(code)}, {escape_sql(fr)}, "
            f"{escape_sql(en)}, {escape_sql(dhatu)}, {escape_sql(desc)}, "
            f"{escape_sql(cat)}, {json_sql(nsm)}, {escape_sql(jack)}, "
            f"{json_sql(levin)}, {escape_sql(ATOM_PUSTEJOVSKY.get(pid))}, "
            f"{escape_sql(vendler)});"
        )

    if dolt_sql_batch(queries):
        print(f"  ✅ Inserted 10 semantic predicates (dhātu)")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Seed nonverbal extensions
# ─────────────────────────────────────────────────────────────────────────────

def seed_nonverbal_extensions():
    """Insert the 4 nonverbal extensions from NSM/BFO gaps."""
    print("\n" + "=" * 70)
    print("STEP 4: Seed nonverbal extensions (4)")
    print("=" * 70)

    extensions = [
        ("ESPACE", "Espace", "Space",
         "Localisation, direction, distance, contenance",
         "ABS", ["WHERE", "HERE", "ABOVE", "BELOW", "FAR", "NEAR", "INSIDE"], "SITUATION"),
        ("TEMPS", "Temps", "Time",
         "Temporalité, séquence, durée, fréquence",
         "ABS", ["WHEN", "NOW", "BEFORE", "AFTER", "A LONG TIME", "A SHORT TIME"], "SITUATION"),
        ("EVAL", "Évaluation", "Evaluation",
         "Jugement de valeur, bon/mauvais, beau/laid",
         "QUAL", ["GOOD", "BAD"], "QUALITÉ"),
        ("TAXO", "Taxonomie", "Taxonomy",
         "Classification, inclusion, partie-tout, hiérarchie",
         "ABS", ["KIND OF", "PART OF"], "RELATION"),
    ]

    queries = []
    for ext_id, fr, en, desc, cat, nsm, dim in extensions:
        queries.append(
            f"REPLACE INTO nonverbal_extensions "
            f"(id, name_fr, name_en, description, ontological_category, nsm_mapping, dimension) "
            f"VALUES ({escape_sql(ext_id)}, {escape_sql(fr)}, {escape_sql(en)}, "
            f"{escape_sql(desc)}, {escape_sql(cat)}, {json_sql(nsm)}, {escape_sql(dim)});"
        )

    if dolt_sql_batch(queries):
        print(f"  ✅ Inserted 4 nonverbal extensions: ESPACE, TEMPS, EVAL, TAXO")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Load, clean, classify, import concepts
# ─────────────────────────────────────────────────────────────────────────────

def parse_formule(raw_formule):
    """Parse a PanLang formule field (dict-string or plain string) → (atoms, formule_simple, format)."""
    if not isinstance(raw_formule, str):
        return None, None, None

    # Try parsing as Python dict literal
    try:
        parsed = ast.literal_eval(raw_formule)
        if isinstance(parsed, dict) and "formule_simple" in parsed:
            formule_simple = parsed["formule_simple"]
            atoms = [a.strip() for a in formule_simple.split("+")]
            return atoms, formule_simple, "dict"
    except (ValueError, SyntaxError):
        pass

    # Try as plain formula: "ATOM + ATOM + ..."
    parts = [p.strip() for p in raw_formule.split("+")]
    if all(p in ATOMS for p in parts) and len(parts) >= 1:
        return parts, raw_formule.strip(), "plain"

    return None, None, None


def classify_quality(concept_name, atoms, validity, formule_simple):
    """Classify concept quality: A (excellent), B (acceptable), C (problematic)."""
    issues = []

    # Tautology: concept = single atom identical to itself
    if concept_name in KNOWN_DUPLICATES:
        issues.append("tautology")

    # Very low validity
    if validity is not None and validity < 0.3:
        issues.append("low_validity")

    # Absurd formula (subjective, but catch obvious ones)
    absurd_combos = {
        ("MUSIQUE", "DESTRUCTION + MOUVEMENT"),
        ("RÉCIT", "DESTRUCTION"),
        ("ÉTOILE", "COMMUNICATION"),
    }
    if (concept_name, formule_simple) in absurd_combos:
        issues.append("absurd_formula")

    # Single-atom concept that is NOT itself an atom definition
    if len(atoms) == 1 and concept_name not in ATOMS:
        issues.append("tautology")

    if not issues:
        if validity is not None and validity >= 0.6:
            return "A", issues
        elif validity is not None and validity >= 0.4:
            return "B", issues
        else:
            return "B", issues  # No validity = default B
    elif "absurd_formula" in issues or "low_validity" in issues:
        return "C", issues
    else:
        return "B", issues


def compute_primary_category(atoms):
    """Determine the primary ontological category based on atoms."""
    # All current atoms are PROC. If we had nonverbal atoms they'd differ.
    return "PROC"


def compute_dimension_coverage(atoms):
    """Compute coverage of the 7 irreducible dimensions for a concept."""
    dims = {"ENTITÉ": 0, "PROCESSUS": 0, "QUALITÉ": 0, "RELATION": 0,
            "STRUCTURE": 0, "SITUATION": 0, "MODALITÉ": 0}

    for atom in atoms:
        if atom in ATOM_DIMENSIONS:
            for dim, score in ATOM_DIMENSIONS[atom].items():
                dims[dim] = max(dims[dim], score)

    return {k: round(v, 2) for k, v in dims.items() if v > 0}


def compute_nsm_coverage(atoms):
    """Which NSM primes this concept touches."""
    nsm = set()
    for atom in atoms:
        if atom in ATOM_NSM:
            nsm.update(ATOM_NSM[atom])
    return sorted(nsm)


def compute_pustejovsky(atoms):
    """Which Pustejovsky qualia are involved."""
    qualia = set()
    for atom in atoms:
        if atom in ATOM_PUSTEJOVSKY and ATOM_PUSTEJOVSKY[atom]:
            qualia.add(ATOM_PUSTEJOVSKY[atom])
    return sorted(qualia)


def load_and_import_concepts():
    """Main import: load JSON, clean, classify, insert."""
    print("\n" + "=" * 70)
    print("STEP 5: Load, clean, classify, import PanLang concepts")
    print("=" * 70)

    # Load JSON
    if not os.path.exists(PANLANG_JSON):
        print(f"  ❌ PanLang JSON not found: {PANLANG_JSON}")
        return False

    with open(PANLANG_JSON, "r") as f:
        data = json.load(f)

    concepts_raw = data.get("concepts", {})
    print(f"  📦 Loaded {len(concepts_raw)} raw entries from PanLang ULTIME")

    # Filter and classify
    imported = 0
    excluded_meta = 0
    excluded_unparseable = 0
    audit_issues = []
    concept_queries = []
    composition_queries = []
    dimension_queries = []

    for key, entry in concepts_raw.items():
        # Skip known metadata/fake
        if key in EXCLUDED_CONCEPTS:
            excluded_meta += 1
            continue

        # Parse formule
        formule_raw = entry.get("formule", "")
        atoms, formule_simple, fmt = parse_formule(formule_raw)

        if atoms is None or formule_simple is None:
            excluded_unparseable += 1
            audit_issues.append((key, "unparseable_formula", "warning",
                                 f"Cannot parse formule: {str(formule_raw)[:100]}"))
            continue

        # Check all atoms are valid
        invalid = [a for a in atoms if a not in ATOMS]
        if invalid:
            excluded_unparseable += 1
            audit_issues.append((key, "invalid_atoms", "warning",
                                 f"Unknown atoms: {invalid}"))
            continue

        # Get metadata
        validity = entry.get("validite")
        complexity = entry.get("complexite", len(atoms))
        source = entry.get("source_metadata", {}).get("fichier_origine", "unknown")

        # Classify quality
        tier, issues = classify_quality(key, atoms, validity, formule_simple)

        # Log audit issues
        for issue in issues:
            severity = "critical" if issue in ("absurd_formula", "low_validity") else "warning"
            audit_issues.append((key, issue, severity,
                                 f"{issue}: {formule_simple} (validity={validity})"))

        # Compute enrichments
        primary_cat = compute_primary_category(atoms)
        dim_coverage = compute_dimension_coverage(atoms)
        nsm_cov = compute_nsm_coverage(atoms)
        pust_q = compute_pustejovsky(atoms)
        dims_list = list(dim_coverage.keys())

        # Build concept INSERT
        concept_queries.append(
            f"REPLACE INTO concepts "
            f"(id, name_fr, formule_simple, atoms, atom_count, complexity, "
            f"validity_score, quality_tier, primary_category, dimensions_covered, "
            f"source, formule_format, nsm_coverage, pustejovsky_qualia) "
            f"VALUES ({escape_sql(key)}, {escape_sql(entry.get('nom', key))}, "
            f"{escape_sql(formule_simple)}, {json_sql(atoms)}, {len(atoms)}, "
            f"{complexity}, {validity if validity else 'NULL'}, "
            f"{escape_sql(tier)}, {escape_sql(primary_cat)}, "
            f"{json_sql(dims_list)}, {escape_sql(source)}, "
            f"{escape_sql(fmt)}, {json_sql(nsm_cov)}, {json_sql(pust_q)});"
        )

        # Build composition_rules INSERTs
        for pos, atom in enumerate(atoms):
            composition_queries.append(
                f"REPLACE INTO composition_rules "
                f"(concept_id, position, atom_id, atom_layer, role) "
                f"VALUES ({escape_sql(key)}, {pos}, {escape_sql(atom)}, "
                f"'predicate', NULL);"
            )

        # Build dimension_coverage INSERTs
        for dim, score in dim_coverage.items():
            covered_by = [a for a in atoms if dim in ATOM_DIMENSIONS.get(a, {})]
            dimension_queries.append(
                f"REPLACE INTO dimension_coverage "
                f"(concept_id, dimension, coverage_score, covered_by) "
                f"VALUES ({escape_sql(key)}, {escape_sql(dim)}, {score}, "
                f"{json_sql(covered_by)});"
            )

        imported += 1

    # Execute concept inserts in batches
    print(f"\n  📊 Results:")
    print(f"     Imported:    {imported} concepts")
    print(f"     Excluded:    {excluded_meta} metadata + {excluded_unparseable} unparseable")
    print(f"     Audit issues: {len(audit_issues)}")

    # Insert concepts
    print(f"\n  💾 Inserting {len(concept_queries)} concepts...")
    batch_size = 25
    for i in range(0, len(concept_queries), batch_size):
        batch = concept_queries[i:i + batch_size]
        if not dolt_sql_batch(batch):
            print(f"     ⚠️  Batch {i // batch_size + 1} had errors")

    # Insert composition rules
    print(f"  💾 Inserting {len(composition_queries)} composition rules...")
    for i in range(0, len(composition_queries), batch_size):
        batch = composition_queries[i:i + batch_size]
        dolt_sql_batch(batch)

    # Insert dimension coverage
    print(f"  💾 Inserting {len(dimension_queries)} dimension coverage entries...")
    for i in range(0, len(dimension_queries), batch_size):
        batch = dimension_queries[i:i + batch_size]
        dolt_sql_batch(batch)

    # Insert audit issues
    if audit_issues:
        print(f"  💾 Logging {len(audit_issues)} audit issues...")
        audit_queries = []
        for concept_id, issue_type, severity, desc in audit_issues:
            audit_queries.append(
                f"INSERT INTO quality_audit "
                f"(concept_id, issue_type, severity, description, resolution) "
                f"VALUES ({escape_sql(concept_id)}, {escape_sql(issue_type)}, "
                f"{escape_sql(severity)}, {escape_sql(desc)}, 'pending');"
            )
        for i in range(0, len(audit_queries), batch_size):
            batch = audit_queries[i:i + batch_size]
            dolt_sql_batch(batch)

    return imported


# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Commit
# ─────────────────────────────────────────────────────────────────────────────

def commit_to_dolt(concept_count):
    """Stage and commit all changes."""
    print("\n" + "=" * 70)
    print("STEP 6: Commit to Dolt")
    print("=" * 70)

    dolt("add", ".")
    msg = (
        f"feat: import {concept_count} PanLang concepts with v2 3-layer schema\n\n"
        f"- 4 ontological categories (ENT, PROC, QUAL, ABS)\n"
        f"- 5 structural operations (COMP, ID, NEG, QUANT, MOD)\n"
        f"- 10 semantic predicates (dhātu)\n"
        f"- 4 nonverbal extensions (ESPACE, TEMPS, EVAL, TAXO)\n"
        f"- {concept_count} concepts imported with quality tiers\n"
        f"- Dimension coverage computed for 7 irreducible dimensions\n"
        f"- Quality audit log with issue tracking"
    )
    dolt("commit", "-m", msg, "--author", "PaniniFS Bot <bot@panini-fs.dev>")
    print(f"  ✅ Committed to Dolt")


# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Verification queries
# ─────────────────────────────────────────────────────────────────────────────

def verify():
    """Run verification queries."""
    print("\n" + "=" * 70)
    print("STEP 7: Verification")
    print("=" * 70)

    queries = [
        ("Ontological categories", "SELECT * FROM ontological_categories;"),
        ("Structural operations", "SELECT id, name_en, arity FROM structural_operations;"),
        ("Semantic predicates", "SELECT id, code, dhatu_sa, vendler_aspect FROM semantic_predicates;"),
        ("Nonverbal extensions", "SELECT * FROM nonverbal_extensions;"),
        ("Concepts by quality tier", "SELECT quality_tier, COUNT(*) as n FROM concepts GROUP BY quality_tier ORDER BY quality_tier;"),
        ("Concepts by atom count", "SELECT atom_count, COUNT(*) as n FROM concepts GROUP BY atom_count ORDER BY atom_count;"),
        ("Audit issues by type", "SELECT issue_type, severity, COUNT(*) as n FROM quality_audit GROUP BY issue_type, severity ORDER BY severity, n DESC;"),
        ("Dimension coverage gaps",
         "SELECT d.dimension, COUNT(DISTINCT dc.concept_id) as covered, "
         "(SELECT COUNT(*) FROM concepts) - COUNT(DISTINCT dc.concept_id) as uncovered "
         "FROM (SELECT 'ENTITÉ' as dimension UNION SELECT 'PROCESSUS' UNION SELECT 'QUALITÉ' "
         "UNION SELECT 'RELATION' UNION SELECT 'STRUCTURE' UNION SELECT 'SITUATION' "
         "UNION SELECT 'MODALITÉ') d "
         "LEFT JOIN dimension_coverage dc ON d.dimension = dc.dimension AND dc.coverage_score > 0 "
         "GROUP BY d.dimension ORDER BY covered DESC;"),
        ("Top 5 most complex concepts",
         "SELECT id, formule_simple, atom_count, quality_tier FROM concepts ORDER BY atom_count DESC LIMIT 5;"),
        ("Quality tier C (problematic)",
         "SELECT id, formule_simple, validity_score FROM concepts WHERE quality_tier = 'C' ORDER BY validity_score;"),
    ]

    for label, query in queries:
        print(f"\n  📊 {label}:")
        result = dolt_sql(query, check=False)
        if result:
            for line in result.split("\n")[:12]:
                print(f"     {line}")
            lines = result.split("\n")
            if len(lines) > 12:
                print(f"     ... ({len(lines) - 12} more rows)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  PanLang v2 Import — 3-Layer Universal Primitives Architecture  ║")
    print("║  Based on interdisciplinary literature review (72 references)   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # Step 0
    init_dolt_db()

    # Step 1-4: Seed reference data
    seed_ontological_categories()
    seed_structural_operations()
    seed_semantic_predicates()
    seed_nonverbal_extensions()

    # Step 5: Import concepts
    concept_count = load_and_import_concepts()
    if not concept_count:
        print("\n  ❌ No concepts imported, aborting")
        sys.exit(1)

    # Step 6: Commit
    commit_to_dolt(concept_count)

    # Step 7: Verify
    verify()

    print("\n" + "=" * 70)
    print(f"✅ DONE — {concept_count} concepts imported with v2 3-layer schema")
    print("=" * 70)


if __name__ == "__main__":
    main()

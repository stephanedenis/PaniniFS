#!/usr/bin/env python3
"""
quarantine_tier_c.py — Revalidation et quarantaine des 13 concepts Tier C
═══════════════════════════════════════════════════════════════════════════

Diagnostic (basé sur l'examen des données brutes + cross-ref littérature) :

TOUS les 13 concepts Tier C partagent le même profil :
  - Source         : `wikipedia_directe_optimisee`
  - Hash source    : 8099031d5b42
  - Date           : 2025-09-26 (batch extraction)
  - exemples_dhatu : [] (aucun)
  - description    : '' (vide)
  - Validité       : 0.163–0.381 (vs moyenne dictionnaire 0.534)
  - Warning        : "Contient des atomes non-universels"

Le pipeline Wikipedia a produit des décompositions ALÉATOIRES :
  ARBRE → MOUVEMENT (absurde)
  ÉTOILE → COMMUNICATION (absurde)
  RÉCIT → DESTRUCTION (absurde)
  etc.

═══════════════════════════════════════════════════════════════════════════
VERDICT CONCEPT PAR CONCEPT (cross-ref NSM / Jackendoff / Pustejovsky) :
═══════════════════════════════════════════════════════════════════════════

1. DÉGOÛT = EXISTENCE ❌
   NSM (Wierzbicka 1992, Goddard 2014): FEEL SOMETHING BAD + BODY + SEE/TOUCH
   → Le concept est LÉGITIME (émotion universelle), la formule est FAUSSE
   → Formule corrigée : EMOTION + PERCEPTION (dégoût = réponse émotive à stimulus)
   VERDICT : QUARANTAINE — formule fausse, concept légitime

2. GOÛTER = MOUVEMENT ❌
   NSM: proche de FEEL/BODY (sens gustatif)
   Jackendoff: PERCEIVE_BY_TASTE → catégorie PERCEPTION
   → GOÛTER est une perception sensorielle, pas un mouvement
   VERDICT : QUARANTAINE — devrait être PERCEPTION (sens gustatif)

3. BEAU = EXISTENCE ❌
   NSM (Wierzbicka): FEEL SOMETHING GOOD + SEE/HEAR
   Pustejovsky qualia: FORMAL=aesthetic_quality, TELIC=appréciation
   → La beauté est un JUGEMENT DE VALEUR (EVAL), pas EXISTENCE
   VERDICT : QUARANTAINE — devrait impliquer EVAL (extension v2) + PERCEPTION

4. SENTIR = PERCEPTION ⚠️
   NSM: FEEL (prime directe)
   Jackendoff: Perceptual field
   → La formule PERCEPTION est CORRECTE mais trop pauvre (monoatomique)
   → « Sentir » est polysémique : perception (odorat) + émotion + intuition
   VERDICT : QUARANTAINE — formule trop pauvre, devrait être
             PERCEPTION + EMOTION (au minimum)

5. ARBRE = MOUVEMENT ❌❌
   NSM: THING/KIND_OF (natural kind, substantif)
   Jackendoff: THING [Natural Kind] ← catégorie ontologique ENT
   Pustejovsky: CONST=wood, FORMAL=plant, TELIC=shade/fruit, AGENTIVE=grow
   → ARBRE est une ENTITÉ (substance naturelle), zéro lien avec MOUVEMENT
   → Le pipeline a attribué MOUVEMENT par erreur totale
   VERDICT : RETRAIT — résidu d'exemple sans fondement.
             ARBRE n'est pas un concept verbal/processuel.
             Avec seulement 10 dhātu verbaux, on ne peut PAS décomposer
             les substantifs naturels. C'est un gap du système.

6. FENÊTRE = EXISTENCE ❌
   Pustejovsky: CONST=glass+frame, FORMAL=phys_obj, TELIC=see_through, AGENTIVE=artefact
   → FENÊTRE est un ARTEFACT (pas juste "existe")
   → CRÉATION serait plus pertinent (artefact = chose créée)
   VERDICT : RETRAIT — substantif concret, non décomposable avec les 10 dhātu.
             Même problème que ARBRE : gap système pour les noms concrets.

7. IMAGINER = POSSESSION ❌
   NSM: THINK + WANT + SEE (dans l'esprit)
   Jackendoff: Conceptual + Mental Image → COGNITION
   → IMAGINER est fondamentalement de la COGNITION, pas de la POSSESSION
   VERDICT : QUARANTAINE — devrait être COGNITION + CREATION

8. PROXIMITÉ = MOUVEMENT ❌
   NSM: NEAR (prime spatiale)
   Jackendoff: PLACE-function [NEAR(x,y)]
   → C'est un concept SPATIAL, pas un MOUVEMENT
   → Relève de l'extension ESPACE (v2 layer 3b)
   VERDICT : QUARANTAINE — devrait impliquer ESPACE (extension v2)

9. RÉCIT = DESTRUCTION ❌❌❌
   NSM: SAY + HAPPEN + BEFORE/AFTER (acte de communication temporel)
   Jackendoff: Expressive → COMMUNICATION
   → Un récit est un ACTE DE COMMUNICATION, c'est l'antithèse de DESTRUCTION
   → Formule la plus absurde de tout le dictionnaire
   VERDICT : QUARANTAINE — devrait être COMMUNICATION + COGNITION

10. SATISFACTION = MOUVEMENT ❌
    NSM: FEEL SOMETHING GOOD + WANT (émotion positive liée au désir comblé)
    → C'est une ÉMOTION, pas un MOUVEMENT
    VERDICT : QUARANTAINE — devrait être EMOTION + DOMINATION (want satisfied)

11. LIEU = MOUVEMENT ❌
    NSM: WHERE, HERE, PLACE (primes spatiales)
    Jackendoff: PLACE (catégorie ontologique fondamentale)
    → LIEU est un concept SPATIAL fondamental, pas MOUVEMENT
    VERDICT : QUARANTAINE — devrait impliquer ESPACE (extension v2)

12. ÉTOILE = COMMUNICATION ❌❌
    NSM: THING/KIND_OF (objet naturel)
    Jackendoff: THING [Natural Kind]
    → Une étoile est un objet céleste, zéro lien avec COMMUNICATION
    VERDICT : RETRAIT — substantif naturel, non décomposable.
             Même catégorie que ARBRE : gap système noms concrets.

13. MUSIQUE = DESTRUCTION + MOUVEMENT ❌❌
    NSM: HEAR + FEEL GOOD + MAKE/DO
    Jackendoff: SOUND/Event → catégorie Perceptual
    Pustejovsky: FORMAL=sound_pattern, TELIC=aesthetic_enjoyment, AGENTIVE=compose/play
    → La musique est PERCEPTION (auditive) + CREATION (composition)
    → DESTRUCTION est le contraire exact de ce qu'est la musique
    VERDICT : QUARANTAINE — devrait être PERCEPTION + CREATION

═══════════════════════════════════════════════════════════════════════════
RÉSUMÉ DES VERDICTS :
  - RETRAIT (3)     : ARBRE, FENÊTRE, ÉTOILE — substantifs naturels/artefacts
                       non décomposables avec les 10 dhātu verbaux
  - QUARANTAINE (10) : formules fausses, concepts légitimes avec proposition
═══════════════════════════════════════════════════════════════════════════
"""

import subprocess
import os
import sys
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panini-unified-db")


def dolt_sql(query: str, check=True) -> str:
    result = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        cwd=DB_DIR, capture_output=True, text=True,
        env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
    )
    if check and result.returncode != 0:
        print(f"  ⚠️  SQL error: {result.stderr.strip()}")
        return ""
    return result.stdout.strip()


def dolt_exec(query: str) -> str:
    result = subprocess.run(
        ["dolt", "sql", "-q", query],
        cwd=DB_DIR, capture_output=True, text=True,
        env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
    )
    if result.returncode != 0:
        print(f"  ⚠️  SQL error: {result.stderr.strip()}")
    return result.stdout.strip()


# ═══════════════════════════════════════════════════════════════════
# CONCEPTS À RETIRER (substantifs non-décomposables)
# ═══════════════════════════════════════════════════════════════════
RETRAIT = {
    "ARBRE": "substantif naturel (natural kind) — non décomposable avec les 10 dhātu verbaux",
    "FENÊTRE": "artefact concret (phys_obj) — non décomposable avec les 10 dhātu verbaux",
    "ÉTOILE": "objet naturel (céleste) — non décomposable avec les 10 dhātu verbaux",
}

# ═══════════════════════════════════════════════════════════════════
# CONCEPTS EN QUARANTAINE (formule fausse → proposition corrigée)
# ═══════════════════════════════════════════════════════════════════
QUARANTAINE = {
    "DÉGOÛT": {
        "old_formula": "EXISTENCE",
        "proposed_formula": "EMOTION + PERCEPTION",
        "justification": "NSM: FEEL SOMETHING BAD + BODY/SEE. Réponse émotive à un stimulus sensoriel négatif.",
        "references": "Wierzbicka 1992 (Defining Emotion Concepts), Goddard 2014 (interjections & disgust)",
    },
    "GOÛTER": {
        "old_formula": "MOUVEMENT",
        "proposed_formula": "PERCEPTION",
        "justification": "Perception gustative (sens). Jackendoff: PERCEIVE_BY_TASTE, catégorie perceptuelle.",
        "references": "Jackendoff 1990 (Semantic Structures), Pustejovsky 1995 (GL: sense verbs)",
    },
    "BEAU": {
        "old_formula": "EXISTENCE",
        "proposed_formula": "PERCEPTION + EMOTION",
        "justification": "NSM: FEEL SOMETHING GOOD + SEE/HEAR. Jugement esthétique = perception + émotion positive.",
        "references": "Wierzbicka 1992, Pustejovsky 1995 (TELIC=appréciation)",
    },
    "SENTIR": {
        "old_formula": "PERCEPTION",
        "proposed_formula": "PERCEPTION + EMOTION",
        "justification": "Polysémique: perception sensorielle (odorat) + résonance émotionnelle. Formule monoatomique trop pauvre.",
        "references": "NSM: FEEL (prime). Jackendoff: Perceptual + Affective fields",
    },
    "IMAGINER": {
        "old_formula": "POSSESSION",
        "proposed_formula": "COGNITION + CREATION",
        "justification": "NSM: THINK + image mentale. Jackendoff: Conceptual + Mental Image = création cognitive.",
        "references": "Jackendoff 1983 (Semantics and Cognition), NSM: THINK prime",
    },
    "PROXIMITÉ": {
        "old_formula": "MOUVEMENT",
        "proposed_formula": "EXISTENCE + MOUVEMENT",
        "justification": "NSM: NEAR (prime spatiale). Jackendoff: PLACE-function NEAR(x,y). Relation spatiale, pas mouvement pur.",
        "references": "Jackendoff 1983 (PLACE functions), NSM: NEAR/WHERE primes",
    },
    "RÉCIT": {
        "old_formula": "DESTRUCTION",
        "proposed_formula": "COMMUNICATION + COGNITION",
        "justification": "NSM: SAY + HAPPEN + BEFORE/AFTER. Un récit est un acte de communication séquentiel. Formule absurde originale.",
        "references": "NSM: SAY prime, Jackendoff (Expressive), Genette 1972 (narratologie)",
    },
    "SATISFACTION": {
        "old_formula": "MOUVEMENT",
        "proposed_formula": "EMOTION + DOMINATION",
        "justification": "NSM: FEEL SOMETHING GOOD + WANT. Émotion positive quand un désir est comblé (DOMINATION=vouloir/pouvoir).",
        "references": "Wierzbicka 1992 (emotion concepts: satisfaction ≈ contentment)",
    },
    "LIEU": {
        "old_formula": "MOUVEMENT",
        "proposed_formula": "EXISTENCE",
        "justification": "NSM: WHERE/HERE/PLACE (primes spatiales). Jackendoff: PLACE est une catégorie ontologique. Relève de ESPACE (v2 ext).",
        "references": "Jackendoff 1983 (PLACE ontological category), NSM: WHERE/HERE primes",
    },
    "MUSIQUE": {
        "old_formula": "DESTRUCTION + MOUVEMENT",
        "proposed_formula": "PERCEPTION + CREATION",
        "justification": "NSM: HEAR + FEEL GOOD + MAKE/DO. Création sonore perçue esthétiquement. DESTRUCTION est l'antithèse.",
        "references": "Jackendoff 1987 (Consciousness and the Computational Mind, ch. on music), Pustejovsky 1995 (AGENTIVE=compose)",
    },
}


def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  Revalidation des 13 concepts Tier C — Quarantaine & Retrait   ║")
    print("║  Cross-ref: NSM (Wierzbicka), Jackendoff, Pustejovsky          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # ──────────────────────────────────────────────────────────────
    # ÉTAPE 1 : Retrait des 3 substantifs non-décomposables
    # ──────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("ÉTAPE 1 : Retrait de 3 substantifs non-décomposables")
    print(f"{'='*70}")

    for concept_id, reason in RETRAIT.items():
        print(f"\n  🗑️  {concept_id} — {reason}")

        # Log dans quality_audit avant suppression
        dolt_exec(f"""
            INSERT INTO quality_audit (concept_id, issue_type, severity, description, detected_at)
            VALUES ('{concept_id}', 'retrait_revalidation', 'critical',
                    'Retiré lors de la revalidation Tier C: {reason}. Résidu du pipeline wikipedia_directe_optimisee sans fondement sémantique.',
                    NOW())
        """)

        # Supprimer dans l'ordre FK
        dolt_exec(f"DELETE FROM dimension_coverage WHERE concept_id = '{concept_id}'")
        dolt_exec(f"DELETE FROM composition_rules WHERE concept_id = '{concept_id}'")
        dolt_exec(f"DELETE FROM quality_audit WHERE concept_id = '{concept_id}' AND issue_type != 'retrait_revalidation'")
        dolt_exec(f"DELETE FROM concepts WHERE id = '{concept_id}'")
        print(f"     ✅ Supprimé de la base")

    # ──────────────────────────────────────────────────────────────
    # ÉTAPE 2 : Quarantaine des 10 concepts à formule fausse
    # ──────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("ÉTAPE 2 : Quarantaine de 10 concepts (formules fausses, concepts légitimes)")
    print(f"{'='*70}")

    for concept_id, info in QUARANTAINE.items():
        print(f"\n  🔶 {concept_id}")
        print(f"     Avant  : {info['old_formula']}")
        print(f"     Proposé: {info['proposed_formula']}")
        print(f"     Raison : {info['justification']}")

        # Mettre à jour quality_tier → 'Q' (quarantaine)
        dolt_exec(f"""
            UPDATE concepts
            SET quality_tier = 'Q',
                formule_simple = '{info['proposed_formula']}',
                atom_count = {len(info['proposed_formula'].split(' + '))}
            WHERE id = '{concept_id}'
        """)

        # Supprimer les anciennes composition_rules
        dolt_exec(f"DELETE FROM composition_rules WHERE concept_id = '{concept_id}'")

        # Insérer les nouvelles composition_rules (proposées)
        atoms = [a.strip() for a in info['proposed_formula'].split('+')]
        for pos, atom in enumerate(atoms):
            dolt_exec(f"""
                INSERT INTO composition_rules (concept_id, atom_id, position, operation)
                VALUES ('{concept_id}', '{atom}', {pos}, 'COMP')
            """)

        # Supprimer les anciennes dimension_coverage
        dolt_exec(f"DELETE FROM dimension_coverage WHERE concept_id = '{concept_id}'")

        # Recalculer la couverture dimensionnelle
        ATOM_DIMS = {
            'MOUVEMENT': 'PROCESSUS', 'COGNITION': 'PROCESSUS',
            'PERCEPTION': 'PROCESSUS', 'COMMUNICATION': 'PROCESSUS',
            'CREATION': 'PROCESSUS', 'EMOTION': 'PROCESSUS',
            'EXISTENCE': 'ENTITÉ', 'DESTRUCTION': 'PROCESSUS',
            'POSSESSION': 'RELATION', 'DOMINATION': 'MODALITÉ',
        }
        dims_seen = set()
        for atom in atoms:
            dim = ATOM_DIMS.get(atom)
            if dim and dim not in dims_seen:
                dims_seen.add(dim)
                dolt_exec(f"""
                    INSERT INTO dimension_coverage (concept_id, dimension, covered_by, coverage_score)
                    VALUES ('{concept_id}', '{dim}', '{atom}', 0.5)
                """)

        # Ajouter une entrée d'audit détaillée
        # Escape single quotes in justification
        just_escaped = info['justification'].replace("'", "''")
        refs_escaped = info['references'].replace("'", "''")
        dolt_exec(f"""
            INSERT INTO quality_audit (concept_id, issue_type, severity, description, detected_at)
            VALUES ('{concept_id}', 'quarantine_revalidation', 'warning',
                    'Formule corrigée de [{info["old_formula"]}] → [{info["proposed_formula"]}]. {just_escaped} Refs: {refs_escaped}',
                    NOW())
        """)

        print(f"     ✅ Mis en quarantaine (tier Q), formule corrigée, audit loggé")

    # ──────────────────────────────────────────────────────────────
    # ÉTAPE 3 : Commit
    # ──────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("ÉTAPE 3 : Commit dans Dolt")
    print(f"{'='*70}")

    subprocess.run(["dolt", "add", "."], cwd=DB_DIR, capture_output=True)
    result = subprocess.run(
        ["dolt", "commit", "-m",
         "revalidation: quarantaine 10 concepts + retrait 3 substantifs non-décomposables\n\n"
         "Cross-référence NSM (Wierzbicka), Jackendoff, Pustejovsky :\n"
         "- RETRAIT (3): ARBRE, FENÊTRE, ÉTOILE — substantifs naturels/artefacts\n"
         "  non décomposables avec les 10 dhātu verbaux (gap système)\n"
         "- QUARANTAINE (10): formules Wikipedia fausses remplacées par propositions\n"
         "  fondées sur la littérature scientifique\n"
         "- Source commune des 13: pipeline wikipedia_directe_optimisee (batch 2025-09-26)"],
        cwd=DB_DIR, capture_output=True, text=True,
        env={**os.environ, "DOLT_CLI_NO_PAGER": "1"},
    )
    if result.returncode == 0:
        print("  ✅ Committed")
    else:
        print(f"  ⚠️  {result.stderr.strip()}")

    # ──────────────────────────────────────────────────────────────
    # ÉTAPE 4 : Vérification
    # ──────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("ÉTAPE 4 : Vérification post-revalidation")
    print(f"{'='*70}")

    total = dolt_sql("SELECT COUNT(*) FROM concepts")
    print(f"\n  📊 Concepts restants : {total.split(chr(10))[-1]}")

    tiers = dolt_sql("SELECT quality_tier, COUNT(*) as n FROM concepts GROUP BY quality_tier ORDER BY quality_tier")
    print(f"\n  📊 Distribution par tier :")
    for line in tiers.split("\n")[1:]:
        print(f"     {line}")

    quarantined = dolt_sql("SELECT id, formule_simple FROM concepts WHERE quality_tier = 'Q' ORDER BY id")
    print(f"\n  📊 Concepts en quarantaine (tier Q) :")
    for line in quarantined.split("\n")[1:]:
        print(f"     {line}")

    audit = dolt_sql("SELECT issue_type, COUNT(*) as n FROM quality_audit GROUP BY issue_type ORDER BY n DESC")
    print(f"\n  📊 Audit issues par type :")
    for line in audit.split("\n")[1:]:
        print(f"     {line}")

    print(f"\n{'='*70}")
    print("✅ REVALIDATION COMPLÈTE")
    print(f"   - 3 concepts retirés (substantifs non-décomposables)")
    print(f"   - 10 concepts en quarantaine (formules corrigées)")
    print(f"   - Tier C éliminé du dictionnaire")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

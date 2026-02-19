# 2026-02-18 — v2.3 Concept Revision: Formula Overrides + FK Fix + CONCEPT_MAPPINGS Expansion

**Agent** : GitHub Copilot (Claude Opus 4.6) — session hauru
**Branche** : master

## Contexte

Suite à l'ajout des 7 atomes ABS (commit 0a52283), diagnostic stratégique
révélant que seulement 29/104 concepts étaient activés dans le corpus littéraire.
Causes identifiées : 9 formules dupliquées, 10 concepts Tier Q mal spécifiés,
CONCEPT_MAPPINGS hardcodé à 29 entrées, et un bug critique de FK dans Dolt
empêchant la persistance des overrides.

## Décisions clés

### 1. Fix du bug FK sur REPLACE INTO
- **Constat** : `REPLACE INTO concepts` fait DELETE+INSERT, violant la FK
  `composition_rules_ibfk_1`. 104/104 concepts échouaient silencieusement.
- **Décision** : Ajouter `DELETE FROM composition_rules/dimension_coverage/quality_audit`
  avant les insertions de concepts. Ajout d'un retry individuel sur échec de batch.
- **Impact** : Tous les concepts s'insèrent maintenant correctement.

### 2. FORMULA_OVERRIDES_V23 : 24 → 27 overrides
- **Constat** : 4 doublons restaient après les 24 premiers overrides
  (BEAU/BEAUTÉ, ENTENDRE/SENTIR, IMAGINER/INVENTER, LIEU/MUR).
- **Décision** : Ajout de 3 overrides supplémentaires :
  - BEAUTÉ → PERCEPTION + SEEKING + INVARIANCE (ABS atom)
  - ENTENDRE → PERCEPTION + COMMUNICATION (audition = réception de signal)
  - INVENTER → COGNITION + CREATION + SEEKING (vs IMAGINER = pure création mentale)
  - MUR → EXISTENCE + STRUCTURE + DESTRUCTION (barrière physique)
- **Impact** : 0 formules dupliquées dans Dolt (vérifié par SQL GROUP BY).

### 3. CONCEPT_MAPPINGS : 29 → 78 concepts
- **Constat** : Le moteur 7-layers utilisait un dict hardcodé à 29 concepts.
  Les 75 autres concepts existaient dans Dolt mais n'étaient jamais détectés.
- **Décision** : Expansion à 78 concepts (tous ceux dont les atomes sont
  détectables dans un corpus littéraire — sans atomes ABS). Chaque concept
  a un atom-set unique (0 doublons).
- **Impact** : 76 concepts activés dans le corpus (vs 29 avant, +262%).

### 4. Distribution des tiers : A=49, B=46, C=9
- **Constat** : Anciens Q=10 reconvertis en C=9 (formules révisées mais
  validity_score bas car pas encore validé sur corpus élargi).
- **Décision** : Acceptable — les C sont les anciens Q avec des formules
  maintenant correctes. La validity_score remontera avec un corpus plus large.

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `import_panlang_v2.py` | FK fix (DELETE child tables), 27 overrides v2.3, commit message v2.3 |
| `seven_layers_engine.py` | CONCEPT_MAPPINGS 29→78, 0 doublons d'atom-sets |

## Tests effectués

- `test_morpho_semantic_bridge.py` : 90/90 ✅
- `test_seven_layers.py` : 72/72 ✅
- **Total : 162/162 tests passent** (aucune régression)
- Dolt SQL : 0 formules dupliquées, 104 concepts insérés, 76 activés dans corpus

## Métriques d'impact

| Métrique | Avant | Après | Δ |
|----------|-------|-------|---|
| Formules dupliquées | 9 groupes | 0 | -100% |
| Concepts activés (corpus) | 29 | 76 | +262% |
| CONCEPT_MAPPINGS | 29 | 78 | +169% |
| Tier Q concepts | 10 | 0 (→ C=9) | -100% |
| Tests passants | 162/162 | 162/162 | = |
| Atomes ABS utilisés (Dolt) | 0 | 6/7 | +6 |
| Overrides | 4 (v2.2) | 27 (v2.3) | +575% |

## Prochaines étapes

1. **Élargir le corpus** : Ajouter des textes scientifiques/philosophiques
   pour activer les atomes ABS (MESURE, STRUCTURE, etc.)
2. **Valider les C-tier** : Tester les 9 concepts C sur corpus élargi
   pour améliorer leur validity_score
3. **ABS atom keywords** : Vérifier que les 608 keywords ABS sont
   suffisamment discriminants pour les textes techniques
4. **BEAUTÉ** : Concept avec INVARIANCE (ABS) — actuellement non détectable
   dans le corpus littéraire. Potentiellement activable en corpus philosophique.

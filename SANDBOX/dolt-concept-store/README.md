# Dolt Concept Store pour PaniniFS

**Proof of Concept v2** : Architecture universelle 3 couches pour les primitifs sémantiques de PaniniFS, fondée sur une revue interdisciplinaire de 72 références.

## 🎯 Vision

PaniniFS décompose l'information en **primitifs conceptuels universels**. Ce POC implémente une architecture rigoureuse de **23 primitifs en 3 couches**, validée par convergence entre 10 domaines scientifiques (théorie de l'information, sémiotique, théorie des catégories, ontologies formelles, linguistique computationnelle).

Le stockage utilise **Dolt**, une base SQL avec workflows Git, permettant versioning, expérimentation par branches, et traçabilité complète.

## 🏗️ Architecture v2 : 3 Couches de Primitifs Universels

```
╔══════════════════════════════════════════════════════════════════════╗
║  COUCHE 1 — CATÉGORIES ONTOLOGIQUES (DOLCE/BFO/SUMO convergence)   ║
║  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐              ║
║  │  ENT   │ │   PROC   │ │  QUAL   │ │     ABS     │              ║
║  │ Entité │ │ Processus│ │ Qualité │ │ Abstraction │              ║
║  │dravya  │ │  kriyā   │ │  guṇa   │ │  sāmānya   │              ║
║  └────────┘ └──────────┘ └─────────┘ └─────────────┘              ║
╠══════════════════════════════════════════════════════════════════════╣
║  COUCHE 2 — OPÉRATIONS STRUCTURELLES (logique/catégories/calcul)   ║
║  ┌──────┐ ┌─────┐ ┌──────┐ ┌───────┐ ┌──────────┐                ║
║  │ COMP │ │ ID  │ │ NEG  │ │ QUANT │ │   MOD    │                ║
║  └──────┘ └─────┘ └──────┘ └───────┘ └──────────┘                ║
╠══════════════════════════════════════════════════════════════════════╣
║  COUCHE 3a — PRÉDICATS SÉMANTIQUES (10 dhātu / racines verbales)   ║
║  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐       ║
║  │ MOUVEMENT  │ │ COGNITION │ │PERCEPTION│ │COMMUNICATION │       ║
║  │   √gam     │ │   √jñā    │ │   √dṛś   │ │    √vac      │       ║
║  ├────────────┤ ├───────────┤ ├──────────┤ ├──────────────┤       ║
║  │  CREATION  │ │  EMOTION  │ │EXISTENCE │ │ DESTRUCTION  │       ║
║  │   √kṛ      │ │   √hṛd    │ │   √as    │ │              │       ║
║  ├────────────┤ ├───────────┤ └──────────┘ └──────────────┘       ║
║  │ POSSESSION │ │DOMINATION │                                      ║
║  │   √labh    │ │   √īś     │                                      ║
║  └────────────┘ └───────────┘                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  COUCHE 3b — EXTENSIONS NON-VERBALES (dimensions manquantes)       ║
║  ┌─────────┐ ┌───────┐ ┌──────────┐ ┌──────────┐                 ║
║  │ ESPACE  │ │ TEMPS │ │   EVAL   │ │   TAXO   │                 ║
║  └─────────┘ └───────┘ └──────────┘ └──────────┘                 ║
╚══════════════════════════════════════════════════════════════════════╝
         4          5          10           4    =  23 primitifs
```

### Couverture des 7 dimensions irréductibles

| Dimension  | Couverture PanLang actuelle | Primitifs responsables        |
|------------|----------------------------|-------------------------------|
| PROCESSUS  | ✅ Forte (100% des concepts)| 10 dhātu                     |
| ENTITÉ     | ⚠️ Partielle               | EXISTENCE, POSSESSION         |
| QUALITÉ    | ⚠️ Partielle               | EVAL (extension)             |
| RELATION   | ⚠️ Partielle               | TAXO (extension)             |
| MODALITÉ   | ✅ Via couche 2             | MOD, QUANT                   |
| STRUCTURE  | ❌ Gap identifié            | COMP, ID, NEG (à intégrer)   |
| SITUATION  | ❌ Gap identifié            | ESPACE, TEMPS (à intégrer)   |

## 📦 Structure du POC

```
SANDBOX/dolt-concept-store/
├── README.md                          # Ce fichier
├── requirements.txt                   # Dépendances Python
│
├── # ═══ v1 (POC initial) ═══════════
├── schema.sql                         # Schéma v1 (7 dhātu)
├── init_dolt.py                       # Init + seed v1
├── demo_workflow.py                   # Démo workflow v1
├── rust_bridge_stub.py                # Stub bridge Rust ↔ Dolt
│
├── # ═══ Unified POC ════════════════
├── schema_unified.sql                 # Schéma 3-tier (17 tables)
├── dolt_unified_storage.py            # POC stockage unifié
├── demo_multilingual_dedup.py         # Dédup cross-langue (5035 phrases)
├── setup_dolt_acl.py                  # Config ACL branches
├── test_branch_acl.py                 # Tests ACL (14/14)
├── test_cascade_topology.py           # Tests cascade (20/20)
│
├── # ═══ v2 (Architecture 3 couches) ═
├── schema_v2_universals.sql           # Schéma v2 (10 tables + 4 views)
├── import_panlang_v2.py               # Import PanLang → Dolt v2
├── test_v2_validation.py              # Tests validation v2 (38/38)
├── UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md  # Revue 72 refs
├── ARCHITECTURE_UNIFIED_DOLT.md       # Doc architecture
│
├── panini-concepts-db/                # Base Dolt v1 (ignorée par git)
└── panini-unified-db/                 # Base Dolt v2 (ignorée par git)
```

## 🚀 Quick Start — Architecture v2

### Étape 1 : Installer Dolt

```bash
sudo bash -c 'curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh | bash'
dolt version  # v1.82.1+
```

### Étape 2 : Importer PanLang avec le schéma v2

```bash
cd SANDBOX/dolt-concept-store/
python3 import_panlang_v2.py
```

Ce script :
- ✅ Initialise la DB Dolt (`panini-unified-db/`)
- ✅ Applique le schéma 3 couches (10 tables + 4 views)
- ✅ Seed les 23 primitifs (4 onto + 5 struct + 10 pred + 4 ext)
- ✅ Importe 107 concepts PanLang nettoyés (48 metadata exclus)
- ✅ Classifie en quality tiers (A/B/C) avec audit trail
- ✅ Calcule la couverture des 7 dimensions irréductibles
- ✅ Commit dans Dolt

### Étape 3 : Valider l'import

```bash
python3 test_v2_validation.py   # 38/38 tests ✅
```

## 📊 Schéma v2 — 10 Tables + 4 Vues

### Layer 1 : `ontological_categories`
4 catégories convergentes DOLCE/BFO/SUMO.

| id   | name_fr      | name_sa   | dolce_equiv | bfo_equiv                       |
|------|-------------|-----------|-------------|---------------------------------|
| ENT  | Entité      | dravya    | Endurant    | Continuant                      |
| PROC | Processus   | kriyā     | Perdurant   | Occurrent                       |
| QUAL | Qualité     | guṇa      | Quality     | Specifically Dependent Continuant|
| ABS  | Abstraction | sāmānya  | Abstract    | Generically Dependent Continuant|

### Layer 2 : `structural_operations`
5 opérations issues de la théorie des catégories et de la logique.

| id    | name_en      | category_theory    | logical_equiv       |
|-------|--------------|--------------------|---------------------|
| COMP  | Composition  | Composition ∘      | ∧ (conjunction)     |
| ID    | Identity     | Identity morphism  | = (identity)        |
| NEG   | Negation     | Complement         | ¬ (negation)        |
| QUANT | Quantification| Quantifier        | ∀/∃ (quantifiers)   |
| MOD   | Modality     | Functor            | □/◇ (modal)         |

### Layer 3a : `semantic_predicates`
10 dhātu avec mappings cross-frameworks.

| id            | dhātu  | NSM prime         | Vendler aspect | Jackendoff      |
|---------------|--------|--------------------|----------------|-----------------|
| MOUVEMENT     | √gam   | MOVE               | activity       | GO              |
| COGNITION     | √jñā   | THINK, KNOW        | state          | Conceptual      |
| PERCEPTION    | √dṛś   | SEE, HEAR, FEEL    | achievement    | Perceptual      |
| COMMUNICATION | √vac   | SAY                | activity       | Expressive      |
| CREATION      | √kṛ    | MAKE, DO           | accomplishment | CAUSE+BECOME    |
| EMOTION       | √hṛd   | FEEL               | state          | Affective       |
| EXISTENCE     | √as    | EXIST, LIVE, DIE   | state          | BE              |
| DESTRUCTION   |        | (inverse CREATION) | achievement    | CAUSE+NOT+BE    |
| POSSESSION    | √labh  | HAVE               | state          | HAVE            |
| DOMINATION    | √īś    | WANT, CAN          | state          | Volitional      |

### Layer 3b : `nonverbal_extensions`
4 extensions pour combler les gaps dimensionnels.

| id     | dimension | NSM primes                                |
|--------|-----------|-------------------------------------------|
| ESPACE | SITUATION | WHERE, HERE, ABOVE, BELOW, FAR, NEAR      |
| TEMPS  | SITUATION | WHEN, NOW, BEFORE, AFTER, A LONG TIME     |
| EVAL   | QUALITÉ   | GOOD, BAD                                 |
| TAXO   | RELATION  | KIND OF, PART OF                          |

### Tables d'import

| Table               | Contenu                                       | Rows  |
|---------------------|-----------------------------------------------|-------|
| `concepts`          | 107 concepts PanLang nettoyés                 | 107   |
| `composition_rules` | Décomposition atome par atome                 | 250   |
| `dimension_coverage`| Couverture des 7 dimensions par concept       | 254   |
| `quality_audit`     | Issues identifiées (tautologies, absurdités)  | 38    |

### 4 Vues analytiques

| Vue                        | Description                              |
|----------------------------|------------------------------------------|
| `v_atom_distribution`      | Fréquence d'usage de chaque atome        |
| `v_quality_summary`        | Résumé par tier de qualité               |
| `v_dimension_gap_analysis` | Analyse des gaps dimensionnels           |
| `v_problematic_concepts`   | Concepts flaggés (tier C, audit issues)  |

## � Requêtes utiles

### Distribution des atomes
```sql
SELECT * FROM v_atom_distribution ORDER BY usage_count DESC;
```

### Concepts problématiques (tier C)
```sql
SELECT * FROM v_problematic_concepts;
```

### Gaps dimensionnels
```sql
SELECT * FROM v_dimension_gap_analysis;
```

### Composition d'un concept
```sql
SELECT c.id, c.formule_simple, cr.atom_id, cr.position
FROM concepts c
JOIN composition_rules cr ON c.id = cr.concept_id
WHERE c.id = 'AMOUR'
ORDER BY cr.position;
```

### Concepts par catégorie ontologique
```sql
SELECT sp.ontological_category, COUNT(cr.concept_id) AS concepts
FROM composition_rules cr
JOIN semantic_predicates sp ON cr.atom_id = sp.id
GROUP BY sp.ontological_category;
```

## 📈 Résultats de l'Import v2

| Métrique                  | Valeur                |
|---------------------------|-----------------------|
| Concepts importés         | 107                   |
| Entrées metadata exclues  | 48                    |
| Tier A (haute qualité)    | 49                    |
| Tier B (qualité moyenne)  | 45                    |
| Tier C (problématique)    | 13                    |
| Règles de composition     | 250                   |
| Entrées couverture dim.   | 254                   |
| Issues d'audit            | 38                    |
| Tests de validation       | 38/38 ✅              |

### Issues identifiées

| Type              | Sévérité | Count | Exemple                       |
|-------------------|----------|-------|-------------------------------|
| Tautologie        | warning  | 23    | ÉTOILE = COMMUNICATION        |
| Low validity      | critical | 12    | DÉGOÛT (validity 0.16)        |
| Formule absurde   | critical | 3     | MUSIQUE = DESTRUCTION+MOUVEMENT|

## 🎓 Fondements Scientifiques

L'architecture v2 repose sur la convergence de 10 domaines :

1. **Théorie de l'information** — Shannon, Kolmogorov, MDL
2. **Communication sémantique** — Rate-distortion, Information Bottleneck
3. **Calculabilité** — SKI combinateurs, Church encoding
4. **Théorie des catégories** — Lawvere 1963, constructions universelles
5. **Ontologies formelles** — DOLCE, BFO, SUMO
6. **NSM** — Wierzbicka (65 primes)
7. **Sémantique lexicale** — Jackendoff, Pustejovsky (Generative Lexicon)
8. **Sémiotique** — Peirce (triadic), Hjelmslev
9. **Grammaire universelle** — Chomsky (Merge), Montague
10. **Tradition sanskrite** — Dhātupāṭha, Pāṇini, Bhartṛhari

Voir : `UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md` (72 références, 886 lignes)

## 🚧 Prochaines Étapes

### Court terme
- [ ] Combler les gaps STRUCTURE et SITUATION dans les formules PanLang
- [ ] Intégrer les 50 NSM primes manquants (logiques, déictiques, substantifs)
- [ ] Tests de couverture sur corpus PanLang v2

### Moyen terme
- [ ] Implémenter l'analyzer Rust avec output JSON → Dolt v2
- [ ] Validation cross-framework (NSM, Jackendoff, Pustejovsky)
- [ ] ACL branches (public/confidential/private) sur schéma v2

### Long terme
- [ ] Expérimentation de nouveaux primitifs via branches Dolt
- [ ] Publication du dataset versionné sur DoltHub
- [ ] Alignement avec BabelNet / WordNet / FrameNet

## 📝 Historique des Versions

| Version | Date       | Description                                          | Tests      |
|---------|------------|------------------------------------------------------|------------|
| v0.1    | 2025-01-15 | POC initial : 7 dhātu, dédup cross-langue            | ✅          |
| v1.0    | 2025-02    | Unified storage : 17 tables, 3-tier, cascade, ACL    | 34/34 ✅    |
| **v2.0**| **2025-02**| **3-layer universals : 23 primitifs, 107 concepts**  | **38/38 ✅**|

## 📄 Licence

Ce sandbox fait partie du projet PaniniFS.
Voir `LICENSE` à la racine du projet.

---

**Auteur:** PaniniFS Core Team  
**Version:** 2.0.0  
**Date:** 2025-02-17  
**Status:** Proof of Concept (validated)

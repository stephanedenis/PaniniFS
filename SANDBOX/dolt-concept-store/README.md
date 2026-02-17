# Dolt Concept Store pour PaniniFS

**Proof of Concept v2.2 + v3-alpha** : Architecture universelle 3 couches + axes émotionnels pour les primitifs sémantiques de PaniniFS, fondée sur une revue interdisciplinaire de 72 références, **validée empiriquement** sur un corpus multilingue Gutenberg (10 traductions, 6 langues, 46 segments), enrichie de **8 sous-primitifs émotionnels neurophysiologiques** (Panksepp/Ekman/Plutchik/Damasio), et complétée par une **analyse des gaps de reconstruction** avec un POC phrase-level (122 phrases, 176 attributions mot→atome, profils stylistiques par traducteur).

## 🎯 Vision

PaniniFS décompose l'information en **primitifs conceptuels universels**. Ce POC implémente une architecture rigoureuse de **30 primitifs en 3 couches + axes émotionnels**, validée par convergence entre 10 domaines scientifiques (théorie de l'information, sémiotique, théorie des catégories, ontologies formelles, linguistique computationnelle, neurosciences affectives), puis **validée empiriquement** via un corpus multilingue de traductions Gutenberg avec chaîne de provenance complète (édition → traducteur → époque → source).

Le stockage utilise **Dolt**, une base SQL avec workflows Git, permettant versioning, expérimentation par branches, et traçabilité complète.

## 🏗️ Architecture v2.2 : 3 Couches + Axes Émotionnels (30 Primitifs)

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
║  COUCHE 3a — PRÉDICATS SÉMANTIQUES (9 dhātu — EMOTION → couche 3c)║
║  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐       ║
║  │ MOUVEMENT  │ │ COGNITION │ │PERCEPTION│ │COMMUNICATION │       ║
║  │   √gam     │ │   √jñā    │ │   √dṛś   │ │    √vac      │       ║
║  ├────────────┤ ├───────────┤ ├──────────┤ ├──────────────┤       ║
║  │  CREATION  │ │ EXISTENCE │ │POSSESSION│ │ DESTRUCTION  │       ║
║  │   √kṛ      │ │   √as     │ │  √labh   │ │              │       ║
║  ├────────────┤ └───────────┘ └──────────┘ └──────────────┘       ║
║  │ DOMINATION │                                                    ║
║  │   √īś      │                                                    ║
║  └────────────┘                                                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  COUCHE 3b — EXTENSIONS NON-VERBALES (dimensions manquantes)       ║
║  ┌─────────┐ ┌───────┐ ┌──────────┐ ┌──────────┐                 ║
║  │ ESPACE  │ │ TEMPS │ │   EVAL   │ │   TAXO   │                 ║
║  └─────────┘ └───────┘ └──────────┘ └──────────┘                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  COUCHE 3c — AXES ÉMOTIONNELS (8 sous-primitifs, 4 axes bipolaires)║
║  ┌─────────────────────────────────────────────────────────────┐   ║
║  │  APPÉTENCE :  SEEKING (√iṣ)   ↔  FEAR    (√bhī)           │   ║
║  │  LIEN      :  CARE    (√snuh) ↔  GRIEF   (√śuc)           │   ║
║  │  ASSERTION :  RAGE    (√krudh)↔  DISGUST (√jugupsā)       │   ║
║  │  JOUISSANCE:  PLAY    (√krīḍ) ↔  TEDIUM  (√glai)          │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════╝
         4          5          9      4      8   =  30 primitifs
```

### Couverture des 7 dimensions irréductibles

| Dimension  | Couverture PanLang actuelle | Primitifs responsables               |
|------------|----------------------------|--------------------------------------|
| PROCESSUS  | ✅ Forte (100% des concepts)| 9 dhātu + 8 axes émotionnels        |
| ENTITÉ     | ⚠️ Partielle               | EXISTENCE, POSSESSION                |
| QUALITÉ    | ⚠️ Partielle               | EVAL (extension)                     |
| RELATION   | ⚠️ Partielle               | TAXO (extension)                     |
| MODALITÉ   | ✅ Via couche 2             | MOD, QUANT                           |
| STRUCTURE  | ❌ Gap identifié            | COMP, ID, NEG (à intégrer)           |
| SITUATION  | ❌ Gap identifié            | ESPACE, TEMPS (à intégrer)           |
| ÉMOTION    | ✅ Forte (v2.2)            | 8 axes neurophysiologiques (couche 3c)|

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
├── test_v2_validation.py              # Tests validation v2 (44/44)
├── UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md  # Revue 72 refs
├── ARCHITECTURE_UNIFIED_DOLT.md       # Doc architecture
│
├── PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md  # Justification modèle émotionnel (v2.2)
│
├── # ═══ v3-alpha (Reconstruction phrase-level) ═
├── ANALYSE_GAPS_RECONSTRUCTION.md     # Diagnostic : peut-on reconstituer un texte ?
├── schema_v3_reconstruction.sql       # Schéma v3 (4 tables + 2 vues)
├── poc_reconstruction_phrases.py      # POC phrase-level (7 étapes)
│
├── # ═══ v2.1 (Validation Gutenberg) ═
├── schema_gutenberg_provenance.sql    # Schéma provenance (5 tables + 3 views)
├── gutenberg_multilingual_validator.py # Pipeline validation 8 étapes
├── test_gutenberg_validation.py       # Tests Gutenberg (39/39)
├── gutenberg_corpus/                  # Textes téléchargés (gitignored)
│   ├── pg11_en.txt                    #   Alice — Carroll (original)
│   ├── pg55456_fr.txt                 #   Alice — Bué (1869)
│   ├── pg19778_de.txt                 #   Alice — Zimmermann (1869)
│   ├── pg28371_it.txt                 #   Alice — Pietrocòla-Rossetti (1872)
│   ├── pg17482_eo.txt                 #   Alice — Kearney (1910, Esperanto)
│   ├── pg46569_fi.txt                 #   Alice — Swan (1906, Finnish)
│   ├── pg4650_fr.txt                  #   Candide — Voltaire (original, 1759)
│   ├── pg19942_en.txt                 #   Candide — English translation
│   ├── pg7109_es.txt                  #   Candide — Spanish translation
│   └── pg52336_fi.txt                 #   Candide — Onerva (Finnish)
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
- ✅ Applique le schéma 3 couches + axes émotionnels (11 tables + 4 views)
- ✅ Seed les 30 primitifs (4 onto + 5 struct + 9 pred + 4 ext + 8 émotionnels)
- ✅ Importe 107 concepts PanLang nettoyés (48 metadata exclus)
- ✅ Classifie en quality tiers (A/B/C) avec audit trail
- ✅ Calcule la couverture des 7 dimensions irréductibles
- ✅ Commit dans Dolt

### Étape 3 : Valider l'import

```bash
python3 test_v2_validation.py   # 48/48 tests ✅
```

## 📊 Schéma v2.2 — 11 Tables + 4 Vues

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
9 dhātu avec mappings cross-frameworks (EMOTION → couche 3c).

| id            | dhātu  | NSM prime         | Vendler aspect | Jackendoff      |
|---------------|--------|--------------------|----------------|-----------------|
| MOUVEMENT     | √gam   | MOVE               | activity       | GO              |
| COGNITION     | √jñā   | THINK, KNOW        | state          | Conceptual      |
| PERCEPTION    | √dṛś   | SEE, HEAR, FEEL    | achievement    | Perceptual      |
| COMMUNICATION | √vac   | SAY                | activity       | Expressive      |
| CREATION      | √kṛ    | MAKE, DO           | accomplishment | CAUSE+BECOME    |
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

### Layer 3c : `emotional_axes` (v2.2)
8 sous-primitifs émotionnels organisés en 4 axes bipolaires, fondés sur la convergence Panksepp (7 systems) / Ekman (6 basic) / Plutchik (8 primary) / Damasio (somatic markers).

| Axe        | Pôle +   | dhātu     | Pôle −   | dhātu      | Circuit neural             |
|------------|----------|-----------|----------|------------|----------------------------|
| APPÉTENCE  | SEEKING  | √iṣ       | FEAR     | √bhī       | VTA→NAcc / Amygdale→PAG    |
| LIEN       | CARE     | √snuh     | GRIEF    | √śuc       | Ocytocine / Opioïdes↓      |
| ASSERTION  | RAGE     | √krudh    | DISGUST  | √jugupsā   | PAG-hypothalamus / Insula  |
| JOUISSANCE | PLAY     | √krīḍ     | TEDIUM   | √glai      | Thalamo-striatal / hypo-DA |

> **Justification** : L'atome EMOTION (√hṛd) unique produisait 0 concept à convergence majoritaire dans la validation Gutenberg. Les 8 sous-primitifs sont ancrés dans les circuits neuraux identifiés par Panksepp (1998/2012) et convergent avec 5 autres cadres théoriques. Voir `PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md` pour la justification complète.

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
| Concepts importés         | 104                   |
| Entrées metadata exclues  | 48                    |
| Tier A (haute qualité)    | 49                    |
| Tier B (qualité moyenne)  | 45                    |
| Tier C (quarantaine)      | 10                    |
| Tier C (retirés)          | 3                     |
| Axes émotionnels          | 8 (4 axes bipolaires) |
| Règles de composition     | 250                   |
| Entrées couverture dim.   | 254                   |
| Issues d'audit            | 38                    |
| Tests validation v2.2     | 48/48 ✅              |

### Validation Gutenberg

| Métrique                  | Valeur                |
|---------------------------|-----------------------|
| Œuvres                    | 2 (Alice, Candide)    |
| Éditions (traductions)    | 10                    |
| Langues                   | 6 (EN, FR, DE, IT, EO, FI) |
| Segments extraits         | 46                    |
| Décompositions atomiques  | 340                   |
| Enregistrements convergence | 202                 |
| Concepts majorités        | 21 (50 détections)    |
| Tests Gutenberg           | 39/39 ✅              |
| **Tests totaux**          | **87/87 ✅**          |

### Issues identifiées

| Type              | Sévérité | Count | Exemple                       |
|-------------------|----------|-------|-------------------------------|
| Tautologie        | warning  | 23    | ÉTOILE = COMMUNICATION        |
| Low validity      | critical | 12    | DÉGOÛT (validity 0.16)        |
| Formule absurde   | critical | 3     | MUSIQUE = DESTRUCTION+MOUVEMENT|

## � Validation Gutenberg — Corpus Multilingue avec Provenance

### Méthodologie

Le modèle PanLang est validé empiriquement sur des œuvres littéraires du Projet Gutenberg traduites en plusieurs langues. Chaque traduction est attribuée à son traducteur avec provenance complète :

```
Œuvre (Carroll/Voltaire) → Édition Gutenberg → Traducteur (nom, époque, année)
                                             → Source (URL, credits, release date)
```

**Principe fondamental** : « Séparer ce qui est commun de ce qui est spécifique » — chaque traducteur ayant sa propre interprétation, on attribue d'abord les décompositions atomiques aux auteurs/traducteurs respectifs, puis on collige les convergences inter-traductions pour identifier les concepts véritablement transversaux.

### Corpus

| Œuvre | Langues | Éditions | Passages-clés |
|-------|---------|----------|---------------|
| **Alice au pays des merveilles** (Carroll, 1865) | EN, FR, DE, IT, EO, FI | 6 | 5 (ouverture, chute, chapelier, chenille, verdict) |
| **Candide** (Voltaire, 1759) | FR, EN, ES, FI | 4 | 4 (ouverture, guerre, autodafé, jardin) |

### Traducteurs et provenance

| Édition | Traducteur | Époque | Année trad. |
|---------|-----------|--------|-------------|
| Alice EN | Lewis Carroll | Victorien | 1865 (original) |
| Alice FR | Henri Bué (1843–1929) | Victorien | 1869 |
| Alice DE | Antonie Zimmermann | Victorien | 1869 |
| Alice IT | T. Pietrocòla-Rossetti | Victorien | 1872 |
| Alice EO | Elfric L. Kearney (1856–1913) | Edwardien | 1910 |
| Alice FI | Anni Swan (1875–1958) | Edwardien | 1906 |
| Candide FR | Voltaire | Lumières | 1759 (original) |
| Candide EN | Inconnu | — | — |
| Candide ES | Inconnu | — | — |
| Candide FI | L. Onerva (1882–1972) | Moderne | — |

### Pipeline de validation (8 étapes)

```bash
cd SANDBOX/dolt-concept-store/
python3 gutenberg_multilingual_validator.py
```

1. **Schema** — Applique 5 tables + 3 vues de provenance
2. **Register** — Enregistre 2 œuvres + 10 éditions avec métadonnées
3. **Download** — Télécharge 10 textes depuis Gutenberg
4. **Segments** — Extrait 46 passages-clés par marqueurs textuels
5. **Decompose** — Décompose chaque segment en atomes PanLang (340 détections)
6. **Convergence** — Calcule la convergence inter-traductions (202 enregistrements)
7. **Report** — Génère le rapport de synthèse
8. **Commit** — Commit dans Dolt

### Résultats de convergence

| Type | Count | Ratio moyen | Description |
|------|-------|-------------|-------------|
| **Majority** | 50 | 52.3% | Concept détecté dans >50% des traductions |
| Minority | 46 | 33.3% | Concept détecté dans 33–50% des traductions |
| Unique | 106 | 19.4% | Concept spécifique à un seul traducteur |

### Top 10 concepts majorités (les plus transversaux)

| Concept | Passages | Convergence moy. | Description |
|---------|----------|-------------------|-------------|
| RÉALISER | 5 | 50.0% | Détecté dans 5/9 passages — le plus répandu |
| RACONTER | 4 | 54.2% | Acte narratif transversal |
| PARTAGER | 4 | 54.2% | Échange, communication |
| EXPLIQUER | 4 | 50.0% | Explication, dialogue |
| COMPRENDRE | 3 | 61.1% | Plus haute convergence moyenne |
| ENTENDRE | 3 | 61.1% | Perception auditive/compréhension |
| COMMANDER | 3 | 55.6% | Autorité, pouvoir |
| VOIR | 3 | 50.0% | Perception visuelle |
| EXPLORER | 3 | 50.0% | Découverte, curiosité |
| SAVOIR | 3 | 50.0% | Connaissance |

### Enseignements clés

1. **Aucun concept n'atteint 100% d'universalité** avec le mapping strict des 46 concepts v2 — c'est un résultat honnête qui reflète la complexité réelle de la traduction littéraire.

2. **Les concepts cognitifs et communicatifs sont les plus transversaux** (COMPRENDRE, ENTENDRE, EXPLIQUER, RACONTER) — convergence avec les NSM primes THINK, KNOW, SAY.

3. **Les concepts émotionnels sont culturellement spécifiques** (COLÈRE, JOIE, BEAUTÉ souvent uniques à un traducteur) — confirmation de la thèse de Wierzbicka sur les « cultural keywords ». **→ v2.2 : EMOTION atomique remplacé par 8 sous-primitifs neurophysiologiques** pour capturer la granularité émotionnelle (SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM).

4. **Le finnois et l'espéranto posent des défis spécifiques** :
   - Finnois : formes agglutinatives (cas partitif/génitif) nécessitant des marqueurs morphologiquement adaptés
   - Espéranto : encodage x-system dans Gutenberg (cx/sx/ux/gx) au lieu d'Unicode (ĉ/ŝ/ŭ/ĝ)

5. **La richesse du dictionnaire de mots-clés français** favorise la détection dans les traductions françaises — biais méthodologique à corriger en enrichissant les dictionnaires des autres langues.

### Schéma de provenance (5 tables + 3 vues)

```sql
-- Tables
gutenberg_works        -- Œuvres (id, titre, auteur, année)
gutenberg_editions     -- Éditions (traducteur, époque, année, URL Gutenberg)
gutenberg_segments     -- Segments textuels extraits
segment_decompositions -- Décomposition atome par atome
translation_convergence -- Convergence inter-traductions

-- Vues
v_provenance_chain     -- Chaîne complète œuvre → édition → traducteur
v_concept_universality -- Score d'universalité par concept
v_translator_profile   -- Profil atomique par traducteur
```

## �🎓 Fondements Scientifiques

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
11. **Neurosciences affectives** — Panksepp (7 systèmes), Ekman (6 basic), Plutchik (8 primary), Damasio (marqueurs somatiques), Barrett (émotions construites), LeDoux (circuits de survie)

Voir : `UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md` (72 références, 886 lignes)
Voir : `PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md` (justification émotionnelle, 24 références)

## 🚧 Prochaines Étapes

### Court terme (fait)
- [x] Combler les gaps STRUCTURE et SITUATION dans les formules PanLang
- [x] Validation empirique sur corpus Gutenberg multilingue (10 traductions, 6 langues)
- [x] Axes émotionnels v2.2 : 8 sous-primitifs neurophysiologiques
- [x] Analyse des gaps de reconstruction (ANALYSE_GAPS_RECONSTRUCTION.md)
- [x] POC v3-alpha : phrase-level avec attribution mot→atome ciblée
- [x] Profils stylistiques par traducteur (TTR, hapax, ponctuation)

### Court terme (à faire)
- [ ] Enrichir les dictionnaires de mots-clés (DE, IT, ES, EO, FI) pour réduire le biais français
- [ ] Ajouter des œuvres supplémentaires (Pinocchio, Grimm, Divine Comédie)
- [ ] Intégrer les 50 NSM primes manquants (logiques, déictiques, substantifs)
- [ ] Étendre le POC v3 à tous les segments (pas seulement ch01_falling)

### Moyen terme — Vers la reconstruction
- [ ] Alignement phrase-par-phrase inter-traductions (Hunalign/Bleualign)
- [ ] Arbres de dépendances syntaxiques par phrase (via spaCy/Stanza)
- [ ] Rôles sémantiques (AGENT, PATIENT, GOAL, etc.)
- [ ] Implémenter l'analyzer Rust avec output JSON → Dolt v2
- [ ] Validation cross-framework (NSM, Jackendoff, Pustejovsky)
- [ ] Analyse statistique de la convergence (bootstrap, intervalles de confiance)

### Long terme — Codec sémantique complet
- [ ] Formule de reconstruction : graphe_sémantique + syntaxe + style → texte
- [ ] Expérimentation de nouveaux primitifs via branches Dolt
- [ ] Publication du dataset versionné sur DoltHub
- [ ] Alignement avec BabelNet / WordNet / FrameNet
- [ ] Extension du corpus à 20+ langues (langues non-indo-européennes)

## 📝 Historique des Versions

| Version | Date       | Description                                              | Tests       |
|---------|------------|----------------------------------------------------------|-------------|
| v0.1    | 2025-01-15 | POC initial : 7 dhātu, dédup cross-langue                | ✅           |
| v1.0    | 2025-02    | Unified storage : 17 tables, 3-tier, cascade, ACL        | 34/34 ✅     |
| v2.0    | 2025-02    | 3-layer universals : 23 primitifs, 107 concepts          | 38/38 ✅     |
| v2.0.1  | 2025-02    | Revalidation Tier C : 3 retrait, 10 quarantaine          | 44/44 ✅     |
| v2.1    | 2025-02    | Validation Gutenberg : 10 traductions, 6 langues, 46 segments | 82/82 ✅     |
| **v2.2**| **2025-02**| **Axes émotionnels : 8 sous-primitifs neurophysiologiques (Panksepp/Ekman/Plutchik/Damasio), EMOTION → couche 3c, 30 primitifs** | **87/87 ✅** |
| v3-alpha| 2026-02 | Analyse gaps reconstruction + POC phrase-level (122 phrases, 176 attributions mot→atome, profils stylistiques, 4 tables + 2 vues) | 87/87 ✅ |

## 📄 Licence

Ce sandbox fait partie du projet PaniniFS.
Voir `LICENSE` à la racine du projet.

---

**Auteur:** PaniniFS Core Team  
**Version:** 2.2.0 + v3-alpha  
**Date:** 2026-02-17  
**Status:** Proof of Concept (empirically validated + neurophysiological grounding + reconstruction gap analysis)

# 📋 Registre des expérimentations — PaniniFS Dolt Concept Store

> **Créé** : 2026-02-19
> **Maintenu par** : équipe Panini (humains + agents)
> **Dernière mise à jour** : 2026-02-19 (roadmap NA-004 COMPLET ✅)
> **Référence journal** : [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md)

---

## 📌 Pourquoi ce registre

L'écosystème Panini a accumulé **3 systèmes de numérotation indépendants**
pour ses « phases » et « expérimentations », sans aucun document central les
reliant. Ce registre les unifie et documente chaque étape avec :
- Numéro de session / version
- Commit(s) Git correspondant(s)
- Entrée journal associée
- Résultats et métriques

### Les 3 systèmes historiques (avant ce registre)

| Système | Repo | Portée | Numérotation |
|---------|------|--------|-------------|
| **A — Spec Kit** | Panini-FS | Implémentation Rust initiale | Phases 1→10.8.3, puis MASSIVE |
| **B — Migration** | Panini | Réorganisation repo | P1→P4, puis 6→7 |
| **C — Sessions Dolt** | Panini-FS SANDBOX | Sessions agent concept store | 17, 35, 36 (trou 18–34) |

Ce registre adopte une numérotation **unifiée par version sémantique** (v0.1, v1.0, v2.x, v3.x)
et par **identifiant d'expérience** (E1, E2, ...) pour les hypothèses formelles.

---

## 🧪 Expériences formelles (hypothèses à vérifier)

### E1 — FORMAT-SEMANTIC UNIVERSALITY

| Champ | Valeur |
|-------|--------|
| **Hypothèse** | Tout format de fichier peut être décomposé en atomes sémantiques universels et reconstruit fidèlement |
| **Repo** | Panini (branche `gpu-experiments`, mergée dans `main`) |
| **Code** | `experiments/e1_format_decomposition.py` (410 lignes, 4 phases) |
| **Notebook** | `notebooks/E1_COLAB_EXECUTOR.ipynb` |
| **Corpus** | 100 fichiers auto-générés, 5 formats (CSV, JSON, PNG, PDF, edge_cases) |
| **Commit résultat** | `7d9700ac` (2025-12-24) |
| **Commit merge** | `f60f54c1` (2026-01-05) |
| **Résultat** | ✅ HYPOTHESIS SUPPORTED — fidélité 99.95% |
| **Documentation** | `README_E1_COLAB.md`, `E1_COMPLETION_REPORT.md`, `outputs/e1_results.json` |

**Limites identifiées** (session 2026-02-18) :
- Phase 3 mesure le temps de lecture fichier, pas une vraie décomposition sémantique
- Phase 4 calcule la fidélité par ratio structure/taille, pas par reconstruction effective
- Corpus auto-généré (5.6 KB total) — très petit
- **Ce qui est prouvé** : détection de format + intégrité par hash SHA256
- **Ce qui reste à prouver** : décomposition sémantique → reconstruction bit-perfect

### E2 — RECONSTRUCTION BIT-PERFECT

| Champ | Valeur |
|-------|--------|
| **Hypothèse** | $\forall f \in \text{Files}, \text{reconstruct}(\text{decompose}(f)) = f$ vérifié par SHA256 |
| **Statut** | 📋 Spécifié — données préparatoires collectées (v4.2d) |
| **Corpus prévu** | Alice EN (26 521 mots), Alice FR (26 272 mots), + 8 fichiers supplémentaires |
| **Critère de succès** | 100% reconstruction identique (SHA256 match) |
| **Pré-requis validés (v4.2)** | |
| • Sérialisation | ✅ `semantic_serializer.py` export/import JSON (schema v1.0) |
| • Comparaison | ✅ Cross-language universality score 0.8671 (Alice EN↔FR) |
| • Atomes universels | 13/17 partagés EN↔FR, couvrant 79.6% des détections |
| • Atomes les + stables | COMMUNICATION (CV=0.019), MOUVEMENT (CV=0.022), GRAND (CV=0.037) |
| • Seuil E2 | ≥15 atomes universels recommandés → besoin de 2 atomes ENT/QUAL en plus |

**Protocole E2 proposé** :

1. **Phase 1 — Corpus bilingue** : Analyser ≥5 paires de traductions (Gutenberg)
   pour stabiliser le set d'atomes universels
2. **Phase 2 — Atom encoding** : Encoder chaque paragraphe comme vecteur d'atomes
   (proportions normalisées) + concepts + opérateurs
3. **Phase 3 — Reconstruction** : À partir du vecteur d'atomes, générer un texte
   dans la langue cible et comparer sémantiquement
4. **Phase 4 — Mesure** : Scoring BLEU/BERTScore du texte reconstruit vs original

**Note** : La reconstruction « bit-perfect » au sens strict (SHA256 match)
n'est pas réaliste pour du texte naturel. L'objectif réel est de démontrer
que la décomposition sémantique préserve le sens (mesuré par les métriques
de similarité sémantique), pas les bits exacts.

---

## 📦 Versions du Concept Store (SANDBOX/dolt-concept-store)

### v0.1 — POC initial (2025-01-15)

| Champ | Valeur |
|-------|--------|
| **Contenu** | 7 dhātu, déduplication cross-langue |
| **Tests** | ✅ |
| **Commit** | (avant historique Dolt SANDBOX) |
| **Journal** | — |

### v1.0 — Unified Storage (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Stockage unifié Dolt : 17 tables, 3-tier (public/confidentiel/privé), cascade, ACL |
| **Tests** | 34/34 ✅ |
| **Commits** | `b795b81` (unified storage), `6f16e92` (ACL 14/14), `ab9ee26` (cascade 20/20) |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) |
| **Fichiers clés** | `dolt_unified_storage.py`, `setup_dolt_acl.py`, `test_branch_acl.py`, `test_cascade_topology.py` |
| **Documentation** | `ARCHITECTURE_UNIFIED_DOLT.md` |

### v2.0 — 3-Layer Universals (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | 23 primitifs sémantiques universels, 107 concepts importés depuis PanLang, ontologie 4 catégories |
| **Primitifs** | 15 PROC + 8 racine (EXISTENCE, COGNITION, PERCEPTION, COMMUNICATION, CREATION, DESTRUCTION, EVAL, EMOTION) |
| **Tests** | 38/38 ✅ |
| **Commit** | `454425d` |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) §6 |
| **Fichier clé** | `import_panlang_v2.py` |
| **Revue interdisciplinaire** | `UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md` (72 références) |

### v2.0.1 — Revalidation Tier C (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Retrait de 3 substantifs, quarantaine de 10 concepts douteux |
| **Tests** | 44/44 ✅ |
| **Commit** | `3618c50` |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) §7 |
| **Fichier clé** | `quarantine_tier_c.py` |
| **Session historique** | « Phase 17 » (audit qualité mentionné dans la revue interdisciplinaire) |

### v2.1 — Validation Gutenberg (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Validation empirique sur corpus Gutenberg multilingue : 10 traductions, 6 langues (EN, FR, DE, IT, EO, FI), 46 segments, provenance édition/traducteur/époque |
| **Tests** | 82/82 ✅ |
| **Commits** | `567195f` (validation), `dfa1a5e` (fix mappings), `85059c9` (synthèse) |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) §8 |
| **Fichiers clés** | `gutenberg_multilingual_validator.py`, `schema_gutenberg_provenance.sql` |
| **Documentation** | `SYNTHESE_GUTENBERG_VALIDATION.md` |
| **Corpus** | Alice (6 langues) + Candide (4 langues) |

### v2.2 — Axes émotionnels (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | 8 sous-primitifs neurophysiologiques (Panksepp/Ekman/Plutchik/Damasio) : SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM. EMOTION atomique → couche 3c. 30 primitifs total. |
| **Tests** | 87/87 ✅ |
| **Commit** | `0b31743` |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) §9 |
| **Fichiers clés** | `import_panlang_v2.py`, `gutenberg_multilingual_validator.py` (ATOM_KEYWORDS ×8) |
| **Documentation** | `PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md` |

### v3-alpha — Analyse gaps + POC phrase-level (2026-02-17)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Analyse des gaps de reconstruction (quelles informations se perdent dans la décomposition), POC d'analyse au niveau phrase (122 phrases, 176 attributions mot→atome) |
| **Tests** | 87/87 ✅ |
| **Commit** | `a7ca994` |
| **Journal** | [2026-02-17-reconstitue-pipeline-semantique-complet.md](../../Copilotage/journal/2026-02-17-reconstitue-pipeline-semantique-complet.md) §10 |
| **Fichiers clés** | `poc_reconstruction_phrases.py`, `schema_v3_reconstruction.sql` |
| **Documentation** | `ANALYSE_GAPS_RECONSTRUCTION.md` |

### v3 — Moteur 7 couches multilingue (2026-02-18)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Analyse à 7 couches au niveau paragraphe : syntaxe, alignement mot-atome, morphologie, registre/style, discours, prosodie, référents culturels. 445 paragraphes, 7 langues, ~1515 choix de traducteur. Pont morpho-sémantique. 100% couverture paragraphes (87→0 orphelins). |
| **Tests** | 159/159 ✅ (72 seven_layers + 87+90 morpho_bridge) |
| **Commits** | `1561454` (moteur), `1b381ac` (pont morpho), `f94195c` (100% couverture) |
| **Journal** | [2026-02-18-reconstitue-seven-layers-100pct.md](../../Copilotage/journal/2026-02-18-reconstitue-seven-layers-100pct.md) |
| **Fichiers clés** | `seven_layers_engine.py` (2296→2436 lignes), `morpho_semantic_bridge.py`, `schema_v3_seven_layers.sql` |
| **Tables** | 12 tables + 3 vues SQL |

### v2.3 — 7 atomes ABS + Concept Revision (2026-02-18)

| Champ | Valeur |
|-------|--------|
| **Contenu** | 7 atomes abstraits (RELATION, STRUCTURE, INVARIANCE, RÉCURRENCE, DUALITÉ, MESURE, ORDRE) pour couvrir mathématiques/physique. Fix bug FK critique (`REPLACE INTO` → `DELETE` children d'abord). 27 formula overrides. CONCEPT_MAPPINGS 29→78. |
| **Tests** | 162/162 ✅ |
| **Commits** | `0a72ac8` (7 ABS), `0a52283` (seed fix), `68925bd` (v2.3 revision) |
| **Journal** | [2026-02-18-hauru-v23-concept-revision.md](../../Copilotage/journal/2026-02-18-hauru-v23-concept-revision.md) |
| **Session historique** | « Phase 35 » |
| **Fichiers clés** | `import_panlang_v2.py` (6 dicts étendus), `gutenberg_multilingual_validator.py` (+608 keywords) |
| **Documentation** | `elargissement-horizon-mathematiques-physique.md` (RFC) |
| **Métriques** | Concepts activés : 29→76 (+262%), 0 formules dupliquées |

### v2.4 — ABS Activation (2026-02-18)

| Champ | Valeur |
|-------|--------|
| **Contenu** | Activation des atomes ABS dans le corpus littéraire (les mots comme "encore", "même", "entre" détectent les ABS dans Alice/Candide). +17 concepts ABS-dépendants. Fix MÉLANCOLIE (TEDIUM≠DESTRUCTION). |
| **Tests** | 162/162 ✅ |
| **Commit** | `bf938d1` |
| **Journal** | [2026-02-18-hauru-v24-abs-activation.md](../../Copilotage/journal/2026-02-18-hauru-v24-abs-activation.md) |
| **Session historique** | « Phase 36 » |
| **Fichiers clés** | `seven_layers_engine.py` (CONCEPT_MAPPINGS 78→95, step4b ajouté) |
| **Métriques** | Concepts activés : 76→92/104 (+21%), 28 overrides, 0 mismatches CM↔Dolt |

### v2.4b — Corpus Quality Upgrade (2026-02-19, ✅ TERMINÉ)

| Champ | Valeur |
|-------|--------|
| **Contenu** | `step4b_corpus_quality_upgrade()` : reclassification empirique des tiers de qualité basée sur les détections réelles dans le corpus. Seuils : ≥20 détections→A-tier, ≥5→B-tier. |
| **Statut** | ✅ **TERMINÉ** — PID 668992 terminé normalement |
| **Commit Dolt** | `hdc7787s` (HEAD) |
| **Journal** | [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md) §12 |
| **Fichiers clés** | `seven_layers_engine.py` (step4b, lignes 2309–2395) |
| **Résultats finaux** | Tiers avant: A=49, B=46, C=9 → **après step4b: A=78, B=25, C=2**. +29 concepts promus empiriquement. C restants: PROXIMITÉ (4 dét.), DÉGOÛT (1 dét.) |
| **Métriques Dolt finales** | 105 concepts, 42 tables+vues. Score moyen: 0.673. A avg=0.747, B avg=0.480, C avg=0.190. Catégories: PROC=81, ABS=13, QUAL=9, ENT=2 |

---

## 📐 Notes architecturales

### NA-001 — Étude LLVM (2026-02-19) : ❌ Non pertinent

| Champ | Valeur |
|-------|--------|
| **Question** | LLVM (IR, JIT, passes) serait-il utile pour PaniniFS ? |
| **Verdict** | ❌ Non. Mismatch fondamental : LLVM = infrastructure de compilation de code. PaniniFS = transformation de données. |
| **Journal** | [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md) §7 |

**Raisons clés :**
- LLVM IR représente du code exécutable (SSA, registres, flux de contrôle) ≠ atomes sémantiques
- JIT : latence 5-50ms = budget FUSE entier. Hot paths PaniniFS sont I/O-bound, pas compute-bound
- Rust compile déjà via LLVM → LTO/PGO disponibles sans dépendance explicite
- Passes custom LLVM : 6-12 mois d'apprentissage pour bénéfice nul

**Stack Rust recommandée :**

| Besoin | Outil recommandé | Alternative |
|--------|-------------------|-------------|
| Parsing binaire (chunker) | `winnow` ou `nom` | `binrw` / `deku` (déclaratif) |
| Plugins format extensibles | **Wasmtime + WIT** (WASM) | Extism (plus simple) |
| Fingerprinting | `sha2` (accéléré hardware) | — |
| Multi-pattern matching | `aho-corasick` | — |
| Full-text search | Tantivy | — |
| FUSE filesystem | `fuser` | — |
| Cache local | RocksDB | — |
| Texte structuré | Tree-sitter (🟡 optionnel) | — |
| Optimisation LLVM | `cargo` LTO + PGO (via rustc) | — |

### NA-002 — Stratégie WASM unifiée : serveur + browser + visualisation (2026-02-19)

| Champ | Valeur |
|-------|--------|
| **Question** | Peut-on aller plus loin que les plugins serveur avec WASM ? |
| **Verdict** | ✅ Oui — WASM unifie 3 surfaces avec le même code |
| **Journal** | [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md) §8 |

**Constat** : WASM n'est pas juste une solution de plugins côté serveur. C'est une
**stratégie de convergence** qui unifie 3 surfaces d'exécution avec le même code Rust :

```
                    panini-core (Rust)
                         │
                    compile to .wasm
                    ┌────┴────┐
                    │         │
              ┌─────▼──┐  ┌──▼──────────────────────┐
              │ Server │  │       Browser            │
              │ (WASI) │  │  (wasm-bindgen/wasm-pack) │
              └────────┘  └──────────────────────────┘
                    │              │
              ┌─────▼──┐    ┌─────▼──────────────────┐
              │ Format │    │ 3 cibles navigateur :   │
              │ parsers│    │  1. PaniniFS-Web (démo) │
              │ plugins│    │  2. Graphes de concepts │
              │        │    │  3. Docs interactives   │
              └────────┘    └────────────────────────┘
```

**Surface 1 — PaniniFS-Web** (version navigateur stabilisée) :
- Le même `panini-core` qui tourne en natif/FUSE peut s'exécuter dans le browser
- Démonstration en ligne : déposer un fichier → voir sa décomposition en atomes en temps réel
- Pas de serveur requis — tout calcul local dans le browser (privacy by design)
- Technologie : `wasm-pack` + `wasm-bindgen` compilent le crate Rust directement

**Surface 2 — Visualisation des graphes de concepts** :
- Les 104 concepts, leurs formules d'atomes, et les liens de co-occurrence
  forment un graphe riche qui gagne à être visualisé interactivement
- Le moteur sémantique (détection d'atomes, calcul de distances) tourne en WASM
- Le rendu graphique utilise une lib JS native (D3.js, Cytoscape.js, ou Sigma.js)
- L'`AtomExplorer.tsx` existant dans `web-ui/` pourrait évoluer vers cet explorateur
- Cas d'usage : naviguer visuellement les résultats Gutenberg (7 langues, 95 concepts, 1515 choix traducteur)

**Surface 3 — Documentation dynamique MkDocs** :
- MkDocs supporte les `extra_javascript` — des composants WASM peuvent enrichir les pages de docs
- Exemples interactifs dans la doc : "essayez la décomposition sur ce texte"
- Visualisation live des arbres de décomposition dans les pages de recherche
- Les mêmes modules WASM que le site principal, embarqués dans la doc

**Stack technique unifiée** :

| Couche | Côté serveur | Côté browser |
|--------|-------------|-------------|
| Moteur sémantique | Rust natif ou WASI | `wasm-pack` → WASM |
| Format parsers | Wasmtime (WASI plugins) | Même `.wasm` via Web APIs |
| Graphes de concepts | Dolt SQL → JSON API | WASM calcul + D3.js/Cytoscape.js rendu |
| Documentation | MkDocs (statique) | `extra_javascript` + WASM interactif |
| UI framework | — | React (existant `web-ui/`) ou vanilla JS |

**Avantage clé** : écrire `panini-core` **une seule fois** en Rust, le compiler pour
3 cibles (`x86_64-unknown-linux-gnu`, `wasm32-wasi`, `wasm32-unknown-unknown`) et
servir les mêmes algorithmes partout. Pas de réécriture JavaScript.

### NA-003 — Inférence symbolique parallèle, réseaux bayésiens & modèles probabilistes (2026-02-19)

| Champ | Valeur |
|-------|--------|
| **Question** | Peut-on ajouter une couche de raisonnement formel et probabiliste sur le graphe de concepts dhātu ? |
| **Verdict** | ✅ Oui — 3 axes complémentaires à l'approche déterministe actuelle |
| **Journal** | [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md) §10 |
| **Inventaire** | [IDEAS_INVENTORY.md](../../Copilotage/IDEAS_INVENTORY.md) #131-133 |

**Constat** : Le pipeline actuel (`seven_layers_engine.py`, `import_panlang_v2.py`)
fonctionne de manière **purement déterministe** : chaque mot est mappé à un ou
plusieurs atomes via des dictionnaires de keywords. Cette approche a des limites :
- La polysémie est résolue par heuristique (#21), pas par probabilité
- Les formules de concepts (ex : `AMOUR = FEEL + CARE + RELATE`) sont fixées manuellement
- Il n'y a aucune propagation d'inférence dans le graphe (si on ajoute un atome,
  quelles conséquences sur les concepts voisins ?)
- L'incertitude de chaque attribution mot→atome n'est pas quantifiée

**Axe 1 — Moteur d'inférence symbolique massivement parallèle** :

```
        Graphe de concepts (104+ nœuds)
              ┌──────────┐
              │  Règles  │ ← ontologie 4 catégories (ENT, PROC, QUAL, ABS)
              │ formelles│ ← formules d'atomes (AMOUR = FEEL + CARE + ...)
              │   (FOL)  │ ← contraintes de co-occurrence
              └────┬─────┘
                   │
         ┌─────────▼─────────┐
         │   Moteur Rete /   │ ← chaînage avant : propager les détections
         │   Datalog compilé │ ← chaînage arrière : quels atomes manquent ?
         │   (massivement    │ ← résolution de contraintes
         │    parallèle)     │ ← détection de contradictions
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  GPU / WASM workers│ ← 104 concepts × N paragraphes en parallèle
         └───────────────────┘
```

- **Objectif** : Inférer automatiquement les formules d'atomes manquantes, détecter
  les contradictions ontologiques, propager les conséquences d'un ajout d'atome.
- **Inspirations** : Prolog/Datalog compilé, miniKanren, Rete network, Answer Set
  Programming (ASP), Soufflé Datalog.
- **Lien Rust** : `crepe` (Datalog compilé en Rust), `scryer-prolog` (Prolog en Rust),
  ou implémentation custom avec `petgraph` (déjà dans `Cargo.toml`).
- **Lien WASM** : le moteur d'inférence compilé en WASM peut tourner dans le browser
  pour de l'inférence interactive dans la documentation (NA-002 surface 3).

**Axe 2 — Réseaux bayésiens sur les dhātu** :

```
     Corpus Gutenberg (7 langues, 445 paragraphes)
              │
              ▼
     Comptage co-occurrences atome × atome
              │
              ▼
     ┌────────────────────────┐
     │  Apprentissage de      │
     │  structure bayésienne  │ ← PC algorithm / score-based (BIC, K2)
     │  DAG causal dhātu      │
     └───────────┬────────────┘
                 │
                 ▼
     P(atome_i | contexte) pour chaque mot
```

- **Objectif** : Modéliser les co-occurrences d'atomes comme un réseau bayésien
  (DAG causal). Estimer $P(\text{atome}_i \mid \text{contexte})$ pour la
  désambiguïsation sémantique (remplacement de l'heuristique polysémie #21).
- **Applications** : résolution de polysémie, prédiction du tier de qualité d'un
  concept, détection d'anomalies dans les formules, suggestion de nouveaux concepts.
- **Données** : les 445 paragraphes × 7 langues du corpus Gutenberg fournissent déjà
  les co-occurrences atome-atome nécessaires à l'apprentissage de structure.
- **Libs candidates** : `pgmpy` (Python, immédiat), `bnlearn` (R), ou implémentation
  Rust custom pour l'embarquement WASM.

**Axe 3 — Modèles probabilistes pour la sémantique** :

- **Topic models** (LDA, Embedded Topic Models) sur les séquences d'atomes → découvrir
  des « thèmes dhātu » émergents (cluster de concepts non prévus par l'ontologie).
- **CRF** (Conditional Random Fields) sur les séquences mot→atome → modéliser les
  dépendances contextuelles entre attributions consécutives (le mot « encore » est
  RÉCURRENCE ou ITER ? → dépend du mot précédent).
- **Modèles de mélange** par langue/registre/époque → profils sémantiques typés
  (ex : français littéraire XVIIIe vs anglais technique XXIe).
- **Quantification de l'incertitude** : chaque attribution mot→atome reçoit une
  confiance $\in [0,1]$ au lieu d'un mapping déterministe binaire.
- **Complément naturel** à `seven_layers_engine.py` : la couche probabiliste s'ajoute
  au-dessus des 7 couches existantes sans les remplacer.

**Synergie entre les 3 axes** :

| Axe | Entrée | Sortie | Interagit avec |
|-----|--------|--------|----------------|
| Symbolique | Ontologie + règles formelles | Inférences logiques, contradictions | Graphes de concepts (#38, #48) |
| Bayésien | Corpus + co-occurrences | $P(\text{atome} \mid \text{contexte})$ | Polysémie (#21), tiers qualité (v2.4b) |
| Probabiliste | Séquences mot→atome | Clusters thématiques, confiance | 7 couches (v3), reconstruction (E2) |

Les 3 axes convergent vers la même cible : **remplacer les mappings déterministes
manuels par un système appris et probabiliste**, tout en gardant la transparence
symbolique (explicabilité des décisions = avantage majeur vs pure deep learning).

### NA-004 — Roadmap priorisé : Linguistique → Médias texte (2026-02-19)

| Champ | Valeur |
|-------|--------|
| **Question** | Quel ordre d'exécution pour maximiser la valeur du pipeline sémantique ? |
| **Verdict** | ✅ Priorité 1 : compléter le modèle linguistique. Priorité 2 : connecter les médias texte. |
| **Journal** | [2026-02-19-hauru-experiment-registry.md](../../Copilotage/journal/2026-02-19-hauru-experiment-registry.md) §13 |

**Constat de l'audit du 2026-02-19** :

Le pipeline sémantique est coupé en deux moitiés déconnectées :

```
MOITIÉ A — Le moteur linguistique (fonctionne) :
  Texte brut (.txt) → seven_layers_engine.py → 7 couches → atomes → Dolt
  • 24 atomes (PROC=9, ABS=7, émotion=8)
  • 95 concepts, 1831 keywords, 7 langues
  • 105 concepts en Dolt : A=78, B=25, C=2

MOITIÉ B — Le chunker binaire (fonctionne séparément) :
  Fichier binaire → semantic_chunker.py → chunks binaires (PNG, JPEG, MP4, PDF…)
  • 13 grammaires de format
  • PDF : magic number + split obj/endobj (pas d'extraction de texte)
  • EPUB, DOCX, ODT : rien du tout

LE PONT MANQUANT :
  PDF → [??? extraction texte ???] → texte brut → seven_layers_engine → atomes
```

#### Priorité 1 — Compléter le modèle linguistique (v2.5 → v2.7)

L'ontologie déclare 4 catégories mais seules 2 ont des atomes :

| Catégorie | Atomes actuels | Manque | Impact |
|-----------|---------------|--------|--------|
| **PROC** | 9 + 8 émotions = 17 | — | ✅ Couvert |
| **ABS** | 7 | — | ✅ Couvert |
| **ENT** | 0 | 🔴 Critique | Pas de primitifs pour les entités (objets, substances, lieux) |
| **QUAL** | 0 | 🔴 Critique | Pas de primitifs pour les qualités (couleur, taille, température) |

Sans ENT et QUAL, les concepts comme POISSON, BEAU, GRAND, FEU sont approximés
avec des atomes PROC/ABS — une béquille, pas une solution.

**v2.5 — Atomes ENT (entités)** — ✅ IMPLÉMENTÉ (2026-02-19)

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 2.5a | Identifier 5 primitifs ENT : CHOSE (√dhṛ), AGENT (√jan), CORPS (√tan), LIEU (√vas), MATIÈRE (√bhū) | ✅ |
| 2.5b | Mappés dans les 6 dictionnaires (DIMENSIONS, NSM, JACKENDOFF, PUSTEJOVSKY, DHATU) | ✅ |
| 2.5c | Keywords ENT dans `gutenberg_multilingual_validator.py` (×7 langues, ~100 mots/atome) | ✅ |
| 2.5d | CONCEPT_MAPPINGS : 18 re-décompositions + 10 nouveaux concepts (95→105) | ✅ |
| 2.5e | Validation croisée 3 fichiers : syntaxe + imports + compute_primary_category → ENT | ✅ |
| 2.5f | Relancer le pipeline sur le corpus Gutenberg, vérifier les tiers | ✅ (18.3s, BEAU B→A) |

**v2.6 — Atomes QUAL (qualités)** ✅ IMPLÉMENTÉ

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 2.6a | 5 primitifs QUAL : BON (√śubh), GRAND (√bṛh), VRAI (√sat), INTENSE (√tīv), ANCIEN (√pur) | ✅ |
| 2.6b | Mappés dans les 6 dictionnaires (DIMENSIONS, NSM, JACKENDOFF, PUSTEJOVSKY, DHATU) | ✅ |
| 2.6c | Keywords QUAL dans `gutenberg_multilingual_validator.py` (×7 langues, ~20 mots/atome = 700 mots) | ✅ |
| 2.6d | CONCEPT_MAPPINGS : 9 concepts améliorés + 15 nouveaux = 120 concepts total | ✅ |
| 2.6e | Validation corpus : 18.3s, 445/445 para, BON=159, INTENSE=114, GRAND=96, VRAI=80, ANCIEN=46 | ✅ |

**v2.7 — Opérations structurelles + WSD** ✅ `2025-02-19` commit pending

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 2.7a | Jackendoff : 6 nouveaux mappings (ORIENT, INCH, HAVE, AFFECT, STAY, AMOUNT) → 11/35 mapped | ✅ |
| 2.7b | WSD POS-aware : `align_words_to_atoms()` collecte TOUS les candidats, ranke par POS→catégorie (VERB→PROC, NOUN→ENT, ADJ→QUAL) | ✅ |
| 2.7c | Opérations structurelles : `detect_structural_operators()` détecte NEG/QUANT/MOD dans ±3 mots (7 langues, lexiques multilingues) | ✅ |
| 2.7d | Concepts annotés : `detect_paragraph_concepts()` reçoit flags negated/quantified/modal, NEG réduit confiance ×0.7 | ✅ |
| 2.7e | Validation : 18.8s, 445/445 para, A=80 (+2), B=24, C=1, score 0.667 (+0.017) | ✅ |
| 2.7f | Métriques WSD : 3.6% mots désambiguïsés, 71 ops structurelles / 50 paragraphes (NEG=51, QUANT=11, MOD=9) | ✅ |

**Critère de succès Priorité 1** :
- ✅ 4 catégories ontologiques couvertes (ENT=5, PROC=9+8, QUAL=5, ABS=7 — 35 atomes total)
- ✅ ≥120 concepts (120 atteints en v2.6)
- ✅ WSD contextuel via POS tags (23 disambiguations / 638 atoms sur échantillon 50 para)
- ⚠️ 11/35 Jackendoff mappés (24 restent None — limites intrinsèques du modèle de Jackendoff sur émotions/qualités)

#### Priorité 2 — Médias texte : connecter le pont (v4.0 → v4.2)

Objectif : qu'un fichier PDF ou EPUB entre d'un côté, et que des atomes
sémantiques sortent de l'autre.

**v4.0 — Extracteur de texte multi-format** ✅

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 4.0a | Installé `pdfminer.six`, `ebooklib`, `python-docx`, `langdetect` (pip3) | ✅ |
| 4.0b | Créé `text_extractor.py` (~420 lignes) : extracteur unifié PDF/EPUB/DOCX/HTML/MD/TXT | ✅ |
| 4.0c | Pipeline PDF : `pdfminer.six` extract_pages → page par page avec numéros | ✅ |
| 4.0d | Pipeline EPUB : `ebooklib` → chapitres XHTML → BS4 → paragraphes avec titres h1/h2/h3 | ✅ |
| 4.0e | Pipeline HTML : BS4 → suppression script/style/nav, préférence article/main/body | ✅ |
| 4.0f | Pipeline Markdown : `markdown-it-py` → parsing tokens, headings, paragraphes | ✅ |
| 4.0g | Pipeline DOCX : `python-docx` → détection headings, extraction paragraphes | ✅ |
| 4.0h | Pipeline TXT : `chardet` encoding detection, stripping header/footer Gutenberg (case-insensitive) | ✅ |
| 4.0i | Tests : README.md→49¶/523w ✅, CONTRIBUTING.md→35¶/346w ✅, Alice Gutenberg→814¶/26521w ✅ | ✅ |

Fonctionnalités transversales :
- `detect_format()` : magic numbers (PDF `%PDF-`, ZIP `PK\x03\x04` → EPUB vs DOCX) + fallback extension
- `ExtractionResult` / `ExtractedParagraph` dataclasses
- `_clean_paragraphs()` : split `\n\n`, normalize whitespace, filtre min_length
- CLI : `python text_extractor.py <fichier> [format]`

**v4.1 — Pont extracteur ↔ moteur d'atomes** ✅

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 4.1a | Créé `document_analyzer.py` (~310 lignes) : orchestrateur fichier → text_extractor → seven_layers_engine | ✅ |
| 4.1b | Détection automatique de langue via `langdetect` (seeded, déterministe) + fallback trigrams, 7 langues supportées | ✅ |
| 4.1c | Analyse paragraphe par paragraphe : syntaxe → atomes (WSD) → morpho → struct_ops → concepts | ✅ |
| 4.1d | Stockage Dolt : table `document_analyses` (14 colonnes), INSERT ON DUPLICATE KEY UPDATE | ✅ |
| 4.1e | CLI : `python document_analyzer.py <fichier> [--lang] [--format] [--store] [--verbose] [--json]` | ✅ |

Résultats de validation :
- README.md (FR) : 49¶, 1.05s, 25 atomes uniques, 18 concepts, 3 WSD, NEG=4/QUANT=3/MOD=1
- Alice in Wonderland 11.txt (EN) : 814¶, 20.4s (41 para/s), 34 atomes, 119 concepts, 593 WSD, NEG=304/QUANT=378/MOD=348
- Stockage Dolt : table créée, requête SQL vérifiée ✅

**v4.2 — Reconstruction et round-trip** ✅

| Sous-étape | Contenu | Statut |
|------------|---------|--------|
| 4.2a | `semantic_serializer.py` : export JSON portable (SemanticExport, schema v1.0) | ✅ |
| 4.2b | Comparaison cross-language Alice EN vs FR : **universality score 0.8671 EXCELLENT** | ✅ |
| 4.2c | Dashboard terminal : overview, score bar, atom/concept/operator breakdown, E2 prep report | ✅ |
| 4.2d | Spec E2 reconstruction rédigée (voir section E2 ci-dessous) | ✅ |

Résultats de la comparaison Alice EN ↔ FR :
- Score d'universalité : **0.8671** (EXCELLENT)
- Cosine similarity atomes : **0.9307**
- Rank correlation atomes : **0.8462**
- Jaccard atomes : 13/17 partagés (76.5%)
- Cosine similarity concepts : **0.8303**
- Jaccard concepts : 11/19 partagés (57.9%)
- Atomes les plus stables (CV) : COMMUNICATION (0.019), MOUVEMENT (0.022), GRAND (0.037)
- 13 atomes universels couvrent **79.6%** des détections
- E2 readiness : ≥15 atomes universels recommandés pour reconstruction

**Critère de succès Priorité 2** : ✅ ATTEINT
- ✅ `python document_analyzer.py mon.pdf` → rapport avec atomes, concepts, tiers
- ✅ Support PDF, EPUB, HTML, Markdown, texte brut, DOCX (6 formats)
- ✅ Détection automatique de langue (langdetect + trigrams, 7 langues)
- ✅ Résultats stockés en Dolt (table `document_analyses`)
- ⚠️ Extraction fidèle : validé sur TXT+MD, PDF/EPUB/DOCX à tester sur plus de fichiers

#### Diagramme du pipeline cible

```
                     ┌──────────────┐
                     │  Fichier     │
                     │  d'entrée    │
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ Format       │ PDF? EPUB? HTML? TXT? MD?
                     │ Detection    │ (magic number + heuristique)
                     └──────┬───────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
        ┌─────▼──┐   ┌─────▼──┐    ┌──────▼─────┐
        │pdfminer│   │ebooklib│    │ BeautifulSoup│
        │  .six  │   │ + BS4  │    │ / markdown  │
        └───┬────┘   └───┬────┘    └──────┬──────┘
            │             │               │
            └─────────────┼───────────────┘
                          │
                   ┌──────▼───────┐
                   │  Texte brut  │
                   │  structuré   │ paragraphes, chapitres
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │  Détection   │ langdetect / trigrams
                   │  de langue   │
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │  seven_      │
                   │  layers_     │ 7 couches × N paragraphes
                   │  engine      │
                   └──────┬───────┘
                          │
              ┌───────────┼──────────┐
              │           │          │
        ┌─────▼──┐  ┌─────▼──┐ ┌────▼─────┐
        │ Atomes │  │Concepts│ │ Rapport  │
        │détectés│  │ mappés │ │ 7 couches│
        └───┬────┘  └───┬────┘ └────┬─────┘
            │           │           │
            └───────────┼───────────┘
                        │
                 ┌──────▼───────┐
                 │  Dolt DB     │
                 │ (stockage)   │
                 └──────────────┘
```

#### Ordre d'exécution recommandé

```
FAIT ✅        v2.5 (atomes ENT)          ← commit b08f91a
     │         v2.6 (atomes QUAL)          ← commit ff1b0df
     │         v2.7 (struct ops + WSD)     ← commit e912f6c
     │
     │     Le modèle linguistique est complet (4 catégories, WSD, ≥120 concepts)
     │
FAIT ✅        v4.0 (text_extractor.py)    ← 420 lignes, 6 formats
FAIT ✅        v4.1 (document_analyzer.py) ← 310 lignes, pipeline E2E validé
FAIT ✅        v4.2 (semantic_serializer)  ← universality 0.87, E2 spec prête
     │
     │     Roadmap NA-004 COMPLET ✅
     │
PROCHAIN       E2 (reconstruction bit-perfect) ← hypothèse formelle
```

---

## 🗺️ Chronologie complète

```
2020-05-29  ─── Création repo PaniniFS (CNAME, doc initiale)
     │
     5 ans de pause
     │
2025-08-15  ─── Renaissance : vision architecturale, gouvernance données
2025-08-17  ─── Publications, Colab GPU, missions autonomes
2025-08-18  ─── Spec Kit Phases 1-10.8.3 → v1.0.0 tag (Rust scaffold)
2025-08-19  ─── Cycles autonomes
2025-08-30  ─── Sessions camping (5 journaux)
2025-09-01  ─── Sessions Copilot (rattrapage, sessions)
2025-09-02  ─── CI Copilotage, auto-labeler, sous-module shared
2025-09-03  ─── Migration MkDocs Pages (24 commits marathon)
2025-09-04  ─── OntoWave rebrand, Playwright e2e, Dhātu v0.1
2025-09-05  ─── OntoWave sous-module, agrégation docs
2025-09-06  ─── Cleanup 3 phases (ECOSYSTEM, DevOps, MAJUSCULES)
     │
     ~2 mois de pause
     │
2025-11-12  ─── Journalisation auto, réorg modules, Cargo.toml
2025-11-13  ─── v0.2.0-0.2.2 : vidéo multi-format, audio fingerprint, web UI
     │
     ~3 mois de pause
     │
2026-02-16  ─── Dolt Concept Store créé (PR #88, agent Copilot)
2026-02-17  ─── Journée marathon : v1.0 → v2.0 → v2.0.1 → v2.1 → v2.2 → v3-alpha
                 (15 commits, Gutenberg, ACL, cascade, émotions, gaps)
2026-02-18  ─── v3 (7 couches) + v2.3 (ABS + revision) + v2.4 (ABS activation)
                 Journal obligatoire, pre-commit hook, reconstitution 10 journaux
2026-02-19  ─── v2.4b en cours (corpus quality upgrade)
                 Création de ce registre d'expérimentations
```

---

## 🔗 Fichiers de documentation associés

| Document | Rôle |
|----------|------|
| [README.md](README.md) | Vue d'ensemble du concept store, architecture, historique versions |
| [ARCHITECTURE_UNIFIED_DOLT.md](ARCHITECTURE_UNIFIED_DOLT.md) | Architecture 3-tier Dolt (branches, ACL, cascade) |
| [UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md](UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md) | Revue 72 références (linguistique, neuro, philo, CS) |
| [PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md](PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md) | Justification des 8 axes émotionnels |
| [SYNTHESE_GUTENBERG_VALIDATION.md](SYNTHESE_GUTENBERG_VALIDATION.md) | Résultats validation multilingue |
| [ANALYSE_GAPS_RECONSTRUCTION.md](ANALYSE_GAPS_RECONSTRUCTION.md) | Gaps identifiés pour reconstruction texte |
| [WIKIPEDIA_TEST.md](WIKIPEDIA_TEST.md) | Plan de test Wikipedia (non exécuté) |
| [../../Copilotage/elargissement-horizon-mathematiques-physique.md](../../Copilotage/elargissement-horizon-mathematiques-physique.md) | RFC extension math/physique |

### Journaux de bord (Copilotage/journal/)

| Date | Fichier | Contenu principal |
|------|---------|-------------------|
| 2026-02-19 | `2026-02-19-hauru-experiment-registry.md` | Création registre, audit documentation |
| 2026-02-18 | `2026-02-18-hauru-v24-abs-activation.md` | v2.4 ABS activation, 92/104 concepts |
| 2026-02-18 | `2026-02-18-hauru-v23-concept-revision.md` | v2.3 revision, 27 overrides, FK fix |
| 2026-02-18 | `2026-02-18-hauru-session-atoms-abs.md` | Session Copilot : ABS atoms, journal, hooks |
| 2026-02-18 | `2026-02-18-reconstitue-seven-layers-100pct.md` | 🔄 v3 moteur 7 couches, 100% couverture |
| 2026-02-17 | `2026-02-17-reconstitue-pipeline-semantique-complet.md` | 🔄 Pipeline complet v2→v3-alpha |
| 2026-02-16 | `2026-02-16-reconstitue-dolt-concept-store.md` | 🔄 Création concept store (PR #88) |

---

## ⚠️ Lacunes documentaires connues

### Trou noir : « Phases 18–34 »

Les journaux mentionnent « Phase 17 » (audit qualité, ~v2.0.1) et « Phase 35 »
(v2.3). Les « phases » 18 à 34 **n'existent probablement pas** — le compteur
semble être un compteur de sessions agent cumulé sur l'ensemble de l'écosystème,
pas spécifique au concept store. Ces sessions non-documentées concernent
vraisemblablement d'autres repos (Panini main, Pensine-Web, etc.).

**Action** : le système de numérotation « Phase N » est **déprécié**. Ce registre
utilise désormais les **versions sémantiques** (v2.3, v2.4, etc.) comme référence
canonique.

### E1 — Validité partielle

L'expérience E1 prouve la détection de format et le hashing, mais **pas** la
décomposition sémantique réelle ni la reconstruction. Voir section E1 ci-dessus.

### Repo Panini main — Documentation parallèle

Le repo Panini a sa propre documentation (ROADMAP_PHASED_4PHASES.md, 
AI_DOCUMENTATION_HUB.md, etc.) qui n'est pas synchronisée avec ce registre.
Une unification est souhaitable mais non urgente.

---

## 📏 Convention de nommage (à respecter désormais)

| Type | Format | Exemple |
|------|--------|---------|
| **Version code** | `vX.Y[.Z]` | v2.4, v3-alpha |
| **Expérience formelle** | `E{N}` | E1, E2 |
| **Journal de bord** | `YYYY-MM-DD-<host>-<description>.md` | 2026-02-19-hauru-experiment-registry.md |
| **Commit message** | `type(scope): description` | `feat(v2.4): activate ABS atoms` |
| ~~Phase N~~ | **DÉPRÉCIÉ** | Utiliser vX.Y à la place |

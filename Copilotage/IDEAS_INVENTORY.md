# 📦 Inventaire complet des idées — Écosystème Panini

> **Créé** : 2026-02-19
> **Méthode** : Audit systématique de 14 repos (Panini, Panini-FS, 12 satellites)
> **Maintenu par** : équipe Panini (humains + agents)
> **Dernière mise à jour** : 2026-02-19
> **Référence** : [journal 2026-02-19](journal/2026-02-19-hauru-experiment-registry.md)

---

## Pourquoi cet inventaire

L'écosystème Panini comporte 14 repos GitHub, ~200 fichiers Markdown, ~150 scripts
Python, et des dizaines de concepts dispersés. Avant cet inventaire, **seulement
les versions du Concept Store** (v0.1→v2.4b) et **2 expériences** (E1, E2) étaient
formellement documentées dans le [EXPERIMENT_REGISTRY.md](../SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md).

Cet audit a révélé **~120+ idées/plans/concepts** dont **~85 n'étaient dans aucun
registre central**, plus 3 nouvelles directions de recherche (inférence symbolique,
réseaux bayésiens, modèles probabilistes). Ce document les inventorie tous, classés
par maturité et domaine.

---

## Légende des statuts

| Statut | Signification |
|--------|---------------|
| ✅ **Fait** | Implémenté, testé, en production |
| 🟢 **MVP** | Prototype fonctionnel, à stabiliser |
| 🟡 **Spec** | Design/spec documenté, pas de code |
| 🔵 **Code stub** | Fichier créé mais vide (0 bytes) ou squelette |
| 🟠 **Idée** | Mentionné dans un doc, pas de spec formelle |
| ❌ **Abandonné** | Explicitement remplacé ou obsolète |
| 📋 **Registre** | Déjà dans EXPERIMENT_REGISTRY.md |

---

## 1. 🔬 Moteur sémantique — Cœur du système

### 1.1 Pipeline de décomposition

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 1 | Moteur 7 couches (syntaxe, morphologie, registre, discours, prosodie, référents, alignement) | Panini-FS | `seven_layers_engine.py` | 📋 v3 | ✅ |
| 2 | Pont morpho-sémantique | Panini-FS | `morpho_semantic_bridge.py` | 📋 v3 | ✅ |
| 3 | Analyse au niveau phrase (122 phrases, 176 attributions) | Panini-FS | `poc_reconstruction_phrases.py` | 📋 v3-alpha | ✅ |
| 4 | Quarantaine tier C (10 concepts douteux isolés) | Panini-FS | `quarantine_tier_c.py` | 📋 v2.0.1 | ✅ |
| 5 | Validation Gutenberg multilingue (6 langues, 46 segments) | Panini-FS | `gutenberg_multilingual_validator.py` | 📋 v2.1 | ✅ |
| 6 | 8 sous-primitifs émotionnels (Panksepp/Ekman/Plutchik/Damasio) | Panini-FS | `import_panlang_v2.py` | 📋 v2.2 | ✅ |
| 7 | 7 atomes ABS (RELATION, STRUCTURE, INVARIANCE, etc.) | Panini-FS | `import_panlang_v2.py` | 📋 v2.3 | ✅ |
| 8 | Corpus quality upgrade (reclassification tiers empirique) | Panini-FS | `seven_layers_engine.py` step4b | 📋 v2.4b | ✅ |

### 1.2 Décomposition de formats

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 9 | Chunker sémantique (13 grammaires, 957 lignes) | Panini-FS | `src/semantic_chunker.py` | ✅ Fait | ❌ Absent |
| 10 | 44 grammaires de format (PNG, JPEG, MP3, PDF, ZIP, WASM, ELF, MIDI…) | Panini | `RUST_PRODUCTION_ROADMAP.md` | 🟡 Spec | ❌ Absent |
| 11 | Audio fingerprinting Shazam-like (constellation map, 482 lignes) | Panini-FS | `src/audio_fingerprint.py` | ✅ Fait | ❌ Absent |
| 12 | Tests vidéo multi-format (MP4, MOV, WebM, AVI) | Panini | `tools/validation/test_video_formats.py` | 🟡 Spec | ❌ Absent |
| 13 | Compression tripartite (sémantique + fractale + anti-récursion) | Panini | `COMPRESSION_TRIPARTITE_DHATU.md` | 🟠 Idée | ❌ Absent |
| 14 | « 100% lossless semantic compression » (publication Nature/Science) | Panini | `STRATEGIE_PUBLICATION_ACADEMIQUE_DHATU_BREAKTHROUGH.md` | 🟠 Idée | ❌ Absent |

### 1.3 Dhātu — Primitifs sémantiques

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 15 | 9 dhātu universels (COMM, ITER, DECIDE, EXIST, EVAL, CAUSE, MODAL, RELATE, FEEL) | Panini | `RAPPORT_DHATU_OPTIMAL.md` | ✅ Fait | ❌ Absent |
| 16 | Géométrie dhātu en espace 9D (cosine distance, inclusion/exclusion) | Panini | `DHATU_GEOMETRY_OPENCOLAB_STRATEGY.md` | 🟢 MVP | ❌ Absent |
| 17 | Primitifs aspectuels (couverture temporelle 100%) | Panini | `src/dhatu/aspect_dhatu.py` | 🟢 MVP | ❌ Absent |
| 18 | Dhātu modaux (possibilité, nécessité) | Panini | `src/dhatu/modal_dhatu.py` | 🟢 MVP | ❌ Absent |
| 19 | Dhātu quantitatifs | Panini | `src/dhatu/quant_dhatu.py` | 🟢 MVP | ❌ Absent |
| 20 | Convertisseur FL↔dhātu (lexique fonctionnel) | Panini | `src/dhatu/convertisseur_fl_dhatu.py` | 🟢 MVP | ❌ Absent |
| 21 | Résolution polysémie contextuelle | Panini | `src/analysis/resolution_polysemie_contextuelle.py` | 🟢 MVP | ❌ Absent |
| 22 | Opérateurs n-aires (trinaires, contraintes) | Panini | `src/analysis/operateurs_trinaires_innovation.py` | 🟢 MVP | ❌ Absent |
| 23 | Système marqueurs onomastiques (noms propres) v7.2 | Panini | `src/core/systeme_marqueurs_onomastiques.py`, `MANUEL_ONOMASTIQUE_v7.2.md` | 🟢 MVP | ❌ Absent |
| 24 | Molecular pattern builder (molécules dhātu) | Panini | `src/corpus/molecular_pattern_builder.py` | 🟢 MVP | ❌ Absent |
| 25 | Atomes ENT et QUAL (entités, qualités — prochaine phase) | Panini-FS | `EXPERIMENT_REGISTRY.md` lacunes | 🟠 Idée | ❌ Absent |
| 26 | Grammaire de requêtes dhātu (JSON/DSL) | Panini-FS | `docs/knowledge-base/systeme-dhatu-primitifs.md` | 🟠 Idée | ❌ Absent |
| 27 | Système tripartite dhātu (compression 3-axes) | Panini | `src/compression/dhatu_tripartite_system.py` | 🟢 MVP | ❌ Absent |

---

## 2. 🦀 Architecture Rust & FUSE

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 28 | FUSE3 virtual filesystem (`/mnt/panini/*`, <100ms latence) | Panini-FS | `Cargo.toml` (`fuser`), spec Multi-Repos | 🟡 Spec | ❌ Absent |
| 29 | RocksDB atom storage (1M+ key-value pairs) | Panini-FS | `Cargo.toml` | 🟡 Spec | ❌ Absent |
| 30 | Tantivy fulltext search (20+ langues, <50ms) | Panini-FS | `Cargo.toml` | 🟡 Spec | ❌ Absent |
| 31 | Workspace Rust (`panini-core` + `panini-api`) | Panini-FS | `Cargo.toml` | 🔵 Stub | ❌ Absent |
| 32 | Port Python→Rust du décomposeur (1527 lignes, 44 formats) | Panini | `RUST_PRODUCTION_ROADMAP.md` | 🟡 Spec | ❌ Absent |
| 33 | Multi-repos Git (Private→Team→Public, filtrage) | Panini-FS | `PANINIFS_MULTI_REPOS_TIME_TRAVEL_SPEC.md` | 🟡 Spec | ❌ Absent |
| 34 | Time-travel snapshots (navigation historique) | Panini-FS | `PANINIFS_MULTI_REPOS_TIME_TRAVEL_SPEC.md` | 🟡 Spec | ❌ Absent |
| 35 | Content-Addressed Storage CAS (SHA-256, 25-65% compression) | Panini | (validé en E1) | ✅ Fait | ❌ Absent |
| 36 | Plugins WASM (Wasmtime + WIT) | Panini-FS | `EXPERIMENT_REGISTRY.md` NA-002 | 📋 NA-002 | ✅ |
| 37 | Compilation triple cible (native, wasm32-wasi, wasm32-unknown-unknown) | Panini-FS | `EXPERIMENT_REGISTRY.md` NA-002 | 📋 NA-002 | ✅ |
| 38 | `petgraph` pour graphes de concepts | Panini-FS | `Cargo.toml` | 🔵 Stub | ❌ Absent |
| 39 | REST API Axum pour concept store | Panini-FS | `Cargo.toml` | 🔵 Stub | ❌ Absent |
| 40 | Pont Rust↔Dolt (JSON contract, 586 lignes) | Panini-FS | `SANDBOX/dolt-concept-store/rust_bridge_stub.py` | 🟢 MVP | ❌ Absent |

---

## 3. 🌐 Applications & Interfaces

### 3.1 Web UI (React)

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 41 | Deduplication Dashboard (`/dedup` — KPI, Recharts) | Panini-FS | `web-ui/src/pages/DeduplicationDashboard.tsx` | 🟢 MVP (frontend seul) | ❌ Absent |
| 42 | Atom Explorer (`/atoms` — recherche par hash) | Panini-FS | `web-ui/src/pages/AtomExplorer.tsx` | 🟢 MVP (frontend seul) | ❌ Absent |
| 43 | File Upload & Analysis (`/upload` — drag-and-drop) | Panini-FS | `web-ui/src/pages/FileUploadAnalysis.tsx` | 🟢 MVP (frontend seul) | ❌ Absent |
| 44 | 5 API REST endpoints (dedup/stats, atoms/search…) | Panini-FS | `web-ui/PHASE_7_README.md` | 🟡 Spec | ❌ Absent |
| 45 | Phase 8: Interface FUSE (navigation filesystem) | Panini-FS | `web-ui/PHASE_7_README.md` | 🟠 Idée | ❌ Absent |
| 46 | Pages Concepts, Timeline, Snapshots (routes déclarées) | Panini-FS | `web-ui/src/App.tsx` routes | 🔵 Stub | ❌ Absent |
| 47 | PaniniFS-Web (version navigateur WASM, privacy by design) | Panini-FS | `EXPERIMENT_REGISTRY.md` NA-002 | 📋 NA-002 | ✅ |
| 48 | Graphes de concepts interactifs (D3.js/Cytoscape.js + WASM) | Panini-FS | `EXPERIMENT_REGISTRY.md` NA-002 | 📋 NA-002 | ✅ |
| 49 | Documentation dynamique MkDocs (WASM extra_javascript) | Panini-FS | `EXPERIMENT_REGISTRY.md` NA-002 | 📋 NA-002 | ✅ |

### 3.2 Pensine-Web

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 50 | Pensine-Web (remplacement Logseq — rich editor 3 modes, calendrier, GitHub OAuth) | Panini | `ARCHITECTURE_REAL_6PROJECTS.md` | 🟢 v0.0.22 | ❌ Absent |
| 51 | Pensine-Web → FS backend (remplacer GitHub API par décomposition Panini-FS) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 2 | 🟡 Spec (Mar-Avr 2026) | ❌ Absent |

### 3.3 OntoWave

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 52 | OntoWave (visualisation ontologique TypeScript/Node) | Panini | `ARCHITECTURE_REAL_6PROJECTS.md` | 🟢 MVP | ❌ Absent |
| 53 | Plugin architecture + marketplace + SDK | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 3 | 🟡 Spec (Mai-Juin 2026) | ❌ Absent |
| 54 | Extension VS Code (semantic editor, preview synchronisé) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 55 | Extension web navigateur (enrichissement pages) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 56 | CI intégration (semantic lint, broken links, graph diff) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 57 | Connecteur knowledge graph (dhātu → facettes de navigation) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |

### 3.4 Langue des signes & 3D

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 58 | Avatar 3D langue des signes (glTF, FACS facial, LSQ/ASL) | Panini | `REQUIREMENTS_3D_AVATAR_SIGN_LANG_LINGUISTICS.md` | 🟡 Spec | ❌ Absent |
| 59 | Mains articulées avancées (16+ formes, 3 LOD, contraintes physio) | Panini | `advanced_articulated_hands_guide.md` | 🟡 Spec | ❌ Absent |
| 60 | Interface universelle signe-dhātu (démo 3D interactive) | Panini | `universal_sign_interface.html` | 🟢 MVP | ❌ Absent |
| 61 | Modèle de progression phonétique (4 stades : pré-linguistique → syntactique) | Panini-FS | `docs/knowledge-base/progression-phonetique-stades.md` | 🟡 Spec | ❌ Absent |

### 3.5 Plugins IDE & éditeurs

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 62 | Extension VS Code pour Panini-FS | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 63 | Plugin Vim/Neovim | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 64 | Plugin Obsidian (export Pensine-Web) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |

---

## 4. 🔬 Recherche & Science

### 4.1 Validation empirique

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 65 | E1: Format-Semantic Universality (450 fichiers, 5 formats) | Panini | `experiments/e1_format_decomposition.py` | 📋 E1 | ✅ |
| 66 | E2: Reconstruction bit-perfect (SHA256 round-trip) | Panini-FS | `EXPERIMENT_REGISTRY.md` E2 | 📋 E2 | ✅ |
| 67 | Universalité cross-linguistique (1000+ textes, 12+ familles, 92% couverture) | Panini | `ROADMAP-RECHERCHE.md` | 🟡 Spec | ❌ Absent |
| 68 | Validation baby sign (4-36 mois, 1200+ enfants, 15 cultures) | Panini | `BABY_SIGN_EXHAUSTIVE_ANALYSIS.md` | 🟡 Spec | ❌ Absent |
| 69 | Tests cognitifs utilisateur (30+ personnes, courbes d'apprentissage) | Panini | `ROADMAP-RECHERCHE.md` Phase 2.1 | 🟡 Spec | ❌ Absent |
| 70 | Stress tests typologiques (langues ergatives, sérielles, polysynthétiques) | Panini-FS | `docs/research/hypotheses-et-alternatives.md` | 🟡 Spec | ❌ Absent |
| 71 | Corpus Wikipedia (validation large échelle) | Panini-FS | `SANDBOX/dolt-concept-store/WIKIPEDIA_TEST.md` | 🟡 Spec | ❌ Absent |
| 72 | Mini corpus math (Euclide, Euler, Noether) | Panini-FS | `SANDBOX/dolt-concept-store/` TODO | 🟠 Idée | ❌ Absent |
| 73 | Extracteur cross-modal (audio, visuel, gestuel → dhātu) | Panini | Issue #3 `PROJECT_STATUS_ROADMAP.md` | 🟠 Idée | ❌ Absent |

### 4.2 Fondements théoriques

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 74 | Formalisation mathématique (preuves de compression sémantique) | Panini | Issue #5 `PROJECT_STATUS_ROADMAP.md` | 🟠 Idée | ❌ Absent |
| 75 | State-of-art compétitif (404+ sources, vs Wierzbicka NSM 65 primitifs) | Panini | `ANALYSE_STATE_OF_ART_COMPRESSION_SEMANTIQUE_2025.md` | ✅ Fait | ❌ Absent |
| 76 | Revue interdisciplinaire (72 références — linguistique, neuro, philo, CS) | Panini-FS | `UNIVERSAUX_INTERDISCIPLINAIRES_REVUE_LITTERATURE.md` | ✅ Fait | ❌ Absent |
| 77 | PaniniSpeak — « première langue universelle » (test acquisition naturelle 2-6 ans) | Panini | `PLAN_STRATEGIQUE_RECHERCHES_CROISEES.md` | 🟠 Idée | ❌ Absent |

### 4.3 Publications académiques

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 78 | Article Nature/Science (« 9 Meta-Patterns », 3 mois prep) | Panini | `STRATEGIE_PUBLICATION_ACADEMIQUE_DHATU_BREAKTHROUGH.md` | 🟡 Spec | ❌ Absent |
| 79 | Articles Medium EN/FR (drafts écrits) | Panini | `docs/panini/publications/articles/` | 🟢 Draft | ❌ Absent |
| 80 | Livre Leanpub EN/FR (« L'Odyssée de la Compression Sémantique ») | Panini | `docs/panini/publications/books/` | 🟢 Draft | ❌ Absent |
| 81 | Protocole publication coordonnée multi-plateforme | Panini | `PUBLICATION_COORDONNEE_20250820.md` | ✅ Fait | ❌ Absent |
| 82 | Synchronisation Medium ↔ repo | Panini | `SYNCHRONISATION_MEDIUM_2025.md` | 🟡 Spec | ❌ Absent |
| 83 | Comparaison IPFS vs PaniniFS | Panini-FS | `remarkable_study_pack/` | 🔵 Stub | ❌ Absent |
| 84 | 6 articles scientifiques Remarkable (bibliographie, état art, études de cas…) | Panini-FS | `remarkable_study_pack/scientific_articles/*.md` | 🔵 Stub | ❌ Absent |

---

## 5. 🧠 IA & Neuro-symbolique

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 85 | **LLM2Symbolic** — mapping attention heads LLM → dhātu (GPT-2, LLaMA-2, Mistral) | Panini-Research | `llm2symbolic/` (18 fichiers) | 🟢 MVP (~40%) | ❌ Absent |
| 86 | Sparse autoencoder pour dhātu | Panini-Research | `llm2symbolic/src/sparse_autoencoder.py` | 🟢 MVP | ❌ Absent |
| 87 | Décomposition assistée par IA (ML-powered) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 88 | Vocabulaires dhātu custom par domaine | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 131 | **Moteur d'inférence symbolique massivement parallèle** — raisonnement formel sur les graphes de concepts dhātu : unification, chaînage avant/arrière, résolution de contraintes. Parallélisme GPU/WASM sur les 104+ concepts simultanément. Liens : Prolog/Datalog compilé, miniKanren, rete network. Cible : inférer les formules d'atomes manquantes, détecter les contradictions ontologiques, propager les conséquences d'un ajout d'atome. | Panini-FS | — (nouveau) | 🟠 Idée | ❌ Absent |
| 132 | **Réseaux bayésiens sur les dhātu** — modéliser les co-occurrences d'atomes comme un réseau bayésien (DAG causal). Estimer $P(\text{atome}_i \mid \text{contexte})$ pour la désambiguïsation sémantique. Apprentissage de structure (PC algorithm, score-based) à partir du corpus Gutenberg multilingue. Applications : résolution de polysémie (#21), prédiction du tier de qualité, détection d'anomalies dans les formules de concepts. Libs candidates : `pgmpy` (Python), `bnlearn` (R), ou implémentation Rust custom. | Panini-FS | — (nouveau) | 🟠 Idée | ❌ Absent |
| 133 | **Modèles probabilistes pour la sémantique** — Topic models (LDA, ETM), champs aléatoires de Markov (CRF) sur les séquences d'atomes, et modèles de mélange pour les profils sémantiques par langue/registre/époque. Mesurer l'incertitude de chaque attribution mot→atome au lieu d'un mapping déterministe. Quantifier la confiance de chaque décomposition sémantique. Complément naturel à l'approche déterministe actuelle de `seven_layers_engine.py`. | Panini-FS | — (nouveau) | 🟠 Idée | ❌ Absent |

---

## 6. 🤖 Agents autonomes & Orchestration

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 89 | Système multi-agents (4 agents : Panini, FS, OntoWave, Gest) | Panini | `config/agents/agent_*_spec.json` | 🟡 Spec | ❌ Absent |
| 90 | MCP Server CoLabMCP (Model Context Protocol) | Panini | `PANINI_COLABMCP_BLUEPRINT.md`, `src/panini_colabmcp/` | 🟡 Spec + code partiel | ❌ Absent |
| 91 | ExecutionOrchestrator (CLI Typer, drivers local/colab/cloud) | ExecOrch | `cli.py`, `drivers/*.py`, `missions/*.py` | 🟢 MVP (drivers = stubs) | ❌ Absent |
| 92 | GPU queue management + cost tracking + checkpointing | CoLabController | `README.md` (spec détaillée) | 🟡 Spec | ❌ Absent |
| 93 | Agent critique adversarial | Panini-FS | `Copilotage/agent-critique-adversarial.py` | 🔵 Stub | ❌ Absent |
| 94 | Orchestrateur avec GitHub (crée issues/PRs automatiquement) | Panini-FS | `Copilotage/orchestrateur-avec-github.py` | 🔵 Stub | ❌ Absent |
| 95 | Agent de recherche théorique | Panini-FS | `Copilotage/theoretical-research-agent.py` | 🔵 Stub | ❌ Absent |
| 96 | Mission autonome nocturne | Panini-FS | `nocturnal_autonomous_mission.py` | 🔵 Stub | ❌ Absent |
| 97 | Hot reload modules depuis GitHub | Panini | `src/github_sync/hot_reload.py` | 🟢 MVP | ❌ Absent |
| 98 | Dynamic module manager | Panini | `src/modules/dynamic_manager.py` | 🟢 MVP | ❌ Absent |
| 99 | Event system (processing événementiel) | Panini | `src/core/event_system.py` | 🟢 MVP | ❌ Absent |

---

## 7. ☁️ Infrastructure & Cloud

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 100 | Colab GPU daemon (auto-execute sur T4, watch GitHub) | Panini | `notebooks/colab_gpu_daemon.ipynb`, `tools/colab_daemon_setup.py` | ✅ Fait | ❌ Absent |
| 101 | VSCode ↔ Colab tunnel (debug remote avec breakpoints) | Panini | `notebooks/colab_vscode_tunnel.ipynb` | ✅ Fait | ❌ Absent |
| 102 | Pipeline async compression (GitHub Actions → Colab → Google One) | Panini | `.github/workflows/async_compression.yml` | ❌ Désactivé | ❌ Absent |
| 103 | Total automation (zéro opérations manuelles) | Panini | `AUTOMATISATION_TOTALE.md`, `scripts/total_automation.py` | 🟡 Spec | ❌ Absent |
| 104 | Git Registry Zero-DB (analyses = JSON dans Git, SQLite cache) | Panini | `GIT_REGISTRY_ARCHITECTURE.md`, `src/panini_colabmcp/git_registry.py` | 🟡 Spec + code | ❌ Absent |
| 105 | Stratégie compute gratuit (Colab 12h/jour, Codespaces 120h/mois) | Panini | `compute_strategy.md` | ✅ Fait | ❌ Absent |
| 106 | Hybride local+remote (CPU local → GPU Colab → sync) | Panini | `tech/hybrid_strategy/` | 🟡 Spec | ❌ Absent |
| 107 | RX480 GPU accélération locale (5.83 TFLOPS, 7.12× speedup) | Panini | `rx480_benchmark_specs.json`, `src/core/rx480_*` | 🟡 Spec + benchmark | ❌ Absent |
| 108 | DevContainer (Rust + Python 3.11 + Node 20, 3 ports) | Panini-FS | `.devcontainer/devcontainer.json` | ✅ Fait | ❌ Absent |
| 109 | 28 workflows GitHub Actions (tous désactivés) | Panini-FS | `.github/workflows/*.disabled` | ❌ Désactivés | ❌ Absent |

---

## 8. 📊 Données & Corpus

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 110 | Corpus Gutenberg multi-échelle (basic→massive, 6 langues) | Panini | `data/gutenberg_*` | ✅ Fait | ❌ Absent |
| 111 | Corpus scientifique (ArXiv, HAL, DBLP — 10M+ mots) | Panini | `corpus-collection-strategy.md` | 🟡 Spec | ❌ Absent |
| 112 | Collecteur turbo corpus (parallèle, multi-stratégie) | Panini | `scripts/turbo_corpus_collector.py` | 🟢 MVP | ❌ Absent |
| 113 | Corpus incrémental (croissance continue pour validation) | Panini | `data/incremental_corpus/` | 🟡 Spec | ❌ Absent |
| 114 | PanLang système (61 primitifs NSM + 51 molécules + 35 composés = 147 concepts) | Panini-Research | `semantic-primitives/` (97 fichiers) | ✅ Fait | ❌ Absent |
| 115 | Générateur de corpus synthétique | Panini-FS | `SANDBOX/dolt-concept-store/` | ✅ Fait | ❌ Absent |

---

## 9. 🔧 Gouvernance & Outillage

### 9.1 Gouvernance

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 116 | Constitution universelle (mission, principes, stack, tiers langages) | SpecKit-Shared | `constitution/` | ✅ Fait | ❌ Absent |
| 117 | 7 prompts Spec-Kit (analyze, clarify, implement, plan, specify, tasks, constitution) | SpecKit-Shared | `.specify/prompts/` | ✅ Fait | ❌ Absent |
| 118 | Universal IP Engine (provenance, licensing, attribution, audit, signatures — 73 tests, ~15,950 lignes) | Panini-Research | `universal-engine/` (183 fichiers) | ✅ Fait | ❌ Absent |
| 119 | Pre-commit hook journal obligatoire | Panini-FS | `scripts/hooks/pre-commit` | ✅ Fait | ❌ Absent |
| 120 | Agent provenance labeling (prov:host, prov:pid, agent, model, owner) | Panini-FS | `AGENT_CONVENTION.md` | ✅ Fait | ❌ Absent |
| 121 | Cross-agent review requirement (PR = agent différent) | Panini-FS | `AGENT_CONVENTION.md` | 🟡 Spec | ❌ Absent |

### 9.2 Tests & Qualité

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 122 | Playwright e2e (smoke, modules, research — paninifs.org) | Panini-FS | `e2e/*.spec.ts` | ✅ Fait | ❌ Absent |
| 123 | Validation reconstruction end-to-end | Panini | `tools/validation/reconstruction_validator.py` | 🟢 MVP | ❌ Absent |
| 124 | Validateur cohérence modules | Panini | `tools/validate_module_coherence.py` | 🟢 MVP | ❌ Absent |
| 125 | Copilotage independence check (aucun import prod) | Panini-FS | `scripts/devops/check_copilotage_independence.py` | ✅ Fait | ❌ Absent |
| 126 | Lint/format ruff+black (noté comme manquant) | Panini | `ESSENCE_PANINIFS.md` | 🟡 Spec | ❌ Absent |

---

## 10. 🚀 Fonctionnalités futures (Phase 4+)

| # | Idée | Repo | Fichier(s) | Statut | Roadmap? |
|---|------|------|-----------|--------|----------|
| 127 | Filesystem distribué multi-nœuds | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 128 | Collaboration temps réel (édition collaborative via FS) | Panini | `ROADMAP_PHASED_4PHASES.md` Phase 4 | 🟠 Idée | ❌ Absent |
| 129 | Base hypernodal + lattice de vues (hypergraphe, hyperarcs typés) | Panini-FS | `docs/knowledge-base/` | 🟡 Spec | ❌ Absent |
| 130 | Fingerprints patterns + pièges à récursion (LSH, Tarjan SCC) | Panini-FS | `docs/knowledge-base/` | 🟡 Spec | ❌ Absent |

---

## 11. 📁 Repos satellites — Statut consolidé

| Repo | Fichiers | Contenu réel | Action recommandée |
|------|----------|-------------|-------------------|
| **Panini** (main) | ~200+ | 🟢 Hub R&D principal | **Garder** — moteur de recherche |
| **Panini-FS** | ~300+ | 🟢 Produit principal | **Garder** — cœur technique |
| **Panini-Research** | 51,898 | 🟢 Trésor scientifique | **Garder** — LLM2Symbolic, IP engine, PanLang |
| **Panini-SpecKit-Shared** | 51 | 🟢 Governance | **Garder** — Constitution, prompts |
| **Panini-ExecutionOrchestrator** | 45 | 🟢 Code fonctionnel | **Garder** — architecture mission/driver |
| **Panini-CoLabController** | 33 | 🟡 Docs seulement | **Récolter** README comme spec → archiver |
| **Panini-CopilotageShared** | 39 | 🟡 Config seulement | **Fusionner** dans SpecKit → archiver |
| **Panini-AttributionRegistry** | 37 | 🔴 Coquille vide | **Archiver** (existe dans Research/universal-engine) |
| **Panini-AutonomousMissions** | 37 | 🔴 Coquille vide | **Archiver** (migré dans ExecOrchestrator) |
| **Panini-CloudOrchestrator** | 32 | 🔴 Coquille vide | **Archiver** (fusionné dans ExecOrchestrator) |
| **Panini-DatasetsIngestion** | 37 | 🔴 Coquille vide | **Archiver** (existe dans Research + FS) |
| **Panini-PublicationEngine** | 37 | 🔴 Coquille vide | **Archiver** |
| **Panini-SemanticCore** | 37 | 🔴 Coquille vide | **Archiver** |
| **Panini-UltraReactive** | 37 | 🔴 Coquille vide | **Archiver** |

### Bilan : 5 repos à garder, 2 à récolter+archiver, 7 coquilles vides à archiver.

---

## 12. 🔵 ~70 fichiers Python vides (0 bytes) — Plan fantôme

Des dizaines de scripts `.py` créés mais jamais implémentés révèlent un **plan
d'automatisation ambitieux** qui n'a jamais abouti. Ils sont classés ici pour
mémoire — la plupart devront être supprimés ou remplacés par de vrais outils.

**Par catégorie :**

| Catégorie | Nombre | Exemples | Verdict |
|-----------|--------|----------|---------|
| Autonomie/ops | ~8 | `total_autonomy_engine.py`, `continuous_autonomy_daemon.py` | Remplacer par ExecOrchestrator |
| Recherche/analyse | ~6 | `neurocognitive_language_analyzer.py`, `temporal_emergence_analyzer.py` | Idées intéressantes, à évaluer |
| Linguistique | ~4 | `optimal_vocabulary_generator.py`, `panini_linguistic_integrator.py` | Potentiellement utile |
| Stratégie | ~5 | `social_revolution_strategy.py`, `distribution_strategy_analyzer.py` | Non-code, supprimer |
| Publication | ~3 | `publication_generator.py`, `generate_scientific_bibliography.py` | Remplacer par pipeline réel |
| Cloud/GPU | ~6 | `gpu_analysis_gt630m.py`, `colab_autonomous_controller.py` | Supersédé par CoLab daemon |
| DevOps | ~5 | `traceability_dashboard.py`, `vscode_extensions_manager.py` | À évaluer |
| Consensus | ~3 | `advanced_consensus_engine.py`, `connivance_learning_system.py` | Concept intéressant |
| Rust bridge | 1 | `rust_bridge.py` | Existe déjà : `rust_bridge_stub.py` (586 lignes) |

---

## 📊 Résumé quantitatif

| Catégorie | Total idées | ✅ Fait | 🟢 MVP | 🟡 Spec | 🔵 Stub | 🟠 Idée | 📋 Registre | ❌ Abandonné |
|-----------|------------|---------|--------|---------|---------|---------|------------|-------------|
| Moteur sémantique | 27 | 4 | 10 | 4 | 0 | 2 | 8 | 0 |
| Rust & FUSE | 13 | 1 | 1 | 6 | 3 | 0 | 2 | 0 |
| Applications & UI | 19 | 0 | 6 | 6 | 1 | 4 | 3 | 0 |
| Recherche & Science | 20 | 2 | 2 | 8 | 2 | 4 | 2 | 0 |
| IA & Neuro-symbolique | 7 | 0 | 2 | 0 | 0 | 5 | 0 | 0 |
| Agents & Orchestration | 11 | 0 | 3 | 2 | 3 | 0 | 0 | 0 |
| Infrastructure | 10 | 4 | 0 | 2 | 0 | 0 | 0 | 4 |
| Données & Corpus | 6 | 3 | 1 | 2 | 0 | 0 | 0 | 0 |
| Gouvernance & Tests | 11 | 6 | 2 | 2 | 0 | 0 | 0 | 0 |
| Futures (Phase 4+) | 4 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| **TOTAL** | **~133** | **20** | **27** | **34** | **9** | **17** | **15** | **4** |

### Conclusion

Sur ~133 idées identifiées :
- **15** (11%) étaient dans le registre — le reste était invisible
- **20** (15%) sont réellement terminées
- **27** (20%) ont un prototype fonctionnel
- **34** (26%) ont un design/spec mais pas de code
- **9** (7%) ne sont que des fichiers vides
- **17** (13%) sont de simples mentions ou idées nouvelles dans un doc
- **4** (3%) sont explicitement abandonnées/désactivées

**Les idées les plus impactantes manquantes du roadmap :**

1. **LLM2Symbolic** (#85) — Pont neuro-symbolique unique au monde, 40% avancé
2. **Chunker sémantique** (#9) — 957 lignes fonctionnelles, non inventorié
3. **Audio fingerprinting** (#11) — 482 lignes fonctionnelles, non inventorié
4. **Universal IP Engine** (#118) — 15,950 lignes, 73 tests, complet
5. **PanLang 147 concepts** (#114) — Système complet non référencé depuis FS
6. **Web UI Phase 7** (#41-46) — 3 pages React sans backend
7. **44 grammaires de format** (#10) — Design complet, crucial pour Rust port
8. **Pensine-Web** (#50-51) — Produit en v0.0.22, absente du roadmap FS
9. **Géométrie dhātu 9D** (#16) — Prototype fonctionnel
10. **Corpus Wikipedia** (#71) — Test à grande échelle planifié
---

## 13. 🔀 Analyse de convergence — Comment les 133 idées s'assemblent

### 13.1 Nœuds de convergence — Les 5 hubs gravitationnels

Le graphe des 133 idées n'est pas plat. Certains concepts sont des **points de
convergence** qui connectent 3 domaines ou plus. Ils forment l'ossature structurelle
du projet.

#### Hub 1 : Les dhātu (MÉGA-HUB — 9+ connexions)

Centre gravitationnel absolu. Connecte :
- Moteur 7 couches (#1) — décomposition par dhātu
- PanLang 147 concepts (#114) — composition de dhātu en molécules
- LLM2Symbolic (#85) — attention heads → dhātu
- Baby sign validation (#68) — émergence développementale des dhātu
- Géométrie 9D (#16) — espace vectoriel des dhātu
- Compression tripartite (#13) — encodage fractal via dhātu
- Gutenberg validation (#5) — corrélation cross-linguistique 95%
- Dolt concept store (#1-8) — stockage SQL indexé par signature dhātu
- FUSE3 filesystem (#28) — répertoires `/dhatu/RELATE/`

**⚠️ Tension critique** : le nombre de primitifs est **instable** dans l'écosystème.

| Source | Nombre | Primitifs |
|--------|--------|-----------|
| FS Spec Kit original | 7 | COMM, ITER, TRANS, DECIDE, LOCATE, GROUP, SEQ |
| Dhātu Geometry | 9 | EXIST, RELATE, COMM, EVAL, CAUSE, FLOW, MODAL, ITER, DECIDE |
| PanLang ULTIME | 10 | MOUVEMENT, COGNITION, PERCEPTION, COMMUNICATION, CRÉATION, ÉMOTION, EXISTENCE, DESTRUCTION, POSSESSION, DOMINATION |
| PanLang v2 (3 couches) | 23 | Catégories → opérationnels → composés |
| Dolt v2.2 (+ émotions) | 30 | 3 couches + 8 sous-primitifs Panksepp |
| NSM Wierzbicka | 61 | Primes sémantiques naturels |

→ **Résolution nécessaire** : un théorème de sélection de primitifs formel,
prouvant qu'un ensemble est simultanément *complet*, *minimal*, et *naturel*.

#### Hub 2 : Provenance / Attribution / IP (4+ connexions)

- Universal IP Engine (#118) — 8 composants, 73 tests
- Hypernodal DB (#129) — chaîne d'attribution par assertion
- Dolt 3-tier isolation (#33) — public/confidentiel/privé
- Constitution universelle (#116) — principe de traçabilité
- Gutenberg provenance (#5) — par traducteur/édition/époque

#### Hub 3 : Backend de stockage/indexation (5 connexions)

- RocksDB (#29) — key-value dans Rust core
- Tantivy (#30) — fulltext search
- Dolt SQL (#1-8) — Git workflows + SQL
- Petgraph (#38) — graphes de concepts
- Hypernodal DB (#129) — hypergraphe + lattice de vues

**⚠️ Contradiction** : aucun document ne tranche entre RocksDB et Dolt comme backend
de production, ni ne propose une architecture hybride utilisant les deux.

#### Hub 4 : Validation cross-linguistique (5 connexions)

- Baby sign (#68) — pré-linguistique, 15 cultures
- Gutenberg corpus (#5, #110) — 7 langues, 46 segments
- PanLang NSM (#114) — 61 universaux de Wierzbicka
- LLM2Symbolic (#85) — patterns d'attention cross-lingue
- Stress tests typologiques (#70) — langues ergatives, polysynthétiques

#### Hub 5 : WASM comme surface d'exécution (4 connexions)

- Plugins format (#36) — Wasmtime + WIT côté serveur
- PaniniFS-Web (#47) — browser, privacy by design
- Graphes interactifs (#48) — D3.js/Cytoscape.js + WASM
- Inférence symbolique parallèle (#131) — moteur Rete/Datalog en WASM browser

### 13.2 Chaînes de dépendances — Les chemins critiques

#### Chemin critique A : Théorie → Moteur → Stockage → UI

```
Revue interdisciplinaire (76 refs)
  → Sélection des primitifs dhātu (7? 9? 30?)     ← BLOQUANT : pas de consensus
    → Algorithme de décomposition Panini-FS
      → Stockage RocksDB / Dolt
        → Indexation Tantivy
          → FUSE3 virtual filesystem
            → OntoWave visualisation
              → Pensine-Web interface utilisateur
```

**Goulot** : Le nombre et l'identité des primitifs ne sont pas stabilisés.
Tout ce qui est en aval en dépend.

#### Chemin critique B : Recherche → Validation → Production

```
PanLang v2 (30 primitifs, 3 couches)
  → Gutenberg validation (v2.1)
    → Gap analysis (v3-alpha)
      → Sous-primitifs émotionnels (v2.2)
        → PanLang v3 (stabilisé)                    ← SPEC FORMELLE MANQUANTE
          → LLM2Symbolic mapping (attention ↔ dhātu)
            → Système hybride neuro-symbolique production
              → Réseau bayésien sur le graphe (#132)
```

#### Chemin critique C : IP/Gouvernance → Stockage → Publication

```
Constitution universelle (#116)
  → Universal IP Engine (#118, 73 tests)
    → Dolt 3-tier isolation
      → Hypernodal DB chaînes d'attribution
        → Publication publique avec provenance complète
```

### 13.3 Synergies cachées — Valeur émergente entre repos

#### ⭐ Synergie 1 : LLM2Symbolic × Géométrie 9D = **Pont neuro-géométrique**

LLM2Symbolic (#85) mappe les attention heads vers les dhātu.
La géométrie 9D (#16) modélise les dhātu comme vecteurs avec des distances
cosine (inclusion = hypersphères, exclusion = séparation angulaire).

**Connexion manquante** : utiliser le modèle géométrique pour *prédire* quelles
attention heads devraient corréler, puis valider par sondage LLM. Ceci
fournirait une théorie géométrique falsifiable des internaux LLM — résultat
publiable dans une revue de premier plan.

**Converge avec** : réseaux bayésiens (#132) pour modéliser $P(\text{head}_j
\mid \text{dhātu}_i)$ comme un réseau probabiliste sur l'espace 9D.

#### ⭐ Synergie 2 : Baby Sign × PanLang couches = **L'ontogenèse cognitive récapitule la phylogenèse sémantique**

Le baby sign (#68) montre un ordre d'émergence : EXIST (4 mois) → WANT (5 mois)
→ COMM (6.5 mois) → ITER (7 mois) → POINT/référence (9 mois).
PanLang v2 a 3 couches hiérarchiques.

**Hypothèse non testée** : la hiérarchie des couches PanLang devrait correspondre
à l'ordre d'acquisition développemental. Si couche 1 = gestes les plus précoces
et couche 3 = les plus tardifs (15-24 mois), cela valide la *naturalité cognitive*
de l'architecture en couches.

**Converge avec** : modèles probabilistes (#133) pour mesurer la corrélation
entre âge d'acquisition et position dans la hiérarchie ontologique.

#### ⭐ Synergie 3 : Dolt branches × Universal IP Engine = **Communs de la connaissance auto-gouvernés**

Dolt a déjà l'isolation 3-tier (public/confidentiel/privé).
L'Universal IP Engine a déjà 8 gestionnaires (provenance, licensing, attribution,
audit, signatures, réputation, gouvernance — 73 tests).

**Personne ne les a connectés.** Si le workflow promotion-by-merge de Dolt
déclenche audit trail + vérification de signatures + scoring de réputation de
l'Universal Engine, on obtient une base de connaissances **décentralisée et
auto-gouvernée** où la qualité est garantie par des mécanismes cryptographiques
et sociaux.

#### ⭐ Synergie 4 : Fingerprints × Compression tripartite = **Déduplication anti-récursive à grande échelle**

Les fingerprints patterns (#130) et la compression tripartite (#13) adressent
le même problème profond : identifier *ce qui est identique* au niveau sémantique
et réduire la redondance. Combinés, ils détecteraient l'auto-similarité fractale
dans de grandes bases de connaissances (échelle Wikipedia) et compresseraient
non pas des octets mais du *sens* — avec détection de cycles garantie (Tarjan SCC).

**Converge avec** : inférence symbolique (#131) pour propager les conséquences
de la détection de redondance dans le graphe de concepts.

#### ⭐ Synergie 5 : Pensine-Web × FUSE3 × OntoWave = **Le Knowledge OS manquant**

Pensine-Web (#50) remplace Logseq pour le journaling.
FUSE3 (#28) expose la décomposition comme filesystem.
OntoWave (#52) visualise les ontologies.

**Boucle complète jamais architecturée** :
```
Écrire dans Pensine-Web
  → Auto-décomposition via Panini-FS
    → Apparition dans FUSE3 (`/dhatu/RELATE/mon-texte.panini`)
      → Visualisation dans OntoWave (graphe ontologique vivant)
        → Inférence symbolique (#131) détecte les implications
          → Réseau bayésien (#132) prédit les connexions manquantes
            → Notification dans Pensine-Web : "Ce texte est relié à X"
```

#### ⭐ Synergie 6 : Inférence symbolique × Bayésien × Probabiliste = **Le Raisonneur Hybride**

Les 3 axes de NA-003 ne sont pas indépendants. Ils forment un **raisonneur
hybride** à 3 niveaux :

```
Niveau 3 : Modèles probabilistes (#133)
  │  Quantifient l'incertitude : P(attribution) ∈ [0,1]
  │  Découvrent les thèmes émergents (LDA/ETM)
  │
  ▼
Niveau 2 : Réseaux bayésiens (#132)
  │  Modélisent les dépendances causales entre atomes
  │  Désambiguïsent la polysémie : P(atome | contexte)
  │
  ▼
Niveau 1 : Inférence symbolique (#131)
  │  Raisonnement formel : chaînage, contraintes, contradictions
  │  Garanties logiques : cohérence, complétude (locales)
  │
  ▼
Socle : Ontologie déterministe (seven_layers_engine.py)
  Les 7 couches + 30 primitifs + 104 concepts
```

Chaque niveau enrichit le précédent sans le remplacer :
- Le symbolique donne la **rigueur** (pas de contradiction)
- Le bayésien donne la **probabilité** (pas de certitude fausse)
- Le probabiliste donne l'**humilité** (pas de prétention de couverture totale)
- Le déterministe donne la **transparence** (pas de boîte noire)

### 13.4 Contradictions à résoudre

| # | Contradiction | Impact | Résolution proposée |
|---|--------------|--------|---------------------|
| C1 | **Nombre de primitifs instable** (7, 9, 10, 23, 30, 61) | Bloque tout le chemin A | Définir un *critère de convergence empirique* : le nombre stabilisé par les données Gutenberg+LLM2Symbolic |
| C2 | **"Pas de compression" vs Compression Tripartite** (architecture dit « side effect, not purpose » mais Compression Tripartite revendique 15,847×) | Confusion marketing/scientifique | Cadrage : la décomposition est l'objectif; la compression est une *conséquence mesurable* mais pas le but |
| C3 | **Rust déclaré vs Python réel** (Cargo.toml avec axum/tokio vs 150+ fichiers Python fonctionnels) | Risque de réécriture sans fin | Stratégie **progressive** : panini-core Rust pour les hot paths (CAS, FUSE, hashing), Python reste pour la recherche |
| C4 | **EMOTION — universel ou culturel ?** (Gutenberg : 0 concepts transversaux; Baby sign : gestes émotionnels à 4 mois; Panksepp : 7 systèmes neurobiologiques mammifères) | Remise en cause d'un primitif entier | Le réseau bayésien (#132) peut trancher empiriquement : mesurer $P(\text{EMOTION} \mid \text{langue})$ — si variance faible → universel |

### 13.5 Liens manquants — Connexions évidentes non encore faites

| # | Lien manquant | Entre | Valeur potentielle |
|---|--------------|-------|-------------------|
| L1 | **Théorie des catégories ↔ Implémentation** | Revue interdisciplinaire (Curry-Howard-Lambek) ↔ `petgraph` (#38) | Formaliser les dhātu comme objets, les compositions comme morphismes, l'universalité comme propriété catégorielle. Rigueur mathématique absolue. |
| L2 | **Dolt ↔ Panini-FS core** | Dolt SQL (#1-8) ↔ RocksDB (#29) | Aucun document ne tranche. Architecture hybride : Dolt = source de vérité (Git semantics), RocksDB = cache hot-path (FUSE latence). |
| L3 | **LLM2Symbolic → Dhātu refinement** | LLM2Symbolic (#85) → inventaire dhātu (#15) | Si les attention patterns montrent que EVAL ≈ DECIDE (cosine 0.052 en géométrie 9D), fusionner les primitifs. Boucle de rétroaction absente. |
| L4 | **Constitution → CI automatisé** | SpecKit Constitution (#116) → workflows CI (#109) | Vérifier automatiquement que chaque PR respecte les principes constitutionnels (universalité, réversibilité, séparation des préoccupations). |
| L5 | **Audio fingerprint → Reconnaissance gestuelle** | Audio fingerprint (#11) → Baby sign (#68) | Adapter la technique de constellation map (spectrogramme → fingerprint) à des *vidéos de gestes* (mouvement → fingerprint dhātu). Ferme la boucle entre le système computationnel et la validation développementale. |

### 13.6 La thèse unificatrice

> **Pāṇini a découvert, il y a 2 500 ans, un ensemble fini de primitifs
> cognitifs (dhātu) universels à travers les langues, cultures, stades de
> développement et modalités. Ces primitifs constituent les atomes irréductibles
> du sens. Un système computationnel moderne bâti sur ces primitifs peut
> décomposer, stocker, chercher, reconstruire et visualiser toute connaissance
> humaine — avec provenance, attribution et garanties mathématiques — créant
> un nouveau paradigme d'interaction humain-machine.**

Cette thèse repose sur **4 piliers testables** :

| Pilier | Validé par | Statut |
|--------|-----------|--------|
| **Universalité** — les primitifs ne sont pas culturellement biaisés | Baby sign (#68, pré-culturel), Gutenberg (#5, cross-culturel), LLM2Symbolic (#85, a-culturel) | 🟡 Partiel (Gutenberg : aucun concept 100% transversal) |
| **Compositionnalité** — tout sens se compose de primitifs finis | PanLang (#114, 147 concepts), compression tripartite (#13), reconstruction bit-perfect (E2) | 🟡 E2 pas encore exécutée |
| **Calculabilité** — les primitifs sont algorithmiquement traitables | Moteur 7 couches (#1), géométrie 9D (#16), CAS SHA-256 (#35), FUSE3 (#28) | 🟢 Partiel (Python fonctionne, Rust pas encore) |
| **Gouvernance** — la connaissance porte provenance et droits | Universal IP Engine (#118, 73 tests), Dolt 3-tier (#33), Constitution (#116) | ✅ Complet (mais pas intégré) |

**La tension au cœur** : l'écosystème ne s'accorde pas sur combien il y a de
primitifs. Tant qu'un *théorème de sélection de primitifs* n'est pas prouvé —
montrant qu'un ensemble spécifique est simultanément complet, minimal et naturel —
la thèse reste un *programme de recherche* plutôt qu'une *fondation prouvée*.

Le constat honnête de la validation Gutenberg — « aucun concept n'atteint 100%
d'universalité » — est à la fois la plus grande force du projet (honnêteté
intellectuelle) et son défi le plus profond.

**Le chemin** : résoudre C1 (combien de primitifs ?) par convergence empirique
des 3 sources (Gutenberg + LLM2Symbolic + Baby Sign), puis propager cette
décision dans toute la stack — du schéma Dolt aux répertoires FUSE en passant
par les cibles LLM2Symbolic et les nœuds du réseau bayésien.

### 13.7 Diagramme de convergence global

```
                           ┌─────────────────────┐
                           │   THÈSE UNIFICATRICE │
                           │  Primitifs cognitifs  │
                           │    universels (dhātu)  │
                           └──────────┬──────────┘
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
    ┌──────────▼──────┐    ┌──────────▼──────┐    ┌──────────▼──────┐
    │  UNIVERSALITÉ   │    │ COMPOSITIONNALITÉ│    │  CALCULABILITÉ  │
    │                 │    │                  │    │                 │
    │ Baby sign  #68  │    │ PanLang     #114 │    │ Moteur 7c   #1 │
    │ Gutenberg  #5   │    │ Compression #13  │    │ FUSE3       #28│
    │ LLM2Symb.  #85  │    │ E2 (à faire) #66 │    │ RocksDB     #29│
    │ Typo tests #70  │    │ Mol. builder #24 │    │ Tantivy     #30│
    └────────┬────────┘    └────────┬─────────┘    └────────┬────────┘
             │                      │                       │
             └──────────────┬───────┘                       │
                            │                               │
                   ┌────────▼────────┐             ┌────────▼────────┐
                   │ RAISONNEUR      │             │ SURFACES        │
                   │ HYBRIDE (NA-003)│             │ WASM (NA-002)   │
                   │                 │             │                 │
                   │ Symbolique #131 │◄────────────│ Browser    #47  │
                   │ Bayésien   #132 │             │ Graphes    #48  │
                   │ Probabiliste#133│             │ Docs       #49  │
                   └────────┬────────┘             └────────┬────────┘
                            │                               │
                   ┌────────▼────────┐             ┌────────▼────────┐
                   │  GOUVERNANCE    │             │  KNOWLEDGE OS   │
                   │                 │             │  (Synergie 5)   │
                   │ IP Engine  #118 │             │                 │
                   │ Dolt 3-tier     │             │ Pensine-Web #50 │
                   │ Constitution#116│             │ OntoWave    #52 │
                   │ Hypernodal #129 │             │ FUSE3       #28 │
                   └─────────────────┘             └─────────────────┘
```
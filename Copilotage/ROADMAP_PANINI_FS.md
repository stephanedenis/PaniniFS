# 🗺️ Roadmap — Panini-FS fonctionnel

> **Créé** : 2026-02-21
> **Auteur** : GitHub Copilot (Claude Opus 4.6) · hauru
> **Statut** : Proposition v1.0
> **Référence** : Audit complet + `IDEAS_INVENTORY.md` + 55 entrées journal

---

## Diagnostic de départ

### Ce qui fonctionne (le capital réel)

| Acquis | Détail | Valeur |
|--------|--------|--------|
| Moteur 7 couches | `seven_layers_engine.py` — 3 320 lignes, 14 langues, 34 atomes | 🟢 Production-ready en tant que bibliothèque |
| Couverture lexicale | 91.2% global, 7/7 langues EU ≥90% | 🟢 Résultat de recherche solide |
| Corpus Gutenberg | 37+ textes, 7+ langues, 3M+ mots ingérés | 🟢 Dataset validé |
| Corpus Wikipedia | 973 articles, 14 langues, 2.2M mots | 🟢 Dataset validé |
| Morpho-sémantique | Lemmatisation 7+ langues, voikko FI, cascade 5 niveaux | 🟢 Robuste |
| Normalisation Unicode | `text_normalizer.py` — NFC, BCP 47, époques, scripts | 🟢 Fraîchement intégré |
| Bases Dolt | 3 DB (~215 Mo), schéma v3 | 🟢 Données structurées |
| Documentation MkDocs | ~97 fichiers, bilingue FR/EN, paninifs.org | 🟡 Contenu existant |
| Journal Copilotage | 55 entrées, traçabilité complète | 🟢 Discipline établie |
| Expérience E2 | Reconstruction texte←→atomes (round-trip) | 🟡 POC validé |

### Ce qui manque (le gouffre vision↔réalité)

| Manque | Gravité | Détail |
|--------|---------|--------|
| **Aucun code Rust** | 🔴 | `Cargo.toml` référence `crates/panini-core` et `crates/panini-api` — **aucun n'existe** |
| **Aucun package installable** | 🔴 | Pas de `pyproject.toml`, `setup.py`, ni CLI. On ne peut pas `pip install panini-fs` |
| **SANDBOX = scripts en vrac** | 🔴 | 48 fichiers .py avec `sys.path.insert(0, ...)`. Pas de `__init__.py`, pas de package |
| **Aucun serveur API** | 🔴 | Le Web UI appelle `/api/atoms/search` etc. — ces endpoints n'existent nulle part |
| **29/31 workflows CI désactivés** | 🟠 | Seuls CodeQL + status badge tournent. Zéro test en CI |
| **10 submodules déclarés, 0 clonés** | 🟠 | L'architecture "écosystème" est un plan, pas une réalité |
| **Web UI = 3 fichiers TSX orphelins** | 🟠 | Pas de `package.json`, pas de build, pas de backend |
| **README décrit une structure fictive** | 🟠 | Références à `CORE/`, `RESEARCH/`, `GOVERNANCE/legal/` — aucun n'existe |
| **~50 fichiers orphelins à la racine** | 🟡 | Scripts de monitoring, déploiement, docteur — non organisés |
| **Dépendance DoltDB non déclarée** | 🟡 | Le pipeline entier nécessite Dolt installé, pas documenté |

### Décision stratégique fondamentale

> **Le Panini-FS fonctionnel est un outil Python avec un moteur sémantique éprouvé,
> pas un filesystem Rust/FUSE.**
>
> La valeur du projet réside dans son moteur d'analyse 7 couches et ses 34 atomes
> universels validés sur 14 langues. Le "FS" dans Panini-FS signifie que la sémantique
> **organise** les fichiers — pas qu'on écrit un driver kernel.
>
> Le Rust viendra quand le Python sera empaqueté, testé et déployable.

---

## Phase 0 — Assainissement (2 semaines)

> **Objectif** : Le repo reflète la réalité. Plus de fiction.

### 0.1 — Nettoyage structurel

- [ ] **Supprimer `Cargo.toml`** (ou le déplacer dans `future/rust/`) — il référence du code inexistant
- [ ] **Supprimer les références aux 10 submodules** dans `.gitmodules` (s'il existe)
- [ ] **Déplacer les ~50 fichiers orphelins** de la racine vers `scripts/legacy/` :
  - `*.sh` scripts de déploiement/monitoring → `scripts/ops/`
  - `*.py` scripts autonomes → `scripts/tools/`
  - `*.json` logs/rapports → `artifacts/logs/`
- [ ] **Réécrire `README.md`** pour décrire ce qui EXISTE, pas ce qui est rêvé :
  - Supprimer la section "Quick Start" avec `cargo build`
  - Supprimer les références à `CORE/`, `OPERATIONS/`, `DOCUMENTATION/`
  - Ajouter : "Le cœur est dans `panini/` (ex-SANDBOX)" avec exemples réels

### 0.2 — Refonte `SANDBOX/` → package Python `panini/`

- [ ] **Renommer** `SANDBOX/dolt-concept-store/` → `panini/` (à la racine)
- [ ] **Créer `panini/__init__.py`** avec version et exports publics
- [ ] **Créer `panini/engine/`** : regrouper le moteur d'analyse
  - `__init__.py`, `seven_layers.py`, `morpho_bridge.py`, `text_normalizer.py`
- [ ] **Créer `panini/ingest/`** : regrouper l'ingestion
  - `text_extractor.py`, `document_analyzer.py`, `gutenberg_ingest.py`, `wikipedia_loader.py`
- [ ] **Créer `panini/storage/`** : regrouper Dolt
  - `dolt_manager.py`, `branch_acl.py`, `schema/` (les .sql)
- [ ] **Créer `panini/export/`** : sérialisation
  - `semantic_serializer.py`, `reconstruction.py`
- [ ] **Créer `panini/data/`** : keywords, stopwords, configs
  - `atom_keywords.py` (extrait de `gutenberg_multilingual_validator.py`), `exotic_keywords.py`
- [ ] **Éliminer tous les `sys.path.insert(0, ...)`** — remplacer par des imports relatifs
- [ ] **Conserver `SANDBOX/`** pour les vrais expériences jetables

### 0.3 — Fichier `pyproject.toml`

```toml
[project]
name = "panini-fs"
version = "0.5.0"
description = "Semantic analysis engine — 34 universal atoms across 14 languages"
requires-python = ">=3.10"
license = {text = "MIT"}
dependencies = [
    "chardet>=5.0",
    "langdetect>=1.0.9",
]

[project.optional-dependencies]
dolt = ["mysqlclient>=2.1"]
ingest = ["pdfminer.six", "ebooklib", "python-docx", "beautifulsoup4", "markdown-it-py"]
finnish = ["voikko"]
all = ["panini-fs[dolt,ingest,finnish]"]

[project.scripts]
panini = "panini.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 0.4 — CLI minimale

```
panini analyze <fichier>           → analyse 7 couches, sortie JSON
panini analyze <fichier> --lang fr → avec hint de langue
panini info                        → version, langues supportées, atomes
panini validate-keywords           → vérifie NFC des dictionnaires
```

**Livrable Phase 0** : `pip install -e .` fonctionne. `panini analyze mon_texte.txt` produit du JSON.

---

## Phase 1 — Qualité & CI (2 semaines)

> **Objectif** : Le code est testé, linté, et chaque PR est vérifiée automatiquement.

### 1.1 — Tests unitaires

- [ ] **Migrer les 7 fichiers test existants** de SANDBOX vers `tests/`
- [ ] **Ajouter des tests pour le normalizer** : NFC, mojibake, BCP 47, ISO 639
- [ ] **Ajouter des tests pour la CLI** : smoke tests avec des fichiers sample
- [ ] **Fixture de corpus** : 1 paragraphe par langue (14 fichiers, <1 Ko chacun) dans `tests/fixtures/`
- [ ] **Cible** : ≥80% de couverture sur `panini/engine/` et `panini/ingest/`

### 1.2 — CI active

- [ ] **Réactiver 1 workflow** : `ci.yml` — lint + tests sur push/PR
  ```yaml
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: { python-version: "3.12" }
        - run: pip install -e ".[all]" && pip install pytest ruff
        - run: ruff check panini/
        - run: pytest tests/ -x --tb=short
  ```
- [ ] **Réactiver le déploiement docs** : `deploy-pages-mkdocs.yml`
- [ ] **Supprimer les 28 autres workflows désactivés** (ou les archiver dans `future/ci/`)
- [ ] **Protection de branche `master`** : exiger CI verte

### 1.3 — Lint & format

- [ ] `ruff` en mode check (pas bloquant au début, bloquant à Phase 2)
- [ ] Pre-commit hook : `ruff check --fix` + journal check existant
- [ ] Typage progressif : `py.typed` marker, annotations sur les fonctions publiques

**Livrable Phase 1** : Chaque PR passe ruff + pytest. MkDocs se déploie automatiquement.

---

## Phase 2 — API & Intégration (3 semaines)

> **Objectif** : Le moteur est accessible par HTTP. Les données sont exploitables.

### 2.1 — Serveur FastAPI

- [ ] **Créer `panini/api/`** avec FastAPI
- [ ] **Endpoints v1** :
  ```
  POST /api/v1/analyze          — analyser un texte (body JSON ou fichier uploadé)
  GET  /api/v1/atoms            — lister les 34 atomes avec descriptions
  GET  /api/v1/atoms/{atom}     — détail d'un atome + keywords par langue
  GET  /api/v1/languages        — langues supportées + scripts + couverture
  POST /api/v1/compare          — comparer 2 textes (cosinus sémantique)
  GET  /api/v1/health           — version, uptime, langues chargées
  ```
- [ ] **Modèles Pydantic** pour les requêtes/réponses (documentation OpenAPI gratuite)
- [ ] **Mode sans Dolt** : le moteur d'analyse fonctionne en mémoire, Dolt est optionnel pour la persistance
- [ ] Commande CLI : `panini serve --port 8080`

### 2.2 — Connecter le Web UI

- [ ] **Créer `web-ui/package.json`** avec Vite + React + TypeScript
- [ ] **Connecter les 3 composants TSX existants** aux endpoints API réels
- [ ] **Ajouter une page "Playground"** : coller du texte → voir l'analyse 7 couches en temps réel
- [ ] Proxy dev : `vite.config.ts` → `/api` → `localhost:8080`

### 2.3 — Pont `src/` ↔ `panini/`

- [ ] **Intégrer `src/semantic_chunker.py`** dans `panini/ingest/chunker.py`
  - Le chunker découpe → chaque chunk passe dans le 7-layer engine
- [ ] **Intégrer `src/audio_fingerprint.py`** dans `panini/ingest/audio.py` (optionnel, module séparé)
- [ ] Supprimer `src/` une fois intégré

**Livrable Phase 2** : `panini serve` démarre un serveur. On colle du texte dans le navigateur, on voit les atomes.

---

## Phase 3 — Pipeline de données robuste (2 semaines)

> **Objectif** : Ingestion reproductible, données versionnées, exports standardisés.

### 3.1 — Setup Dolt reproductible

- [ ] **Script `scripts/setup_dolt.sh`** : installe Dolt, crée les DB, applique les schémas
- [ ] **Documenter** dans README : prérequis Dolt, versions supportées
- [ ] **Mode "sans Dolt"** : toutes les fonctions du moteur marchent avec SQLite ou en mémoire
- [ ] **Docker Compose** : `dolt-server` + `panini-api` + `panini-web` en 3 conteneurs

### 3.2 — Pipeline d'ingestion end-to-end

- [ ] `panini ingest gutenberg --lang fr` → télécharge + analyse + stocke
- [ ] `panini ingest wikipedia --lang ja --count 50` → idem
- [ ] `panini ingest file mon_rapport.pdf` → extraction + analyse
- [ ] `panini export --format json --output results/` → export reproductible
- [ ] **Idempotence** : re-ingérer le même texte = no-op (hash de contenu)

### 3.3 — Validation des données

- [ ] `panini validate` → vérifie NFC des keywords, couverture par langue, cohérence atomes
- [ ] **Rapport de couverture automatique** : inclus dans CI (régression si couverture baisse)
- [ ] **Golden tests** : 14 textes de référence (1/langue) avec résultat attendu figé

**Livrable Phase 3** : `docker compose up` donne un Panini-FS complet. Pipeline idempotent.

---

## Phase 4 — Recherche & Expériences (continu, en parallèle)

> **Objectif** : Formaliser les résultats de recherche. Publier.

### 4.1 — Expérience E2 : Reconstruction

- [ ] **Formaliser le protocole** dans `docs/research/e2-reconstruction.md`
- [ ] **Métriques standardisées** : BLEU, ROUGE, F1 sémantique, fidélité morphologique
- [ ] **Baseline** : score actuel par langue (FR F1=51.3%, EN F1=60.6%)
- [ ] **Cible** : FR F1≥70%, EN F1≥75% via améliorations L2 (couverture lexicale)

### 4.2 — Compression sémantique

- [ ] **Mesurer le ratio réel** : taille texte original vs export JSON atomes
- [ ] **Comparer** : gzip(texte) vs panini(texte) vs gzip(panini(texte))
- [ ] **Publier** : article Medium ou preprint avec résultats reproductibles

### 4.3 — Stabilisation des atomes

- [ ] **Figer les 34 atomes** dans un document normatif versionné
- [ ] **Résoudre les tensions** identifiées dans `IDEAS_INVENTORY.md` :
  - Nombre d'atomes : 7/9/10/23/30/34/61 → documenter pourquoi 34
  - EMOTION : universel ou culturel ? → documenter la position
  - Compression : but ou effet secondaire ? → clarifier
- [ ] **Registre des atomes** : `panini/data/atoms.yaml` — source of truth

### 4.4 — Langues non-européennes

- [ ] **Consolider CJK** : zh, ja déjà supportés — mesurer la couverture réelle
- [ ] **Consolider Indic** : hi, sa — valider le Devanagari + ITRANS
- [ ] **Ajouter arabe** (ar) : scripts, keywords, trigrams → 15e langue
- [ ] **Cible** : 15 langues, 6 écritures, ≥85% couverture sur les nouvelles

**Livrable Phase 4** : Papier de recherche publiable avec résultats E2 + compression.

---

## Phase 5 — Filesystem sémantique (Phase ambitieuse, 2-3 mois)

> **Objectif** : Le "FS" dans Panini-FS — organiser des fichiers par sémantique.

### 5.1 — Index sémantique de fichiers

- [ ] `panini index ~/Documents/` → analyse chaque fichier, stocke les atomes dans un index local
- [ ] **Index SQLite local** : `~/.panini/index.db` — pas besoin de Dolt pour usage personnel
- [ ] **Recherche sémantique** : `panini search "mouvement vers un lieu"` → fichiers pertinents
- [ ] **Tags automatiques** : chaque fichier reçoit ses top-3 atomes comme tags

### 5.2 — Déduplication sémantique

- [ ] **Détection de duplicatas** : deux fichiers avec le même profil atomique → signalés
- [ ] **Cross-langue** : `rapport_fr.pdf` et `report_en.pdf` → cosinus ≥0.8 → "même contenu"
- [ ] **Dashboard** : `panini dedup ~/Documents/` → rapport HTML interactif

### 5.3 — Vue virtuelle (optionnel, avancé)

- [ ] **FUSE mount** (Python `fusepy`, pas Rust) :
  ```
  panini mount ~/semantic-view/ --source ~/Documents/
  ~/semantic-view/MOUVEMENT/
  ~/semantic-view/COGNITION/
  ~/semantic-view/CRÉATION/
  ```
- [ ] Chaque "dossier atome" contient des symlinks vers les fichiers ayant cet atome dominant
- [ ] **Alternative sans FUSE** : `panini tree ~/Documents/` → arborescence sémantique en terminal

### 5.4 — API de plugins (futur)

- [ ] **Plugin VS Code** : panneau latéral montrant les atomes du fichier ouvert
- [ ] **Plugin Obsidian** : liens sémantiques entre notes
- [ ] **Hook Git** : `panini diff --semantic` → diff par atomes, pas par lignes

**Livrable Phase 5** : `panini index` + `panini search` fonctionnent. On peut chercher ses fichiers par sémantique.

---

## Phase 6 — Scalabilité & Distribution (horizon long)

> **Objectif** : Panini-FS à l'échelle. Multi-utilisateur. Cloud.

### 6.1 — Performance

- [ ] **Profiler** le 7-layer engine : identifier les goulots (probablement keyword matching O(n×m))
- [ ] **Cache de lemmatisation** : mots déjà résolus → lookup O(1)
- [ ] **Parallélisation** : analyse multi-fichiers en parallèle (ProcessPoolExecutor)
- [ ] **Cible** : 1000 pages/minute sur un laptop moderne

### 6.2 — Rust (si justifié)

- [ ] **Portage du keyword matching** en Rust (via PyO3) pour le hotpath
- [ ] **Portage du NFC normalizer** en Rust (marginal, Python `unicodedata` est en C)
- [ ] **Ne PAS réécrire tout en Rust** — seulement les hotpaths profilés

### 6.3 — Multi-utilisateur

- [ ] **Auth JWT** sur l'API FastAPI
- [ ] **Index partagé** : Dolt branches par utilisateur (ACL existant dans `branch_acl.py`)
- [ ] **Déploiement cloud** : Docker sur un VPS ou Fly.io

---

## Résumé des phases & jalons

```
Phase 0 ─ Assainissement ─────────── 2 sem ─── pip install -e .
Phase 1 ─ Qualité & CI ───────────── 2 sem ─── CI verte, pytest, ruff
Phase 2 ─ API & Intégration ──────── 3 sem ─── panini serve, web UI
Phase 3 ─ Pipeline robuste ───────── 2 sem ─── docker compose up
Phase 4 ─ Recherche ──────────────── continu ── papier publiable
Phase 5 ─ Filesystem sémantique ──── 2-3 mois ─ panini index + search
Phase 6 ─ Scale & Distribution ───── horizon ── multi-user, cloud
```

```
                  MAINTENANT
                      │
                      ▼
              ┌──────────────┐
              │   Phase 0    │  Assainissement
              │  "La vérité" │  Supprimer la fiction
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   Phase 1    │  Qualité
              │  "Confiance" │  Tests + CI + lint
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   Phase 2    │  API
              │  "Utilisable"│  HTTP + Web UI
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   Phase 3    │  Pipeline
              │  "Robuste"   │  Docker + idempotent
              └──────┬───────┘
                     │
         ┌───────────┼───────────┐
         │                       │
  ┌──────▼───────┐       ┌──────▼───────┐
  │   Phase 4    │       │   Phase 5    │
  │  "Publier"   │       │  "Le FS"    │
  │  Recherche   │       │  Index+Search│
  └──────────────┘       └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │   Phase 6    │
                         │  "Scale"     │
                         │  Cloud+Rust  │
                         └──────────────┘
```

---

## Principes directeurs

### 1. Python d'abord, Rust ensuite
Le moteur est en Python. Il fonctionne. Le porter en Rust n'a de sens que pour les
hotpaths profilés (Phase 6), pas comme point de départ.

### 2. Pas de submodules
L'architecture à 10 submodules n'a jamais fonctionné. Monorepo avec des packages
Python bien structurés. Si un module grandit trop, on le sépare *quand* c'est justifié.

### 3. Le README dit la vérité
Chaque fonctionnalité listée dans README.md doit être exécutable en ≤3 commandes.
Pas de "coming soon" implicite.

### 4. CI verte = qualité
Aucun merge sans CI verte. Les tests sont la documentation exécutable du contrat.

### 5. Dolt est optionnel
Le moteur d'analyse fonctionne sans Dolt (mode mémoire ou SQLite). Dolt est pour
la persistance versionnée, pas un prérequis pour utiliser l'outil.

### 6. La base Dolt est un cache calculé (Règle n°3)
Toujours reconstructible. Jamais la seule copie.

### 7. Chaque session produit un journal (Règle n°1)
Traçabilité de chaque décision architecturale.

---

## Risques & mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Phase 0 casse des scripts existants | 🟠 Moyenne | 🟡 Moyen | Faire les renames en un commit atomique, vérifier les imports |
| DoltDB indisponible sur CI | 🟡 Faible | 🟠 Élevé | Mode SQLite/mémoire obligatoire (Phase 3) |
| Couverture régresse après restructuration | 🟠 Moyenne | 🟠 Élevé | Golden tests figés AVANT la restructuration |
| Scope creep (ajouter des langues au lieu de consolider) | 🟠 Moyenne | 🟡 Moyen | Gel des langues à 14 jusqu'à Phase 4 |
| Motivation : refactor sans nouvelle fonctionnalité | 🟡 Faible | 🟠 Élevé | Phase 2 (API + Web) fournit un résultat visible rapidement |

---

## Métriques de succès par phase

| Phase | Métrique | Cible |
|-------|---------|-------|
| 0 | `pip install -e .` et `panini analyze` fonctionnent | ✅/❌ |
| 0 | Nombre de fichiers à la racine du repo | ≤15 |
| 0 | `sys.path.insert` dans le code | 0 |
| 1 | Couverture de tests (`panini/engine/`) | ≥80% |
| 1 | CI verte sur chaque PR | 100% |
| 1 | Temps de CI | <5 min |
| 2 | `curl localhost:8080/api/v1/analyze` retourne du JSON | ✅/❌ |
| 2 | Web UI affiche les atomes d'un texte | ✅/❌ |
| 3 | `docker compose up` → tout fonctionne | ✅/❌ |
| 3 | Re-ingestion du même texte = no-op | ✅/❌ |
| 4 | F1 reconstruction E2 (FR) | ≥70% |
| 4 | Article publié (Medium ou preprint) | ✅/❌ |
| 5 | `panini search "concept"` retourne des fichiers pertinents | ✅/❌ |
| 5 | Temps d'indexation de 1000 fichiers | <10 min |

---

## Annexe A — Arborescence cible (post Phase 0)

```
Panini-FS/
├── panini/                      ← Package Python principal
│   ├── __init__.py              ← version, exports
│   ├── cli.py                   ← Point d'entrée CLI
│   ├── engine/                  ← Moteur d'analyse
│   │   ├── __init__.py
│   │   ├── seven_layers.py      ← ex seven_layers_engine.py
│   │   ├── morpho_bridge.py     ← ex morpho_semantic_bridge.py
│   │   ├── text_normalizer.py   ← NFC, BCP 47, époques
│   │   └── reconstruction.py    ← ex reconstruction_engine.py
│   ├── ingest/                  ← Extracteurs & ingestion
│   │   ├── __init__.py
│   │   ├── text_extractor.py
│   │   ├── document_analyzer.py
│   │   ├── gutenberg.py         ← ex gutenberg_ingest.py
│   │   ├── wikipedia.py         ← ex wikipedia_corpus_loader.py
│   │   └── chunker.py           ← ex src/semantic_chunker.py
│   ├── storage/                 ← Persistance (Dolt/SQLite)
│   │   ├── __init__.py
│   │   ├── dolt_manager.py
│   │   ├── branch_acl.py
│   │   └── schema/              ← fichiers .sql
│   ├── export/                  ← Sérialisation
│   │   ├── __init__.py
│   │   └── semantic_serializer.py
│   ├── data/                    ← Données statiques
│   │   ├── atoms.yaml           ← Définition normative des 34 atomes
│   │   ├── atom_keywords.py     ← Dictionnaires mot→atome
│   │   ├── exotic_keywords.py   ← CJK, Indic
│   │   └── language_profiles.py ← Profils linguistiques
│   └── api/                     ← Serveur HTTP (Phase 2)
│       ├── __init__.py
│       ├── server.py            ← FastAPI app
│       └── models.py            ← Pydantic schemas
├── tests/                       ← Tests
│   ├── fixtures/                ← 14 fichiers sample (1/langue)
│   ├── test_engine.py
│   ├── test_ingest.py
│   ├── test_normalizer.py
│   └── test_cli.py
├── web-ui/                      ← Interface web (Phase 2)
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── docs/                        ← MkDocs
├── scripts/                     ← Outillage DevOps
│   ├── ops/                     ← Scripts opérationnels
│   ├── devops/                  ← CI/CD helpers
│   └── legacy/                  ← Anciens scripts racine
├── Copilotage/                  ← Journal & coordination
├── governance/                  ← Gouvernance
├── e2e/                         ← Tests Playwright
├── pyproject.toml               ← Configuration du package
├── mkdocs.yml                   ← Configuration docs
├── README.md                    ← LA VÉRITÉ
├── LICENSE
└── .github/workflows/
    ├── ci.yml                   ← Tests + lint
    └── deploy-docs.yml          ← MkDocs → GitHub Pages
```

---

## Annexe B — Correspondance `IDEAS_INVENTORY.md` → Phases

| ID Inventaire | Idée | Phase |
|---------------|------|-------|
| Moteur 7 couches | ✅ Fait — restructurer en package | 0 |
| Pipeline extraction multi-format | ✅ Fait — intégrer dans `panini/ingest/` | 0 |
| CLI d'analyse | `panini analyze` | 0 |
| Tests unitaires | pytest + CI | 1 |
| API REST sémantique | FastAPI `/api/v1/` | 2 |
| Web UI React | Connecter les stubs existants | 2 |
| Docker Compose | Dolt + API + Web | 3 |
| Expérience E2 formalisée | Protocole + métriques | 4 |
| Compression sémantique mesurée | Benchmarks publiables | 4 |
| Index sémantique de fichiers | `panini index` | 5 |
| Recherche sémantique | `panini search` | 5 |
| FUSE mount | Python fusepy | 5 (optionnel) |
| Rust hotpath | PyO3 keyword matching | 6 |
| Multi-utilisateur | JWT + branches Dolt | 6 |

---

## Annexe C — Ce qu'on ne fait PAS (et pourquoi)

| Tentation | Raison de ne pas le faire |
|-----------|--------------------------|
| Réécrire en Rust maintenant | Le Python marche. Rust sans tests ni CI = encore plus de dette |
| Ajouter des langues (arabe, coréen) | Consolider les 14 existantes d'abord |
| 10 submodules GitHub | Complexité de synchronisation sans bénéfice prouvé |
| Base de données PostgreSQL | Dolt suffit (versionné + MySQL). SQLite pour le local |
| Plugin VS Code maintenant | Pas d'API pour l'alimenter. Phase 2 d'abord |
| Intelligence artificielle / LLM | Le moteur est rule-based par design. LLM = optionnel, pas requis |
| Android/iOS app | Web first. Mobile quand le web est stable |

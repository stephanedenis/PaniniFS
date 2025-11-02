# 🥖 Panini-FS# 🥖 Panini-FS v2.0



**Content-Addressed Filesystem with Emotional Intelligence****Système de graphe de connaissances distribué avec Git**



[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/stephanedenis/Panini-FS)[![Tests](https://img.shields.io/badge/tests-149%2F149%20passing-brightgreen)](TEST_RESULTS.md)

[![Rust](https://img.shields.io/badge/rust-1.70%2B-orange)](https://www.rust-lang.org/)[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/stephanedenis/Panini-FS)

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)[![Rust](https://img.shields.io/badge/rust-1.88%2B-orange)](https://www.rust-lang.org/)

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Panini is a filesystem that understands both *what* your files contain and *how* they make you feel. Named after the Sanskrit grammarian Pāṇini, it decomposes content to its atomic elements and classifies it using affective neuroscience.

---

---

## 🎯 En Bref

## ✨ Features

Panini-FS est un système de **gestion de connaissances** qui combine:

### 🎯 Content-Addressed Storage (CAS)

- **Automatic Deduplication**: Store each piece of content only once- 🌳 **Git** pour le versionning distribué

- **SHA-256 Addressing**: Cryptographically secure content identification  - 📝 **Markdown + YAML** pour le format lisible

- **Bit-Perfect Reconstruction**: Lossless recovery of original files- 🔍 **RocksDB + Tantivy** pour l'indexation rapide

- **Atomic Decomposition**: Files broken into reusable atoms- 🔗 **Graphe de connaissances** pour relier les concepts

- 💻 **CLI moderne** en Rust

### 🧠 Emotional Intelligence (Dhātu)

- **7 Primary Emotions**: Based on Jaak Panksepp's affective neuroscience```bash

- **Sanskrit Roots**: Connects to 2000+ years of linguistic analysis# Créer votre base de connaissances en 30 secondes

- **Emotional Profiles**: Classify files by emotional contentpanini init mon-savoir

- **Resonance Calculation**: Find emotionally similar contentcd mon-savoir

panini create rust --title "Rust Programming"

### 🗂️ FUSE Filesystempanini list

- **Virtual Filesystem**: Browse content as directories```

- **Concept Trees**: Semantic organization beyond folders

- **Time-Travel**: Access historical versions via content addressing---

- **Read-Only Safety**: Prevents accidental modification

## ✨ Fonctionnalités

### 🌐 REST API

- **Upload & Search**: Full deduplication API- ✅ **Git-native**: Chaque concept est versionné, branché, fusionné

- **Emotional Classification**: Analyze text for emotional content- ✅ **Format ouvert**: Markdown + YAML = éditable partout

- **Statistics & Analytics**: Real-time metrics- ✅ **Recherche rapide**: Tantivy pour recherche fulltext 20+ langues

- **CORS Support**: Web-friendly- ✅ **Relations typées**: IsA, PartOf, RelatedTo, Causes, Requires...

- ✅ **Local-first**: Pas de cloud requis, fonctionne offline

### 🎨 Web UI- ✅ **Distribué**: Push/pull comme Git

- **Deduplication Dashboard**: Upload files, view stats, search atoms- ✅ **100% testé**: 149 tests automatisés

- **Dhātu Dashboard**: Classify text, visualize emotions, calculate resonance

- **Real-Time Updates**: Live statistics and charts---

- **Modern React**: TypeScript, Recharts, Tailwind CSS

## 🚀 Installation

---

### Prérequis

## 📊 Seven Primary Emotions

- Rust 1.75+ ([rustup.rs](https://rustup.rs/))

Based on **Jaak Panksepp's** research, Panini classifies content across seven universal emotional systems:- Git



| Emotion | Sanskrit | Meaning | Color |### Build

|---------|----------|---------|-------|

| **SEEKING** | icchā (इच्छा) | Exploration, curiosity, desire | 🟡 Gold |```bash

| **FEAR** | bhaya (भय) | Anxiety, threat avoidance | 🟣 Indigo |git clone https://github.com/stephanedenis/Panini-FS.git

| **RAGE** | krodha (क्रोध) | Anger, frustration, assertion | 🔴 Crimson |cd Panini-FS

| **LUST** | kāma (काम) | Sexual desire, erotic arousal | 🌸 Pink |cargo build --release

| **CARE** | karuṇā (करुणा) | Nurturing, compassion, bonding | 🟢 Green |sudo cp target/release/panini /usr/local/bin/

| **PANIC/GRIEF** | śoka (शोक) | Separation distress, sadness | 🔵 Blue |```

| **PLAY** | krīḍā (क्रीडा) | Joyful engagement, social bonding | 🟠 Orange |

### Vérification

---

```bash

## 🚀 Quick Startpanini --version

# Panini-FS v2.0.0

### Installation```



```bash---

# Clone repository

git clone https://github.com/stephanedenis/Panini-FS.git## 📖 Documentation

cd Panini-FS

- **[⚡ Démarrage Rapide](QUICKSTART.md)** - 5 minutes pour commencer

# Build release binaries- **[📚 Guide Complet](GUIDE_UTILISATION.md)** - Tout ce qu'il faut savoir

cargo build --release- **[🧪 Résultats Tests](TEST_RESULTS.md)** - 149/149 tests passing

- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - Design technique

# Binaries will be in target/release/

ls target/release/panini-*---

```

## 💡 Exemples

### Usage

### Créer une Base de Connaissances Personnelle

#### 1. Start the API Server

```bash

```bashpanini init ~/knowledge

export PANINI_STORAGE="$HOME/.panini/storage"cd ~/knowledge

./target/release/panini-api

```# Ajouter des concepts

panini create rust-ownership \

Server runs on `http://localhost:3030`  --title "Rust Ownership System" \

  --tags "rust,memory-safety"

#### 2. Upload Files (Deduplication)

panini create borrowing \

```bash  --title "Borrowing Rules" \

curl -X POST http://localhost:3030/api/dedup/upload \  --tags "rust,memory-safety"

  -F "file=@example.txt"

```# Relier les concepts

panini add-relation borrowing \

#### 3. Classify Text (Emotional Analysis)  --rel-type part_of \

  rust-ownership \

```bash  --confidence 1.0

curl -X POST http://localhost:3030/api/dhatu/classify \

  -H "Content-Type: application/json" \# Explorer

  -d '{panini relations rust-ownership

    "path": "/test/example.txt",panini search "memory safety"

    "text": "This is an exciting journey of exploration!"```

  }' | jq

```### Documentation de Projet



#### 4. Mount FUSE Filesystem```bash

cd mon-projet/

```bashpanini init docs/knowledge

mkdir /tmp/panini-mount

PANINI_STORAGE="$HOME/.panini/storage" \# Structure de documentation

  ./target/release/panini-mount /tmp/panini-mountpanini create architecture --title "System Architecture"

panini create api --title "API Design"

# Browse contentpanini create deployment --title "Deployment Guide"

ls -la /tmp/panini-mount

# Relations

# Unmountpanini add-relation api --rel-type part_of architecture

fusermount3 -u /tmp/panini-mountpanini add-relation deployment --rel-type requires architecture

``````



#### 5. Launch Web UI### Zettelkasten / Notes Atomiques



```bash```bash

cd web-ui# Notes avec timestamp

npm installpanini create $(date +%Y%m%d%H%M) \

npm run dev  --title "Learning: Rust Lifetimes" \

```  --tags "til,rust,learning"



Open `http://localhost:5173` in your browser.# Liens entre notes

panini add-relation 202510301430 \

---  --rel-type related_to 202510301445

```

## 📚 Documentation

---

- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get running in 15 minutes

- **[FAQ](docs/guides/FAQ.md)** - Frequently asked questions## 🏗️ Architecture

- **[API Reference](docs/api/)** - Full endpoint documentation (coming soon)

- **[Architecture](docs/architecture/)** - System design (coming soon)```

Panini-FS

---│

├── Git Repository          # Storage backend

## 🏗️ Architecture│   └── knowledge/         # Markdown + YAML files

│

```├── Index Layer

┌─────────────────────────────────────────────────────────┐│   ├── RocksDB            # Metadata & relations

│                     Web UI (React)                      ││   └── Tantivy            # Fulltext search

│        Deduplication + Dhātu Dashboards                 ││

└────────────────┬────────────────────────────────────────┘├── Core Library           # Business logic

                 │ HTTP│   ├── Concepts           # CRUD operations

┌────────────────▼────────────────────────────────────────┐│   ├── Relations          # Graph operations

│                  REST API (Axum)                        ││   ├── Query Engine       # Unified search

│   /api/dedup/*  │  /api/dhatu/*  │  /health            ││   └── Git Integration    # Version control

└────────┬────────┴────────┬────────┴─────────────────────┘│

         │                 │└── CLI                    # User interface

         │                 │    └── 12 commands        # init, create, read, ...

┌────────▼────────┐  ┌────▼──────────┐  ┌───────────────┐```

│   CAS Storage   │  │ Dhātu System  │  │ FUSE Mount    │

│   (RocksDB)     │  │  (RocksDB)    │  │ (fuse-rs)     │---

│   - Atoms       │  │  - Profiles   │  │  - /atoms/    │

│   - Index       │  │  - Resonance  │  │  - /concepts/ │## 🎨 Format des Fichiers

│   - Dedup       │  │  - Sanskrit   │  │  - /index/    │

└─────────────────┘  └───────────────┘  └───────────────┘Les concepts sont stockés en **Markdown lisible**:

```

```markdown

### Core Components---

id: rust-ownership

- **panini-core**: Storage engine, dhātu classifier, indicestype: Concept

- **panini-api**: REST API server with Axumtitle: Rust Ownership System

- **panini-fuse**: FUSE filesystem implementationtags: [rust, memory-safety]

- **panini-cli**: Command-line tools (future)relations:

- **panini-benchmarks**: Criterion performance tests  - rel_type: PartOf

    target: rust-lang

---    confidence: 1.0

---

## 🔬 Performance

# Rust Ownership System

Benchmarked on modern hardware (2024):

L'ownership est la fonctionnalité phare de Rust...

| Operation | Performance | Notes |

|-----------|-------------|-------|## Règles

| SHA-256 Hash | ~500 MB/s | Content addressing |

| Dedup Check | <1ms | Hash table lookup |1. Chaque valeur a un owner

| Upload (new) | ~200-500ms | 100MB file |2. Un seul owner à la fois

| Upload (dup) | ~1-2ms | Already stored |3. Quand le owner sort du scope, la valeur est droppée

| Text Classification | <1ms | Medium text (100 chars) |```

| Resonance Calc | <1μs | Profile similarity |

| FUSE Read (cached) | 10-100x faster | LRU cache hit |**Compatible avec**: Obsidian, Logseq, VS Code, tout éditeur Markdown!



Run benchmarks: `cargo bench --package panini-benchmarks`---



---## 🧪 Qualité



## 🧪 Testing- ✅ **149 tests** automatisés (100% passing)

- ✅ **0 erreurs** de compilation

### End-to-End Tests- ✅ **112 tests** core library

- ✅ **12 tests** CLI

```bash- ✅ **25 tests** intégration

# All tests (API + FUSE)- ✅ **Binary release** 7.4 MB fonctionnel

cd e2e && ./tests/run-all.sh

Voir [TEST_RESULTS.md](TEST_RESULTS.md) pour les détails.

# API only

cd e2e && npx playwright test tests/api.spec.js---



# FUSE only## 🛣️ Roadmap

cd e2e && ./tests/fuse-integration.sh

```### v2.0 ✅ (Actuel)

- [x] Git-native storage

### Unit Tests- [x] RocksDB + Tantivy indexing

- [x] CLI complet (12 commandes)

```bash- [x] Relations typées

cargo test --all- [x] Recherche fulltext

```

### v2.1 🚧 (Prochain)

---- [ ] `panini sync` - Synchronisation distribuée

- [ ] `panini status` - État du dépôt

## 🤝 Contributing- [ ] `panini graph` - Visualisation

- [ ] `panini export` - Export HTML/PDF

We welcome contributions! Areas of interest:- [ ] API REST (panini-server)



- **Dhātu System**: Improve emotional classification accuracy### v2.2 🔮 (Futur)

- **ML Integration**: Add machine learning models- [ ] Import Notion/Obsidian

- **File Formats**: Support more types (PDF, audio, video)- [ ] Collaboration temps réel

- **Performance**: Optimize hot paths- [ ] S3-compatible storage

- **Documentation**: Tutorials, guides, examples- [ ] Web UI

- **Sanskrit Expertise**: Better dhātu root mappings

---

See `CONTRIBUTING.md` for guidelines (coming soon).

## 🤝 Contribution

---

Les contributions sont bienvenues! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Roadmap

```bash

### ✅ v1.0 (Current - December 2024)# Development

- Content-addressed storage with deduplicationcargo build

- Dhātu emotional classification systemcargo test --all

- FUSE filesystem with concept treescargo run -- init test-repo

- REST API with full functionality

- Web UI with dashboards# Format

- Performance benchmarkscargo fmt

- LRU cachingcargo clippy

- Comprehensive documentation```



### 🚧 v1.1-1.2 (Q1 2025)---

- Machine learning emotion classifier

- Write support in FUSE## 📊 Statistiques

- S3-compatible distributed storage

- Advanced semantic search- **~10,000** lignes de code production

- Plugin system- **~3,500** lignes de documentation

- More file format support- **149** tests automatisés

- **38** commits depuis le début

### 🔮 v2.0+ (Future)- **6** modules core

- Multi-node clustering- **12** commandes CLI

- Real-time collaboration

- Advanced analytics---

- Mobile apps

- Cloud hosting service## 📜 Licence



---MIT License - Voir [LICENSE](LICENSE)



## 📜 License---



[MIT License](LICENSE) - See LICENSE file for details## 🙏 Remerciements



---- [Git](https://git-scm.com/) pour le stockage distribué

- [Tantivy](https://github.com/quickwit-oss/tantivy) pour la recherche

## 🙏 Acknowledgments- [RocksDB](https://rocksdb.org/) pour l'indexation

- [Rust](https://www.rust-lang.org/) pour la performance et sûreté

- **Jaak Panksepp**: For pioneering affective neuroscience research

- **Pāṇini**: For inspiring our approach to atomic decomposition---

- **Rust Community**: For amazing tools and libraries

- **Contributors**: Everyone who makes Panini better## 📞 Contact



---- **Issues**: https://github.com/stephanedenis/Panini-FS/issues

- **Discussions**: https://github.com/stephanedenis/Panini-FS/discussions

## 📧 Contact

---

- **Website**: https://paninifs.org

- **GitHub**: https://github.com/stephanedenis/Panini-FS<div align="center">

- **Issues**: https://github.com/stephanedenis/Panini-FS/issues

- **Discussions**: https://github.com/stephanedenis/Panini-FS/discussions**Fait avec ❤️ pour les passionnés de gestion des connaissances**



---[⭐ Star sur GitHub](https://github.com/stephanedenis/Panini-FS) | [📖 Documentation](GUIDE_UTILISATION.md) | [🚀 Démarrage Rapide](QUICKSTART.md)



**Made with ❤️ by the Panini Team**</div>


*"देवनागरी लिपि में पाणिनि" - Pāṇini in Devanagari script*

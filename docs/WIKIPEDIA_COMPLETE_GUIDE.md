# 🕉️ Wikipedia dans Panini-FS: Guide Complet

## Vue d'Ensemble

Ce guide explique comment ingérer **toutes les Wikipédias** dans Panini-FS, créer un modèle unifié multilingue, et l'analyser pour des recherches en:
- Déduplication massive inter-langues
- Analyse culturelle émotionnelle (Dhātu)
- Graphe de connaissances universel
- Concepts communs à l'humanité

---

## 🚀 Ingestion Complète

### Prérequis

1. **Dumps Wikipedia téléchargés**:
   ```bash
   # Structure attendue:
   ~/GitHub/Panini/wikipedia_dumps/
   ├── sawiki-latest-pages-articles.xml.bz2  # Sanskrit (19M)
   ├── hiwiki-latest-pages-articles.xml.bz2  # Hindi (217M)
   ├── frwiki-latest-pages-articles.xml.bz2  # Français (6.3G)
   ├── dewiki-latest-pages-articles.xml.bz2  # Allemand (7.2G)
   └── enwiki-latest-pages-articles.xml.bz2  # Anglais (23G)
   ```

2. **Espace disque**: Minimum 300GB disponible
   - Dumps compressés: ~37GB
   - Données décompressées: ~200-300GB
   - **Avec déduplication Panini**: ~100-150GB (50%+ économie)

3. **API Panini lancée**:
   ```bash
   tools/start_api_wikipedia.sh
   ```

### Lancement de l'Ingestion Massive

```bash
# Option 1: Storage par défaut (/tmp)
./tools/ingest_all_wikipedia.sh

# Option 2: Storage personnalisé (recommandé)
export PANINI_STORAGE=/mnt/data/panini-wikipedia-full
./tools/ingest_all_wikipedia.sh
```

Le script va:
1. ✅ Vérifier l'espace disque
2. ✅ Détecter tous les dumps disponibles
3. ✅ Ingérer chaque langue séquentiellement
4. ✅ Classifier avec Dhātu (profils émotionnels)
5. ✅ Sauvegarder des checkpoints (reprise possible)
6. ✅ Générer un rapport global
7. ✅ Optionnel: Créer une archive de backup

### Temps Estimés

| Langue | Taille | Articles Estimés | Temps (130 art/s) |
|--------|--------|------------------|-------------------|
| Sanskrit | 19M | ~5K | ~40 secondes |
| Hindi | 217M | ~150K | ~20 minutes |
| Français | 6.3G | ~2.5M | ~5 heures |
| Allemand | 7.2G | ~2.8M | ~6 heures |
| Anglais | 23G | ~6.5M | ~14 heures |
| **TOTAL** | **~37G** | **~12M articles** | **~25 heures** |

**Avec optimisation batch (future)**: ~2-3 heures seulement!

---

## 📊 Analyse du Modèle

Une fois l'ingestion terminée, analysez le modèle complet:

```bash
python3 tools/analyze_panini_model.py \
    --storage /mnt/data/panini-wikipedia-full \
    --api http://localhost:3000/api
```

### Analyses Disponibles

#### 1. **Déduplication Globale**
- Nombre d'atoms uniques vs réutilisés
- Taux de déduplication inter-langues (attendu: 30-80%)
- Top atoms les plus partagés (dates, structures, citations)
- Économie d'espace réalisée

#### 2. **Profils Émotionnels Culturels**
- Distribution Dhātu par langue
- Comparaison fr vs en vs de vs sa vs hi
- Identification de patterns culturels:
  - Langues "CARE" (compassion élevée)
  - Langues "SEEKING" (curiosité dominante)
  - Langues "PLAY" (engagement ludique)
- Arousal moyen par culture

#### 3. **Concepts Universels**
- Articles présents dans 3+ langues
- Termes techniques identiques
- Noms propres internationaux
- Structures Wikitext communes

#### 4. **Graphe de Connaissances**
- Nœuds: Articles (12M+)
- Arêtes: Liens inter-langues, atoms partagés
- Export GraphML, Neo4j, RDF
- Analyses de centralité, communautés, PageRank

---

## 🔬 Cas d'Usage Scientifiques

### 1. Linguistique Computationnelle
- Identifier les structures syntaxiques universelles
- Comparer évolutions sémantiques entre langues
- Analyser la diffusion de concepts entre cultures

### 2. Anthropologie Numérique
- Profils émotionnels par civilisation
- Valeurs culturelles encodées dans Wikipedia
- Universaux vs particularismes

### 3. Théorie de l'Information
- Mesurer la redondance inter-langues
- Calculer l'entropie informationnelle
- Optimiser la compression multilingue

### 4. Graphes de Connaissances
- Construire un graphe unifié toutes langues
- Aligner les ontologies Wikipedia
- Enrichir DBpedia/Wikidata

### 5. Études Panini
- Retrouver les dhātu (racines) sanskrites dans toutes les langues
- Tracer l'évolution étymologique
- Valider la théorie de Pāṇini à l'échelle mondiale

---

## 📁 Structure du Modèle Sauvegardé

```
$PANINI_STORAGE/
├── atoms/                      # Atoms CAS dédupliqués
│   ├── 00/
│   ├── 01/
│   └── ...                     # ~1-10M atoms uniques
├── index/                      # Index de recherche
│   ├── rocksdb/                # Index RocksDB
│   └── tantivy/                # Index full-text Tantivy
├── dhatu/                      # Profils émotionnels
│   └── rocksdb/                # ~12M profils persistés
└── checkpoints/                # Points de reprise
    ├── sa_checkpoint.json
    ├── hi_checkpoint.json
    ├── fr_checkpoint.json
    ├── de_checkpoint.json
    └── en_checkpoint.json

reports/wikipedia_full/
├── sa_report.json              # Stats par langue
├── hi_report.json
├── fr_report.json
├── de_report.json
├── en_report.json
└── GLOBAL_REPORT.md            # Rapport agrégé
```

---

## 🎯 Requêtes API Utiles

### Statistiques Globales
```bash
# Déduplication
curl http://localhost:3000/api/dedup/stats | jq

# Émotions
curl http://localhost:3000/api/dhatu/stats | jq
```

### Recherche d'Atoms
```bash
# Trouver un concept
curl "http://localhost:3000/api/atoms/search?query=Pāṇini" | jq

# Détails d'un atom
curl "http://localhost:3000/api/atoms/HASH" | jq
```

### Classification Émotionnelle
```bash
curl -X POST http://localhost:3000/api/dhatu/classify \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/wikipedia/sa/0/पाणिनि",
    "content": "पाणिनि महान् वैयाकरणः आसीत्..."
  }' | jq
```

### Montage FUSE
```bash
# Monter le corpus complet
PANINI_STORAGE=/mnt/data/panini-wikipedia-full \
  cargo run --bin panini-mount /mnt/wikipedia

# Explorer
ls /mnt/wikipedia/concepts/
find /mnt/wikipedia -name "*Pāṇini*"
cat /mnt/wikipedia/atoms/HASH
```

---

## 🔧 Optimisations Futures

### Performance
1. **Batch Upload**: Grouper 100 articles → 100x plus rapide
2. **Parallel Workers**: 8-16 workers Dhātu → 10x plus rapide
3. **Streaming Pipeline**: parse → upload → classify en continu
4. **Cible**: **10,000 articles/sec** (77x amélioration)

### Stockage
1. **Compression Atoms**: LZ4/ZSTD sur atoms froids
2. **Tiering**: Hot (SSD) vs Cold (HDD) storage
3. **Sharding**: Distribuer atoms sur plusieurs disques

### Fonctionnalités
1. **API Batch**: `/api/files/analyze-batch` pour uploads multiples
2. **Streaming Stats**: WebSocket pour progression en temps réel
3. **Filtres Langues**: Ingérer seulement certaines langues
4. **Resume**: Reprendre ingestion après crash

---

## 📝 Rapport de Test Sanskrit

**Validation préliminaire** (155 articles Sanskrit):
- ✅ 130 articles/seconde
- ✅ 5.7% déduplication (monolingue)
- ✅ 100% classification Dhātu réussie
- ✅ Profils émotionnels: PLAY (30%), CARE (25%)
- ✅ Bit-perfect garanti (CAS + SHA-256)

Voir: `reports/WIKIPEDIA_TEST_REPORT.md`

---

## 🌍 Impact Scientifique Attendu

### Publications Possibles
1. **"Panini-FS: A Universal Knowledge Graph"** → ACL, EMNLP
2. **"Cultural Emotional Profiles in Wikipedia"** → CHI, CSCW
3. **"Massive Cross-Lingual Deduplication"** → WWW, KDD
4. **"Sanskrit Dhātu Roots in Modern Languages"** → LREC, Coling

### Collaborations
- **Wikimedia Foundation**: Optimiser leur infrastructure
- **Google Knowledge Graph**: Enrichir leur graphe
- **Stanford NLP**: Analyse multilingue
- **Institut Sanskrit**: Études paniniennes computationnelles

### Open Source
- Modèle Panini complet: Téléchargeable (archive .tar.gz)
- API ouverte: Requêtes publiques sur le corpus
- Notebooks Jupyter: Analyses reproductibles
- Datasets: Atoms partagés, profils émotionnels

---

## 📞 Support & Contribution

**Issues**: https://github.com/stephanedenis/Panini-FS/issues
**Discussions**: https://github.com/stephanedenis/Panini-FS/discussions
**Documentation**: https://github.com/stephanedenis/Panini-FS/wiki

---

**Généré par**: Panini-FS v1.0.0
**Auteur**: Stéphane Denis
**Licence**: MIT
**Citation**: Denis, S. (2025). Panini-FS: Content-Addressed Filesystem with Emotional Intelligence.

🕉️ *"यथा पिण्डे तथा ब्रह्माण्डे"* - Comme dans l'atome, ainsi dans l'univers 🕉️

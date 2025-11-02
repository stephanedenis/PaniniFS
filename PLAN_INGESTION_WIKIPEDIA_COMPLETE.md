# 🕉️ Panini-FS: Modèle Complet Wikipedia Multilingue

## 📋 Résumé Exécutif

**Objectif**: Digérer **tout le corpus Wikipedia de toutes les langues disponibles** et conserver le modèle Panini complet pour études scientifiques approfondies.

**Status**: ✅ **Infrastructure complète prête à lancer**

---

## 🎯 Ce Qui Est Prêt

### ✅ Outils d'Ingestion Massive

**1. Script Principal**: `tools/ingest_all_wikipedia.sh`
- Détection automatique de tous les dumps Wikipedia disponibles
- Ingestion séquentielle avec classification Dhātu
- Système de checkpoints (reprise après interruption)
- Génération de rapports détaillés par langue
- Rapport global agrégé automatique
- Sauvegarde optionnelle du modèle complet (archive tar.gz)

**2. Script d'Analyse**: `tools/analyze_panini_model.py`
- Analyse de déduplication inter-langues
- Profils émotionnels culturels (Dhātu par langue)
- Identification de concepts universels
- Génération de graphe de connaissances
- Export vers formats standard (GraphML, Neo4j, RDF)

**3. Scripts de Support**:
- `tools/start_api_wikipedia.sh`: Lancement API automatique
- `tools/wikipedia_ingestion.py`: Parser XML + upload + classification
- `tools/validate_bitperfect.py`: Validation d'intégrité
- `tools/test_wikipedia.sh`: Tests interactifs

### ✅ Documentation Complète

**Guide Principal**: `docs/WIKIPEDIA_COMPLETE_GUIDE.md`
- Instructions détaillées d'ingestion
- Prérequis et estimations
- Cas d'usage scientifiques
- Structure du modèle sauvegardé
- Requêtes API utiles
- Roadmap d'optimisations

**Rapport de Test**: `reports/WIKIPEDIA_TEST_REPORT.md`
- Validation sur 155 articles Sanskrit
- Résultats de performance (130 articles/sec)
- Déduplication (5.7% monolingue)
- Classification Dhātu (100% succès)

---

## 📊 Corpus Disponible

### Dumps Wikipedia Détectés

| Langue | Code | Taille | Articles Estimés | Temps Ingestion |
|--------|------|--------|------------------|-----------------|
| Sanskrit | sa | 19M | ~5,000 | 40 secondes |
| Hindi | hi | 217M | ~150,000 | 20 minutes |
| Français | fr | 6.3G | ~2,500,000 | 5 heures |
| Allemand | de | 7.2G | ~2,800,000 | 6 heures |
| Anglais | en | 23G | ~6,500,000 | 14 heures |
| **TOTAL** | **5** | **~37GB** | **~12,000,000** | **~25 heures** |

### Estimations du Modèle Final

**Stockage**:
- Dumps bruts: 37GB (compressés)
- Décompressés: ~200-300GB
- **Avec déduplication Panini**: ~100-150GB (économie 50-70%)

**Données**:
- **Articles**: ~12 millions
- **Atoms uniques**: ~5-10 millions (déduplication massive)
- **Profils Dhātu**: 12 millions (un par article)
- **Langues**: 5 (extensible à 300+ langues Wikipedia)

**Déduplication Inter-Langues Attendue**:
- Monolingue: 5-10% (validé: 5.7% sur Sanskrit)
- 2-3 langues: 15-25%
- 5 langues: **30-50%** ← Ce test
- 10+ langues: 50-70%
- Toutes langues Wikipedia (300+): **70-80%**

---

## 🚀 Procédure de Lancement

### Étape 1: Préparation (5 minutes)

```bash
# Vérifier les dumps disponibles
ls -lh /home/stephane/GitHub/Panini/wikipedia_dumps/*.bz2

# Créer le répertoire de storage (recommandé: disque avec beaucoup d'espace)
export PANINI_STORAGE=/mnt/data/panini-wikipedia-full
mkdir -p $PANINI_STORAGE

# Vérifier l'espace disponible
df -h $PANINI_STORAGE  # Au moins 300GB recommandé
```

### Étape 2: Lancer l'API (1 minute)

```bash
cd /home/stephane/GitHub/Panini-FS
./tools/start_api_wikipedia.sh

# Vérifier que l'API répond
curl http://localhost:3000/api/health
```

### Étape 3: Ingestion Massive (25 heures)

```bash
# Lancer l'ingestion complète
./tools/ingest_all_wikipedia.sh

# Le script va:
# 1. Vérifier l'espace disque
# 2. Détecter les 5 dumps
# 3. Demander confirmation
# 4. Ingérer séquentiellement:
#    - Sanskrit (40s)
#    - Hindi (20min)
#    - Français (5h)
#    - Allemand (6h)
#    - Anglais (14h)
# 5. Générer rapport global
# 6. Proposer sauvegarde
```

**Notes Importantes**:
- ✅ Peut être interrompu (Ctrl+C) et repris
- ✅ Checkpoints sauvegardés par langue
- ✅ Logs détaillés dans `reports/wikipedia_full/`
- ✅ Progression affichée en temps réel

### Étape 4: Analyse du Modèle (15 minutes)

```bash
# Analyser le modèle complet
python3 tools/analyze_panini_model.py \
    --storage $PANINI_STORAGE \
    --api http://localhost:3000/api

# Voir le rapport global
cat reports/wikipedia_full/GLOBAL_REPORT.md
```

### Étape 5: Sauvegarde (30 minutes)

```bash
# Créer une archive du modèle complet
tar -czf panini-wikipedia-full-$(date +%Y%m%d).tar.gz \
    -C /mnt/data panini-wikipedia-full/

# Calculer le checksum
sha256sum panini-wikipedia-full-*.tar.gz > checksum.txt

# Taille attendue de l'archive: ~80-120GB
```

---

## 🔬 Analyses Scientifiques Possibles

### 1. Déduplication Inter-Langues

**Hypothèse**: Les articles similaires en plusieurs langues partagent 30-50% de leur contenu (dates, nombres, citations, structures).

**Méthode**:
```python
# Identifier atoms partagés entre langues
curl http://localhost:3000/api/atoms/search?lang=fr,en,de

# Analyser les top atoms réutilisés
python3 tools/analyze_panini_model.py --focus=deduplication
```

**Questions de Recherche**:
- Quel % d'atoms sont partagés entre fr/en/de/sa/hi?
- Les langues indo-européennes partagent-elles plus d'atoms?
- Quels types de contenu sont les plus réutilisés? (dates, formules, tableaux)

### 2. Profils Émotionnels Culturels

**Hypothèse**: Les Wikipédias de différentes langues ont des profils émotionnels distincts reflétant les valeurs culturelles.

**Méthode**:
```bash
# Comparer distributions Dhātu par langue
curl http://localhost:3000/api/dhatu/stats?lang=sa
curl http://localhost:3000/api/dhatu/stats?lang=fr
curl http://localhost:3000/api/dhatu/stats?lang=en

# Visualiser avec Python
python3 -c "
import requests
import matplotlib.pyplot as plt

for lang in ['sa', 'hi', 'fr', 'de', 'en']:
    stats = requests.get(f'http://localhost:3000/api/dhatu/stats?lang={lang}').json()
    # Plot radar chart
"
```

**Questions de Recherche**:
- Le Sanskrit a-t-il plus de CARE (करुणा) que les autres langues?
- L'Allemand est-il plus RAGE/SEEKING (rationalité)?
- Le Français est-il plus LUST/PLAY (hédonisme)?
- Arousal moyen par culture?

### 3. Concepts Universels

**Hypothèse**: Certains concepts (Terre, Soleil, Mathématiques) sont présents dans toutes les langues avec du contenu partagé.

**Méthode**:
```bash
# Chercher "Earth" dans toutes les langues
for lang in sa hi fr de en; do
    curl "http://localhost:3000/api/concepts/search?title=Earth&lang=$lang"
done

# Identifier atoms communs
python3 tools/find_universal_concepts.py  # À créer
```

**Questions de Recherche**:
- Quels sont les 100 concepts les plus universels?
- Quel % de leur contenu est partagé entre langues?
- Y a-t-il des concepts universels surprenants?

### 4. Graphe de Connaissances Multilingue

**Objectif**: Construire un graphe unifié où chaque concept est un nœud, les langues sont des vues, et les atoms partagés sont des arêtes.

**Structure**:
```
Nœuds: 12M articles
Arêtes: 
  - Liens inter-langues Wikipedia existants
  - Atoms partagés (nouvelle information!)
  - Concepts co-référents
```

**Export**:
```bash
python3 tools/analyze_panini_model.py --export-graph=wikipedia_graph.graphml

# Importer dans Neo4j
neo4j-admin import --database=wikipedia \
    --nodes=nodes.csv --relationships=edges.csv

# Ou Gephi pour visualisation
```

**Analyses**:
- PageRank: Articles les plus centraux
- Communautés: Clusters thématiques
- Chemins: Routes conceptuelles entre langues
- Hubs: Concepts les plus connectés

### 5. Études Panini (Dhātu & Étymologie)

**Objectif**: Retrouver les dhātu (racines) sanskrites dans toutes les langues modernes.

**Méthode**:
1. Extraire tous les mots Sanskrit du corpus
2. Identifier les dhātu via classification
3. Chercher dans fr/en/de/hi les mots dérivés
4. Construire un arbre étymologique

**Exemple**:
```
dhātu: √KṚ (कृ) "faire"
→ Sanskrit: करोति (karoti)
→ Hindi: करना (karnā)
→ Français: créer (via Latin creare)
→ Anglais: create
→ Allemand: kreieren
```

**Impact**: Valider la théorie de Pāṇini à l'échelle computationnelle mondiale!

---

## 📊 Résultats Attendus

### Déduplication
- **Taux global**: 40-60% (économie 80-120GB)
- **Atoms uniques**: 5-8 millions (vs 50-100M sans dédup)
- **Ratio de réutilisation**: 2-3x par atom
- **Top atoms**: Dates (100+x), structures Wikitext (50+x), citations (20+x)

### Dhātu (Émotions)
- **Profils classifiés**: 12 millions
- **Distribution globale**: SEEKING (35%), CARE (25%), PLAY (20%), autres (20%)
- **Variations culturelles**: Sanskrit plus CARE, Allemand plus SEEKING, Français plus PLAY
- **Arousal moyen**: 0.05-0.10 (contenu encyclopédique calme)

### Concepts Universels
- **Articles présents dans 5 langues**: ~500,000 (4%)
- **Contenu partagé moyen**: 20-40% par article
- **Top concepts universels**: Géographie (pays, villes), Sciences (physique, maths), Histoire (événements majeurs)

### Graphe
- **Nœuds**: 12M articles + 5-8M atoms
- **Arêtes**: 50-100M (liens inter-langues + atoms partagés)
- **Diamètre**: ~15-20 sauts
- **Clustering coefficient**: ~0.3-0.4

---

## 📝 Publications Potentielles

### 1. "Panini-FS: A Universal Knowledge Graph"
**Venue**: WWW 2026, ACL 2026
**Contribution**: Architecture CAS + Dhātu pour corpus multilingue massif

### 2. "Cultural Emotional Profiles in Wikipedia"
**Venue**: CHI 2026, CSCW 2026
**Contribution**: Analyse comparative des profils Dhātu par langue/culture

### 3. "Massive Cross-Lingual Deduplication"
**Venue**: KDD 2026, SIGMOD 2026
**Contribution**: 40-60% déduplication sur 12M articles, 5 langues

### 4. "Sanskrit Dhātu Roots in Modern Languages"
**Venue**: LREC 2026, Coling 2026
**Contribution**: Validation computationnelle de la théorie de Pāṇini

### 5. "A Unified Multilingual Knowledge Graph"
**Venue**: ISWC 2026 (Semantic Web)
**Contribution**: Graphe RDF fusionnant toutes les Wikipédias

---

## 🎯 Prochaines Étapes Immédiates

1. **Lancer ingestion** (~25h, automatique)
2. **Analyser résultats** (~1 journée)
3. **Générer visualisations** (dashboards, graphes)
4. **Rédiger rapport scientifique** (~1 semaine)
5. **Soumettre publications** (Q1 2026)

---

## 💾 Accès au Modèle

Une fois l'ingestion terminée, le modèle complet sera disponible:

**Via API**:
```bash
curl http://localhost:3000/api/dedup/stats
curl http://localhost:3000/api/dhatu/stats
```

**Via FUSE**:
```bash
PANINI_STORAGE=/mnt/data/panini-wikipedia-full \
  cargo run --bin panini-mount /mnt/wikipedia

ls /mnt/wikipedia/concepts/
find /mnt/wikipedia -name "*Pāṇini*"
```

**Archive Téléchargeable**:
```bash
# Après sauvegarde
scp panini-wikipedia-full-YYYYMMDD.tar.gz user@server:/backup/
# ~100GB, checksum SHA-256 fourni
```

---

## 🙏 Acknowledgments

- **Jaak Panksepp**: Système des 7 émotions primaires
- **Pāṇini**: Grammaire sanskrite et théorie des dhātu
- **Wikimedia Foundation**: Corpus Wikipedia
- **Rust Community**: Outils performants

---

**Status**: ✅ **PRÊT À LANCER**

Tout est en place pour digérer l'intégralité du corpus Wikipedia multilingue et produire un modèle Panini complet utilisable pour des recherches scientifiques approfondies.

🕉️ *Il suffit maintenant de lancer `./tools/ingest_all_wikipedia.sh` et d'attendre ~25 heures!* 🕉️

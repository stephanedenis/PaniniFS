# Dolt Concept Store pour PaniniFS

**Proof of Concept** : Intégration de Dolt comme base de données versionnée pour stocker les concepts sémantiques de PaniniFS.

## 🎯 Vision

PaniniFS décompose l'information jusqu'aux **atomes conceptuels universels** — les 7 dhātu informationnels. Ce POC démontre comment **Dolt**, une base SQL avec workflows Git, peut servir de store versionné pour ces concepts, permettant l'expérimentation, la traçabilité et l'évolution du modèle sémantique.

## 🏗️ Architecture : Séparation des Responsabilités

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RUST CORE (CORE/)                            │
│  • Lecture et parsing de fichiers                                   │
│  • Analyse sémantique et extraction des patterns                    │
│  • Détection des atomes dhātu dans le code/texte                   │
│  • Calcul du hash sémantique (déduplication cross-langue)          │
│  • Output: JSON structuré                                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Communication:
                             │  • subprocess + JSON stdout
                             │  • named pipe (streaming)
                             │  • MySQL protocol (direct)
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                    DOLT CONCEPT STORE (SANDBOX/)                     │
│  • Stockage des 7 dhātu et de l'inventaire v0.1                    │
│  • Versioning des mappings sémantiques (Git-like)                  │
│  • Historique complet des analyses (audit trail)                   │
│  • Branches pour expérimentation de nouveaux dhātu                 │
│  • Diff entre versions du modèle sémantique                        │
│  • Attribution et provenance (traçabilité)                         │
│  • Déduplication cross-langue (même concept = même hash)           │
└─────────────────────────────────────────────────────────────────────┘
```

### Frontière de responsabilités claire

| Rust (Analyse)                  | Dolt (Stockage)                   |
|---------------------------------|-----------------------------------|
| Lecture fichiers                | Tables SQL versionnées            |
| Analyse sémantique              | Commits et branches Git-like      |
| Extraction des atomes dhātu     | Historique et audit trail         |
| Calcul des signatures           | Diff entre versions               |
| Hash sémantique                 | Requêtes et agrégations           |
| Output JSON                     | Attribution et provenance         |

## 📚 Les 7 Dhātu Informationnels

Les dhātu sont les atomes conceptuels universels de PaniniFS (référence : `Copilotage/knowledge/SEMANTIC_UNIVERSALS_DHATU.md`):

1. **COMM** (communiquer/partager) — canal, source, cible
2. **ITER** (itérer/répéter) — boucle, fréquence, cumul
3. **TRANS** (transformer) — entrée, opération, sortie
4. **DECIDE** (choisir/régler) — critères, seuils, branches
5. **LOCATE** (localiser/ancrer) — position, contexte, repères
6. **GROUP** (regrouper/structurer) — collection, appartenance
7. **SEQ** (séquencer/ordonner) — ordre, dépendances, timeline

## 📦 Structure du POC

```
SANDBOX/dolt-concept-store/
├── README.md                 # Ce fichier
├── requirements.txt          # Dépendances Python (doltpy)
├── schema.sql               # Schéma SQL complet des tables Dolt
├── init_dolt.py             # Initialisation et seed de la DB
├── demo_workflow.py         # Démonstration du workflow complet
├── rust_bridge_stub.py      # Stub du bridge Rust ↔ Dolt
├── .gitignore              # Ignore la DB locale
└── panini-concepts-db/      # Base Dolt (ignorée par git)
    └── .dolt/              # Repo Dolt (comme .git)
```

## 🚀 Installation et Setup

### Étape 1 : Installer Dolt

Dolt est une base SQL avec Git workflows intégré.

**Linux/macOS:**
```bash
sudo bash -c 'curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh | bash'
```

**Vérifier l'installation:**
```bash
dolt version
```

Documentation complète : https://docs.dolthub.com/introduction/installation

### Étape 2 : Installer les dépendances Python (optionnel)

```bash
cd SANDBOX/dolt-concept-store/
pip install -r requirements.txt
```

**Note:** Le POC utilise principalement `subprocess` pour appeler la CLI `dolt` directement, ce qui est plus fiable que `doltpy` pour les versions récentes de Dolt.

### Étape 3 : Initialiser la base de données

```bash
python init_dolt.py
```

Ce script :
- ✅ Crée un repo Dolt dans `./panini-concepts-db/`
- ✅ Applique le schéma SQL (`schema.sql`)
- ✅ Peuple les 7 dhātu dans `dhatu_definitions`
- ✅ Peuple l'inventaire v0.1 dans `dhatu_inventory`
- ✅ Fait un commit initial : "seed: 7 dhātu + inventory v0.1"

### Étape 4 : Exécuter la démonstration

```bash
python demo_workflow.py
```

Cette démo montre :
- 📝 Déduplication sémantique cross-langue ("Hello world" = "Bonjour monde")
- 📊 Analyse de fichiers avec vecteurs dhātu
- 🌿 Création de branches expérimentales
- 🔍 Diff entre branches (main vs experiment)
- 📜 Historique et audit trail
- 🔎 Requêtes sémantiques avancées

### Étape 5 : Explorer le bridge Rust ↔ Dolt

```bash
python rust_bridge_stub.py
```

Ce stub documente :
- 📡 Contrat d'interface JSON entre Rust et Dolt
- 🔧 3 options de communication (subprocess, named pipe, MySQL protocol)
- 💡 Exemples de code Rust pour connexion directe
- 📝 Comment requêter les résultats depuis n'importe quel langage

## 📊 Schéma des Tables

### 1. `dhatu_definitions`
Définition des 7 dhātu informationnels.

```sql
CREATE TABLE dhatu_definitions (
    id VARCHAR(20) PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name_fr VARCHAR(100),
    name_en VARCHAR(100),
    description TEXT,
    components TEXT,  -- JSON: ["canal", "source", "cible"]
    created_at TIMESTAMP
);
```

### 2. `dhatu_inventory`
Inventaire v0.1 des primitives conceptuelles.

```sql
CREATE TABLE dhatu_inventory (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50),      -- AGENT, ACTION, PATIENT, etc.
    symbol VARCHAR(100),
    stable_id VARCHAR(100),    -- concept:book, action:hunt, etc.
    description TEXT,
    lexicon_alias VARCHAR(100),
    created_at TIMESTAMP
);
```

### 3. `semantic_mappings`
Mappings sémantiques avec déduplication cross-langue.

```sql
CREATE TABLE semantic_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_hash VARCHAR(64),     -- SHA256 du texte original
    source_text TEXT,
    language VARCHAR(10),         -- fr, en, es, etc.
    dhatu_signature JSON,         -- {"COMM": 0.9, "TRANS": 0.1, ...}
    semantic_hash VARCHAR(64),    -- Hash du concept (identique entre langues)
    analyzed_at TIMESTAMP,
    INDEX idx_semantic_hash (semantic_hash)
);
```

**Déduplication:** Textes sémantiquement équivalents partagent le même `semantic_hash`, indépendamment de la langue.

### 4. `analysis_results`
Résultats d'analyse par fichier.

```sql
CREATE TABLE analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(500),
    file_hash VARCHAR(64),
    dhatu_vector JSON,           -- {"COMM": 0.3, "ITER": 0.1, ...}
    dominant_dhatu VARCHAR(20),  -- Dhātu dominant
    analysis_version VARCHAR(20),
    metadata JSON,
    created_at TIMESTAMP,
    INDEX idx_dominant_dhatu (dominant_dhatu)
);
```

### 5. `attribution_log`
Log d'attribution et provenance (traçabilité).

```sql
CREATE TABLE attribution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_type VARCHAR(50),      -- 'semantic_mapping', 'analysis_result'
    entry_id INT,
    semantic_hash VARCHAR(64),
    source VARCHAR(200),         -- URL, file path, etc.
    author VARCHAR(100),
    license VARCHAR(100),
    attribution_text TEXT,
    logged_at TIMESTAMP
);
```

## 🔄 Workflow Git-like avec Dolt

### Branches
```bash
cd panini-concepts-db

# Créer une branche expérimentale
dolt branch experiment/new-dhatu

# Basculer sur la branche
dolt checkout experiment/new-dhatu

# Ajouter un nouveau dhātu candidat
dolt sql -q "INSERT INTO dhatu_definitions ..."

# Commit
dolt add .
dolt commit -m "experiment: add COMPOSE dhatu"
```

### Diff
```bash
# Voir les différences entre branches
dolt diff main experiment/new-dhatu

# Ou via SQL
dolt sql -q "SELECT * FROM dolt_diff_dhatu_definitions"
```

### Merge
```bash
# Merger l'expérimentation si concluante
dolt checkout main
dolt merge experiment/new-dhatu
```

### Historique
```bash
# Voir l'historique complet
dolt log

# Audit trail détaillé
dolt log --oneline
```

## 🌐 Options de Communication Rust ↔ Dolt

### Option 1 : Subprocess (recommandé pour MVP)
**Le plus simple.**

```python
# Python bridge
import subprocess
import json

# Rust analyzer output JSON sur stdout
result = subprocess.run(
    ["rust-analyzer", "analyze", "src/main.rs", "--format", "json"],
    capture_output=True, text=True
)

# Parse et insère dans Dolt
analysis = json.loads(result.stdout)
subprocess.run(
    ["dolt", "sql", "-q", f"INSERT INTO analysis_results ..."],
    cwd="panini-concepts-db"
)
```

### Option 2 : Named Pipe (pour streaming)
**Temps réel, watch mode.**

```bash
# Terminal 1: Rust analyzer en daemon
mkfifo /tmp/panini-analyzer
rust-analyzer watch --output-pipe /tmp/panini-analyzer

# Terminal 2: Python bridge listener
python bridge_daemon.py --input-pipe /tmp/panini-analyzer
```

### Option 3 : MySQL Protocol (pour production)
**Rust → Dolt direct, pas d'intermédiaire.**

```rust
// Rust avec driver MySQL
use mysql::*;

let pool = Pool::new("mysql://root@localhost:3306/panini-concepts-db")?;
let mut conn = pool.get_conn()?;

conn.exec_drop(
    "INSERT INTO analysis_results (file_path, dhatu_vector, ...) VALUES (?, ?, ...)",
    (path, json, ...)
)?;

// Commit via SQL
conn.exec_drop("CALL dolt_commit('-am', 'Analysis from Rust')", ())?;
```

Démarrer le serveur SQL :
```bash
cd panini-concepts-db
dolt sql-server --host 0.0.0.0 --port 3306
```

## 🔍 Requêter les Concepts

### Via CLI
```bash
cd panini-concepts-db

# Les 7 dhātu
dolt sql -q "SELECT code, name_fr, name_en FROM dhatu_definitions"

# Analyses récentes
dolt sql -q "SELECT file_path, dominant_dhatu FROM analysis_results ORDER BY created_at DESC LIMIT 10"

# Déduplication cross-langue
dolt sql -q "SELECT * FROM semantic_deduplication"
```

### Via MySQL Client
```bash
mysql -h 127.0.0.1 -u root panini-concepts-db

mysql> SELECT * FROM dhatu_definitions;
mysql> SELECT * FROM analysis_results WHERE dominant_dhatu = 'TRANS';
```

### Via Python/Rust/autre
```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    database='panini-concepts-db'
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM dhatu_definitions")
for row in cursor:
    print(row)
```

## 📈 Cas d'Usage

### 1. Expérimentation de Nouveaux Dhātu
```bash
# Créer une branche
dolt checkout -b experiment/spatial-dhatu

# Ajouter un dhātu spatial candidat
dolt sql -q "INSERT INTO dhatu_definitions (id, code, name_fr, name_en) 
             VALUES ('dhatu_spatial', 'SPATIAL', 'Spatialiser', 'Spatialize')"

# Tester sur un corpus
python analyze_corpus.py --dhatu spatial

# Si concluant, merger dans main
dolt checkout main
dolt merge experiment/spatial-dhatu
```

### 2. Audit Trail des Analyses
```bash
# Qui a analysé quoi, quand?
dolt log --table analysis_results

# Voir l'évolution d'un fichier spécifique
dolt sql -q "SELECT * FROM analysis_results WHERE file_path = 'src/main.rs' ORDER BY created_at"

# Attribution et provenance
dolt sql -q "SELECT * FROM attribution_log WHERE entry_type = 'analysis_result'"
```

### 3. Déduplication Cross-Langue
```sql
-- Trouver les concepts partagés entre langues
SELECT 
    semantic_hash,
    COUNT(DISTINCT language) as language_count,
    GROUP_CONCAT(source_text SEPARATOR ' | ') as translations
FROM semantic_mappings
GROUP BY semantic_hash
HAVING language_count > 1;
```

### 4. Évolution du Modèle Sémantique
```bash
# Diff entre versions du modèle
dolt diff v0.1 v0.2 dhatu_definitions

# Voir l'impact d'un changement de modèle
dolt checkout v0.1
python analyze_corpus.py --output results_v0.1.json

dolt checkout v0.2
python analyze_corpus.py --output results_v0.2.json

diff results_v0.1.json results_v0.2.json
```

## 🎓 Références

### Documentation PaniniFS
- `Copilotage/knowledge/SEMANTIC_UNIVERSALS_DHATU.md` — Les 7 dhātu informationnels
- `docs/en/research/dhatu-inventory-v0-1.md` — Inventaire des primitives v0.1

### Documentation Dolt
- [Installation](https://docs.dolthub.com/introduction/installation)
- [Getting Started](https://docs.dolthub.com/introduction/getting-started)
- [Git for Data](https://www.dolthub.com/blog/2021-09-17-database-version-control/)
- [SQL Server](https://docs.dolthub.com/sql-reference/server)

## 🚧 Prochaines Étapes

### Court terme (POC validé)
- [ ] Implémenter l'analyzer Rust avec output JSON conforme
- [ ] Choisir l'option de communication (recommandation: subprocess → MySQL)
- [ ] Intégrer le bridge dans le workflow de CI/CD
- [ ] Tester sur un corpus réel de fichiers

### Moyen terme (production)
- [ ] Serveur Dolt SQL permanent avec backups
- [ ] API REST au-dessus de Dolt (optionnel)
- [ ] Tableaux de bord pour visualiser les distributions dhātu
- [ ] Synchronisation multi-repos (DoltHub remote)

### Long terme (recherche)
- [ ] Expérimentation de nouveaux dhātu via branches
- [ ] Analyse comparative cross-projets
- [ ] Détection automatique de patterns sémantiques
- [ ] Publication du dataset sémantique versionné

## 📝 Notes de Design

### Pourquoi Dolt?

1. **Versioning natif** : Tout l'historique des concepts est préservé
2. **Branches** : Expérimentation sans risque
3. **Diff** : Comparer les versions du modèle sémantique
4. **SQL standard** : Requêtes familières, pas de nouveau langage
5. **Git workflows** : Commit, merge, branch, log, diff
6. **MySQL compatible** : S'intègre avec tous les outils existants
7. **Provenance** : Traçabilité complète via commits

### Pourquoi séparer Rust et Dolt?

**Séparation des responsabilités :**
- **Rust** : Excellent pour analyse haute performance, parsing, extraction
- **Dolt** : Excellent pour stockage versionné, requêtes, collaboration

**Flexibilité :**
- Changer l'analyzer sans toucher au store
- Expérimenter avec plusieurs analyseurs en parallèle
- Requêter depuis n'importe quel langage/outil

**Scalabilité :**
- Distribuer l'analyse (plusieurs workers Rust)
- Centraliser le stockage (un seul Dolt server)
- Synchronisation via DoltHub (remotes Git-like)

## 🤝 Contribution

Ce POC est un point de départ pour discussion et itération.

**Feedback bienvenu sur :**
- Le schéma des tables
- Les options de communication Rust ↔ Dolt
- Les cas d'usage prioritaires
- L'ergonomie du workflow

## 📄 Licence

Ce sandbox fait partie du projet PaniniFS.
Voir `LICENSE` à la racine du projet.

---

**Auteur:** PaniniFS Core Team  
**Version:** 0.1.0  
**Date:** 2025-01-15  
**Status:** Proof of Concept

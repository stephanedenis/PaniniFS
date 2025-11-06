# 🔄 Refactoring : Atom → Chunk + Architecture Asynchrone

**Date :** 2025-11-06  
**Objectif :** Clarifier la terminologie et implémenter le versioning des concepts

---

## 🎯 Vision Architecturale

### Terminologie Actuelle (INCORRECTE)
```
File → [Atoms] → Storage
       ↓
    Concepts (???)
```

**Problèmes :**
- ❌ "Atom" suggère l'unité sémantique minimale (physique)
- ❌ Confusion entre déduplication et extraction sémantique
- ❌ Pas de versioning des concepts
- ❌ Traitement synchrone uniquement

### Terminologie Correcte (NOUVELLE)
```
File → [Chunks] → Storage (immédiat, content-addressed)
       ↓
    Metadata (dhatu, langue, etc.)
       ↓
    [Concepts v1] (asynchrone, extraction NLP)
       ↓
    [Concepts v2, v3...] (réinterprétation évolutive)
```

**Avantages :**
- ✅ **Chunk** = bloc de contenu déduplicable (clair et précis)
- ✅ **Concept** = entité sémantique avec versioning
- ✅ Découplage ingestion / extraction / évolution
- ✅ Possibilité de réinterpréter les chunks au fil du temps
- ✅ Architecture asynchrone scalable

---

## 📋 Plan de Migration

### Phase 1 : Renommage Atom → Chunk

#### 1.1 Fichiers Core à renommer
```bash
# panini-core/src/storage/
atom.rs → chunk.rs
    - struct Atom → struct Chunk
    - enum AtomType → enum ChunkType
    - AtomMetadata → ChunkMetadata
    - fn store_atom() → fn store_chunk()
    - fn get_atom() → fn get_chunk()

# panini-core/src/storage/
cache.rs
    - struct AtomCache → struct ChunkCache
    
decomposer.rs
    - fn decompose() -> Vec<Atom> → Vec<Chunk>
    - Atom::new() → Chunk::new()
```

#### 1.2 Fichiers API à modifier
```bash
# panini-api/src/
dedup_handlers.rs
    - /api/dedup/atoms → /api/dedup/chunks
    - top_atoms → top_chunks
    - unique_atoms → unique_chunks

routes.rs
    - .route("/atoms/:hash") → .route("/chunks/:hash")
```

#### 1.3 Base de données RocksDB
```rust
// Colonnes actuelles
CF_ATOMS → CF_CHUNKS
CF_ATOM_INDEX → CF_CHUNK_INDEX

// Nouvelles colonnes pour concepts
CF_CONCEPTS_V1  // Première extraction
CF_CONCEPTS_V2  // Réinterprétation
CF_CONCEPT_VERSIONS  // Métadonnées de version
```

#### 1.4 Web UI
```typescript
// web-ui/src/pages/GraphExplorer.tsx
interface AtomNode → interface ChunkNode
top_atoms → top_chunks
unique_atoms → unique_chunks
```

---

### Phase 2 : Implémentation Concepts avec Versioning

#### 2.1 Nouvelle Structure de Données
```rust
// crates/panini-core/src/concept.rs

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Concept {
    /// Identifiant unique du concept
    pub id: String,
    
    /// Version du concept (1, 2, 3...)
    pub version: u32,
    
    /// Type de concept
    pub concept_type: ConceptType,
    
    /// Nom canonique
    pub canonical_name: String,
    
    /// Variantes (aliases, traductions)
    pub variants: Vec<String>,
    
    /// Chunks sources
    pub source_chunks: Vec<String>,
    
    /// Métadonnées d'extraction
    pub extraction_metadata: ExtractionMetadata,
    
    /// Timestamp de création
    pub created_at: u64,
    
    /// Algorithme d'extraction utilisé
    pub extractor_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConceptType {
    /// Entité nommée (personne, lieu, organisation)
    NamedEntity { entity_type: EntityType },
    
    /// Terme technique/domaine
    TechnicalTerm { domain: String },
    
    /// Événement historique
    Event { date: Option<String> },
    
    /// Concept abstrait
    Abstract { category: String },
    
    /// Relation entre concepts
    Relation { 
        source: String, 
        target: String, 
        relation_type: String 
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExtractionMetadata {
    /// Confiance (0.0-1.0)
    pub confidence: f32,
    
    /// Langue source
    pub language: String,
    
    /// Profil Dhātu émotionnel
    pub dhatu_profile: Option<DhatuProfile>,
    
    /// Contexte d'extraction
    pub context: Vec<String>,
    
    /// Nombre d'occurrences
    pub occurrence_count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptVersion {
    pub concept_id: String,
    pub version: u32,
    pub parent_version: Option<u32>,
    pub changes: Vec<VersionChange>,
    pub reason: String,
    pub created_at: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VersionChange {
    NameChange { from: String, to: String },
    TypeRefinement { from: ConceptType, to: ConceptType },
    MergedWith { other_concept_id: String },
    SplitInto { new_concept_ids: Vec<String> },
    ConfidenceUpdate { from: f32, to: f32 },
}
```

#### 2.2 Pipeline Asynchrone
```rust
// crates/panini-core/src/pipeline/mod.rs

pub struct ConceptExtractionPipeline {
    chunk_store: ChunkStore,
    concept_store: ConceptStore,
    extractors: Vec<Box<dyn ConceptExtractor>>,
}

#[async_trait]
pub trait ConceptExtractor: Send + Sync {
    /// Version de l'extracteur
    fn version(&self) -> &str;
    
    /// Extraire concepts d'un chunk
    async fn extract(&self, chunk: &Chunk) -> Result<Vec<Concept>>;
    
    /// Types de concepts supportés
    fn supported_types(&self) -> Vec<ConceptType>;
}

impl ConceptExtractionPipeline {
    /// Traiter un batch de chunks
    pub async fn process_batch(
        &self, 
        chunk_hashes: Vec<String>
    ) -> Result<Vec<Concept>> {
        let mut concepts = Vec::new();
        
        for hash in chunk_hashes {
            let chunk = self.chunk_store.get(&hash).await?;
            
            for extractor in &self.extractors {
                let extracted = extractor.extract(&chunk).await?;
                concepts.extend(extracted);
            }
        }
        
        // Déduplication et fusion
        self.merge_similar_concepts(concepts)
    }
    
    /// Réinterpréter avec nouvelle version d'extracteur
    pub async fn reinterpret_all(&self, version: u32) -> Result<()> {
        let all_chunks = self.chunk_store.list_all().await?;
        
        for chunk_hash in all_chunks {
            let chunk = self.chunk_store.get(&chunk_hash).await?;
            let new_concepts = self.extract_with_version(&chunk, version).await?;
            
            self.store_concept_version(new_concepts, version).await?;
        }
        
        Ok(())
    }
}
```

#### 2.3 Extracteurs de Concepts
```rust
// crates/panini-extractors/src/

// Extracteur NER (Named Entity Recognition)
pub struct NERExtractor {
    model: Box<dyn NERModel>,
}

// Extracteur Dhātu-Sémantique
pub struct DhatuSemanticExtractor {
    dhatu_classifier: DhatuClassifier,
}

// Extracteur de Relations
pub struct RelationExtractor {
    dependency_parser: DependencyParser,
}

// Extracteur Wikipedia-spécifique
pub struct WikipediaExtractor {
    infobox_parser: InfoboxParser,
    category_parser: CategoryParser,
}
```

#### 2.4 API Endpoints pour Concepts
```rust
// GET /api/concepts?version=2
// Liste tous les concepts d'une version

// GET /api/concepts/:id
// Récupère toutes les versions d'un concept

// GET /api/concepts/:id/version/:v
// Récupère une version spécifique

// GET /api/concepts/:id/history
// Historique d'évolution du concept

// GET /api/concepts/search?q=Einstein&version=2
// Recherche dans une version spécifique

// POST /api/concepts/extract
// Déclencher extraction asynchrone

// GET /api/concepts/extraction/status/:job_id
// Statut d'extraction
```

---

### Phase 3 : Migration du Storage Existant

#### 3.1 Script de Migration
```python
#!/usr/bin/env python3
# tools/migrate_atoms_to_chunks.py

import rocksdb
import json
from pathlib import Path

def migrate_storage(storage_path: Path):
    """Migrer atoms → chunks dans RocksDB"""
    
    db = rocksdb.DB(str(storage_path / "index"), rocksdb.Options())
    
    # Lire tous les atoms
    atoms = []
    it = db.iteritems()
    it.seek_to_first()
    for key, value in it:
        if key.startswith(b'atom:'):
            atoms.append((key, value))
    
    # Réécrire en tant que chunks
    wb = rocksdb.WriteBatch()
    for old_key, value in atoms:
        new_key = old_key.replace(b'atom:', b'chunk:')
        wb.put(new_key, value)
        wb.delete(old_key)
    
    db.write(wb)
    print(f"✅ Migré {len(atoms)} atoms → chunks")

def verify_chunks(storage_path: Path):
    """Vérifier que tous les fichiers existent"""
    chunks = list((storage_path).rglob('*'))
    chunks = [c for c in chunks if c.is_file() and 'dhatu' not in str(c)]
    
    print(f"✅ Trouvé {len(chunks)} chunk files")
    
    # Vérifier qu'on peut lire chaque chunk
    for chunk_path in chunks[:10]:  # Test 10 premiers
        content = chunk_path.read_bytes()
        print(f"  ✓ {chunk_path.name}: {len(content)} bytes")

if __name__ == '__main__':
    storage = Path('/home/stephane/panini-wikipedia-full')
    migrate_storage(storage)
    verify_chunks(storage)
```

#### 3.2 Vérifications Post-Migration
```bash
# Vérifier la structure
ls -la /home/stephane/panini-wikipedia-full/

# Compter les chunks
find /home/stephane/panini-wikipedia-full -type f \
  ! -path '*/dhatu/*' ! -path '*/checkpoints/*' | wc -l

# Tester l'API
curl http://localhost:3000/api/chunks/stats
curl http://localhost:3000/api/concepts?version=1
```

---

### Phase 4 : Extraction Initiale des Concepts

#### 4.1 Pipeline Wikipedia
```python
# tools/extract_wikipedia_concepts.py

import asyncio
from pathlib import Path
from panini_extractors import (
    WikipediaExtractor,
    NERExtractor,
    DhatuSemanticExtractor
)

async def extract_concepts_from_wikipedia(storage_path: Path):
    """
    Extraire concepts v1 depuis les chunks Wikipedia
    """
    extractors = [
        WikipediaExtractor(),
        NERExtractor(model='de_core_news_lg'),
        DhatuSemanticExtractor()
    ]
    
    pipeline = ConceptExtractionPipeline(
        chunk_store=ChunkStore(storage_path),
        concept_store=ConceptStore(storage_path),
        extractors=extractors
    )
    
    # Traiter par batches de 100 chunks
    all_chunks = await pipeline.chunk_store.list_all()
    
    for i in range(0, len(all_chunks), 100):
        batch = all_chunks[i:i+100]
        concepts = await pipeline.process_batch(batch)
        
        print(f"Batch {i//100}: {len(concepts)} concepts extraits")
    
    print(f"✅ Extraction complète : {len(concepts)} concepts v1")
```

#### 4.2 Statistiques Attendues
```
Wikipedia Allemand (1,470 articles) :

Chunks :
  - Total : 1,458 chunks
  - Taille : 55 MB
  - Déduplication : 0.81%

Concepts v1 (estimé) :
  - Entités nommées : ~3,000-5,000
    * Personnes : ~1,500
    * Lieux : ~800
    * Organisations : ~500
  - Termes techniques : ~1,000-2,000
  - Événements : ~200-500
  - Relations : ~2,000-4,000

Total estimé : 6,200-11,500 concepts
```

---

## 📊 Calendrier de Migration

### Semaine 1 : Refactoring Code
- **Jour 1-2** : Renommer Atom → Chunk dans panini-core
- **Jour 3** : Adapter panini-api et endpoints
- **Jour 4** : Mettre à jour Web UI
- **Jour 5** : Tests et validation

### Semaine 2 : Concepts Infrastructure
- **Jour 1-2** : Implémenter structures de données Concept
- **Jour 3** : Pipeline asynchrone
- **Jour 4-5** : Extracteurs de base (NER, Wikipedia)

### Semaine 3 : Migration & Extraction
- **Jour 1** : Migrer storage existant
- **Jour 2-3** : Extraction concepts v1 depuis Wikipedia
- **Jour 4-5** : Tests, validation, documentation

### Semaine 4 : Optimisation & Web UI
- **Jour 1-2** : Interface de navigation concepts
- **Jour 3** : Visualisation évolution concepts
- **Jour 4-5** : Performance, cache, optimisations

---

## ✅ Checklist de Validation

### Code
- [ ] Tous les fichiers renommés Atom → Chunk
- [ ] Compilation sans warnings
- [ ] Tests unitaires passent
- [ ] Documentation à jour

### Storage
- [ ] Migration RocksDB complète
- [ ] 1,458 chunks accessibles
- [ ] Métadonnées Dhātu préservées
- [ ] Checkpoints fonctionnels

### API
- [ ] Endpoints /chunks/* fonctionnels
- [ ] Endpoints /concepts/* implémentés
- [ ] Extraction asynchrone opérationnelle
- [ ] Versioning concepts testé

### Web UI
- [ ] Page Chunks mise à jour
- [ ] Page Concepts créée
- [ ] Timeline concepts fonctionnelle
- [ ] Export données OK

### Extraction
- [ ] NER extractor fonctionnel
- [ ] Wikipedia extractor OK
- [ ] Dhātu-Semantic extractor testé
- [ ] Pipeline asynchrone stable
- [ ] >5,000 concepts extraits

---

## 🚀 Commandes de Démarrage

### Après migration complète

```bash
# 1. Stopper ancienne API
pkill -f panini-api

# 2. Migration storage
cd /home/stephane/GitHub/Panini-FS
python3 tools/migrate_atoms_to_chunks.py

# 3. Relancer API (nouvelle version)
PANINI_STORAGE=/home/stephane/panini-wikipedia-full \
  cargo run --release --bin panini-api &

# 4. Lancer extraction concepts v1
python3 tools/extract_wikipedia_concepts.py \
  --storage /home/stephane/panini-wikipedia-full \
  --version 1 \
  --workers 8

# 5. Vérifier résultats
curl http://localhost:3000/api/chunks/stats | jq
curl http://localhost:3000/api/concepts?version=1 | jq '.total'

# 6. Lancer Web UI
cd web-ui && npm run dev
```

---

## 📚 Bénéfices Finaux

### Clarté Conceptuelle
- ✅ Terminologie cohérente et précise
- ✅ Séparation claire storage / sémantique
- ✅ Architecture évolutive et maintenable

### Performance
- ✅ Extraction asynchrone non-bloquante
- ✅ Réinterprétation sans réingestion
- ✅ Versioning permet A/B testing d'extracteurs

### Scientifique
- ✅ Concepts versionnés = reproductibilité
- ✅ Évolution traçable dans le temps
- ✅ Comparaison inter-langues facilitée
- ✅ Datasets publiables avec métadonnées complètes

### Publications
- Paper 1 : "Chunk-based Deduplication for Large-Scale Wikipedia"
- Paper 2 : "Versioned Concept Extraction with Dhātu Profiles"
- Paper 3 : "Cross-lingual Concept Evolution in Knowledge Graphs"

---

**Prochaine étape recommandée :** Commencer Phase 1.1 (Renommage Atom → Chunk dans panini-core)

Voulez-vous que je commence l'implémentation ?

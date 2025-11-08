//! RocksDB Persistence for Extracted Concepts

use panini_core::concept::Concept;
use rocksdb::{DB, Options, IteratorMode};
use serde::{Serialize, Deserialize};
use std::path::Path;
use std::sync::Arc;

pub struct ConceptStore {
    db: Arc<DB>,
}

impl ConceptStore {
    /// Open or create concept store
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self, String> {
        let mut opts = Options::default();
        opts.create_if_missing(true);
        opts.create_missing_column_families(true);
        
        let db = DB::open(&opts, path)
            .map_err(|e| format!("Failed to open RocksDB: {}", e))?;
        
        Ok(Self { db: Arc::new(db) })
    }
    
    /// Save a concept
    pub fn save_concept(&self, concept: &Concept) -> Result<(), String> {
        let key = format!("concept:{}", concept.id);
        let value = serde_json::to_vec(concept)
            .map_err(|e| format!("Serialization error: {}", e))?;
        
        self.db
            .put(key.as_bytes(), value)
            .map_err(|e| format!("RocksDB put error: {}", e))
    }
    
    /// Save multiple concepts in batch
    pub fn save_batch(&self, concepts: &[Concept]) -> Result<usize, String> {
        let mut batch = rocksdb::WriteBatch::default();
        
        for concept in concepts {
            let key = format!("concept:{}", concept.id);
            let value = serde_json::to_vec(concept)
                .map_err(|e| format!("Serialization error: {}", e))?;
            batch.put(key.as_bytes(), value);
        }
        
        self.db
            .write(batch)
            .map_err(|e| format!("RocksDB batch write error: {}", e))?;
        
        Ok(concepts.len())
    }
    
    /// Get concept by ID
    pub fn get_concept(&self, id: &str) -> Result<Option<Concept>, String> {
        let key = format!("concept:{}", id);
        
        match self.db.get(key.as_bytes()) {
            Ok(Some(value)) => {
                let concept: Concept = serde_json::from_slice(&value)
                    .map_err(|e| format!("Deserialization error: {}", e))?;
                Ok(Some(concept))
            }
            Ok(None) => Ok(None),
            Err(e) => Err(format!("RocksDB get error: {}", e)),
        }
    }
    
    /// List all concepts
    pub fn list_all_concepts(&self) -> Result<Vec<Concept>, String> {
        let mut concepts = Vec::new();
        let prefix = b"concept:";
        
        let iter = self.db.iterator(IteratorMode::From(prefix, rocksdb::Direction::Forward));
        
        for item in iter {
            match item {
                Ok((key, value)) => {
                    // Check if key starts with prefix
                    if key.starts_with(prefix) {
                        match serde_json::from_slice::<Concept>(&value) {
                            Ok(concept) => concepts.push(concept),
                            Err(e) => eprintln!("Failed to deserialize concept: {}", e),
                        }
                    } else {
                        break; // Past our prefix
                    }
                }
                Err(e) => {
                    eprintln!("Iterator error: {}", e);
                    break;
                }
            }
        }
        
        Ok(concepts)
    }
    
    /// Count concepts
    pub fn count_concepts(&self) -> Result<usize, String> {
        let prefix = b"concept:";
        let iter = self.db.iterator(IteratorMode::From(prefix, rocksdb::Direction::Forward));
        
        let mut count = 0;
        for item in iter {
            match item {
                Ok((key, _)) => {
                    if key.starts_with(prefix) {
                        count += 1;
                    } else {
                        break;
                    }
                }
                Err(_) => break,
            }
        }
        
        Ok(count)
    }
    
    /// Get stats
    pub fn get_stats(&self) -> Result<ConceptStoreStats, String> {
        let concepts = self.list_all_concepts()?;
        
        let total_concepts = concepts.len();
        let mut by_type = std::collections::HashMap::new();
        let mut total_confidence = 0.0;
        let mut total_versions = 0;
        
        for concept in concepts {
            *by_type.entry(format!("{:?}", concept.concept_type)).or_insert(0) += 1;
            total_confidence += concept.confidence as f64;
            total_versions += concept.versions.len();
        }
        
        let avg_confidence = if total_concepts > 0 {
            total_confidence / total_concepts as f64
        } else {
            0.0
        };
        
        Ok(ConceptStoreStats {
            total_concepts,
            by_type,
            avg_confidence,
            total_versions,
        })
    }
    
    /// Clear all concepts (for testing)
    pub fn clear_all(&self) -> Result<usize, String> {
        let prefix = b"concept:";
        let keys_to_delete: Vec<Vec<u8>> = self
            .db
            .iterator(IteratorMode::From(prefix, rocksdb::Direction::Forward))
            .filter_map(|item| item.ok())
            .take_while(|(key, _)| key.starts_with(prefix))
            .map(|(key, _)| key.to_vec())
            .collect();
        
        let count = keys_to_delete.len();
        
        let mut batch = rocksdb::WriteBatch::default();
        for key in keys_to_delete {
            batch.delete(&key);
        }
        
        self.db
            .write(batch)
            .map_err(|e| format!("RocksDB batch delete error: {}", e))?;
        
        Ok(count)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptStoreStats {
    pub total_concepts: usize,
    pub by_type: std::collections::HashMap<String, usize>,
    pub avg_confidence: f64,
    pub total_versions: usize,
}

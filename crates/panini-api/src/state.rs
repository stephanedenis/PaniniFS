//! Application state shared across handlers

use crate::concept_handlers::ConceptExtractionState;
use crate::concept_persistence::ConceptStore;
use crate::dhatu_handlers::DhatuState;
use panini_core::storage::{
    backends::localfs::LocalFsBackend, cas::ContentAddressedStorage, immutable::TemporalIndex,
};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock as TokioRwLock;
use std::sync::RwLock as StdRwLock;

/// Shared application state
#[derive(Clone)]
pub struct AppState {
    /// Temporal index for time-travel queries
    pub temporal_index: Arc<StdRwLock<TemporalIndex>>,

    /// Content-addressed storage
    pub cas: Arc<ContentAddressedStorage<LocalFsBackend>>,

    /// Dhātu emotional classification system
    pub dhatu: Arc<DhatuState>,

    /// Concept extraction pipeline
    pub extraction_state: Arc<ConceptExtractionState>,
    
    /// Persistent concept store (RocksDB)
    pub concept_store: Arc<ConceptStore>,
}

impl AppState {
    /// Create new application state
    pub fn new(
        temporal_index: Arc<StdRwLock<TemporalIndex>>,
        cas: Arc<ContentAddressedStorage<LocalFsBackend>>,
        storage_path: PathBuf,
    ) -> Self {
        let concept_store_path = storage_path.join("concepts");
        let concept_store = ConceptStore::open(&concept_store_path)
            .expect("Failed to open concept store");
        
        println!("📦 Concept store opened at: {:?}", concept_store_path);
        
        // Try to load existing concepts count
        match concept_store.count_concepts() {
            Ok(count) => println!("📊 Found {} existing concepts in store", count),
            Err(e) => eprintln!("⚠️  Failed to count concepts: {}", e),
        }
        
        Self {
            temporal_index,
            cas,
            dhatu: DhatuState::new(storage_path),
            extraction_state: Arc::new(ConceptExtractionState::new()),
            concept_store: Arc::new(concept_store),
        }
    }
}

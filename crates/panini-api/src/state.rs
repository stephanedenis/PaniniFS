//! Application state shared across handlers

use crate::concept_handlers::ConceptExtractionState;
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
}

impl AppState {
    /// Create new application state
    pub fn new(
        temporal_index: Arc<StdRwLock<TemporalIndex>>,
        cas: Arc<ContentAddressedStorage<LocalFsBackend>>,
        storage_path: PathBuf,
    ) -> Self {
        Self {
            temporal_index,
            cas,
            dhatu: DhatuState::new(storage_path),
            extraction_state: Arc::new(ConceptExtractionState::new()),
        }
    }
}

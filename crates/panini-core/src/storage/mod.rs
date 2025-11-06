//! Storage module - Content-addressed storage with atomic decomposition
//!
//! This module provides:
//! - Atomic decomposition of binary files (PNG, JPEG, MP4, etc.)
//! - Content-addressed storage (CAS) with SHA-256 hashing
//! - Automatic deduplication
//! - Multiple storage backends (LocalFS, S3-compatible)
//! - Lossless reconstruction

pub mod chunk;
pub mod backends;
pub mod cache;
pub mod cas;
pub mod decomposer;
pub mod reconstructor;

// Re-export from existing modules
pub use backend::{StorageBackend as LegacyStorageBackend, UploadResult as LegacyUploadResult};
pub use dedup::DedupManager;

// Re-export main types
pub use chunk::{Chunk, ChunkMetadata, ChunkType};
pub use backends::{BackendStats, LocalFsBackend, StorageBackend, UploadResult};
pub use cache::{ChunkCache, CacheConfig, CacheStats, CachedChunk};
pub use cas::{ContentAddressedStorage, GcStats, StorageConfig, StorageStats};
pub use decomposer::{Decomposer, FileFormat};
pub use reconstructor::Reconstructor;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Reference to a content atom in storage
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ContentRef {
    /// SHA-256 hash of the atom
    pub chunk_hash: String,

    /// Type of the atom
    pub chunk_type: ChunkType,

    /// Offset in the reconstructed file (bytes)
    pub offset: u64,

    /// Size of the atom (bytes)
    pub size: u64,

    /// Optional metadata (codec, resolution, etc.)
    #[serde(default)]
    pub metadata: HashMap<String, String>,
}

impl ContentRef {
    pub fn new(chunk_hash: String, chunk_type: ChunkType, offset: u64, size: u64) -> Self {
        Self {
            chunk_hash,
            chunk_type,
            offset,
            size,
            metadata: HashMap::new(),
        }
    }

    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata.insert(key, value);
        self
    }
}

// Keep existing modules for backwards compatibility
mod backend;
mod dedup;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_content_ref_creation() {
        let cref = ContentRef::new("abc123".to_string(), ChunkType::Container, 0, 1024);

        assert_eq!(cref.chunk_hash, "abc123");
        assert_eq!(cref.offset, 0);
        assert_eq!(cref.size, 1024);
    }
}
pub mod immutable;

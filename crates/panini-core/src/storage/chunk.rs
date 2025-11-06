//! Atomic content representation for decomposed binary formats

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;

/// Type of content chunk
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ChunkType {
    /// File container metadata (MP4 ftyp, moov, PNG header)
    Container,

    /// Video stream (H.264, VP8, etc.)
    VideoStream,

    /// Audio stream (AAC, MP3, etc.)
    AudioStream,

    /// Video I-Frame (keyframe)
    IFrame,

    /// Video P-Frame (predictive frame)
    PFrame,

    /// Video B-Frame (bidirectional frame)
    BFrame,

    /// Subtitle track (SRT, VTT, etc.)
    Subtitle,

    /// Image data (PNG IDAT, JPEG scan, etc.)
    ImageData,

    /// Metadata (EXIF, ID3, etc.)
    Metadata,

    /// Audio chunk (AAC frame, MP3 frame)
    AudioChunk,

    /// Compressed data (ZIP entry, etc.)
    Compressed,

    /// Raw binary data
    Raw,
}

impl ChunkType {
    /// Check if chunk type typically has high deduplication potential
    pub fn is_dedupable(&self) -> bool {
        matches!(
            self,
            ChunkType::IFrame
                | ChunkType::AudioChunk
                | ChunkType::Subtitle
                | ChunkType::Metadata
                | ChunkType::Container
        )
    }

    /// Get typical size range for this chunk type (min, max in bytes)
    pub fn size_range(&self) -> (u64, u64) {
        match self {
            ChunkType::Container => (1024, 10 * 1024),         // 1-10 KB
            ChunkType::Metadata => (512, 100 * 1024),          // 512B-100KB
            ChunkType::IFrame => (50 * 1024, 5 * 1024 * 1024), // 50KB-5MB
            ChunkType::PFrame | ChunkType::BFrame => (10 * 1024, 500 * 1024), // 10-500KB
            ChunkType::AudioChunk => (1024, 50 * 1024),        // 1-50KB
            ChunkType::Subtitle => (100, 10 * 1024),           // 100B-10KB
            ChunkType::ImageData => (1024, 10 * 1024 * 1024),  // 1KB-10MB
            ChunkType::VideoStream | ChunkType::AudioStream => (100 * 1024, 1024 * 1024 * 1024), // 100KB-1GB
            ChunkType::Compressed => (1024, 100 * 1024 * 1024), // 1KB-100MB
            ChunkType::Raw => (0, u64::MAX),
        }
    }
}

impl std::fmt::Display for ChunkType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ChunkType::Container => write!(f, "Container"),
            ChunkType::VideoStream => write!(f, "VideoStream"),
            ChunkType::AudioStream => write!(f, "AudioStream"),
            ChunkType::IFrame => write!(f, "VideoStream/IFrame"),
            ChunkType::PFrame => write!(f, "VideoStream/PFrame"),
            ChunkType::BFrame => write!(f, "VideoStream/BFrame"),
            ChunkType::Subtitle => write!(f, "Subtitle"),
            ChunkType::ImageData => write!(f, "ImageData"),
            ChunkType::Metadata => write!(f, "Metadata"),
            ChunkType::AudioChunk => write!(f, "AudioChunk"),
            ChunkType::Compressed => write!(f, "Compressed"),
            ChunkType::Raw => write!(f, "Raw"),
        }
    }
}

/// Content chunk - smallest unit of storage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Chunk {
    /// SHA-256 content hash
    pub hash: String,

    /// Chunk type
    pub chunk_type: ChunkType,

    /// Size in bytes
    pub size: u64,

    /// Optional parent chunk hash (for hierarchical decomposition)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent: Option<String>,

    /// Optional child chunk hashes
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub children: Vec<String>,

    /// Format-specific metadata
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub metadata: HashMap<String, String>,

    /// Original offset in source file
    #[serde(default)]
    pub source_offset: u64,

    /// Reference count (how many concepts use this chunk)
    #[serde(default)]
    pub ref_count: u32,
}

impl Chunk {
    /// Create new chunk from data
    pub fn new(data: &[u8], chunk_type: ChunkType) -> Self {
        let hash = Self::compute_hash(data);
        Self {
            hash,
            chunk_type,
            size: data.len() as u64,
            parent: None,
            children: Vec::new(),
            metadata: HashMap::new(),
            source_offset: 0,
            ref_count: 0,
        }
    }

    /// Create chunk with metadata
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    /// Set parent chunk
    pub fn with_parent(mut self, parent_hash: String) -> Self {
        self.parent = Some(parent_hash);
        self
    }

    /// Add child chunk
    pub fn add_child(&mut self, child_hash: String) {
        if !self.children.contains(&child_hash) {
            self.children.push(child_hash);
        }
    }

    /// Compute SHA-256 hash of data
    pub fn compute_hash(data: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data);
        format!("{:x}", hasher.finalize())
    }

    /// Increment reference count
    pub fn increment_refs(&mut self) {
        self.ref_count = self.ref_count.saturating_add(1);
    }

    /// Decrement reference count
    pub fn decrement_refs(&mut self) {
        self.ref_count = self.ref_count.saturating_sub(1);
    }

    /// Check if chunk is orphaned (no references)
    pub fn is_orphaned(&self) -> bool {
        self.ref_count == 0
    }
}

/// Lightweight chunk metadata (for indexing)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChunkMetadata {
    pub hash: String,
    pub chunk_type: ChunkType,
    pub size: u64,
    pub ref_count: u32,
    #[serde(default)]
    pub created_at: u64,
}

impl From<&Chunk> for ChunkMetadata {
    fn from(chunk: &Chunk) -> Self {
        Self {
            hash: chunk.hash.clone(),
            chunk_type: chunk.chunk_type,
            size: chunk.size,
            ref_count: chunk.ref_count,
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_atom_creation() {
        let data = b"test data";
        let chunk = Chunk::new(data, ChunkType::Container);

        assert_eq!(chunk.size, 9);
        assert_eq!(chunk.chunk_type, ChunkType::Container);
        assert!(!chunk.hash.is_empty());
        assert_eq!(chunk.ref_count, 0);
    }

    #[test]
    fn test_atom_hash_consistency() {
        let data = b"consistent data";
        let atom1 = Chunk::new(data, ChunkType::Container);
        let atom2 = Chunk::new(data, ChunkType::Raw);

        assert_eq!(atom1.hash, atom2.hash);
    }

    #[test]
    fn test_atom_with_metadata() {
        let chunk = Chunk::new(b"data", ChunkType::VideoStream)
            .with_metadata("codec", "h264")
            .with_metadata("fps", "30");

        assert_eq!(chunk.metadata.get("codec"), Some(&"h264".to_string()));
        assert_eq!(chunk.metadata.get("fps"), Some(&"30".to_string()));
    }

    #[test]
    fn test_atom_ref_counting() {
        let mut chunk = Chunk::new(b"data", ChunkType::Container);

        assert_eq!(chunk.ref_count, 0);
        assert!(chunk.is_orphaned());

        chunk.increment_refs();
        assert_eq!(chunk.ref_count, 1);
        assert!(!chunk.is_orphaned());

        chunk.decrement_refs();
        assert_eq!(chunk.ref_count, 0);
        assert!(chunk.is_orphaned());
    }

    #[test]
    fn test_atom_type_dedupable() {
        assert!(ChunkType::IFrame.is_dedupable());
        assert!(ChunkType::AudioChunk.is_dedupable());
        assert!(ChunkType::Metadata.is_dedupable());
        assert!(!ChunkType::PFrame.is_dedupable());
        assert!(!ChunkType::Raw.is_dedupable());
    }

    #[test]
    fn test_atom_parent_child() {
        let mut parent = Chunk::new(b"parent", ChunkType::Container);
        let child1 = Chunk::new(b"child1", ChunkType::IFrame);
        let child2 = Chunk::new(b"child2", ChunkType::PFrame);

        parent.add_child(child1.hash.clone());
        parent.add_child(child2.hash.clone());

        assert_eq!(parent.children.len(), 2);
        assert!(parent.children.contains(&child1.hash));

        // Test duplicate prevention
        parent.add_child(child1.hash.clone());
        assert_eq!(parent.children.len(), 2);
    }
}

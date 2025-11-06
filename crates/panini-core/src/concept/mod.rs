//! Concept Module - Semantic Entity Extraction
//!
//! This module provides structures and methods for extracting semantic concepts
//! from chunks. Concepts represent semantic entities like named entities,
//! technical terms, events, and abstract ideas.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Type of semantic concept
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum ConceptType {
    /// Named entity (person, organization, location)
    NamedEntity,
    /// Technical or domain-specific term
    TechnicalTerm,
    /// Event or happening
    Event,
    /// Abstract concept or idea
    Abstract,
    /// Relationship between entities
    Relation,
    /// Wikipedia category
    Category,
    /// Temporal reference (date, time period)
    Temporal,
}

/// Subtype for named entities
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum EntitySubtype {
    Person,
    Organization,
    Location,
    Other,
}

/// Version of a concept with temporal information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptVersion {
    /// Unique version ID
    pub version_id: String,
    /// Text representation at this version
    pub text: String,
    /// Language code (ISO 639-1)
    pub language: String,
    /// Source chunk hash
    pub source_chunk: String,
    /// Timestamp when this version was created
    pub timestamp: u64,
    /// Confidence score (0.0 to 1.0)
    pub confidence: f64,
    /// Context window around the concept
    pub context: Option<String>,
}

/// Semantic concept extracted from chunks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Concept {
    /// Unique concept identifier (UUID)
    pub id: String,
    /// Canonical name (normalized form)
    pub canonical_name: String,
    /// Type of concept
    pub concept_type: ConceptType,
    /// Entity subtype (if applicable)
    pub entity_subtype: Option<EntitySubtype>,
    /// All known versions/variations
    pub versions: Vec<ConceptVersion>,
    /// Source chunk hashes where this concept appears
    pub source_chunks: Vec<String>,
    /// Related concept IDs
    pub related_concepts: Vec<String>,
    /// Metadata extracted from Wikipedia (categories, infobox, etc.)
    pub metadata: HashMap<String, String>,
    /// Dhātu emotional profile mapping
    pub dhatu_profile: Option<String>,
    /// Overall confidence score
    pub confidence: f64,
    /// Creation timestamp
    pub created_at: u64,
    /// Last update timestamp
    pub updated_at: u64,
}

impl Concept {
    /// Create a new concept
    pub fn new(canonical_name: String, concept_type: ConceptType) -> Self {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            id: uuid::Uuid::new_v4().to_string(),
            canonical_name,
            concept_type,
            entity_subtype: None,
            versions: Vec::new(),
            source_chunks: Vec::new(),
            related_concepts: Vec::new(),
            metadata: HashMap::new(),
            dhatu_profile: None,
            confidence: 0.0,
            created_at: now,
            updated_at: now,
        }
    }

    /// Add a version to this concept
    pub fn add_version(&mut self, version: ConceptVersion) {
        // Update confidence based on version confidence
        if !self.versions.is_empty() {
            let total_confidence: f64 = self.versions.iter().map(|v| v.confidence).sum();
            self.confidence = (total_confidence + version.confidence) / (self.versions.len() as f64 + 1.0);
        } else {
            self.confidence = version.confidence;
        }

        // Add source chunk if not already present
        if !self.source_chunks.contains(&version.source_chunk) {
            self.source_chunks.push(version.source_chunk.clone());
        }

        self.versions.push(version);
        self.updated_at = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
    }

    /// Get the most recent version
    pub fn latest_version(&self) -> Option<&ConceptVersion> {
        self.versions.iter().max_by_key(|v| v.timestamp)
    }

    /// Get all versions in a specific language
    pub fn versions_by_language(&self, language: &str) -> Vec<&ConceptVersion> {
        self.versions.iter()
            .filter(|v| v.language == language)
            .collect()
    }
}

/// Statistics about extracted concepts
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptStats {
    pub total_concepts: usize,
    pub by_type: HashMap<ConceptType, usize>,
    pub avg_versions_per_concept: f64,
    pub avg_confidence: f64,
    pub total_versions: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_concept_creation() {
        let concept = Concept::new("Rust Programming".to_string(), ConceptType::TechnicalTerm);
        assert_eq!(concept.canonical_name, "Rust Programming");
        assert_eq!(concept.concept_type, ConceptType::TechnicalTerm);
        assert_eq!(concept.versions.len(), 0);
    }

    #[test]
    fn test_add_version() {
        let mut concept = Concept::new("Paris".to_string(), ConceptType::NamedEntity);
        
        let version = ConceptVersion {
            version_id: "v1".to_string(),
            text: "Paris".to_string(),
            language: "en".to_string(),
            source_chunk: "chunk123".to_string(),
            timestamp: 1000,
            confidence: 0.95,
            context: Some("The capital of France".to_string()),
        };

        concept.add_version(version);
        assert_eq!(concept.versions.len(), 1);
        assert_eq!(concept.source_chunks.len(), 1);
        assert!(concept.confidence > 0.0);
    }
}

pub mod extractor;
pub use extractor::{ConceptExtractor, NERExtractor, WikipediaExtractor};

pub mod pipeline;
pub use pipeline::{ExtractionPipeline, ExtractionJob, ExtractionStatus, ProgressUpdate};

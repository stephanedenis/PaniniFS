//! Extraction Pipeline - Concept extraction with progress tracking

use super::{Concept, ConceptExtractor, ConceptStats};
use crate::storage::ChunkMetadata;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum ExtractionStatus {
    Pending,
    Running { processed: usize, total: usize },
    Completed { concepts_extracted: usize },
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ExtractionJob {
    pub job_id: String,
    pub status: ExtractionStatus,
    pub started_at: Option<u64>,
    pub completed_at: Option<u64>,
}

pub enum ProgressUpdate {
    Started,
    Progress { processed: usize, total: usize },
    Completed { total_concepts: usize },
}

pub struct ExtractionPipeline {
    extractors: Vec<Box<dyn ConceptExtractor>>,
    jobs: Arc<Mutex<HashMap<String, ExtractionJob>>>,
    concepts: Arc<Mutex<Vec<Concept>>>,
}

impl ExtractionPipeline {
    pub fn new() -> Self {
        Self {
            extractors: Vec::new(),
            jobs: Arc::new(Mutex::new(HashMap::new())),
            concepts: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn add_extractor(&mut self, extractor: Box<dyn ConceptExtractor>) {
        self.extractors.push(extractor);
    }

    pub fn extract_from_chunks(
        &self,
        chunks: Vec<(ChunkMetadata, String)>,
        job_id: String,
    ) -> Vec<Concept> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // Create job
        {
            let mut jobs = self.jobs.lock().unwrap();
            let mut job = ExtractionJob {
                job_id: job_id.clone(),
                status: ExtractionStatus::Running { processed: 0, total: chunks.len() },
                started_at: Some(now),
                completed_at: None,
            };
            jobs.insert(job_id.clone(), job);
        }

        let mut all_concepts = Vec::new();
        let total = chunks.len();

        for (i, (metadata, content)) in chunks.iter().enumerate() {
            for extractor in &self.extractors {
                let extracted = extractor.extract(&content, &metadata.hash);
                all_concepts.extend(extracted);
            }

            // Update progress
            let processed = i + 1;
            {
                let mut jobs = self.jobs.lock().unwrap();
                if let Some(job) = jobs.get_mut(&job_id) {
                    job.status = ExtractionStatus::Running { processed, total };
                }
            }
        }

        // Merge duplicates
        let merged = Self::merge_concepts(all_concepts);
        let concept_count = merged.len();

        // Store concepts
        {
            let mut concepts = self.concepts.lock().unwrap();
            concepts.extend(merged.clone());
        }

        // Mark completed
        let completed_at = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        {
            let mut jobs = self.jobs.lock().unwrap();
            if let Some(job) = jobs.get_mut(&job_id) {
                job.status = ExtractionStatus::Completed { concepts_extracted: concept_count };
                job.completed_at = Some(completed_at);
            }
        }

        merged
    }

    fn merge_concepts(concepts: Vec<Concept>) -> Vec<Concept> {
        let mut merged: HashMap<String, Concept> = HashMap::new();

        for concept in concepts {
            let key = concept.canonical_name.clone();
            
            if let Some(existing) = merged.get_mut(&key) {
                for version in concept.versions {
                    existing.add_version(version);
                }
                for (k, v) in concept.metadata {
                    existing.metadata.entry(k).or_insert(v);
                }
                for related in concept.related_concepts {
                    if !existing.related_concepts.contains(&related) {
                        existing.related_concepts.push(related);
                    }
                }
            } else {
                merged.insert(key, concept);
            }
        }

        merged.into_values().collect()
    }

    pub fn get_job_status(&self, job_id: &str) -> Option<ExtractionJob> {
        let jobs = self.jobs.lock().unwrap();
        jobs.get(job_id).cloned()
    }

    pub fn get_concepts(&self) -> Vec<Concept> {
        let concepts = self.concepts.lock().unwrap();
        concepts.clone()
    }

    pub fn get_stats(&self) -> ConceptStats {
        let concepts = self.concepts.lock().unwrap();
        
        let mut by_type = HashMap::new();
        let mut total_versions = 0;
        let mut total_confidence = 0.0;

        for concept in concepts.iter() {
            *by_type.entry(concept.concept_type.clone()).or_insert(0) += 1;
            total_versions += concept.versions.len();
            total_confidence += concept.confidence;
        }

        let total = concepts.len();
        
        ConceptStats {
            total_concepts: total,
            by_type,
            avg_versions_per_concept: if total > 0 { total_versions as f64 / total as f64 } else { 0.0 },
            avg_confidence: if total > 0 { total_confidence / total as f64 } else { 0.0 },
            total_versions,
        }
    }
}

impl Default for ExtractionPipeline {
    fn default() -> Self {
        Self::new()
    }
}

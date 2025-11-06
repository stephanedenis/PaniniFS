//! Concept Extraction API Handlers - Simplified version extracting from chunk hashes

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use panini_core::concept::{ExtractionPipeline, NERExtractor, WikipediaExtractor};
use panini_core::storage::ChunkMetadata;
use serde::Serialize;
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::state::AppState;

pub struct ConceptExtractionState {
    pub pipeline: Arc<RwLock<ExtractionPipeline>>,
}

impl ConceptExtractionState {
    pub fn new() -> Self {
        let mut pipeline = ExtractionPipeline::new();
        pipeline.add_extractor(Box::new(NERExtractor::new()));
        pipeline.add_extractor(Box::new(WikipediaExtractor::new()));
        
        Self {
            pipeline: Arc::new(RwLock::new(pipeline)),
        }
    }
}

#[derive(Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }
}

#[derive(Serialize)]
pub struct ExtractResponse {
    pub job_id: String,
    pub message: String,
    pub note: String,
}

/// POST /api/concepts/extract - Start extraction (mock for now)
pub async fn extract_concepts(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<ExtractResponse>>, (StatusCode, String)> {
    let job_id = uuid::Uuid::new_v4().to_string();
    
    // TODO: Real extraction will read chunks from storage
    // For now, just acknowledge the request
    
    Ok(Json(ApiResponse::success(ExtractResponse {
        job_id: job_id.clone(),
        message: "Extraction job created".to_string(),
        note: "Real extraction requires chunk content access - will be implemented with storage API enhancement".to_string(),
    })))
}

#[derive(Serialize)]
pub struct ConceptStats {
    pub total_concepts: usize,
    pub by_type: std::collections::HashMap<String, usize>,
    pub avg_confidence: f64,
    pub total_versions: usize,
}

/// GET /api/concepts/stats - Get concept statistics
pub async fn get_concept_stats(
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<ConceptStats>>, (StatusCode, String)> {
    let extraction_state = state.extraction_state.clone();
    let pipeline = extraction_state.pipeline.read().await;
    let stats = pipeline.get_stats();
    
    let by_type: std::collections::HashMap<String, usize> = stats
        .by_type
        .into_iter()
        .map(|(k, v)| (format!("{:?}", k), v))
        .collect();

    Ok(Json(ApiResponse::success(ConceptStats {
        total_concepts: stats.total_concepts,
        by_type,
        avg_confidence: stats.avg_confidence,
        total_versions: stats.total_versions,
    })))
}

#[derive(Serialize)]
pub struct ConceptList {
    pub concepts: Vec<panini_core::concept::Concept>,
    pub total: usize,
}

/// GET /api/concepts/list - List extracted concepts
pub async fn list_concepts(
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<ConceptList>>, (StatusCode, String)> {
    let extraction_state = state.extraction_state.clone();
    let pipeline = extraction_state.pipeline.read().await;
    let concepts = pipeline.get_concepts();
    let total = concepts.len();

    Ok(Json(ApiResponse::success(ConceptList {
        concepts,
        total,
    })))
}

/// GET /api/concepts/:id/details - Get specific concept
pub async fn get_concept(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<ApiResponse<panini_core::concept::Concept>>, (StatusCode, String)> {
    let extraction_state = state.extraction_state.clone();
    let pipeline = extraction_state.pipeline.read().await;
    let concepts = pipeline.get_concepts();

    if let Some(concept) = concepts.iter().find(|c| c.id == id) {
        Ok(Json(ApiResponse::success(concept.clone())))
    } else {
        Err((
            StatusCode::NOT_FOUND,
            format!("Concept {} not found", id),
        ))
    }
}

#[derive(Serialize)]
pub struct JobStatus {
    pub job_id: String,
    pub status: String,
}

/// GET /api/extraction/status/:job_id - Get extraction job status
pub async fn get_extraction_status(
    State(state): State<AppState>,
    Path(job_id): Path<String>,
) -> Result<Json<ApiResponse<JobStatus>>, (StatusCode, String)> {
    let extraction_state = state.extraction_state.clone();
    let pipeline = extraction_state.pipeline.read().await;

    if let Some(job) = pipeline.get_job_status(&job_id) {
        let status = match job.status {
            panini_core::concept::ExtractionStatus::Pending => "pending",
            panini_core::concept::ExtractionStatus::Running { .. } => "running",
            panini_core::concept::ExtractionStatus::Completed { .. } => "completed",
        };

        Ok(Json(ApiResponse::success(JobStatus {
            job_id: job.job_id,
            status: status.to_string(),
        })))
    } else {
        Err((
            StatusCode::NOT_FOUND,
            format!("Job {} not found", job_id),
        ))
    }
}

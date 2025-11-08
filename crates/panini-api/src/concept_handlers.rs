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

/// POST /api/concepts/extract/bulk - Start bulk extraction from all chunks
#[derive(serde::Deserialize)]
pub struct BulkExtractParams {
    pub max_chunks: Option<usize>,
    pub parallel: Option<bool>,
    pub parallelism: Option<usize>,
}

#[derive(Serialize)]
pub struct BulkExtractResponse {
    pub chunks_processed: usize,
    pub chunks_skipped: usize,
    pub concepts_extracted: usize,
    pub errors: usize,
    pub elapsed_seconds: f64,
    pub chunks_per_second: f64,
}

pub async fn bulk_extract_concepts(
    State(state): State<AppState>,
    Json(params): Json<BulkExtractParams>,
) -> Result<Json<ApiResponse<BulkExtractResponse>>, (StatusCode, String)> {
    use crate::bulk_extraction;
    
    let state_arc = Arc::new(state);
    
    let stats = if params.parallel.unwrap_or(false) {
        let parallelism = params.parallelism.unwrap_or(4);
        bulk_extraction::extract_from_all_chunks_parallel(
            state_arc,
            params.max_chunks,
            parallelism,
        )
        .await
    } else {
        bulk_extraction::extract_from_all_chunks(
            state_arc,
            params.max_chunks,
        )
        .await
    };
    
    match stats {
        Ok(s) => Ok(Json(ApiResponse::success(BulkExtractResponse {
            chunks_processed: s.chunks_processed,
            chunks_skipped: s.chunks_skipped,
            concepts_extracted: s.concepts_extracted,
            errors: s.errors,
            elapsed_seconds: s.elapsed_seconds,
            chunks_per_second: s.chunks_per_second,
        }))),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Bulk extraction failed: {}", e),
        )),
    }
}

/// POST /api/concepts/extract/filesystem - Extract directly from FS
pub async fn filesystem_extract_concepts(
    State(state): State<AppState>,
    Json(params): Json<BulkExtractParams>,
) -> Result<Json<ApiResponse<BulkExtractResponse>>, (StatusCode, String)> {
    use crate::direct_extraction;
    use std::env;
    
    let storage_path = env::var("PANINI_STORAGE")
        .unwrap_or_else(|_| "/tmp/panini-storage".to_string());
    
    let state_arc = Arc::new(state);
    
    let stats = direct_extraction::extract_from_filesystem(
        state_arc,
        std::path::PathBuf::from(storage_path),
        params.max_chunks,
    )
    .await;
    
    match stats {
        Ok(s) => Ok(Json(ApiResponse::success(BulkExtractResponse {
            chunks_processed: s.chunks_processed,
            chunks_skipped: s.chunks_skipped,
            concepts_extracted: s.concepts_extracted,
            errors: s.errors,
            elapsed_seconds: s.elapsed_seconds,
            chunks_per_second: s.chunks_per_second,
        }))),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Filesystem extraction failed: {}", e),
        )),
    }
}

/// GET /api/concepts/graph - Get concept co-occurrence graph
#[derive(serde::Deserialize)]
pub struct GraphParams {
    pub limit: Option<usize>,
    pub min_connections: Option<usize>,
}

#[derive(Serialize)]
pub struct ConceptNode {
    pub id: String,
    pub name: String,
    pub concept_type: String,
    pub usage_count: usize,
    pub confidence: f32,
}

#[derive(Serialize)]
pub struct ConceptEdge {
    pub source: String,
    pub target: String,
    pub weight: usize,
}

#[derive(Serialize)]
pub struct ConceptGraph {
    pub nodes: Vec<ConceptNode>,
    pub edges: Vec<ConceptEdge>,
}

pub async fn get_concept_graph(
    State(state): State<AppState>,
    axum::extract::Query(params): axum::extract::Query<GraphParams>,
) -> Result<Json<ApiResponse<ConceptGraph>>, (StatusCode, String)> {
    use std::collections::HashMap;
    
    let extraction_state = state.extraction_state.clone();
    let pipeline = extraction_state.pipeline.read().await;
    let all_concepts = pipeline.get_concepts();
    
    let limit = params.limit.unwrap_or(100);
    let min_connections = params.min_connections.unwrap_or(2);
    
    // Build chunk -> concepts map for co-occurrence
    let mut chunk_concepts: HashMap<String, Vec<String>> = HashMap::new();
    
    for concept in &all_concepts {
        for chunk_hash in &concept.source_chunks {
            chunk_concepts
                .entry(chunk_hash.clone())
                .or_insert_with(Vec::new)
                .push(concept.id.clone());
        }
    }
    
    // Calculate co-occurrences
    let mut co_occurrence: HashMap<(String, String), usize> = HashMap::new();
    
    for concepts_in_chunk in chunk_concepts.values() {
        // For each pair of concepts in same chunk
        for i in 0..concepts_in_chunk.len() {
            for j in (i + 1)..concepts_in_chunk.len() {
                let mut pair = (
                    concepts_in_chunk[i].clone(),
                    concepts_in_chunk[j].clone(),
                );
                // Normalize pair order
                if pair.0 > pair.1 {
                    pair = (pair.1, pair.0);
                }
                *co_occurrence.entry(pair).or_insert(0) += 1;
            }
        }
    }
    
    // Filter co-occurrences by min_connections
    let edges: Vec<ConceptEdge> = co_occurrence
        .iter()
        .filter(|(_, &count)| count >= min_connections)
        .map(|((src, tgt), &weight)| ConceptEdge {
            source: src.clone(),
            target: tgt.clone(),
            weight,
        })
        .collect();
    
    // Get unique concept IDs from edges
    let mut concept_ids = std::collections::HashSet::new();
    for edge in &edges {
        concept_ids.insert(edge.source.clone());
        concept_ids.insert(edge.target.clone());
    }
    
    // Build node list
    let concept_map: HashMap<String, &panini_core::concept::Concept> =
        all_concepts.iter().map(|c| (c.id.clone(), c)).collect();
    
    let mut nodes: Vec<ConceptNode> = concept_ids
        .iter()
        .filter_map(|id| {
            concept_map.get(id).map(|c| ConceptNode {
                id: c.id.clone(),
                name: c.canonical_name.clone(),
                concept_type: format!("{:?}", c.concept_type),
                usage_count: c.source_chunks.len(),
                confidence: c.confidence,
            })
        })
        .collect();
    
    // Sort by usage and take top N
    nodes.sort_by(|a, b| b.usage_count.cmp(&a.usage_count));
    nodes.truncate(limit);
    
    // Filter edges to only included nodes
    let node_ids: std::collections::HashSet<String> =
        nodes.iter().map(|n| n.id.clone()).collect();
    
    let filtered_edges: Vec<ConceptEdge> = edges
        .into_iter()
        .filter(|e| node_ids.contains(&e.source) && node_ids.contains(&e.target))
        .collect();
    
    Ok(Json(ApiResponse::success(ConceptGraph {
        nodes,
        edges: filtered_edges,
    })))
}

//! Routing configuration for Panini-FS API

use axum::{
    routing::{get, post},
    Router,
};
use tower_http::cors::CorsLayer;

use crate::{concept_handlers, dedup_handlers, dhatu_handlers, handlers, state::AppState};

/// Create the main API router with all endpoints
pub fn create_router(state: AppState) -> Router {
    // API routes
    let api_routes = Router::new()
        // Health check
        .route("/health", get(handlers::health_check))
        // Legacy concept endpoints (temporal)
        .route("/concepts", get(handlers::list_concepts))
        .route("/concepts/:id", get(handlers::get_concept))
        .route(
            "/concepts/:id/versions/:version_id",
            get(handlers::get_version),
        )
        .route("/concepts/:id/diff", get(handlers::get_diff))
        // NEW: Concept extraction endpoints
        .route("/concepts/extract", post(concept_handlers::extract_concepts))
        .route("/concepts/extract/bulk", post(concept_handlers::bulk_extract_concepts))
        .route("/concepts/extract/filesystem", post(concept_handlers::filesystem_extract_concepts))
        .route("/concepts/extract/persist", post(concept_handlers::persist_extract_concepts))
        .route("/concepts/stats", get(concept_handlers::get_concept_stats))
        .route("/concepts/stored/stats", get(concept_handlers::get_stored_concepts_stats))
        .route("/concepts/list", get(concept_handlers::list_concepts))
        .route("/concepts/graph", get(concept_handlers::get_concept_graph))
        .route("/concepts/:id/details", get(concept_handlers::get_concept))
        .route(
            "/extraction/status/:job_id",
            get(concept_handlers::get_extraction_status),
        )
        // Timeline endpoint
        .route("/timeline", get(handlers::get_timeline))
        // Snapshot endpoints
        .route("/snapshots", get(handlers::list_snapshots))
        .route("/snapshots/:id", get(handlers::get_snapshot))
        // Time-travel endpoint
        .route("/time-travel", get(handlers::time_travel))
        // Stats endpoint
        .route("/stats", get(handlers::get_stats))
        // Deduplication endpoints (Phase 7)
        .route("/dedup/stats", get(dedup_handlers::get_dedup_stats))
        .route("/chunks/search", get(dedup_handlers::search_atoms))
        .route("/chunks/:hash", get(dedup_handlers::get_atom_details))
        .route("/files/analyze", post(dedup_handlers::analyze_file))
        .route("/files/:hash/chunks", get(dedup_handlers::get_file_atoms))
        // Dhātu emotional classification endpoints (Phase 9)
        .route("/dhatu/emotions", get(dhatu_handlers::get_emotions))
        .route("/dhatu/roots/:emotion", get(dhatu_handlers::get_roots))
        .route("/dhatu/classify", post(dhatu_handlers::classify_content))
        .route("/dhatu/search", get(dhatu_handlers::search_profiles))
        .route("/dhatu/stats", get(dhatu_handlers::get_stats))
        .route(
            "/dhatu/resonance",
            post(dhatu_handlers::calculate_resonance),
        );

    // Main router with /api prefix
    Router::new()
        .nest("/api", api_routes)
        .layer(CorsLayer::permissive()) // Allow CORS for Web UI
        .with_state(state)
}

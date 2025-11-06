//! Panini-FS API Server
//!
//! REST API server for temporal filesystem with time-travel capabilities

use anyhow::Result;
use panini_api::{ApiServer, AppState};
use panini_core::storage::{
    backends::localfs::LocalFsBackend,
    cas::{ContentAddressedStorage, StorageConfig},
    immutable::TemporalIndex,
    ChunkType,
};
use serde_json::Value;
use std::{
    net::SocketAddr,
    path::Path,
    sync::{Arc, RwLock},
};
use tracing::{info, warn, Level};
use tracing_subscriber::FmtSubscriber;

/// Load chunks from rebuilt_index.json file
async fn load_chunk_index(
    storage_dir: &str,
    cas: &Arc<ContentAddressedStorage<LocalFsBackend>>,
) -> Result<usize> {
    let index_path = Path::new(storage_dir).join("index/rebuilt_index.json");
    
    if !index_path.exists() {
        return Ok(0);
    }
    
    info!("📂 Loading chunk index from: {:?}", index_path);
    
    let index_data = std::fs::read_to_string(&index_path)?;
    let index: Value = serde_json::from_str(&index_data)?;
    
    let chunks = index["chunks"].as_array()
        .ok_or_else(|| anyhow::anyhow!("No 'chunks' array in index"))?;
    
    let mut loaded = 0;
    for chunk_obj in chunks {
        if let (Some(hash), Some(size), Some(chunk_type_str), created_at) = (
            chunk_obj["hash"].as_str(),
            chunk_obj["size"].as_u64(),
            chunk_obj["chunk_type"].as_str(),
            chunk_obj["created_at"].as_u64(),
        ) {
            // Parse chunk type
            let chunk_type = match chunk_type_str {
                "Raw" => ChunkType::Raw,
                "Container" => ChunkType::Container,
                "Compressed" => ChunkType::Compressed,
                "VideoStream" => ChunkType::VideoStream,
                "AudioStream" => ChunkType::AudioStream,
                "IFrame" => ChunkType::IFrame,
                "PFrame" => ChunkType::PFrame,
                "BFrame" => ChunkType::BFrame,
                "Subtitle" => ChunkType::Subtitle,
                "ImageData" => ChunkType::ImageData,
                "Metadata" => ChunkType::Metadata,
                "AudioChunk" => ChunkType::AudioChunk,
                _ => ChunkType::Raw,
            };
            
            // Register with CAS
            if let Err(e) = cas.register_existing_chunk(
                hash.to_string(),
                size,
                chunk_type,
                created_at.unwrap_or(0),
            ) {
                warn!("Failed to register chunk {}: {}", hash, e);
                continue;
            }
            
            loaded += 1;
        }
    }
    
    info!("✅ Loaded {} chunks from index", loaded);
    Ok(loaded)
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("🚀 Panini-FS API Server Starting...");

    // Create storage directories
    let storage_dir =
        std::env::var("PANINI_STORAGE").unwrap_or_else(|_| "/tmp/panini-storage".to_string());

    info!("Storage directory: {}", storage_dir);
    std::fs::create_dir_all(&storage_dir)?;

    // Initialize backend (not async)
    let backend = Arc::new(LocalFsBackend::new(&storage_dir)?);
    info!("✓ Storage backend initialized");

    // Initialize CAS with config
    let config = StorageConfig {
        max_atom_size: 64 * 1024, // 64KB
        enable_dedup: true,
        compression: None,
    };
    let cas = Arc::new(ContentAddressedStorage::new(backend, config));
    info!("✓ Content-Addressed Storage initialized");

    // Load existing chunks from index
    match load_chunk_index(&storage_dir, &cas).await {
        Ok(count) if count > 0 => {
            info!("✅ Loaded {} existing chunks from index", count);
        }
        Ok(_) => {
            info!("ℹ️  No existing index found, starting with empty storage");
        }
        Err(e) => {
            warn!("⚠️  Could not load chunk index: {}", e);
            info!("Continuing with empty storage...");
        }
    }

    // Initialize temporal index (use std::sync::RwLock, not tokio::sync::RwLock)
    let temporal_index = Arc::new(RwLock::new(TemporalIndex::new()));
    info!("✓ Temporal Index initialized");

    // Create application state with storage path for Dhātu persistence
    let state = AppState::new(temporal_index, cas, storage_dir.into());
    info!("✓ Application state created (Dhātu persistence enabled)");

    // Parse server address
    let host = std::env::var("PANINI_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port = std::env::var("PANINI_PORT")
        .unwrap_or_else(|_| "3000".to_string())
        .parse::<u16>()?;
    let addr: SocketAddr = format!("{}:{}", host, port).parse()?;

    info!("Server address: http://{}", addr);

    // Create and run server
    let server = ApiServer::new(addr, state);
    info!("✓ API server configured");

    info!("🎯 Starting HTTP server...");
    server.run().await?;

    Ok(())
}

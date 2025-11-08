//! Direct extraction from filesystem - bypass CAS index

use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;
use tokio::fs;
use panini_core::storage::ChunkMetadata;
use panini_core::storage::chunk::ChunkType;

use crate::state::AppState;
use crate::bulk_extraction::BulkExtractionStats;

/// Extract concepts by scanning filesystem directly
pub async fn extract_from_filesystem(
    state: Arc<AppState>,
    storage_path: PathBuf,
    max_chunks: Option<usize>,
) -> Result<BulkExtractionStats, String> {
    let start = Instant::now();
    let extraction_state = state.extraction_state.clone();
    
    println!("🔍 Scanning filesystem: {:?}", storage_path);
    
    // Scan all shard directories
    let mut chunks_with_content = Vec::new();
    let mut processed = 0;
    let mut skipped = 0;
    let mut errors = 0;
    
    // Iterate through shard dirs (00-ff)
    for prefix1 in 0..=255u8 {
        let dir1 = storage_path.join(format!("{:02x}", prefix1));
        
        if !dir1.exists() {
            continue;
        }
        
        let mut read_dir = match fs::read_dir(&dir1).await {
            Ok(rd) => rd,
            Err(_) => continue,
        };
        
        while let Ok(Some(entry)) = read_dir.next_entry().await {
            let dir2 = entry.path();
            
            if !dir2.is_dir() {
                continue;
            }
            
            let mut read_dir2 = match fs::read_dir(&dir2).await {
                Ok(rd) => rd,
                Err(_) => continue,
            };
            
            while let Ok(Some(file_entry)) = read_dir2.next_entry().await {
                let file_path = file_entry.path();
                
                if !file_path.is_file() {
                    continue;
                }
                
                // Extract hash from filename
                if let Some(hash) = file_path.file_name().and_then(|n| n.to_str()) {
                    // Read content
                    match fs::read(&file_path).await {
                        Ok(bytes) => {
                            match String::from_utf8(bytes) {
                                Ok(text) => {
                                    if text.trim().len() < 20 {
                                        skipped += 1;
                                        continue;
                                    }
                                    
                                    // Create minimal metadata
                                    let metadata = ChunkMetadata {
                                        hash: hash.to_string(),
                                        size: text.len() as u64,
                                        chunk_type: ChunkType::Container,
                                        created_at: 0,
                                        ref_count: 1,
                                    };
                                    
                                    chunks_with_content.push((metadata, text));
                                    processed += 1;
                                    
                                    if processed % 100 == 0 {
                                        let elapsed = start.elapsed().as_secs_f64();
                                        let rate = processed as f64 / elapsed;
                                        println!("  [{}] {:.1} chunks/sec loaded", processed, rate);
                                    }
                                    
                                    // Check max limit
                                    if let Some(max) = max_chunks {
                                        if processed >= max {
                                            break;
                                        }
                                    }
                                }
                                Err(_) => skipped += 1,
                            }
                        }
                        Err(_) => errors += 1,
                    }
                }
                
                // Break outer loops if max reached
                if let Some(max) = max_chunks {
                    if processed >= max {
                        break;
                    }
                }
            }
            
            if let Some(max) = max_chunks {
                if processed >= max {
                    break;
                }
            }
        }
        
        if let Some(max) = max_chunks {
            if processed >= max {
                break;
            }
        }
    }
    
    println!("✅ Scanned filesystem: {} chunks loaded", chunks_with_content.len());
    
    // Extract concepts
    let pipeline = extraction_state.pipeline.read().await;
    let job_id = uuid::Uuid::new_v4().to_string();
    let concepts = pipeline.extract_from_chunks(chunks_with_content, job_id);
    let concepts_extracted = concepts.len();
    
    let elapsed = start.elapsed().as_secs_f64();
    let chunks_per_second = if elapsed > 0.0 {
        processed as f64 / elapsed
    } else {
        0.0
    };
    
    println!("\n✅ Filesystem extraction completed:");
    println!("   - Chunks processed: {}", processed);
    println!("   - Chunks skipped: {}", skipped);
    println!("   - Concepts extracted: {}", concepts_extracted);
    println!("   - Errors: {}", errors);
    println!("   - Time: {:.2}s ({:.1} chunks/sec)", elapsed, chunks_per_second);
    
    Ok(BulkExtractionStats {
        chunks_processed: processed,
        chunks_skipped: skipped,
        concepts_extracted,
        errors,
        elapsed_seconds: elapsed,
        chunks_per_second,
    })
}

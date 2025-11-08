//! Bulk Concept Extraction from All Chunks

use crate::state::AppState;
use std::sync::Arc;
use std::time::Instant;

/// Statistics for bulk extraction
#[derive(Debug, Clone, serde::Serialize)]
pub struct BulkExtractionStats {
    pub chunks_processed: usize,
    pub chunks_skipped: usize,
    pub concepts_extracted: usize,
    pub errors: usize,
    pub elapsed_seconds: f64,
    pub chunks_per_second: f64,
}

/// Extract concepts from all chunks in storage (Sequential)
pub async fn extract_from_all_chunks(
    state: Arc<AppState>,
    max_chunks: Option<usize>,
) -> Result<BulkExtractionStats, String> {
    let start = Instant::now();
    let extraction_state = state.extraction_state.clone();
    
    // Get all atoms from storage
    let all_atoms = state.cas.list_atoms();
    
    let total_to_process = if let Some(max) = max_chunks {
        all_atoms.len().min(max)
    } else {
        all_atoms.len()
    };
    
    println!(
        "🚀 Starting extraction from {} chunks",
        total_to_process
    );
    
    let mut processed = 0;
    let mut skipped = 0;
    let mut errors = 0;
    let mut chunks_with_content = Vec::new();
    
    // Collect chunks with their content
    for (idx, atom) in all_atoms.iter().take(total_to_process).enumerate() {
        // Progress report every 100 chunks
        if idx > 0 && idx % 100 == 0 {
            let elapsed = start.elapsed().as_secs_f64();
            let rate = idx as f64 / elapsed;
            println!("  [{}/{}] {:.1} chunks/sec loaded", idx, total_to_process, rate);
        }
        
        // Read chunk content
        match state.cas.get_atom(&atom.hash).await {
            Ok(bytes) => {
                match String::from_utf8(bytes.to_vec()) {
                    Ok(text) => {
                        // Skip very short or empty chunks
                        if text.trim().len() < 20 {
                            skipped += 1;
                            continue;
                        }
                        
                        chunks_with_content.push((atom.clone(), text));
                        processed += 1;
                    }
                    Err(_) => {
                        // Binary content, skip
                        skipped += 1;
                    }
                }
            }
            Err(e) => {
                eprintln!("⚠️  Failed to read atom {}: {}", atom.hash, e);
                errors += 1;
            }
        }
    }
    
    println!("✅ Loaded {} chunks, extracting concepts...", chunks_with_content.len());
    
    // Extract concepts from all chunks at once
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
    
    println!("\n✅ Bulk extraction completed:");
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

/// Extract from chunks in parallel batches
pub async fn extract_from_all_chunks_parallel(
    state: Arc<AppState>,
    max_chunks: Option<usize>,
    parallelism: usize,
) -> Result<BulkExtractionStats, String> {
    let start = Instant::now();
    let extraction_state = state.extraction_state.clone();
    
    // Get all chunks
    let all_atoms = state.cas.list_atoms();
    
    let total_to_process = if let Some(max) = max_chunks {
        all_atoms.len().min(max)
    } else {
        all_atoms.len()
    };
    
    println!(
        "🚀 Starting PARALLEL extraction from {} chunks with {} workers",
        total_to_process, parallelism
    );
    
    // Split chunks into batches
    let chunks_per_batch = (total_to_process / parallelism).max(1);
    let mut handles = vec![];
    
    for batch_idx in 0..parallelism {
        let start_idx = batch_idx * chunks_per_batch;
        let end_idx = ((batch_idx + 1) * chunks_per_batch).min(total_to_process);
        
        if start_idx >= total_to_process {
            break;
        }
        
        let batch = all_atoms[start_idx..end_idx].to_vec();
        let state_clone = state.clone();
        let extraction_state_clone = extraction_state.clone();
        
        let handle = tokio::spawn(async move {
            let mut processed = 0;
            let mut skipped = 0;
            let mut errors = 0;
            let mut chunks_with_content = Vec::new();
            
            // Load chunks
            for atom in batch {
                match state_clone.cas.get_atom(&atom.hash).await {
                    Ok(bytes) => {
                        match String::from_utf8(bytes.to_vec()) {
                            Ok(text) => {
                                if text.trim().len() < 20 {
                                    skipped += 1;
                                    continue;
                                }
                                chunks_with_content.push((atom.clone(), text));
                                processed += 1;
                            }
                            Err(_) => skipped += 1,
                        }
                    }
                    Err(_) => errors += 1,
                }
            }
            
            // Extract concepts
            let pipeline = extraction_state_clone.pipeline.read().await;
            let job_id = format!("batch_{}", batch_idx);
            let concepts = pipeline.extract_from_chunks(chunks_with_content, job_id);
            let concepts_count = concepts.len();
            
            (processed, skipped, errors, concepts_count)
        });
        
        handles.push(handle);
    }
    
    // Wait for all batches
    let mut total_processed = 0;
    let mut total_skipped = 0;
    let mut total_errors = 0;
    let mut total_concepts = 0;
    
    for handle in handles {
        match handle.await {
            Ok((processed, skipped, errors, concepts)) => {
                total_processed += processed;
                total_skipped += skipped;
                total_errors += errors;
                total_concepts += concepts;
            }
            Err(e) => {
                eprintln!("⚠️  Worker task failed: {}", e);
            }
        }
    }
    
    let elapsed = start.elapsed().as_secs_f64();
    let chunks_per_second = if elapsed > 0.0 {
        total_processed as f64 / elapsed
    } else {
        0.0
    };
    
    println!("\n✅ Parallel extraction completed:");
    println!("   - Chunks processed: {}", total_processed);
    println!("   - Chunks skipped: {}", total_skipped);
    println!("   - Concepts extracted: {}", total_concepts);
    println!("   - Errors: {}", total_errors);
    println!("   - Time: {:.2}s ({:.1} chunks/sec)", elapsed, chunks_per_second);
    
    Ok(BulkExtractionStats {
        chunks_processed: total_processed,
        chunks_skipped: total_skipped,
        concepts_extracted: total_concepts,
        errors: total_errors,
        elapsed_seconds: elapsed,
        chunks_per_second,
    })
}

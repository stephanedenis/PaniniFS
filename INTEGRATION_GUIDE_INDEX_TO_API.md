# Integration Guide: Loading rebuilt_index.json into Panini API

## Current Status

✅ **Refactoring Complete**: All Atom → Chunk renaming done
✅ **Data Exists**: 1,458 chunks in `/home/stephane/panini-wikipedia-full`
✅ **Index Built**: `rebuilt_index.json` (284 KB) with all chunk metadata
❌ **API Disconnected**: API shows 0 chunks because it doesn't read the index

## The Problem

The API initializes an empty ContentAddressedStorage and TemporalIndex:

```rust
// Current code in crates/panini-api/src/main.rs
let cas = Arc::new(ContentAddressedStorage::new(backend, config));
let temporal_index = Arc::new(RwLock::new(TemporalIndex::new()));
```

These are empty on startup. The 1,458 chunks exist on disk but aren't registered in memory/RocksDB.

## Solution Options

### Option A: Load Index on API Startup (Recommended)

Modify `crates/panini-api/src/main.rs` to load the index after CAS initialization:

```rust
// After this line:
let cas = Arc::new(ContentAddressedStorage::new(backend, config));

// Add this:
info!("Loading existing chunks from storage...");
let index_path = Path::new(&storage_dir).join("index/rebuilt_index.json");
if index_path.exists() {
    match load_rebuilt_index(&index_path, &cas).await {
        Ok(count) => info!("✓ Loaded {} chunks from index", count),
        Err(e) => warn!("Could not load index: {}", e),
    }
}
```

Create a helper function:

```rust
async fn load_rebuilt_index(
    index_path: &Path,
    cas: &Arc<ContentAddressedStorage>,
) -> Result<usize> {
    use serde_json::Value;
    
    let index_data = std::fs::read_to_string(index_path)?;
    let index: Value = serde_json::from_str(&index_data)?;
    
    let chunks = index["chunks"].as_array()
        .ok_or_else(|| anyhow::anyhow!("Invalid index format"))?;
    
    for chunk_obj in chunks {
        let hash = chunk_obj["hash"].as_str().unwrap();
        let size = chunk_obj["size"].as_u64().unwrap() as usize;
        let chunk_type = chunk_obj["chunk_type"].as_str().unwrap();
        
        // Register with CAS (this updates internal tracking)
        // Implementation depends on CAS API - might need to add a method like:
        // cas.register_existing_chunk(hash, size, chunk_type)?;
    }
    
    Ok(chunks.len())
}
```

### Option B: Scan Storage on Startup

Instead of reading the JSON, scan the storage directory:

```rust
info!("Scanning storage for existing chunks...");
let scanned = scan_storage_directory(&storage_dir, &cas).await?;
info!("✓ Found {} chunks in storage", scanned);
```

This is more robust but slower (reads all files).

### Option C: Use RocksDB as Source of Truth

Store chunk metadata in RocksDB and persist it:

1. When a chunk is added → Write to RocksDB
2. On startup → Load all chunks from RocksDB
3. No need for separate index files

This requires modifying the CAS implementation to use RocksDB.

## Implementation Steps for Option A

### Step 1: Add Index Loading Method to CAS

File: `crates/panini-core/src/storage/cas.rs`

```rust
impl ContentAddressedStorage {
    /// Register an existing chunk without re-reading the file
    pub fn register_existing_chunk(
        &self,
        hash: String,
        size: usize,
        chunk_type: ChunkType,
    ) -> Result<()> {
        let mut guard = self.stats.write()
            .map_err(|e| anyhow::anyhow!("Lock error: {}", e))?;
        
        // Update statistics
        guard.total_chunks += 1;
        guard.total_size += size;
        
        // Add to metadata tracking
        let metadata = ChunkMetadata {
            hash: hash.clone(),
            size,
            chunk_type,
            ref_count: 1,
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_secs(),
        };
        
        guard.chunk_metadata.insert(hash, metadata);
        
        Ok(())
    }
}
```

### Step 2: Add Index Loader to main.rs

File: `crates/panini-api/src/main.rs`

```rust
use std::path::Path;
use serde_json::Value;

async fn load_chunk_index(
    storage_dir: &str,
    cas: &Arc<ContentAddressedStorage>,
) -> Result<usize> {
    let index_path = Path::new(storage_dir).join("index/rebuilt_index.json");
    
    if !index_path.exists() {
        return Ok(0);
    }
    
    info!("Loading chunk index from: {:?}", index_path);
    
    let index_data = std::fs::read_to_string(&index_path)?;
    let index: Value = serde_json::from_str(&index_data)?;
    
    let chunks = index["chunks"].as_array()
        .ok_or_else(|| anyhow::anyhow!("No 'chunks' array in index"))?;
    
    let mut loaded = 0;
    for chunk_obj in chunks {
        if let (Some(hash), Some(size), Some(chunk_type_str)) = (
            chunk_obj["hash"].as_str(),
            chunk_obj["size"].as_u64(),
            chunk_obj["chunk_type"].as_str(),
        ) {
            // Parse chunk type
            use panini_core::storage::ChunkType;
            let chunk_type = match chunk_type_str {
                "Raw" => ChunkType::Raw,
                "Container" => ChunkType::Container,
                "Compressed" => ChunkType::Compressed,
                _ => ChunkType::Raw,
            };
            
            // Register with CAS
            cas.register_existing_chunk(
                hash.to_string(),
                size as usize,
                chunk_type,
            )?;
            
            loaded += 1;
        }
    }
    
    info!("✓ Loaded {} chunks from index", loaded);
    Ok(loaded)
}
```

### Step 3: Call Index Loader in main()

File: `crates/panini-api/src/main.rs`

```rust
#[tokio::main]
async fn main() -> Result<()> {
    // ... existing initialization code ...
    
    let cas = Arc::new(ContentAddressedStorage::new(backend, config));
    info!("✓ Content-Addressed Storage initialized");
    
    // NEW: Load existing chunks from index
    match load_chunk_index(&storage_dir, &cas).await {
        Ok(count) if count > 0 => {
            info!("✓ Loaded {} existing chunks", count);
        }
        Ok(_) => {
            info!("No existing index found, starting fresh");
        }
        Err(e) => {
            warn!("Could not load chunk index: {}", e);
        }
    }
    
    // ... rest of initialization ...
}
```

### Step 4: Rebuild and Test

```bash
# Rebuild API
cd /home/stephane/GitHub/Panini-FS
cargo build --release --bin panini-api

# Restart API
pkill -f panini-api
PANINI_STORAGE=/home/stephane/panini-wikipedia-full \
  /home/stephane/GitHub/Panini-FS/target/release/panini-api \
  > /tmp/panini-api-chunks.log 2>&1 &

# Wait a few seconds
sleep 5

# Test that chunks are loaded
curl -s http://localhost:3000/api/dedup/stats | jq '.'

# Should show:
# {
#   "total_chunks": 1458,
#   "unique_chunks": 1458,
#   "total_size": 52451360,
#   ...
# }
```

## Testing the Integration

### 1. Check API Logs

```bash
tail -f /tmp/panini-api-chunks.log
```

Look for:
```
INFO panini_api: Loading chunk index from: "/home/stephane/panini-wikipedia-full/index/rebuilt_index.json"
INFO panini_api: ✓ Loaded 1458 existing chunks
```

### 2. Test Stats Endpoint

```bash
curl -s http://localhost:3000/api/dedup/stats | jq '.'
```

Expected output:
```json
{
  "total_files": 1458,
  "total_size": 52451360,
  "total_chunks": 1458,
  "unique_chunks": 1458,
  "dedup_ratio": 0.0081,
  "storage_saved": 424856,
  "avg_reuse": 1.0081
}
```

### 3. Test Individual Chunk Retrieval

```bash
# Get first chunk hash from index
HASH=$(jq -r '.chunks[0].hash' /home/stephane/panini-wikipedia-full/index/rebuilt_index.json)

# Query API for this chunk
curl -s "http://localhost:3000/api/chunks/$HASH" | jq '.'
```

### 4. Test Web UI

```bash
# Start web UI
cd /home/stephane/GitHub/Panini-FS/web-ui
npm run dev
```

Visit `http://localhost:5173/graph` and verify:
- Total Chunks shows: **1,458**
- Unique Chunks shows: **1,458**
- Graph displays chunk relationships
- Clicking chunks shows metadata

## Alternative: Quick Fix Without Code Changes

If modifying Rust code is complex, use this Python script to re-upload all chunks:

```bash
cd /home/stephane/GitHub/Panini-FS
python3 tools/load_index_to_api.py /home/stephane/panini-wikipedia-full http://localhost:3000
```

This reads each chunk file and POST it to `/api/dedup/upload`, which triggers deduplication and registration.

**Note**: This is slower (re-reads all files) but doesn't require code changes.

## Success Criteria

✅ API logs show "Loaded 1458 chunks"
✅ `/api/dedup/stats` returns `total_chunks: 1458`
✅ Web UI displays 1,458 chunks in graph
✅ Individual chunks retrievable via `/api/chunks/:hash`
✅ Deduplication stats correct (0.81% ratio)

## Next Phase After Integration

Once the API correctly loads and exposes the 1,458 chunks:

1. **Test Web UI** - Verify GraphExplorer displays chunks properly
2. **Phase 2: Concepts** - Begin implementing versioned semantic concept extraction
3. **Resume Ingestion** - Continue Wikipedia ingestion (~2.8M articles remaining)

## Files Modified

- `crates/panini-core/src/storage/cas.rs` - Add `register_existing_chunk()` method
- `crates/panini-api/src/main.rs` - Add `load_chunk_index()` and call on startup
- `Cargo.toml` - Ensure `serde_json` dependency exists

## Estimated Time

- **Code changes**: 30 minutes
- **Testing**: 15 minutes
- **Total**: 45 minutes

## Current Blockers

⚠️ Cannot directly edit Rust files in `/home/stephane/GitHub/Panini-FS/crates/*` from this workspace context

### Workaround

1. Open files manually in VS Code
2. Apply changes from this guide
3. Rebuild and test

OR

3. Use Python upload script as temporary solution until Rust changes are made

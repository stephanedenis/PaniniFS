//! LRU Cache for Content-Addressed Storage
//!
//! Provides a caching layer on top of CAS to reduce disk I/O for frequently accessed atoms.

use anyhow::Result;
use lru::LruCache;
use std::num::NonZeroUsize;
use std::sync::{Arc, Mutex};

/// Cached chunk data
#[derive(Clone, Debug)]
pub struct CachedChunk {
    /// Chunk hash
    pub hash: String,
    /// Chunk content
    pub content: Vec<u8>,
    /// Content size in bytes
    pub size: usize,
}

/// LRU cache configuration
#[derive(Clone, Debug)]
pub struct CacheConfig {
    /// Maximum number of atoms to cache
    pub max_chunks: usize,
    /// Maximum total cache size in bytes (0 = unlimited)
    pub max_bytes: usize,
}

impl Default for CacheConfig {
    fn default() -> Self {
        Self {
            max_chunks: 1000,
            max_bytes: 100 * 1024 * 1024, // 100MB
        }
    }
}

/// LRU cache for atoms
pub struct ChunkCache {
    cache: Arc<Mutex<LruCache<String, CachedChunk>>>,
    config: CacheConfig,
    current_size: Arc<Mutex<usize>>,
    stats: Arc<Mutex<CacheStats>>,
}

/// Cache statistics
#[derive(Clone, Debug, Default)]
pub struct CacheStats {
    pub hits: u64,
    pub misses: u64,
    pub evictions: u64,
    pub total_size: usize,
}

impl CacheStats {
    pub fn hit_rate(&self) -> f64 {
        let total = self.hits + self.misses;
        if total == 0 {
            0.0
        } else {
            self.hits as f64 / total as f64
        }
    }
}

impl ChunkCache {
    /// Create a new cache with default configuration
    pub fn new() -> Self {
        Self::with_config(CacheConfig::default())
    }

    /// Create a new cache with custom configuration
    pub fn with_config(config: CacheConfig) -> Self {
        let capacity = NonZeroUsize::new(config.max_chunks).unwrap();

        Self {
            cache: Arc::new(Mutex::new(LruCache::new(capacity))),
            config,
            current_size: Arc::new(Mutex::new(0)),
            stats: Arc::new(Mutex::new(CacheStats::default())),
        }
    }

    /// Get an chunk from cache
    pub fn get(&self, hash: &str) -> Option<CachedChunk> {
        let mut cache = self.cache.lock().unwrap();
        let mut stats = self.stats.lock().unwrap();

        if let Some(chunk) = cache.get(hash) {
            stats.hits += 1;
            Some(chunk.clone())
        } else {
            stats.misses += 1;
            None
        }
    }

    /// Put an chunk into cache
    pub fn put(&self, hash: String, content: Vec<u8>) -> Result<()> {
        let size = content.len();
        let chunk = CachedChunk {
            hash: hash.clone(),
            content,
            size,
        };

        // Check if adding this chunk would exceed max_bytes
        if self.config.max_bytes > 0 {
            let mut current_size = self.current_size.lock().unwrap();

            // Evict entries if needed
            while *current_size + size > self.config.max_bytes && !self.is_empty() {
                self.evict_one()?;
                *current_size = self.calculate_size();
            }

            // Don't cache if single chunk exceeds max_bytes
            if size > self.config.max_bytes {
                return Ok(());
            }
        }

        let mut cache = self.cache.lock().unwrap();

        // LRU eviction may occur here
        if let Some((_, evicted)) = cache.push(hash, chunk) {
            let mut stats = self.stats.lock().unwrap();
            stats.evictions += 1;

            let mut current_size = self.current_size.lock().unwrap();
            *current_size = current_size.saturating_sub(evicted.size);
        }

        // Update size
        let mut current_size = self.current_size.lock().unwrap();
        *current_size += size;

        // Update stats
        let mut stats = self.stats.lock().unwrap();
        stats.total_size = *current_size;

        Ok(())
    }

    /// Clear the cache
    pub fn clear(&self) {
        let mut cache = self.cache.lock().unwrap();
        cache.clear();

        let mut current_size = self.current_size.lock().unwrap();
        *current_size = 0;

        let mut stats = self.stats.lock().unwrap();
        stats.total_size = 0;
    }

    /// Get cache statistics
    pub fn stats(&self) -> CacheStats {
        self.stats.lock().unwrap().clone()
    }

    /// Check if cache is empty
    pub fn is_empty(&self) -> bool {
        self.cache.lock().unwrap().is_empty()
    }

    /// Get current number of cached atoms
    pub fn len(&self) -> usize {
        self.cache.lock().unwrap().len()
    }

    fn evict_one(&self) -> Result<()> {
        let mut cache = self.cache.lock().unwrap();
        if let Some((_, evicted)) = cache.pop_lru() {
            let mut stats = self.stats.lock().unwrap();
            stats.evictions += 1;

            let mut current_size = self.current_size.lock().unwrap();
            *current_size = current_size.saturating_sub(evicted.size);
        }
        Ok(())
    }

    fn calculate_size(&self) -> usize {
        let cache = self.cache.lock().unwrap();
        cache.iter().map(|(_, chunk)| chunk.size).sum()
    }
}

impl Default for ChunkCache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_basic() {
        let cache = ChunkCache::new();

        // Miss on empty cache
        assert!(cache.get("hash1").is_none());

        // Put and retrieve
        cache.put("hash1".to_string(), vec![1, 2, 3]).unwrap();
        assert!(cache.get("hash1").is_some());

        let chunk = cache.get("hash1").unwrap();
        assert_eq!(chunk.content, vec![1, 2, 3]);
        assert_eq!(chunk.size, 3);
    }

    #[test]
    fn test_cache_eviction() {
        let config = CacheConfig {
            max_chunks: 2,
            max_bytes: 0,
        };
        let cache = ChunkCache::with_config(config);

        cache.put("hash1".to_string(), vec![1]).unwrap();
        cache.put("hash2".to_string(), vec![2]).unwrap();
        cache.put("hash3".to_string(), vec![3]).unwrap();

        // hash1 should be evicted (LRU)
        assert!(cache.get("hash1").is_none());
        assert!(cache.get("hash2").is_some());
        assert!(cache.get("hash3").is_some());
    }

    #[test]
    fn test_cache_size_limit() {
        let config = CacheConfig {
            max_chunks: 100,
            max_bytes: 10,
        };
        let cache = ChunkCache::with_config(config);

        cache.put("hash1".to_string(), vec![1, 2, 3, 4]).unwrap();
        cache.put("hash2".to_string(), vec![5, 6, 7]).unwrap();
        cache.put("hash3".to_string(), vec![8, 9]).unwrap();

        // Should only keep hash2 and hash3 (7 bytes total)
        let stats = cache.stats();
        assert!(stats.total_size <= 10);
    }

    #[test]
    fn test_cache_stats() {
        let cache = ChunkCache::new();

        cache.put("hash1".to_string(), vec![1, 2, 3]).unwrap();

        cache.get("hash1"); // Hit
        cache.get("hash2"); // Miss
        cache.get("hash1"); // Hit

        let stats = cache.stats();
        assert_eq!(stats.hits, 2);
        assert_eq!(stats.misses, 1);
        assert_eq!(stats.hit_rate(), 2.0 / 3.0);
    }
}

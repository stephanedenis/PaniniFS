//! Persistent storage for Dhātu emotional profiles using RocksDB

use anyhow::{Context, Result};
use panini_core::dhatu::profile::EmotionalProfile;
use rocksdb::{IteratorMode, Options, DB};
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::sync::Arc;
use tracing;

/// Persistent store for emotional profiles
pub struct DhatuStore {
    db: Arc<DB>,
}

impl DhatuStore {
    /// Open or create a new Dhātu store
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self> {
        let mut opts = Options::default();
        opts.create_if_missing(true);
        // No compression for maximum compatibility
        opts.set_compression_type(rocksdb::DBCompressionType::None);

        let db = DB::open(&opts, path.as_ref()).context("Failed to open Dhātu RocksDB")?;

        tracing::info!("Opened Dhātu persistent store at {:?}", path.as_ref());

        Ok(Self { db: Arc::new(db) })
    }

    /// Store an emotional profile
    pub fn store_profile(&self, path: &str, profile: &EmotionalProfile) -> Result<()> {
        let key = Self::make_key(path);
        let value = serde_json::to_vec(profile).context("Failed to serialize profile")?;

        self.db
            .put(&key, value)
            .context("Failed to store profile in RocksDB")?;

        tracing::debug!("Stored profile for path: {}", path);
        Ok(())
    }

    /// Retrieve an emotional profile
    pub fn get_profile(&self, path: &str) -> Result<Option<EmotionalProfile>> {
        let key = Self::make_key(path);

        match self.db.get(&key)? {
            Some(value) => {
                let profile =
                    serde_json::from_slice(&value).context("Failed to deserialize profile")?;
                Ok(Some(profile))
            }
            None => Ok(None),
        }
    }

    /// List all profiles
    pub fn list_profiles(&self) -> Result<Vec<(String, EmotionalProfile)>> {
        let mut profiles = Vec::new();

        for item in self.db.iterator(IteratorMode::Start) {
            let (key, value) = item?;

            let path = String::from_utf8_lossy(&key)
                .trim_start_matches("profile:")
                .to_string();

            let profile: EmotionalProfile =
                serde_json::from_slice(&value).context("Failed to deserialize profile")?;

            profiles.push((path, profile));
        }

        Ok(profiles)
    }

    /// Count total profiles
    pub fn count(&self) -> usize {
        self.db.iterator(IteratorMode::Start).count()
    }

    /// Get profiles by dominant emotion
    pub fn get_by_emotion(&self, emotion: &str) -> Result<Vec<(String, EmotionalProfile)>> {
        let all_profiles = self.list_profiles()?;

        Ok(all_profiles
            .into_iter()
            .filter(|(_, profile)| {
                profile
                    .dominant_emotion
                    .map(|e| format!("{:?}", e).to_lowercase() == emotion.to_lowercase())
                    .unwrap_or(false)
            })
            .collect())
    }

    /// Get profiles with high arousal (>= threshold)
    pub fn get_high_arousal(&self, threshold: f64) -> Result<Vec<(String, EmotionalProfile)>> {
        let all_profiles = self.list_profiles()?;

        Ok(all_profiles
            .into_iter()
            .filter(|(_, profile)| profile.intensity.arousal() >= threshold)
            .collect())
    }

    /// Delete a profile
    pub fn delete_profile(&self, path: &str) -> Result<()> {
        let key = Self::make_key(path);
        self.db.delete(&key).context("Failed to delete profile")?;

        tracing::debug!("Deleted profile for path: {}", path);
        Ok(())
    }

    /// Clear all profiles
    pub fn clear(&self) -> Result<()> {
        let keys: Vec<_> = self
            .db
            .iterator(IteratorMode::Start)
            .map(|item| item.map(|(k, _)| k))
            .collect::<Result<_, _>>()?;

        for key in keys {
            self.db.delete(key)?;
        }

        tracing::info!("Cleared all profiles from store");
        Ok(())
    }

    /// Get statistics about stored profiles
    pub fn get_stats(&self) -> Result<StoreStats> {
        let profiles = self.list_profiles()?;

        let total = profiles.len();

        if total == 0 {
            return Ok(StoreStats {
                total_profiles: 0,
                avg_arousal: 0.0,
                avg_confidence: 0.0,
                emotions: vec![],
            });
        }

        let avg_arousal = profiles
            .iter()
            .map(|(_, p)| p.intensity.arousal())
            .sum::<f64>()
            / total as f64;

        let avg_confidence = profiles.iter().map(|(_, p)| p.confidence).sum::<f64>() / total as f64;

        // Count emotions
        let mut emotion_counts: std::collections::HashMap<String, usize> =
            std::collections::HashMap::new();
        for (_, profile) in &profiles {
            if let Some(emotion) = profile.dominant_emotion {
                let name = format!("{:?}", emotion);
                *emotion_counts.entry(name).or_insert(0) += 1;
            }
        }

        let mut emotions: Vec<_> = emotion_counts.into_iter().collect();
        emotions.sort_by(|a, b| b.1.cmp(&a.1));

        Ok(StoreStats {
            total_profiles: total,
            avg_arousal,
            avg_confidence,
            emotions: emotions
                .into_iter()
                .map(|(name, count)| EmotionCount { name, count })
                .collect(),
        })
    }

    fn make_key(path: &str) -> Vec<u8> {
        format!("profile:{}", path).into_bytes()
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StoreStats {
    pub total_profiles: usize,
    pub avg_arousal: f64,
    pub avg_confidence: f64,
    pub emotions: Vec<EmotionCount>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EmotionCount {
    pub name: String,
    pub count: usize,
}

// TODO: Add tests using actual EmotionalIntensity and EmotionalProfile::new()
// Tests temporarily removed during refactoring to use panini-core types

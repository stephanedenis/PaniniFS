//! Dhātu: Emotional Classification System
//!
//! Named after Sanskrit धातु (dhātu) - "root" or "element"
//! Combines Panksepp's affective neuroscience with Sanskrit linguistic roots
//!
//! ## Features
//! - Seven primary emotion classification (Panksepp model)
//! - Sanskrit verbal root (dhātu) association
//! - Automatic file/content emotional profiling
//! - Emotional resonance calculation
//! - Temporal emotional analysis

pub mod classifier;
pub mod emotion;
pub mod profile;
pub mod root;

pub use classifier::DhatuClassifier;
pub use emotion::{EmotionalIntensity, PankseppEmotion};
pub use profile::{EmotionalProfile, EmotionalResonance, ResonanceType};
pub use root::{DhatuCatalog, DhatuRoot};

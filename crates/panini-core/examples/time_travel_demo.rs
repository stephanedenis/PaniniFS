//! Demonstration of Immutable Time-Travel Filesystem
//!
//! This example shows:
//! 1. Creating concepts with versioning
//! 2. Making modifications (Copy-on-Write)
//! 3. Time-travel queries
//! 4. Snapshots
//! 5. Diffs between versions

use chrono::{Duration, Utc};
use panini_core::storage::immutable::{Concept, ConceptId, TemporalIndex, TimelineEvent};
use std::thread;
use std::time::Duration as StdDuration;

fn main() -> anyhow::Result<()> {
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║  Panini-FS: Immutable Time-Travel Filesystem Demo           ║");
    println!("║  Système de Fichiers Immutable avec Voyage Temporel         ║");
    println!("╚══════════════════════════════════════════════════════════════╝");
    println!();

    // Create temporal index
    let mut index = TemporalIndex::new();

    println!("🕐 Step 1: Creating initial concepts");
    println!("─────────────────────────────────────");

    // Create first concept
    let concept1 = Concept::new(
        "project_plan.md".to_string(),
        vec!["atom_abc123".to_string(), "atom_def456".to_string()],
        2048,
        "Alice".to_string(),
        "Initial project plan".to_string(),
    );

    let concept1_id = concept1.id.clone();
    let t0 = concept1.created_at;
    let v1_id = concept1.current_version.clone();

    println!(
        "  ✅ Created: {} (ID: {})",
        concept1.name,
        &concept1.id[..24]
    );
    println!(
        "     Version: {} at {}",
        &v1_id[..24],
        t0.format("%H:%M:%S%.3f")
    );
    println!(
        "     Atoms: {}",
        concept1.get_current_version().unwrap().atoms.len()
    );

    index.add_concept(concept1);

    // Wait a bit for distinguishable timestamps
    thread::sleep(StdDuration::from_millis(100));

    // Create second concept
    let concept2 = Concept::new(
        "technical_spec.md".to_string(),
        vec!["atom_ghi789".to_string()],
        1024,
        "Bob".to_string(),
        "Technical specifications".to_string(),
    );

    let concept2_id = concept2.id.clone();
    let t1 = concept2.created_at;

    println!(
        "  ✅ Created: {} (ID: {})",
        concept2.name,
        &concept2.id[..24]
    );
    println!("     Time: {}", t1.format("%H:%M:%S%.3f"));

    index.add_concept(concept2);

    thread::sleep(StdDuration::from_millis(100));

    // Create snapshot
    println!();
    println!("📸 Step 2: Creating snapshot (before modifications)");
    println!("───────────────────────────────────────────────────");

    let snap1 = index.create_snapshot("Project Initialization".to_string());
    let t_snap1 = snap1.timestamp;

    println!("  ✅ Snapshot: {} (ID: {})", snap1.name, &snap1.id);
    println!("     Concepts captured: {}", snap1.concepts.len());
    println!("     Time: {}", t_snap1.format("%H:%M:%S%.3f"));

    thread::sleep(StdDuration::from_millis(100));

    // Modify first concept
    println!();
    println!("✏️  Step 3: Modifying concepts (Copy-on-Write)");
    println!("──────────────────────────────────────────────");

    let mut concept1 = (*index.get_concept(&concept1_id).unwrap()).clone();
    let v2_id = concept1.add_version(
        vec![
            "atom_abc123".to_string(),
            "atom_def456".to_string(),
            "atom_xyz999".to_string(), // Added new atom
        ],
        3072,
        "Alice".to_string(),
        "Added milestone section".to_string(),
    );
    let t2 = concept1.updated_at;

    println!("  ✅ Modified: {}", concept1.name);
    println!(
        "     New version: {} at {}",
        &v2_id[..24],
        t2.format("%H:%M:%S%.3f")
    );
    println!(
        "     Atoms: {} -> {}",
        concept1.get_version(&v1_id).unwrap().atoms.len(),
        concept1.get_current_version().unwrap().atoms.len()
    );

    index.update_concept(concept1);

    thread::sleep(StdDuration::from_millis(100));

    // Modify again
    let mut concept1 = (*index.get_concept(&concept1_id).unwrap()).clone();
    let v3_id = concept1.add_version(
        vec![
            "atom_abc123".to_string(),
            "atom_xyz999".to_string(), // Removed atom_def456
            "atom_new111".to_string(),
        ],
        2560,
        "Bob".to_string(),
        "Restructured sections".to_string(),
    );
    let t3 = concept1.updated_at;

    println!("  ✅ Modified: {} (again)", concept1.name);
    println!(
        "     New version: {} at {}",
        &v3_id[..24],
        t3.format("%H:%M:%S%.3f")
    );
    println!(
        "     Size: {} bytes",
        concept1.get_current_version().unwrap().size
    );

    index.update_concept(concept1);

    thread::sleep(StdDuration::from_millis(100));

    // Create another snapshot
    let snap2 = index.create_snapshot("After major edits".to_string());
    let t_snap2 = snap2.timestamp;

    println!();
    println!("📸 Step 4: Creating second snapshot");
    println!("───────────────────────────────────");
    println!("  ✅ Snapshot: {} (ID: {})", snap2.name, &snap2.id);
    println!("     Time: {}", t_snap2.format("%H:%M:%S%.3f"));

    // Demonstrate time travel
    println!();
    println!("⏰ Step 5: Time Travel Demonstration");
    println!("────────────────────────────────────");

    println!();
    println!("  🕐 State at t0 (initial creation):");
    let state_t0 = index.get_state_at(t0);
    for (concept_id, version_id) in &state_t0 {
        let concept = index.get_concept(concept_id).unwrap();
        let version = concept.get_version(version_id).unwrap();
        println!(
            "     • {} - v{} ({} atoms)",
            concept.name,
            &version_id[..12],
            version.atoms.len()
        );
    }

    println!();
    println!("  🕑 State at t1 (after second concept):");
    let state_t1 = index.get_state_at(t1);
    println!("     Total concepts: {}", state_t1.len());

    println!();
    println!("  🕒 State at t2 (after first modification):");
    let state_t2 = index.get_state_at(t2);
    for (concept_id, version_id) in &state_t2 {
        let concept = index.get_concept(concept_id).unwrap();
        if &concept.id == &concept1_id {
            let version = concept.get_version(version_id).unwrap();
            println!(
                "     • {} - v{} ({} atoms)",
                concept.name,
                &version_id[..12],
                version.atoms.len()
            );
        }
    }

    println!();
    println!("  🕓 State at t3 (current/latest):");
    let state_t3 = index.get_state_at(t3);
    for (concept_id, version_id) in &state_t3 {
        let concept = index.get_concept(concept_id).unwrap();
        let version = concept.get_version(version_id).unwrap();
        println!(
            "     • {} - v{} ({} atoms, {} bytes)",
            concept.name,
            &version_id[..12],
            version.atoms.len(),
            version.size
        );
    }

    // Show timeline
    println!();
    println!("📜 Step 6: Timeline of Events");
    println!("─────────────────────────────");

    let timeline = index.get_timeline_range(t0, t3 + Duration::seconds(1));
    for (timestamp, event) in timeline {
        match event {
            TimelineEvent::ConceptCreated {
                concept_id,
                version_id,
            } => {
                let concept = index.get_concept(concept_id).unwrap();
                println!(
                    "  🆕 {} - Created: {} (v{})",
                    timestamp.format("%H:%M:%S%.3f"),
                    concept.name,
                    &version_id[..12]
                );
            }
            TimelineEvent::ConceptModified {
                concept_id,
                version_id,
                previous_version,
            } => {
                let concept = index.get_concept(concept_id).unwrap();
                let version = concept.get_version(version_id).unwrap();
                println!(
                    "  ✏️  {} - Modified: {} (v{} -> v{})",
                    timestamp.format("%H:%M:%S%.3f"),
                    concept.name,
                    &previous_version[..12],
                    &version_id[..12]
                );
                println!("        \"{}\"", version.message);
            }
            TimelineEvent::SnapshotCreated { snapshot_id } => {
                println!(
                    "  📸 {} - Snapshot: {}",
                    timestamp.format("%H:%M:%S%.3f"),
                    snapshot_id
                );
            }
        }
    }

    // Show version diff
    println!();
    println!("🔍 Step 7: Version Diff Analysis");
    println!("─────────────────────────────────");

    let concept1 = index.get_concept(&concept1_id).unwrap();

    if let Some(diff_v1_v2) = concept1.diff(&v1_id, &v2_id) {
        println!();
        println!("  📊 Diff: v{} → v{}", &v1_id[..12], &v2_id[..12]);
        println!("     Added atoms: {}", diff_v1_v2.added_atoms.len());
        for atom in &diff_v1_v2.added_atoms {
            println!("       + {}", atom);
        }
        println!("     Removed atoms: {}", diff_v1_v2.removed_atoms.len());
        println!("     Size change: {:+} bytes", diff_v1_v2.size_change);
    }

    if let Some(diff_v2_v3) = concept1.diff(&v2_id, &v3_id) {
        println!();
        println!("  📊 Diff: v{} → v{}", &v2_id[..12], &v3_id[..12]);
        println!("     Added atoms: {}", diff_v2_v3.added_atoms.len());
        for atom in &diff_v2_v3.added_atoms {
            println!("       + {}", atom);
        }
        println!("     Removed atoms: {}", diff_v2_v3.removed_atoms.len());
        for atom in &diff_v2_v3.removed_atoms {
            println!("       - {}", atom);
        }
        println!("     Size change: {:+} bytes", diff_v2_v3.size_change);
    }

    // Show version history
    println!();
    println!("📚 Step 8: Version History");
    println!("──────────────────────────");

    let history = concept1.get_history();
    println!();
    println!("  📖 History of: {}", concept1.name);
    for (i, version) in history.iter().enumerate() {
        println!();
        println!(
            "    {} Version {} ({})",
            if i == history.len() - 1 { "→" } else { " " },
            i + 1,
            &version.version_id[..24]
        );
        println!("      Time: {}", version.timestamp.format("%H:%M:%S%.3f"));
        println!("      Author: {}", version.author);
        println!("      Message: \"{}\"", version.message);
        println!(
            "      Atoms: {}, Size: {} bytes",
            version.atoms.len(),
            version.size
        );
        if let Some(parent) = &version.parent {
            println!("      Parent: {}", &parent[..24]);
        }
    }

    // Demonstrate revert
    println!();
    println!("↩️  Step 9: Revert Demonstration");
    println!("────────────────────────────────");

    let mut concept1 = (*index.get_concept(&concept1_id).unwrap()).clone();
    println!();
    println!("  🔙 Reverting {} to version 1...", concept1.name);

    let v4_id = concept1.revert_to(&v1_id, "Alice".to_string())?;
    println!("  ✅ Reverted! New version: {}", &v4_id[..24]);

    let v4 = concept1.get_current_version().unwrap();
    let v1 = concept1.get_version(&v1_id).unwrap();

    println!("     Content matches v1: {}", v4.atoms == v1.atoms);
    println!("     Version count: {}", concept1.versions.len());

    index.update_concept(concept1);

    // Summary
    println!();
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║  Summary / Résumé                                            ║");
    println!("╚══════════════════════════════════════════════════════════════╝");
    println!();

    let all_concepts = index.get_all_concepts();
    let total_versions: usize = all_concepts.iter().map(|c| c.versions.len()).sum();
    let snapshots = index.get_snapshots();

    println!("📊 System Statistics:");
    println!("   • Total concepts: {}", all_concepts.len());
    println!("   • Total versions: {}", total_versions);
    println!("   • Total snapshots: {}", snapshots.len());
    println!(
        "   • Timeline events: {}",
        index
            .get_timeline_range(
                Utc::now() - Duration::hours(1),
                Utc::now() + Duration::hours(1)
            )
            .len()
    );
    println!();

    println!("✨ Key Features Demonstrated:");
    println!("   ✅ Copy-on-Write: Every modification creates new version");
    println!("   ✅ Immutability: Old versions never change");
    println!("   ✅ Time Travel: Query state at any point in time");
    println!("   ✅ Snapshots: Capture entire filesystem state");
    println!("   ✅ Diffs: Compare any two versions");
    println!("   ✅ Revert: Restore old content (creates new version)");
    println!("   ✅ Timeline: Chronological history of all changes");
    println!();

    println!("🎯 Perfect Foundation For:");
    println!("   • FUSE filesystem with temporal navigation");
    println!("   • Web UI with timeline visualization");
    println!("   • Git-like branching and merging");
    println!("   • Atomic operations (all-or-nothing commits)");
    println!("   • Instant rollback and disaster recovery");
    println!();

    Ok(())
}

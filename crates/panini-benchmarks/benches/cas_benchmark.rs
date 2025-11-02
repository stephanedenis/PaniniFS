use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use std::collections::HashMap;

// Simplified benchmarks for hash-based storage operations
fn bench_hash_computation(c: &mut Criterion) {
    use sha2::{Sha256, Digest};
    
    let mut group = c.benchmark_group("Hash Computation");
    
    let sizes = vec![
        ("small_100B", vec![b'x'; 100]),
        ("medium_1KB", vec![b'x'; 1024]),
        ("large_10KB", vec![b'x'; 10 * 1024]),
        ("xlarge_100KB", vec![b'x'; 100 * 1024]),
    ];
    
    for (name, content) in sizes.iter() {
        group.bench_with_input(BenchmarkId::from_parameter(name), content, |b, content| {
            b.iter(|| {
                let mut hasher = Sha256::new();
                hasher.update(black_box(content));
                format!("{:x}", hasher.finalize())
            });
        });
    }
    
    group.finish();
}

fn bench_dedup_lookup(c: &mut Criterion) {
    let mut group = c.benchmark_group("Dedup Lookup");
    
    // Simulate dedup index
    let mut index: HashMap<String, usize> = HashMap::new();
    for i in 0..1000 {
        index.insert(format!("hash_{:064x}", i), i);
    }
    
    let existing_key = "hash_0000000000000000000000000000000000000000000000000000000000000100";
    let missing_key = "hash_ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";
    
    group.bench_function("existing_key", |b| {
        b.iter(|| {
            black_box(index.get(black_box(existing_key)))
        });
    });
    
    group.bench_function("missing_key", |b| {
        b.iter(|| {
            black_box(index.get(black_box(missing_key)))
        });
    });
    
    group.finish();
}

fn bench_json_serialization(c: &mut Criterion) {
    use serde::{Deserialize, Serialize};
    
    #[derive(Serialize, Deserialize)]
    struct MockAtom {
        hash: String,
        size: usize,
        refs: Vec<String>,
    }
    
    let atom = MockAtom {
        hash: "a".repeat(64),
        size: 1024,
        refs: vec!["ref1".to_string(), "ref2".to_string()],
    };
    
    c.bench_function("json_serialize_atom", |b| {
        b.iter(|| {
            serde_json::to_string(black_box(&atom)).unwrap()
        });
    });
    
    let json = serde_json::to_string(&atom).unwrap();
    c.bench_function("json_deserialize_atom", |b| {
        b.iter(|| {
            serde_json::from_str::<MockAtom>(black_box(&json)).unwrap()
        });
    });
}

criterion_group!(
    benches,
    bench_hash_computation,
    bench_dedup_lookup,
    bench_json_serialization
);
criterion_main!(benches);

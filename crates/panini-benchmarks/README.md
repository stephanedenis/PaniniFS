# Panini Performance Benchmarks

Performance benchmarks for Panini filesystem components using Criterion.

## Running Benchmarks

### All benchmarks
```bash
cargo bench --package panini-benchmarks
```

### Specific benchmark suite
```bash
cargo bench --package panini-benchmarks --bench cas_benchmark
cargo bench --package panini-benchmarks --bench dhatu_benchmark
```

### View HTML reports
```bash
cargo bench --package panini-benchmarks
open target/criterion/report/index.html
```

## Benchmark Suites

### CAS Benchmarks (`cas_benchmark.rs`)

#### Hash Computation
- Measures SHA-256 hashing speed across different content sizes
- Sizes: 100B, 1KB, 10KB, 100KB
- Baseline for content addressing performance

#### Dedup Lookup
- HashMap lookup performance for deduplication index
- Tests both cache hits and misses
- Simulates real-world dedup checking

#### JSON Serialization
- Measures atom metadata serialization/deserialization
- Critical for storage I/O performance
- Identifies JSON overhead

### Dhātu Benchmarks (`dhatu_benchmark.rs`)

#### Text Classification
- Emotional classification across different text lengths
- Short (~10 chars), Medium (~100 chars), Long (~500 chars)
- Core Dhātu system performance

#### Emotion Calculation
- Dominant emotion detection speed
- Arousal calculation (sum of intensities)
- Validates algorithmic efficiency

#### Resonance Calculation
- Measures profile-to-profile similarity computation
- Cosine similarity of emotional vectors
- Important for search/recommendation features

## Performance Targets

### Hash Computation
- **Target**: < 1μs for 1KB content
- **Acceptable**: < 10μs for 100KB content

### Dedup Lookup
- **Target**: < 100ns for hash table lookup
- **Critical**: No significant difference between hits/misses

### Text Classification
- **Target**: < 1ms for medium text (100 chars)
- **Acceptable**: < 10ms for long text (500 chars)

### Emotion Calculations
- **Target**: < 100ns for arousal/dominant
- **Critical**: O(1) complexity maintained

### Resonance
- **Target**: < 1μs per pair
- **Acceptable**: < 10μs for complex profiles

## Continuous Benchmarking

Benchmarks should be run:
1. Before major refactorings
2. After optimization changes
3. When adding new features
4. During performance investigations

## Comparing Results

```bash
# Baseline before changes
cargo bench --package panini-benchmarks > baseline.txt

# Make changes...

# Compare after changes
cargo bench --package panini-benchmarks > optimized.txt
```

Use Criterion's built-in comparison features to detect regressions automatically.

## Adding New Benchmarks

1. Create new file in `benches/`
2. Add `[[bench]]` section to `Cargo.toml`
3. Follow Criterion best practices:
   - Use `black_box()` to prevent optimization
   - Measure realistic workloads
   - Include setup/teardown in groups
   - Use meaningful names

## Notes

- Benchmarks run in `release` mode with optimizations
- Results vary by hardware - use relative comparisons
- Criterion automatically detects outliers
- HTML reports include confidence intervals
- Microbenchmarks may not reflect real-world performance

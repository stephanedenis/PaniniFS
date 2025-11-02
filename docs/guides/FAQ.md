# Panini FAQ - Frequently Asked Questions

## General Questions

### What is Panini?

Panini is a content-addressed filesystem with emotional intelligence. It combines:
- **Deduplication**: Automatic detection and elimination of duplicate content
- **Emotional Classification**: Dhātu system based on Panksepp's affective neuroscience
- **FUSE Filesystem**: Browse content as a virtual filesystem
- **REST API**: Programmatic access to all features

### Why "Panini"?

Named after the Sanskrit grammarian Pāṇini, whose work on linguistic structure inspired our approach to decomposing and analyzing content at the atomic level.

### What makes Panini different from other filesystems?

1. **Content-Addressed**: Files stored by content hash, enabling automatic dedup
2. **Emotional Intelligence**: Dhātu system classifies content emotionally
3. **Atomic Decomposition**: Files broken into reusable atoms
4. **Time-Travel**: Access any historical state via content addressing
5. **Semantic Organization**: Concept-based hierarchies, not just folders

## Installation & Setup

### What operating systems are supported?

- **Linux**: Fully supported (Ubuntu, Fedora, Arch, Debian)
- **macOS**: Experimental (FUSE for macOS required)
- **Windows**: Not currently supported (WSL2 recommended)

### Do I need root/admin privileges?

No! Panini runs entirely in userspace via FUSE. You only need:
- Permission to mount FUSE filesystems (usually automatic)
- Write access to your storage directory

### How much disk space do I need?

Minimum 1GB, but more is better. Storage usage depends on:
- Number of unique atoms (deduplicated)
- RocksDB indices (~10% overhead)
- Dhātu emotional profile database
- Metadata and search indices

### Can I use existing storage?

Yes! Point `PANINI_STORAGE` to any directory. Panini will:
- Create necessary subdirectories (`atoms/`, `index/`, `dhatu/`)
- Build indices incrementally
- Never modify your original files (uses CAS storage)

## Usage Questions

### How does deduplication work?

1. File uploaded → SHA-256 hash computed
2. Hash checked against existing atoms
3. If duplicate: reference existing atom (no new storage)
4. If unique: store atom once

Example: 1000 copies of the same 10MB file = 10MB storage (not 10GB)

### What is the Dhātu emotional system?

Based on Jaak Panksepp's 7 primary emotional systems:
- **SEEKING** (icchā): Exploration, curiosity, anticipation
- **FEAR** (bhaya): Anxiety, threat avoidance
- **RAGE** (krodha): Anger, frustration
- **LUST** (kāma): Sexual desire, erotic arousal
- **CARE** (karuṇā): Nurturing, compassion, bonding
- **PANIC/GRIEF** (śoka): Separation distress, loneliness
- **PLAY** (krīḍā): Joyful engagement, social bonding

Files are classified based on content analysis, producing an emotional intensity profile.

### How accurate is emotional classification?

Current classifier uses:
- Keyword matching with dhātu root associations
- Contextual analysis
- Sanskrit etymology
- ~70-80% accuracy on clear emotional content

Future versions will add:
- Machine learning models
- Context-aware analysis
- Multi-language support

### Can I disable emotional classification?

Yes! Classification is optional:
- API: Don't use `/api/dhatu/*` endpoints
- FUSE: `/concepts/` tree won't populate without classifications
- Storage: Dhātu database only grows if you use it

### What file types are supported?

**Fully Supported:**
- Text: .txt, .md, .json, .yaml, .toml
- Binary: Any file (stored as opaque blobs)

**Partial Support:**
- Images: PNG, JPEG (metadata extracted)
- Videos: MP4 (atomic decomposition)
- Archives: .zip, .tar.gz (unpacked on request)

**Planned:**
- PDF text extraction
- Audio transcription
- Code semantic analysis

### How does the FUSE filesystem work?

Panini presents a virtual filesystem structure:

```
/tmp/panini-mount/
├── atoms/          # Individual content atoms by hash
├── concepts/       # Semantic concept tree
├── index/          # Search index
└── metadata/       # File metadata and references
```

All operations are read-only (safety). To add content, use the API.

### Can I write files through FUSE?

Currently no (read-only). This prevents:
- Accidental data corruption
- Race conditions with CAS storage
- Inconsistent deduplication

Use the API for uploads: `POST /api/dedup/upload`

Future versions may support write operations with careful transaction handling.

## Performance Questions

### How fast is deduplication?

Typical performance on modern hardware:
- **Hashing**: ~500 MB/s (SHA-256)
- **Dedup Check**: <1ms (hash table lookup)
- **Storage**: Limited by disk I/O

Uploading 100MB file: ~200-500ms (first time), ~1-2ms (duplicate)

### Does caching help?

Yes! LRU cache (Phase 10.6) speeds up:
- Frequently accessed atoms: 10-100x faster
- FUSE reads: No disk I/O for hot content
- API responses: Reduced RocksDB queries

Default cache: 1000 atoms, 100MB max

### How does it scale?

Tested configurations:
- **Small**: 1,000 files, 1GB storage
- **Medium**: 100,000 files, 100GB storage
- **Large**: 1,000,000+ files, 1TB+ storage

Bottlenecks:
- RocksDB index size (scales logarithmically)
- Filesystem inode limits (use XFS or ext4)
- API concurrency (tokio handles 1000s of connections)

### Can I run multiple instances?

Yes, with separate storage directories:

```bash
# Instance 1
PANINI_STORAGE=/tmp/instance1 API_PORT=3030 panini-api &

# Instance 2
PANINI_STORAGE=/tmp/instance2 API_PORT=3031 panini-api &
```

Shared storage is **not** currently supported (locking needed).

## Troubleshooting

### "FUSE mount failed"

**Causes:**
1. FUSE not installed: `sudo apt install fuse3`
2. Permission denied: `sudo usermod -a -G fuse $USER` (then re-login)
3. Mount point doesn't exist: `mkdir /tmp/panini-mount`
4. Already mounted: `fusermount3 -u /tmp/panini-mount`

### "Address already in use" (API)

Another process using port 3030:
```bash
# Use different port
API_PORT=8080 panini-api

# Or kill existing process
lsof -ti:3030 | xargs kill
```

### Slow performance

**Possible causes:**
1. **Cold cache**: First access always slower
2. **Disk I/O**: Use SSD for storage
3. **Debug logging**: Set `RUST_LOG=info` (not `debug`)
4. **Large indices**: Run garbage collection

**Solutions:**
```bash
# Check storage stats
curl http://localhost:3030/api/dedup/stats

# Clear unused atoms (not implemented yet)
# Future: POST /api/dedup/gc
```

### "Out of disk space"

Check actual usage:
```bash
du -sh $PANINI_STORAGE
```

Deduplication saves space but:
- Metadata has overhead (~10%)
- Many unique files = more storage
- RocksDB compaction needed

### Emotional classification seems wrong

Remember:
- Current classifier is rule-based (not ML)
- Works best with clear emotional language
- Sanskrit roots may not match modern usage
- Confidence scores indicate certainty

You can:
- Ignore low-confidence results (< 0.5)
- Add manual tags via API
- Contribute better dhātu root mappings

### Data corruption / inconsistency

**Prevention** (built-in):
- Content addressing (tamper-evident)
- Atomic writes (crash-safe)
- Read-only FUSE (safety)

**Recovery:**
```bash
# Rebuild indices
rm -rf $PANINI_STORAGE/index/*
# Restart API (auto-rebuilds)

# Verify atom integrity
# Future: panini-cli verify
```

## Development Questions

### How can I contribute?

See `CONTRIBUTING.md` for details. Areas needing help:
- Dhātu root improvements (Sanskrit experts!)
- ML-based emotional classification
- Additional file format support
- Performance optimizations
- Documentation

### Where is the code?

- **GitHub**: https://github.com/stephanedenis/Panini-FS
- **Core**: `crates/panini-core/` - Storage, dhātu, indices
- **API**: `crates/panini-api/` - REST endpoints
- **FUSE**: `crates/panini-fuse/` - Filesystem
- **CLI**: `crates/panini-cli/` - Command-line tools

### What license?

[Specify license here - likely MIT or Apache 2.0]

### Can I use this in production?

Current status: **Beta**
- Core features stable
- API may change
- Backup important data
- Test thoroughly before production use

Recommended for:
- ✅ Personal projects
- ✅ Research and experimentation
- ✅ Non-critical workflows
- ⚠️ Production with backups
- ❌ Mission-critical systems (yet)

### What's the roadmap?

**Near-term** (v1.0):
- ✅ Phase 10.1-10.6: Core features complete
- 🏗️ Phase 10.7-10.8: Documentation & polish

**Medium-term** (v1.1-1.2):
- Machine learning emotion classifier
- Write support in FUSE
- Distributed storage backend (S3)
- Web UI improvements

**Long-term** (v2.0+):
- Multi-node clustering
- Real-time collaboration
- Advanced semantic search
- Plugin system

## Contact & Support

- **Issues**: https://github.com/stephanedenis/Panini-FS/issues
- **Discussions**: https://github.com/stephanedenis/Panini-FS/discussions
- **Email**: [project email]
- **Chat**: [Discord/Matrix link if available]

---

**Didn't find your answer?** Open an issue or ask in Discussions!

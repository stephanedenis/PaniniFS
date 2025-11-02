# Panini Quick Start Guide

Get up and running with Panini in **15 minutes**! This guide covers the essential steps to start using Panini's content-addressed filesystem, deduplication, and emotional classification features.

## Prerequisites

- **Rust**: version 1.70 or later
- **FUSE**: `fuse3` library installed
- **Storage**: At least 1GB free disk space
- **OS**: Linux (tested on Ubuntu, Fedora, Arch)

### Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install fuse3 libfuse3-dev pkg-config build-essential
```

**Fedora:**
```bash
sudo dnf install fuse3 fuse3-devel pkgconfig
```

**Arch:**
```bash
sudo pacman -S fuse3 pkgconf
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/stephanedenis/Panini-FS.git
cd Panini-FS
```

### 2. Build Release Binaries

```bash
cargo build --release
```

This builds:
- `panini-mount` - FUSE filesystem
- `panini-api` - REST API server
- `panini-cli` - Command-line interface

Binaries will be in `target/release/`

## Quick Usage

### Set up Storage

```bash
export PANINI_STORAGE="$HOME/.panini/storage"
mkdir -p "$PANINI_STORAGE"
```

### Option A: Use the REST API

#### 1. Start the API Server

```bash
PANINI_STORAGE="$HOME/.panini/storage" ./target/release/panini-api
```

Server starts on `http://localhost:3030`

#### 2. Upload Files (Deduplication)

```bash
# Upload a file
curl -X POST http://localhost:3030/api/dedup/upload \
  -F "file=@/path/to/your/file.txt"

# Response: {"hash":"abc123...","size":1024,"is_duplicate":false}
```

#### 3. Get Storage Stats

```bash
curl http://localhost:3030/api/dedup/stats | jq
```

#### 4. Classify Text Emotionally (Dhātu)

```bash
curl -X POST http://localhost:3030/api/dhatu/classify \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/test/example.txt",
    "text": "This is an exciting journey of exploration and discovery!"
  }' | jq
```

Response shows emotional profile with Panksepp's 7 emotions (Seeking, Fear, Rage, Lust, Care, Panic/Grief, Play).

### Option B: Use the FUSE Filesystem

#### 1. Create Mount Point

```bash
mkdir -p /tmp/panini-mount
```

#### 2. Mount Filesystem

```bash
PANINI_STORAGE="$HOME/.panini/storage" ./target/release/panini-mount /tmp/panini-mount
```

#### 3. Browse Content

```bash
cd /tmp/panini-mount
ls -la
```

You'll see:
- `/atoms/` - Individual content atoms
- `/concepts/` - Semantic concept tree
- `/index/` - Search index
- `/metadata/` - File metadata

#### 4. Unmount

```bash
fusermount3 -u /tmp/panini-mount
```

### Option C: Use the Web UI

#### 1. Start API Server

```bash
PANINI_STORAGE="$HOME/.panini/storage" ./target/release/panini-api
```

#### 2. Start Web UI

```bash
cd web-ui
npm install
npm run dev
```

#### 3. Open Browser

Navigate to `http://localhost:5173`

Features:
- **Deduplication Dashboard**: Upload files, view stats, search atoms
- **Dhātu Dashboard**: Classify text, view emotional profiles, calculate resonance
- **Real-time Updates**: Live statistics and visualizations

## Common Tasks

### Check Storage Usage

```bash
curl http://localhost:3030/api/dedup/stats | jq '{
  total_atoms: .total_atoms,
  total_size_mb: (.total_size / 1048576 | round),
  dedup_ratio: .dedup_ratio
}'
```

### Search Atoms by Content

```bash
curl "http://localhost:3030/api/dedup/search?query=example" | jq
```

### Find Files by Emotion

```bash
curl "http://localhost:3030/api/dhatu/search?emotion=Seeking" | jq
```

### Calculate Emotional Resonance

```bash
curl "http://localhost:3030/api/dhatu/resonance?path_a=/file1.txt&path_b=/file2.txt" | jq
```

## Environment Variables

- `PANINI_STORAGE`: Storage directory path (required)
- `RUST_LOG`: Logging level (`info`, `debug`, `trace`)
- `API_PORT`: API server port (default: 3030)

Example with debugging:
```bash
RUST_LOG=debug PANINI_STORAGE=/tmp/test cargo run --bin panini-api
```

## Next Steps

- **Tutorial**: Comprehensive examples → `docs/guides/TUTORIAL.md`
- **Best Practices**: Optimization tips → `docs/guides/BEST_PRACTICES.md`
- **FAQ**: Common questions → `docs/guides/FAQ.md`
- **API Reference**: Full endpoint documentation → `docs/api/`

## Troubleshooting

### "Permission denied" when mounting

```bash
# Add yourself to fuse group
sudo usermod -a -G fuse $USER
# Log out and back in
```

### "Address already in use" for API

```bash
# Change port
API_PORT=8080 ./target/release/panini-api
```

### Storage corruption

```bash
# Clear storage and start fresh
rm -rf "$PANINI_STORAGE"/*
```

## Getting Help

- **Issues**: https://github.com/stephanedenis/Panini-FS/issues
- **Discussions**: https://github.com/stephanedenis/Panini-FS/discussions
- **Documentation**: https://paninifs.org/docs

---

**You're now ready to use Panini!** 🎉

Try uploading some files and exploring the emotional classification system. The deduplication will automatically save storage space for duplicate content.

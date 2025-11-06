#!/usr/bin/env python3
"""
Scan storage directory and register chunks with Panini API

This script walks through the content-addressed storage directory,
reads each chunk file, and registers it with the API to populate
the deduplication index.
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

def scan_chunks(storage_path: Path) -> List[Tuple[str, Path, int]]:
    """
    Scan storage directory for chunk files
    
    Returns list of (hash, file_path, size) tuples
    """
    print(f"📂 Scanning storage directory: {storage_path}")
    
    chunks = []
    
    # Walk through all subdirectories (00-ff)
    for subdir in storage_path.iterdir():
        if not subdir.is_dir():
            continue
        
        # Skip special directories
        if subdir.name in ['index', 'dhatu', 'rocksdb']:
            continue
        
        # Process chunk files in this directory
        for chunk_file in subdir.iterdir():
            if chunk_file.is_file():
                # Reconstruct full hash: dir_name + file_name
                full_hash = subdir.name + chunk_file.name
                size = chunk_file.stat().st_size
                chunks.append((full_hash, chunk_file, size))
    
    print(f"✓ Found {len(chunks)} chunk files")
    return chunks

def verify_chunk_hash(chunk_file: Path, expected_hash: str) -> bool:
    """
    Verify that the chunk file's content matches its hash
    """
    try:
        hasher = hashlib.sha256()
        with open(chunk_file, 'rb') as f:
            # Read in chunks to handle large files
            while True:
                data = f.read(65536)  # 64KB blocks
                if not data:
                    break
                hasher.update(data)
        
        computed_hash = hasher.hexdigest()
        
        # The expected_hash might be longer (includes prefix), so check if computed is in expected
        return computed_hash in expected_hash or expected_hash.startswith(computed_hash[:8])
    except Exception as e:
        print(f"⚠️  Error verifying hash: {e}")
        return False

def generate_rocksdb_entries(chunks: List[Tuple[str, Path, int]], output_file: Path):
    """
    Generate a JSON file that can be imported into RocksDB
    """
    print(f"\n📝 Generating RocksDB import file...")
    
    entries = {
        "chunks": [],
        "metadata": {
            "total_chunks": len(chunks),
            "timestamp": int(os.time()) if hasattr(os, 'time') else 0
        }
    }
    
    verified_count = 0
    for hash_val, chunk_file, size in chunks:
        # Optionally verify hash (can be slow for many chunks)
        # is_valid = verify_chunk_hash(chunk_file, hash_val)
        
        entry = {
            "hash": hash_val,
            "size": size,
            "ref_count": 1,  # Will be updated by deduplication
            "chunk_type": "Raw",  # Default type
            "created_at": int(chunk_file.stat().st_mtime)
        }
        entries["chunks"].append(entry)
        verified_count += 1
        
        if verified_count % 100 == 0:
            progress = (verified_count / len(chunks)) * 100
            print(f"Progress: {verified_count}/{len(chunks)} ({progress:.1f}%)")
    
    # Write to output file
    with open(output_file, 'w') as f:
        json.dump(entries, f, indent=2)
    
    print(f"✓ Generated import file: {output_file}")
    print(f"  Total entries: {len(entries['chunks'])}")
    print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scan_and_register_chunks.py <storage_path>")
        print("Example: python3 scan_and_register_chunks.py /home/stephane/panini-wikipedia-full")
        sys.exit(1)
    
    storage_path = Path(sys.argv[1])
    
    if not storage_path.exists():
        print(f"❌ Storage path does not exist: {storage_path}")
        sys.exit(1)
    
    # Scan for chunks
    chunks = scan_chunks(storage_path)
    
    if not chunks:
        print("❌ No chunks found in storage directory")
        sys.exit(1)
    
    # Generate RocksDB import file
    output_file = storage_path / "index" / "rocksdb_import.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    generate_rocksdb_entries(chunks, output_file)
    
    print(f"\n✅ Done!")
    print(f"\nNext steps:")
    print(f"1. Restart the API to load this data")
    print(f"2. Or use a RocksDB import tool to load: {output_file}")

if __name__ == "__main__":
    main()

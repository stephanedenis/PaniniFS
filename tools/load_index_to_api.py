#!/usr/bin/env python3
"""
Load rebuilt_index.json into Panini API

This script reads the rebuilt index and populates the API's storage
by registering all chunks through the dedup endpoint.
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, List

def load_index(index_path: Path) -> Dict:
    """Load the rebuilt index JSON file"""
    print(f"📂 Loading index from: {index_path}")
    with open(index_path, 'r') as f:
        data = json.load(f)
    print(f"✓ Loaded {data['total_chunks']} chunks")
    return data

def register_chunk_with_api(api_url: str, storage_path: Path, chunk_data: Dict) -> bool:
    """Register a chunk with the API by reading its file"""
    chunk_hash = chunk_data['hash']
    
    # Content-addressed path: first 2 chars = directory, rest = filename
    dir_name = chunk_hash[:2]
    file_name = chunk_hash[2:]
    chunk_file = storage_path / dir_name / file_name
    
    if not chunk_file.exists():
        print(f"⚠️  Chunk file not found: {chunk_file}")
        return False
    
    try:
        # Read chunk data
        with open(chunk_file, 'rb') as f:
            chunk_content = f.read()
        
        # Upload to API (this will trigger deduplication)
        response = requests.post(
            f"{api_url}/api/dedup/upload",
            files={'file': ('chunk', chunk_content)},
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  API returned {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"⚠️  Error processing chunk {chunk_hash[:12]}: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 load_index_to_api.py <storage_path> <api_url>")
        print("Example: python3 load_index_to_api.py /home/stephane/panini-wikipedia-full http://localhost:3000")
        sys.exit(1)
    
    storage_path = Path(sys.argv[1])
    api_url = sys.argv[2].rstrip('/')
    
    index_path = storage_path / "index" / "rebuilt_index.json"
    
    if not index_path.exists():
        print(f"❌ Index file not found: {index_path}")
        sys.exit(1)
    
    # Load index
    index_data = load_index(index_path)
    chunks = index_data['chunks']
    total = len(chunks)
    
    print(f"\n🚀 Starting upload of {total} chunks to {api_url}...")
    print(f"📁 Storage path: {storage_path}\n")
    
    # Check API health
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not healthy: {response.status_code}")
            sys.exit(1)
        print("✓ API is healthy\n")
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        sys.exit(1)
    
    # Process chunks in batches
    success_count = 0
    batch_size = 100
    
    for i, chunk in enumerate(chunks, 1):
        if register_chunk_with_api(api_url, storage_path, chunk):
            success_count += 1
        
        # Progress indicator
        if i % batch_size == 0:
            progress = (i / total) * 100
            print(f"Progress: {i}/{total} ({progress:.1f}%) - {success_count} successful")
    
    print(f"\n✅ Completed!")
    print(f"   Successful: {success_count}/{total}")
    print(f"   Failed: {total - success_count}")
    
    # Verify final stats
    print(f"\n📊 Checking final API stats...")
    try:
        response = requests.get(f"{api_url}/api/dedup/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   Unique chunks: {stats.get('unique_chunks', 0)}")
            print(f"   Dedup ratio: {stats.get('dedup_ratio', 0):.2%}")
    except Exception as e:
        print(f"⚠️  Could not fetch stats: {e}")

if __name__ == "__main__":
    main()

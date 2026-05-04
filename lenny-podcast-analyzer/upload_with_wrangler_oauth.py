#!/usr/bin/env python3
"""
Use wrangler CLI to upload vectors with OAuth token.
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")
BATCH_SIZE = 32

def create_vectors_ndjson():
    """Create NDJSON file with padded embeddings."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Please install sentence-transformers: pip install sentence-transformers")
        sys.exit(1)

    print(f"Loading embedding model: all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    output_file = Path("data/vectorize/vectors_local.ndjson")
    
    print(f"Processing segments and creating vectors...")
    
    with SEGMENTS_FILE.open("r", encoding="utf-8") as infile, \
         output_file.open("w", encoding="utf-8") as outfile:
        
        batch = []
        for line in infile:
            if line.strip():
                batch.append(json.loads(line))
                
                if len(batch) >= BATCH_SIZE:
                    process_batch(model, batch, outfile)
                    batch = []
        
        if batch:
            process_batch(model, batch, outfile)
    
    print(f"\n✅ Created: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    return output_file

def process_batch(model, batch, outfile):
    """Process a batch of segments."""
    texts = [item["text"] for item in batch]
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    for item, embedding in zip(batch, embeddings):
        # Pad to 1536 dimensions
        embedding_list = embedding.tolist()
        if len(embedding_list) < 1536:
            embedding_list.extend([0.0] * (1536 - len(embedding_list)))
        
        vector_record = {
            "id": item["id"],
            "values": embedding_list,
            "metadata": item["metadata"]
        }
        
        outfile.write(json.dumps(vector_record) + "\n")

def main():
    """Main entry point."""
    # Create vectors file
    vectors_file = create_vectors_ndjson()
    
    # Use wrangler to upload
    print("\n🚀 Uploading to Vectorize using wrangler...")
    
    cmd = [
        "npx", "wrangler", "vectorize", "upsert", "lenny-podcast",
        "--file", str(vectors_file),
        "--format", "json"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\n✅ Upload successful!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Upload failed!")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

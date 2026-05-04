#!/usr/bin/env python3
"""
Convert JSONL segments to Vectorize NDJSON format.
Each line should contain: id, values (embedding), and metadata.
"""

import json
from pathlib import Path

SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")
OUTPUT_FILE = Path("data/vectorize/vectors.ndjson")

def convert_to_ndjson():
    """Convert segments to Vectorize NDJSON format."""
    with SEGMENTS_FILE.open("r", encoding="utf-8") as infile, \
         OUTPUT_FILE.open("w", encoding="utf-8") as outfile:
        
        for line in infile:
            segment = json.loads(line)
            
            # Vectorize NDJSON format: {"id": "...", "values": [...], "metadata": {...}}
            # Note: values field will be added by embed_and_upsert.py
            vector_record = {
                "id": segment["id"],
                "metadata": segment["metadata"]
            }
            
            outfile.write(json.dumps(vector_record) + "\n")
    
    print(f"Converted {SEGMENTS_FILE} to {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    convert_to_ndjson()

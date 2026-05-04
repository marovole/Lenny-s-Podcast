#!/usr/bin/env python3
"""
Upload segments to Cloudflare Vectorize using Wrangler.
This is a simpler approach that uses wrangler CLI directly.
"""

import subprocess
import json
import os
from pathlib import Path

SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")

def main():
    if not SEGMENTS_FILE.exists():
        print(f"Error: {SEGMENTS_FILE} not found")
        print("Run normalize_segments.py first")
        return
    
    print(f"Uploading {SEGMENTS_FILE} to Vectorize...")
    print("\nTo upload, run:")
    print(f"  npx wrangler vectorize upsert lenny-podcast --file={SEGMENTS_FILE}")
    print("\nOr use the batch upload script with proper API token")

if __name__ == "__main__":
    main()

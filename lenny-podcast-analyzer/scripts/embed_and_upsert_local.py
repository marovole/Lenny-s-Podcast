#!/usr/bin/env python3
"""
Generate embeddings using local sentence-transformers model (FREE).
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Iterator

try:
    from sentence_transformers import SentenceTransformer
    import requests
except ImportError:
    print("Please install dependencies: pip install sentence-transformers requests")
    sys.exit(1)

# Configuration
SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")
BATCH_SIZE = 32  # Smaller batch for local model
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and effective

# Load the model
print(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

def load_segments() -> Iterator[dict]:
    """Load segments from JSONL file."""
    with SEGMENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def upsert_vectors(endpoint: str, headers: dict, vectors: list[dict]) -> None:
    """Upsert vectors to Cloudflare Vectorize."""
    # Vectorize expects NDJSON format for upsert
    ndjson_body = "\n".join(json.dumps(v) for v in vectors)

    response = requests.post(
        endpoint,
        headers={**headers, "Content-Type": "application/x-ndjson"},
        data=ndjson_body,
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Vectorize upsert failed: {result}")

def main():
    """Main entry point."""
    # Validate environment
    account_id = os.environ.get("CF_ACCOUNT_ID")
    cf_api_token = os.environ.get("CF_API_TOKEN")
    index_name = os.environ.get("VECTORIZE_INDEX_NAME", "lenny-podcast")

    if not all([account_id, cf_api_token]):
        print("Error: Missing required environment variables:")
        print("  - CF_ACCOUNT_ID")
        print("  - CF_API_TOKEN")
        sys.exit(1)

    if not SEGMENTS_FILE.exists():
        print(f"Error: Segments file not found: {SEGMENTS_FILE}")
        print("Run normalize_segments.py first.")
        sys.exit(1)

    vectorize_endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/vectorize/v2/indexes/{index_name}/upsert"
    )
    vectorize_headers = {"Authorization": f"Bearer {cf_api_token}"}

    # Process in batches
    batch: list[dict] = []
    total_processed = 0

    print(f"\n🚀 Processing segments from {SEGMENTS_FILE}")
    print(f"Batch size: {BATCH_SIZE}, Model: {MODEL_NAME} (local)")
    print(f"Vector endpoint: {vectorize_endpoint}\n")

    for segment in load_segments():
        batch.append(segment)

        if len(batch) >= BATCH_SIZE:
            process_batch(model, vectorize_endpoint, vectorize_headers, batch)
            total_processed += len(batch)
            print(f"Processed {total_processed} segments...")
            batch = []
            time.sleep(0.5)  # Rate limit protection

    # Process remaining
    if batch:
        process_batch(model, vectorize_endpoint, vectorize_headers, batch)
        total_processed += len(batch)

    print(f"\n✅ Done! Total segments processed: {total_processed}")

def process_batch(
    model,
    vectorize_endpoint: str,
    vectorize_headers: dict,
    batch: list[dict],
) -> None:
    """Process a batch of segments: embed and upsert."""
    texts = [item["text"] for item in batch]
    
    # Generate embeddings using local model
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    # Convert to list format for JSON serialization
    vectors = []
    for item, embedding in zip(batch, embeddings):
        # Pad embedding to 1536 dimensions to match Vectorize index
        embedding_list = embedding.tolist()
        if len(embedding_list) < 1536:
            embedding_list.extend([0.0] * (1536 - len(embedding_list)))

        vectors.append({
            "id": item["id"],
            "values": embedding_list,
            "metadata": item["metadata"],
        })

    upsert_vectors(vectorize_endpoint, vectorize_headers, vectors)

if __name__ == "__main__":
    main()

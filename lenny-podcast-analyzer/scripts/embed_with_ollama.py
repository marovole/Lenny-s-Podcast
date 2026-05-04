#!/usr/bin/env python3
"""
Generate embeddings using Ollama local models (FREE).

Supports models like:
- nomic-embed-text (768 dims, recommended)
- mxbai-embed-large (1024 dims)
- snowflake-arctic-embed (768 dims)

Prerequisites:
    1. Install Ollama: https://ollama.com
    2. Pull model: ollama pull nomic-embed-text
    3. Start Ollama server: ollama serve

Environment Variables:
    CF_ACCOUNT_ID - Cloudflare account ID
    CF_API_TOKEN - Cloudflare API token
    VECTORIZE_INDEX_NAME - Name of the Vectorize index (default: lenny-podcast)
    OLLAMA_MODEL - Ollama embedding model (default: nomic-embed-text)
    OLLAMA_HOST - Ollama server URL (default: http://localhost:11434)
    BATCH_SIZE - Batch size for processing (default: 32)

Usage:
    python scripts/embed_with_ollama.py
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Iterator

try:
    import requests
except ImportError:
    print("Please install dependencies: pip install requests")
    sys.exit(1)

# Configuration
SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "32"))
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
VECTORIZE_DIMS = 1536  # Cloudflare Vectorize index dimension


def check_ollama() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def load_segments() -> Iterator[dict]:
    """Load segments from JSONL file."""
    with SEGMENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def create_embeddings_ollama(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Ollama API."""
    embeddings = []

    # Ollama embedding API processes one text at a time
    for text in texts:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": text,
        }

        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings", json=payload, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        embedding = data.get("embedding", [])

        # Pad or truncate to match Vectorize dimension
        if len(embedding) < VECTORIZE_DIMS:
            embedding.extend([0.0] * (VECTORIZE_DIMS - len(embedding)))
        elif len(embedding) > VECTORIZE_DIMS:
            embedding = embedding[:VECTORIZE_DIMS]

        embeddings.append(embedding)

    return embeddings


def upsert_vectors(endpoint: str, headers: dict, vectors: list[dict]) -> None:
    """Upsert vectors to Cloudflare Vectorize."""
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

    # Check Ollama server
    print(f"Checking Ollama server at {OLLAMA_HOST}...")
    if not check_ollama():
        print("\n❌ Error: Cannot connect to Ollama server!")
        print("\nPlease ensure:")
        print("  1. Ollama is installed: https://ollama.com")
        print(f"  2. Model is pulled: ollama pull {OLLAMA_MODEL}")
        print("  3. Server is running: ollama serve")
        print(f"\nOr set OLLAMA_HOST if running on a different port/host")
        sys.exit(1)

    print(f"✅ Ollama server is running")
    print(f"🤖 Using model: {OLLAMA_MODEL}")

    vectorize_endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/vectorize/v2/indexes/{index_name}/upsert"
    )
    vectorize_headers = {"Authorization": f"Bearer {cf_api_token}"}

    # Process in batches
    batch: list[dict] = []
    total_processed = 0

    print(f"\n🚀 Processing segments from {SEGMENTS_FILE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Vector endpoint: {vectorize_endpoint}\n")

    start_time = time.time()

    for segment in load_segments():
        batch.append(segment)

        if len(batch) >= BATCH_SIZE:
            process_batch(vectorize_endpoint, vectorize_headers, batch)
            total_processed += len(batch)
            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0
            print(f"Processed {total_processed} segments... ({rate:.1f} seg/s)")
            batch = []
            time.sleep(0.1)  # Small delay to avoid overwhelming Ollama

    # Process remaining
    if batch:
        process_batch(vectorize_endpoint, vectorize_headers, batch)
        total_processed += len(batch)

    elapsed = time.time() - start_time
    print(f"\n✅ Done! Total segments processed: {total_processed}")
    print(f"⏱️  Total time: {elapsed:.1f}s ({total_processed / elapsed:.1f} seg/s)")


def process_batch(
    vectorize_endpoint: str,
    vectorize_headers: dict,
    batch: list[dict],
) -> None:
    """Process a batch of segments: embed and upsert."""
    texts = [item["text"] for item in batch]

    # Generate embeddings using Ollama
    embeddings = create_embeddings_ollama(texts)

    # Build vectors
    vectors = []
    for item, embedding in zip(batch, embeddings):
        vectors.append(
            {
                "id": item["id"],
                "values": embedding,
                "metadata": item["metadata"],
            }
        )

    upsert_vectors(vectorize_endpoint, vectorize_headers, vectors)


if __name__ == "__main__":
    main()

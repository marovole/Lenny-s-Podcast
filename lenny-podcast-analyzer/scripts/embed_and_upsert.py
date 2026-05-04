#!/usr/bin/env python3
"""
Generate embeddings and upsert to Cloudflare Vectorize.

Reads normalized segments from data/vectorize/segments.jsonl,
generates embeddings using OpenRouter (free tier available), and upserts to Vectorize.

Environment Variables:
    OPENROUTER_API_KEY - OpenRouter API key (recommended - has free tier)
    OPENAI_API_KEY - OpenAI API key (alternative)
    CF_ACCOUNT_ID - Cloudflare account ID
    CF_API_TOKEN - Cloudflare API token
    VECTORIZE_INDEX_NAME - Name of the Vectorize index (default: lenny-podcast)
    OPENAI_EMBEDDING_MODEL - Embedding model (default: text-embedding-3-small)
    BATCH_SIZE - Batch size for processing (default: 64)

Usage:
    python scripts/embed_and_upsert.py
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
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "64"))
EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def load_segments() -> Iterator[dict]:
    """Load segments from JSONL file."""
    with SEGMENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def create_embeddings(api_key: str, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts using OpenRouter."""
    # Determine API endpoint and headers based on which key is provided
    if os.environ.get("OPENROUTER_API_KEY"):
        endpoint = "https://openrouter.ai/api/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://lennypodcast.com",
            "X-Title": "Lenny Podcast AI Chat",
        }
    else:
        endpoint = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
    }

    response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    return [item["embedding"] for item in data["data"]]


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
    # Validate environment - prefer OpenRouter (has free tier)
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    api_key = openrouter_key or openai_key

    if not api_key:
        print("Error: Missing required environment variable:")
        print("  - OPENROUTER_API_KEY (recommended - has free tier)")
        print("  - OR OPENAI_API_KEY")
        sys.exit(1)

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

    # Determine which API is being used
    api_provider = "OpenRouter" if openrouter_key else "OpenAI"

    vectorize_endpoint = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/vectorize/v2/indexes/{index_name}/upsert"
    )
    vectorize_headers = {"Authorization": f"Bearer {cf_api_token}"}

    # Process in batches
    batch: list[dict] = []
    total_processed = 0

    print(f"Processing segments from {SEGMENTS_FILE}")
    print(f"Batch size: {BATCH_SIZE}, Model: {EMBEDDING_MODEL}")
    print(f"Using API: {api_provider}")

    for segment in load_segments():
        batch.append(segment)

        if len(batch) >= BATCH_SIZE:
            process_batch(api_key, vectorize_endpoint, vectorize_headers, batch)
            total_processed += len(batch)
            print(f"Processed {total_processed} segments...")
            batch = []
            time.sleep(0.5)  # Rate limit protection

    # Process remaining
    if batch:
        process_batch(api_key, vectorize_endpoint, vectorize_headers, batch)
        total_processed += len(batch)

    print(f"Done! Total segments processed: {total_processed}")


def process_batch(
    api_key: str,
    vectorize_endpoint: str,
    vectorize_headers: dict,
    batch: list[dict],
) -> None:
    """Process a batch of segments: embed and upsert."""
    texts = [item["text"] for item in batch]
    embeddings = create_embeddings(api_key, texts)

    vectors = []
    for item, embedding in zip(batch, embeddings):
        vectors.append({
            "id": item["id"],
            "values": embedding,
            "metadata": item["metadata"],
        })

    upsert_vectors(vectorize_endpoint, vectorize_headers, vectors)


if __name__ == "__main__":
    main()

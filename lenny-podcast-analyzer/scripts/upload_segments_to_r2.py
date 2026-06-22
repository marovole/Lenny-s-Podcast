#!/usr/bin/env python3
"""
One-off ops script: upload segment full text from segments.jsonl to R2 bucket lenny-segments.
Object key = metadata.content_key (e.g. ada-chen-rekhi/0.txt). Chat citations fetch content via this key.

Dependencies: pip install boto3
Environment variables:
  CF_ACCOUNT_ID          Cloudflare account ID
  R2_ACCESS_KEY_ID       R2 API token Access Key ID (Object Read & Write)
  R2_SECRET_ACCESS_KEY   R2 API token Secret

Usage:
  python3 scripts/normalize_segments.py
  python3 scripts/upload_segments_to_r2.py
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.config import Config

SEGMENTS_FILE = Path("data/vectorize/segments.jsonl")
BUCKET = "lenny-segments"
WORKERS = 16


def client():
    account_id = os.environ["CF_ACCOUNT_ID"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )


def put(s3, key: str, body: str) -> None:
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )


def load_records() -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    with SEGMENTS_FILE.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            content_key = record["metadata"]["content_key"]
            records.append((content_key, record["content"]))
    return records


def main() -> None:
    missing = [
        name
        for name in ("CF_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        sys.exit(
            "Missing environment variables: "
            + ", ".join(missing)
            + "\nCreate an R2 API token with Object Read & Write at "
            + "https://dash.cloudflare.com → R2 → Manage R2 API Tokens"
        )

    if not SEGMENTS_FILE.exists():
        sys.exit(f"Missing {SEGMENTS_FILE}. Run: python3 scripts/normalize_segments.py")

    s3 = client()
    records = load_records()
    total = len(records)
    print(f"Uploading {total} objects -> r2://{BUCKET} (workers={WORKERS}) ...")

    done = 0
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(put, s3, key, content): key for key, content in records}
        for future in as_completed(futures):
            key = futures[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{key}: {exc}")
            else:
                done += 1
                if done % 2000 == 0:
                    print(f"  {done}/{total}")

    if errors:
        print(f"Failed uploads: {len(errors)}", file=sys.stderr)
        for msg in errors[:10]:
            print(f"  {msg}", file=sys.stderr)
        sys.exit(1)

    print(f"Done: {done}/{total} objects written to r2://{BUCKET}")


if __name__ == "__main__":
    main()

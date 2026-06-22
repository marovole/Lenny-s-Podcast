#!/usr/bin/env python3
"""
Normalize episode segments for vector indexing.

Reads episode JSON files from data/site/en/episodes/ and outputs
a JSONL file suitable for embedding and upserting to Vectorize.

Usage:
    python scripts/normalize_segments.py
"""

import json
import os
from pathlib import Path
from typing import Iterator, TypedDict

# Paths
INPUT_DIR = Path("data/site/en/episodes")
OUTPUT_FILE = Path("data/vectorize/segments.jsonl")

# Skip non-episode files
SKIP_FILES = {"index.json"}


class SegmentRecord(TypedDict):
    id: str
    text: str
    metadata: dict
    content: str


def parse_timestamp(ts: str) -> str:
    """Clean timestamp string (remove trailing parenthesis)."""
    if ts and ts.endswith(")"):
        return ts[:-1]
    return ts or "00:00:00"


def timestamp_to_seconds(ts: str) -> int:
    """Convert HH:MM:SS or MM:SS timestamp string to seconds."""
    cleaned = parse_timestamp(ts)
    parts = cleaned.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(float(parts[1]))
        if len(parts) == 1:
            return int(float(parts[0]))
    except (ValueError, TypeError):
        pass
    return 0


def iter_segments() -> Iterator[SegmentRecord]:
    """Iterate through all segments from all episodes."""
    for path in sorted(INPUT_DIR.glob("*.json")):
        if path.name in SKIP_FILES:
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                episode = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {path}: {e}")
            continue

        slug = episode.get("slug") or path.stem
        title = episode.get("title") or episode.get("episode_name") or path.stem

        segments = episode.get("segments", [])

        for idx, seg in enumerate(segments):
            content = seg.get("content", "").strip()
            if not content:
                continue

            # Build text for embedding (include speaker context)
            speaker = seg.get("speaker", "").strip()
            text_parts = []
            if speaker:
                text_parts.append(f"[{speaker}]")
            text_parts.append(content)
            text = " ".join(text_parts)

            timestamp = parse_timestamp(seg.get("timestamp", ""))
            raw_seconds = seg.get("timestamp_seconds")
            if isinstance(raw_seconds, (int, float)) and raw_seconds > 0:
                timestamp_seconds = int(raw_seconds)
            else:
                timestamp_seconds = timestamp_to_seconds(seg.get("timestamp", ""))

            yield {
                "id": f"{slug}:{idx}",
                "text": text,
                "metadata": {
                    "episode_slug": slug,
                    "episode_title": title,
                    "speaker": speaker,
                    "timestamp": timestamp,
                    "timestamp_seconds": timestamp_seconds,
                    "segment_index": idx,
                    "content_key": f"{slug}/{idx}.txt",
                },
                "content": content,
            }


def main():
    """Main entry point."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        for record in iter_segments():
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} segments to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
One-off ops script: 把 segments.jsonl 里每段全文写入 R2 桶 lenny-segments。
key = metadata.content_key(如 ada-chen-rekhi/0.txt)。chat 引用靠它取原文。

依赖: pip install boto3
环境变量:
  CF_ACCOUNT_ID          Cloudflare 账号 ID
  R2_ACCESS_KEY_ID       R2 API Token 的 Access Key ID(Object Read & Write)
  R2_SECRET_ACCESS_KEY   R2 API Token 的 Secret
运行: python3 scripts/upload_segments_to_r2.py
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
    acc = os.environ["CF_ACCOUNT_ID"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{acc}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )


def put(s3, key, body):
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )


def main():
    if not SEGMENTS_FILE.exists():
        sys.exit(f"找不到 {SEGMENTS_FILE},请先跑 normalize_segments.py")

    s3 = client()
    records = []
    with SEGMENTS_FILE.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                records.append((r["metadata"]["content_key"], r["content"]))

    total = len(records)
    print(f"上传 {total} 个对象 -> r2://{BUCKET} (并发 {WORKERS}) ...")
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(put, s3, k, v): k for k, v in records}
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 2000 == 0:
                print(f"  {done}/{total}")

    print(f"完成: {done}/{total} 个对象已写入 r2://{BUCKET}")


if __name__ == "__main__":
    main()

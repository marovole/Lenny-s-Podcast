#!/bin/bash
export OPENAI_API_KEY="your_openai_key"
export CF_ACCOUNT_ID="b80eef96097fab92f15b574ed5fbb927"
export CF_API_TOKEN="your_cf_api_token"
export VECTORIZE_INDEX_NAME="lenny-podcast"

python3 scripts/embed_and_upsert.py

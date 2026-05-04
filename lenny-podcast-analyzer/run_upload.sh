#!/bin/bash

# Check if OpenRouter API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ Error: OPENROUTER_API_KEY not found"
    echo "Please run: npx wrangler pages secret put OPENROUTER_API_KEY"
    exit 1
fi

# Set Cloudflare account ID
export CF_ACCOUNT_ID="b80eef96097fab92f15b574ed5fbb927"

# For OAuth token, we need to extract it from wrangler
# The script will use wrangler's authentication

echo "🚀 Starting vector upload..."
echo "Account ID: $CF_ACCOUNT_ID"
echo "Using OpenRouter API for embeddings"
echo ""
echo "This will take ~15-20 minutes..."
echo ""

# Run the upload script
python3 scripts/embed_and_upsert.py

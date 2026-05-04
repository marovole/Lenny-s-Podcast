import requests
import json

api_key = "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"

# Test 1: Check models
print("Testing models endpoint...")
resp = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://lennypodcast.com",
        "X-Title": "Lenny Podcast AI Chat"
    }
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    models = resp.json()["data"]
    embedding_models = [m for m in models if "embed" in m["id"].lower()]
    print(f"\nEmbedding models found: {len(embedding_models)}")
    for m in embedding_models[:5]:
        print(f"  - {m['id']}")
else:
    print(f"Error: {resp.text}")

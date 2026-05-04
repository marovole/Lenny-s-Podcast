import requests
import json

api_key = "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"

print("Checking OpenRouter models after credit...")
resp = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://lennypodcast.com",
        "X-Title": "Lenny Podcast AI Chat"
    }
)

if resp.status_code == 200:
    models = resp.json()["data"]
    
    # Look for embedding models
    embedding_models = [m for m in models if "embed" in m["id"].lower()]
    
    print(f"\n✅ Total models available: {len(models)}")
    print(f"\n✅ Embedding models: {len(embedding_models)}")
    
    if embedding_models:
        print("\nAvailable embedding models:")
        for m in embedding_models[:5]:
            print(f"  - {m['id']}")
    else:
        print("\n⚠️ Still no embedding models")
        
    # Also check for OpenAI models
    openai_models = [m for m in models if "openai" in m["id"].lower()]
    print(f"\n✅ OpenAI models: {len(openai_models)}")
    for m in openai_models[:5]:
        print(f"  - {m['id']}")
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)

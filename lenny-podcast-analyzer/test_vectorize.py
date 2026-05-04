import requests

account_id = "b80eef96097fab92f15b574ed5fbb927"
api_token = "QdUPyY8YNx4WyL5rqBpP0fXEm1VBnudTxQH7NMWG"

endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/v2/indexes/lenny-podcast/query"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

payload = {
    "query": [0.1] * 1536,  # Dummy vector
    "topK": 1
}

resp = requests.post(endpoint, headers=headers, json=payload)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

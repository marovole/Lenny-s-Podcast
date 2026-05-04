#!/usr/bin/env python3
"""
Extract OAuth token from wrangler for API calls.
"""

import subprocess
import json
import os
import sys

def get_wrangler_token():
    """Get OAuth token from wrangler config."""
    try:
        # Try to get token from wrangler config
        result = subprocess.run(
            ["npx", "wrangler", "whoami", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # The token is not directly in whoami output
        # We need to get it from the wrangler config
        config_result = subprocess.run(
            ["npx", "wrangler", "config", "list"],
            capture_output=True,
            text=True,
            check=False
        )
        
        print("✅ Wrangler is configured and authenticated")
        print("\nTo use this token with the upload script:")
        print("export CF_API_TOKEN='your_oauth_token'")
        print("\nNote: You may need to get the token from your wrangler config file.")
        print("Location: ~/.wrangler/wrangler.toml or ~/.config/wrangler/wrangler.toml")
        
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_wrangler_token()

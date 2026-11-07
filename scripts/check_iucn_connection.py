#!/usr/bin/env python3
"""Test one authenticated IUCN Red List API v4 request without exposing the key."""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
token = os.environ.get("IUCN_REDLIST_API_TOKEN", "").strip()
if not token:
    sys.exit(
        "No IUCN_REDLIST_API_TOKEN configured. Run 'cp .env.example .env', "
        "edit .env with your fresh IUCN v4 token, and try again."
    )

url = "https://api.iucnredlist.org/api/v4/taxa/scientific_name"
try:
    response = requests.get(
        url,
        params={"genus_name": "Panthera", "species_name": "leo"},
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=20,
    )
    if response.status_code in (401, 403):
        sys.exit(
            f"IUCN rejected the API token (HTTP {response.status_code}). "
            "Check token validity, account access, and permitted API usage."
        )
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict) or "assessments" not in result:
        sys.exit(
            "IUCN responded successfully, but the expected 'assessments' "
            "field was missing. Check the API v4 response format."
        )
    print(
        "IUCN API v4 authentication successful. "
        f"Received {len(result['assessments'])} Panthera leo assessment(s)."
    )
except (requests.RequestException, ValueError, TypeError) as exc:
    sys.exit(f"IUCN connection/test failed: {type(exc).__name__}. "
             "Verify network access, token validity, and the API service.")

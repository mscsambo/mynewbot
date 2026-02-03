import json
from pathlib import Path
import httpx
import sys

tfile = Path("tokens.json")
if not tfile.exists():
    print("tokens.json not found. Run `python main.py --export-tokens` and sign in first.")
    sys.exit(1)

tokens = json.loads(tfile.read_text())
headers = {
    "Authorization": tokens.get("bearer", ""),
    "X-Auth": tokens.get("x_auth", ""),
    "Cookie": tokens.get("cookies", ""),
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://checkout.microsoft365.com",
    "Referer": "https://checkout.microsoft365.com/",
}

with httpx.Client(timeout=30) as client:
    resp = client.get("https://checkout.microsoft365.com/api/verifystudent/status", headers=headers)
    print("HTTP", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
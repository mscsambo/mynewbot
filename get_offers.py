import json
from pathlib import Path
import httpx
import sys
from urllib.parse import urlencode

tfile = Path("tokens.json")
if not tfile.exists():
    print("tokens.json not found. Run `python main.py --export-tokens` and sign in first.")
    sys.exit(1)

tokens = json.loads(tfile.read_text())
headers = {
    "Authorization": tokens.get("bearer", ""),
    "X-Auth": tokens.get("x_auth", ""),
    "Cookie": tokens.get("cookies", ""),
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# You can change params if desired; these match the requests your browser produced
params = {
    "campaign": "StudentFree12M",
    "checkoutSessionId": "",  # leave empty to see what the server returns; if you have a checkoutSessionId, set it
    "client": "poc",
    "language": "en-US",
    "market": "US",
}
url = "https://checkout.microsoft365.com/api/offers/hydrate?" + urlencode(params)
print("GET", url)
with httpx.Client(timeout=30) as client:
    resp = client.get(url, headers=headers)
    print("HTTP", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2)[:4000])  # print first chunk; paste full if needed
    except Exception:
        print(resp.text[:4000])
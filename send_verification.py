import json
from pathlib import Path
import sys
import httpx

tfile = Path("tokens.json")
if not tfile.exists():
    print("tokens.json not found. Run `python main.py --export-tokens` and sign in first.")
    sys.exit(1)

email = sys.argv[1] if len(sys.argv) > 1 else input("Student email: ").strip()

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

payload = {"email": email, "locale": "en-US"}

with httpx.Client(timeout=30) as client:
    resp = client.post("https://checkout.microsoft365.com/api/verifystudent/sendemail", json=payload, headers=headers)
    print("HTTP", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
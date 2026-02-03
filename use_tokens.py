import json, httpx, sys
from pathlib import Path

tokens_file = Path("tokens.json")
if not tokens_file.exists():
    print("tokens.json not found")
    sys.exit(1)

t = json.loads(tokens_file.read_text())
headers = {
    "Authorization": t.get("bearer",""),
    "X-Auth": t.get("x_auth",""),
    "Cookie": t.get("cookies",""),
    "Content-Type": "application/json",
    "Accept": "application/json",
}
email = sys.argv[1] if len(sys.argv) > 1 else "student@example.edu"
payload = {"email": email, "locale": "en-US"}

with httpx.Client(timeout=30) as client:
    resp = client.post("https://checkout.microsoft365.com/api/verifystudent/sendemail", json=payload, headers=headers)
    print("status:", resp.status_code)
    try:
        print("json:", resp.json())
    except Exception:
        print("body:", resp.text)
#!/usr/bin/env python3
"""
Attempt to call the internal verifystudent/sendemail endpoint using the captured tokens.json.

Usage:
    python send_verification_retry.py student@example.edu

Place this file in the project root (next to main.py and tokens.json).
"""
import json
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

TOKENS_FILE = Path("tokens.json")
if not TOKENS_FILE.exists():
    print("tokens.json not found. Run `python main.py --export-tokens` and sign in first.")
    sys.exit(1)

email = sys.argv[1] if len(sys.argv) > 1 else input("Student email: ").strip()
if not email:
    print("No email provided; exiting.")
    sys.exit(1)

tokens = json.loads(TOKENS_FILE.read_text())

headers = {
    "Authorization": tokens.get("bearer", ""),
    "X-Auth": tokens.get("x_auth", ""),
    "Cookie": tokens.get("cookies", ""),
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://checkout.microsoft365.com",
    "Referer": "https://checkout.microsoft365.com/",
    "User-Agent": "Mozilla/5.0",
}

payload = {"email": email, "locale": "en-US"}
url = "https://checkout.microsoft365.com/api/verifystudent/sendemail"

attempts = 3
for attempt in range(1, attempts + 1):
    print(f"[INFO] Attempt {attempt}/{attempts} -> POST {url}")
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, json=payload, headers=headers)
            print("[RESULT] HTTP", resp.status_code)
            try:
                print(json.dumps(resp.json(), indent=2))
            except Exception:
                # print plain text body if not JSON
                print(resp.text[:4000])
            break
    except httpx.ReadTimeout:
        print(f"[WARN] ReadTimeout on attempt {attempt}. Retrying...")
        time.sleep(1)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        break
else:
    print("[ERROR] All attempts failed (timeout or network issue).")
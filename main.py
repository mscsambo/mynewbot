"""
CLI entrypoint for ms365-verifier
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Import verifier implementation
# Make sure verifier/ms365_verifier.py exists and provides MS365Verifier
try:
    from verifier.ms365_verifier import MS365Verifier
except Exception as e:
    print(f"[ERROR] Could not import verifier.ms365_verifier: {e}")
    sys.exit(1)


async def interactive_mode(headless: bool = False):
    verifier = MS365Verifier(headless=headless)
    try:
        await verifier.launch_browser()

        ok = await verifier.navigate_to_checkout()
        if not ok:
            print("[ERROR] Navigation to checkout failed")
            return

        print("[INFO] Browser opened. Complete manual flow in the browser window.")
        print("[INFO] The program will exit automatically if you close the browser window.")

        # Wait until browser/page/context closes (or Ctrl+C)
        try:
            await verifier.wait_for_browser_close(timeout=None)  # wait indefinitely
        except asyncio.CancelledError:
            raise

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    finally:
        await verifier.close()


async def direct_mode(email: str, headless: bool = True):
    verifier = MS365Verifier(headless=headless)
    try:
        await verifier.launch_browser()

        if not await verifier.navigate_to_checkout():
            print("[ERROR] Failed to navigate to checkout")
            return

        # Wait for tokens captured by request handler
        if not await verifier.wait_for_tokens(timeout=60):
            print("[ERROR] Could not capture tokens")
            return

        print("[INFO] Tokens captured, submitting verification...")

        result = verifier.verify_student_email(email)

        if result.get("success"):
            print("\n" + "=" * 60)
            print("   SUCCESS!")
            print("=" * 60)
            print(f"   Verification email sent to: {email}")
            print("   Check your inbox and click the verification link.")
            print("=" * 60)
        else:
            print(f"\n[ERROR] Verification failed: {result.get('error')}")
            if result.get("body"):
                print(f"[DEBUG] Response: {result.get('body')[:200]}")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        await verifier.close()


async def token_export_mode(headless: bool = False):
    verifier = MS365Verifier(headless=headless)
    try:
        await verifier.launch_browser()

        if not await verifier.navigate_to_checkout():
            print("[ERROR] Navigation failed")
            return

        print("[INFO] Complete sign-in and interactions in the browser; tokens will be saved when captured.")

        if await verifier.wait_for_tokens(timeout=120):
            tokens_file = Path(__file__).parent / "tokens.json"
            content = {
                "bearer": verifier.tokens.bearer,
                "x_auth": verifier.tokens.x_auth,
                "cookies": verifier.tokens.cookies,
                "timestamp": verifier.tokens.timestamp,
            }
            tokens_file.write_text(__import__("json").dumps(content, indent=2))
            try:
                tokens_file.chmod(0o600)
            except Exception:
                pass
            print(f"[SUCCESS] Tokens saved to: {tokens_file}")
        else:
            print("[ERROR] Token capture failed")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    finally:
        await verifier.close()


async def send_from_page_mode(email: str, headless: bool = False):
    """
    Capture tokens and then call the verification API from the page context (avoids CSRF timeouts).
    """
    verifier = MS365Verifier(headless=headless)
    try:
        await verifier.launch_browser()

        if not await verifier.navigate_to_checkout():
            print("[ERROR] Navigation failed")
            return

        print("[INFO] Complete sign-in and interactions in the browser.")
        print("[INFO] Once verification screen appears, press Enter here to trigger the API call.")

        # Wait for user to press Enter (they can do sign-in and get to verification screen)
        input("[PRESS ENTER TO CALL VERIFICATION API FROM PAGE]")

        if not verifier.tokens:
            print("[ERROR] No tokens captured yet. Sign in first.")
            return

        # Call the API from the page context
        print(f"[INFO] Calling verification API for {email} from page context...")
        result = await verifier.send_verification_from_page(email)

        if result.get("success") and result["status"] == 200:
            print("\n" + "=" * 60)
            print("   SUCCESS!")
            print("=" * 60)
            print(f"   Verification email sent to: {email}")
            print("   Check your inbox and click the verification link.")
            print("=" * 60)
        else:
            print(f"[ERROR] Page-context API call failed: {result}")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    finally:
        await verifier.close()


def main():
    parser = argparse.ArgumentParser(description="MS365 Education Verification Tool")
    parser.add_argument("--email", help="Student email for direct verification")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    parser.add_argument("--export-tokens", action="store_true", help="Export captured tokens to file")
    parser.add_argument("--send-from-page", help="Capture tokens then call verification API from page context (enter email)")
    args = parser.parse_args()

    # Basic banner
    print()
    print("+" + "=" * 58 + "+")
    print("|" + " MS365 Education Verification Tool".center(58) + "|")
    print("|" + " Student Discount Automation".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print()

    try:
        if args.send_from_page:
            asyncio.run(send_from_page_mode(args.send_from_page, headless=args.headless))
        elif args.export_tokens:
            asyncio.run(token_export_mode(headless=args.headless))
        elif args.email:
            asyncio.run(direct_mode(args.email, headless=args.headless))
        else:
            asyncio.run(interactive_mode(headless=args.headless))
    except Exception as e:
        print(f"[FATAL] Unhandled error: {e}")
        raise


if __name__ == "__main__":
    main()
"""
Horizon Plus Automated Login Test using Playwright

This script automates the login workflow for the Horizon Plus web application.

Safety & Best Practices:
- Reads credentials securely from environment variables.
- Does not hard-code passwords or secrets.
- Uses stable, accessible DOM selectors.
- Captures automated screenshots into the `screenshots/` directory.
- Outputs clear PASS or FAIL status with helpful diagnostics.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

TARGET_URL = "https://horizon-plus.dfp8hwwhcxnpq.amplifyapp.com/languages"
SIGNIN_URL = "https://horizon-plus.dfp8hwwhcxnpq.amplifyapp.com/signin"


def run_login_test():
    print("=================================")
    print("HORIZON LOGIN AUTOMATION")

    username = os.getenv("HORIZON_USERNAME")
    password = os.getenv("HORIZON_PASSWORD")
    headless_setting = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() in ("true", "1", "yes")

    if not username or not password:
        print("LOGIN TEST: FAIL")
        print("\n[Configuration Error]")
        print("Missing credentials! HORIZON_USERNAME and HORIZON_PASSWORD must be set.")
        print("Please create a `.env` file based on `.env.example` with valid credentials:")
        print("  HORIZON_USERNAME=your_email@example.com")
        print("  HORIZON_PASSWORD=your_password")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless_setting,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        auth_response_data = {"checked": False, "success": False, "error_msg": None}

        def handle_response(response):
            """Monitors the Horizon authentication endpoint."""
            if "service/ottuser/action/login" in response.url.lower():
                try:
                    auth_response_data["checked"] = True
                    resp_json = response.json()
                    res = resp_json.get("result", {})
                    if "error" in res:
                        err_obj = res.get("error", {})
                        auth_response_data["success"] = False
                        auth_response_data["error_msg"] = err_obj.get("message", "Invalid credentials")
                    elif "loginSession" in res or "user" in res or "ks" in res:
                        auth_response_data["success"] = True
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            print("Opening website...")
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2000)

            if "/signin" not in page.url:
                page.goto(SIGNIN_URL, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

            email_selector = "input[name='email'], input#email"
            password_selector = "input[name='pass'], input#pass, input[type='password']"
            submit_selector = "button:has-text('Login Now'), button[type='submit']"

            page.wait_for_selector(email_selector, state="visible", timeout=15000)
            print("Login page detected.")

            print("Entering credentials...")
            page.fill(email_selector, username)
            page.fill(password_selector, password)
            print("Clicking Login...")
            page.click(submit_selector)
            print("Checking successful login...")
            page.wait_for_timeout(5000)

            is_login_success = False
            failure_reason = None
            if auth_response_data["checked"]:
                if auth_response_data["success"]:
                    is_login_success = True
                else:
                    failure_reason = auth_response_data["error_msg"]
            elif "/signin" not in page.url:
                is_login_success = True
            else:
                failure_reason = "Page stayed on signin view without successful redirection."

            if is_login_success:
                success_path = SCREENSHOTS_DIR / "login-success.png"
                page.screenshot(path=str(success_path), full_page=True)
                print("LOGIN TEST: PASS")
                print("Screenshot saved to:")
                print("screenshots/login-success.png")
                return True

            fail_path = SCREENSHOTS_DIR / "login-failed.png"
            page.screenshot(path=str(fail_path), full_page=True)
            print("LOGIN TEST: FAIL")
            if failure_reason:
                print(f"Reason: {failure_reason}")
            print("Screenshot saved to:")
            print("screenshots/login-failed.png")
            return False

        except PlaywrightTimeoutError as te:
            fail_path = SCREENSHOTS_DIR / "login-failed.png"
            page.screenshot(path=str(fail_path), full_page=True)
            print("LOGIN TEST: FAIL")
            print(f"Error: Operation timed out waiting for page element ({str(te)})")
            print("Screenshot saved to:")
            print("screenshots/login-failed.png")
            return False

        except Exception as ex:
            fail_path = SCREENSHOTS_DIR / "login-failed.png"
            page.screenshot(path=str(fail_path), full_page=True)
            print("LOGIN TEST: FAIL")
            print(f"Error: {str(ex)}")
            print("Screenshot saved to:")
            print("screenshots/login-failed.png")
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = run_login_test()
    sys.exit(0 if success else 1)

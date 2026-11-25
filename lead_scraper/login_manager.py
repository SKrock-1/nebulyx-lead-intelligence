"""
Instagram Authentication Manager for Nebulyx Lead Intelligence
Supports switching accounts cleanly, storing session state in auth_state.json,
and tracking active username metadata in session_meta.json without storing passwords.
"""

import os
import re
import sys
import json
import time
from playwright.sync_api import sync_playwright

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_STATE_FILE = os.path.join(CURRENT_DIR, "auth_state.json")
SESSION_META_FILE = os.path.join(CURRENT_DIR, "session_meta.json")


def launch_browser(pw, headless: bool = True):
    """Launches Microsoft Edge on Windows if present, falling back to bundled Chromium (Docker/Linux/macOS)."""
    if sys.platform.startswith("win"):
        try:
            return pw.chromium.launch(channel="msedge", headless=headless)
        except Exception:
            pass
    return pw.chromium.launch(headless=headless)


class InstagramLoginManager:
    def __init__(self, auth_file=AUTH_STATE_FILE, meta_file=SESSION_META_FILE):
        self.auth_file = auth_file
        self.meta_file = meta_file
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
        )

    def logout(self):
        """Clears saved auth_state.json and session_meta.json so a new account can log in."""
        removed = []
        for path in [self.auth_file, self.meta_file]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    removed.append(os.path.basename(path))
                except Exception as e:
                    print(f"⚠️ Could not remove {path}: {e}")
        print(f"🧹 Cleared previous Instagram session files: {removed or 'none present'}")
        return True

    def is_logged_in(self):
        """Checks if auth_state.json exists and contains a non-expired sessionid cookie."""
        if not os.path.exists(self.auth_file):
            return False
        try:
            with open(self.auth_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cookies = data.get("cookies", [])
            for c in cookies:
                if c.get("name") == "sessionid" and c.get("value"):
                    expires = c.get("expires", -1)
                    if expires == -1 or expires > time.time():
                        return True
            return False
        except Exception:
            return False

    def get_authenticated_user_id(self):
        """Retrieves ds_user_id from stored session cookies if present."""
        if not os.path.exists(self.auth_file):
            return None
        try:
            with open(self.auth_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for c in data.get("cookies", []):
                if c.get("name") == "ds_user_id":
                    return c.get("value")
            return None
        except Exception:
            return None

    def get_authenticated_username(self):
        """Backward-compatible helper returning username if known, else user_id."""
        meta = self.get_session_info()
        return meta.get("username") or meta.get("user_id")

    def _save_session_meta(self, username=None, user_id=None):
        """Persists non-secret active session display metadata."""
        meta = {
            "username": (username or "").lstrip("@").strip() or None,
            "user_id": user_id or self.get_authenticated_user_id(),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception:
            pass
        return meta

    def _detect_username_from_page(self, page):
        """Attempts to read logged-in Instagram @username from authenticated page DOM/API."""
        try:
            res = page.evaluate("""async () => {
                try {
                    const r = await fetch('https://www.instagram.com/api/v1/accounts/current_user/?edit=true', {
                        headers: { 'x-ig-app-id': '936619743392459' }
                    });
                    if (r.ok) {
                        const j = await r.json();
                        if (j && j.user && j.user.username) return j.user.username;
                    }
                } catch {}
                const links = Array.from(document.querySelectorAll('a[href^="/"]'));
                for (const a of links) {
                    const text = (a.innerText || '').trim().toLowerCase();
                    if (text === 'profile') {
                        const href = a.getAttribute('href') || '';
                        const clean = href.replace(/\\//g, '').trim();
                        if (clean) return clean;
                    }
                }
                return null;
            }""")
            if res and re.match(r"^[A-Za-z0-9_.]{1,35}$", str(res)):
                return str(res)
        except Exception:
            pass
        return None

    def get_session_info(self):
        """Returns complete session status dict for /api/status and dashboard HUD."""
        active = self.is_logged_in()
        user_id = self.get_authenticated_user_id()
        username = None
        updated_at = None

        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                # Only trust cached username if it matches active ds_user_id (or no user_id set)
                if not user_id or meta.get("user_id") == user_id:
                    username = meta.get("username")
                    updated_at = meta.get("updated_at")
            except Exception:
                pass

        return {
            "authenticated": active,
            "user_id": user_id,
            "username": username,
            "updated_at": updated_at,
        }

    def interactive_login(self, prefill_username=None, switch_account=False, timeout_seconds=300):
        """
        Opens a visible Microsoft Edge browser window for the user to log into any Instagram account.
        If switch_account=True, clears existing auth_state.json first for a clean account switch.
        """
        if switch_account:
            self.logout()

        print("\n" + "=" * 70)
        print("🔐 NEBULYX INSTAGRAM AUTHENTICATION")
        print("=" * 70)
        print("Opening Microsoft Edge browser window for Instagram login...")
        print("• Sign into ANY Instagram account you want agents to research with.")
        print("• Enter your credentials / 2FA inside the opened browser window.")
        print("• Once logged in, your new session will be captured automatically.")
        print("=" * 70 + "\n")

        with sync_playwright() as pw:
            browser = launch_browser(pw, headless=False)
            context = browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1280, "height": 850},
            )
            page = context.new_page()

            page.goto("https://www.instagram.com/accounts/login/", timeout=40000)
            page.wait_for_timeout(2000)

            try:
                for text_match in ["Allow all cookies", "Allow essential", "Accept", "Only allow essential"]:
                    btn = page.locator(f'button:has-text("{text_match}")').first
                    if btn.is_visible():
                        btn.click()
                        break
            except Exception:
                pass

            if prefill_username:
                try:
                    clean_u = (
                        prefill_username.strip()
                        .lstrip("@")
                        .replace("https://www.instagram.com/", "")
                        .replace("https://instagram.com/", "")
                        .strip("/")
                    )
                    if clean_u:
                        page.wait_for_selector('input[name="username"]', timeout=10000)
                        page.fill('input[name="username"]', clean_u)
                        print(f"✓ Prefilled username: @{clean_u}")
                except Exception as e:
                    print(f"ℹ️ Could not auto-prefill username ({e}); please enter it in the browser.")

            print("⏳ Browser window is OPEN. Complete Instagram sign-in in the window...")
            start_time = time.time()
            logged_in = False

            while time.time() - start_time < timeout_seconds:
                try:
                    cookies = context.cookies()
                    has_session = any(c.get("name") == "sessionid" and c.get("value") for c in cookies)
                    if has_session and "accounts/login" not in page.url:
                        logged_in = True
                        break
                    page.wait_for_timeout(1500)
                except Exception:
                    break

            if logged_in:
                page.wait_for_timeout(2500)
                detected_username = self._detect_username_from_page(page) or (
                    prefill_username.lstrip("@").strip() if prefill_username else None
                )
                context.storage_state(path=self.auth_file)
                meta = self._save_session_meta(username=detected_username)
                print("\n✅ LOGIN SUCCESSFUL!")
                if meta.get("username"):
                    print(f"👤 Active Account: @{meta['username']} (ID: {meta.get('user_id')})")
                print(f"💾 Session saved to: {self.auth_file}\n")
                browser.close()
                return True

            print("\n⚠️ Login timed out or browser window was closed.")
            try:
                browser.close()
            except Exception:
                pass
            return False

    def login_with_sessionid(self, session_id, username_hint=None):
        """
        Authenticates or switches account immediately using an Instagram sessionid cookie.
        """
        clean_session = session_id.strip().strip('"').strip("'")
        if len(clean_session) < 16 or any(ch.isspace() for ch in clean_session):
            return False, "Invalid sessionid format. Paste the full Instagram sessionid cookie value."

        print("\n🔑 Validating new sessionid with Instagram...")
        with sync_playwright() as pw:
            browser = launch_browser(pw, headless=True)
            context = browser.new_context(user_agent=self.user_agent)
            context.add_cookies([
                {
                    "name": "sessionid",
                    "value": clean_session,
                    "domain": ".instagram.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                }
            ])
            page = context.new_page()

            try:
                page.goto("https://www.instagram.com/", timeout=30000)
                page.wait_for_timeout(3500)

                cookies = context.cookies()
                has_session = any(c.get("name") == "sessionid" and c.get("value") for c in cookies)
                is_logged_in = has_session and ("accounts/login" not in page.url)

                if is_logged_in:
                    detected_username = self._detect_username_from_page(page) or (
                        username_hint.lstrip("@").strip() if username_hint else None
                    )
                    context.storage_state(path=self.auth_file)
                    meta = self._save_session_meta(username=detected_username)
                    print(f"✅ SESSION AUTHENTICATED AS: @{meta.get('username') or meta.get('user_id')}")
                    browser.close()
                    return True, meta

                print("❌ Provided sessionid was rejected or expired by Instagram.")
                browser.close()
                return False, "Provided sessionid was rejected or expired by Instagram."
            except Exception as e:
                print(f"❌ Error validating sessionid: {e}")
                browser.close()
                return False, str(e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Instagram Multi-Account Authentication Manager for Nebulyx")
    parser.add_argument("--check", action="store_true", help="Check current login status")
    parser.add_argument("--logout", action="store_true", help="Clear saved Instagram session")
    parser.add_argument("--switch", action="store_true", help="Clear current session and open login for a new account")
    parser.add_argument("--interactive", action="store_true", help="Open visible browser window to log in")
    parser.add_argument("--sessionid", type=str, help="Authenticate instantly with browser sessionid cookie")
    parser.add_argument("--username", type=str, help="Optional Instagram handle hint / prefill")

    args = parser.parse_args()
    mgr = InstagramLoginManager()

    if args.check:
        info = mgr.get_session_info()
        print(f"Status: {'✅ Logged In' if info['authenticated'] else '❌ Not Logged In'}")
        if info.get("username"):
            print(f"Username: @{info['username']}")
        if info.get("user_id"):
            print(f"User ID: {info['user_id']}")
        return

    if args.logout:
        mgr.logout()
        return

    if args.sessionid:
        ok, detail = mgr.login_with_sessionid(args.sessionid, username_hint=args.username)
        if not ok:
            sys.exit(1)
        return

    mgr.interactive_login(prefill_username=args.username, switch_account=args.switch)


if __name__ == "__main__":
    main()

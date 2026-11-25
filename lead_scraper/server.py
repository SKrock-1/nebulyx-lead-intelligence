"""
Nebulyx Lead Intelligence Local Server & REST API
Serves dashboard.html, static flyer/captured media assets, and exposes:
- GET /api/status (Dynamic IG auth user, Gemini Vision status, Agent-Reach health)
- GET /api/leads, /api/leads/stage, /api/sellbird/lead
- GET /api/research, /api/reels, /api/discover, /api/marketplace/scout (incl. dorks & reach)
- POST /api/settings/gemini (saves GEMINI_API_KEY locally to .env.local without echoing secret)
- POST /api/settings/account (logout or switch IG account via sessionid)
"""

import os
import sys
import json
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from config_env import get_masked_gemini_status, load_env_local, save_gemini_api_key
from handle_researcher import InstagramHandleResearcher, LEADS_JSON
from login_manager import InstagramLoginManager
from reels_researcher import InstagramReelsResearcher
from marketplace_scout import InstagramMarketplaceScout
from sellbird_engine import SellbirdSalesEngine
from agent_reach_adapter import AgentReachAdapter

load_env_local()

sellbird_engine = SellbirdSalesEngine()
reach_adapter = AgentReachAdapter()

PORT = int(os.environ.get("PORT", 8088))
HOST = os.environ.get("HOST", "127.0.0.1")


class NebulyxLeadHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=current_dir, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        super().end_headers()

    def _send_json(self, status_code: int, payload: object):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                return {}
            raw = self.rfile.read(length).decode("utf-8", errors="ignore")
            return json.loads(raw) if raw else {}
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/settings/gemini":
            api_key = (body.get("api_key") or "").strip()
            save_gemini_api_key(api_key)
            status = get_masked_gemini_status()
            self._send_json(200, {"ok": True, **status})
            return

        if path == "/api/settings/account":
            action = (body.get("action") or "").strip().lower()
            mgr = InstagramLoginManager()

            if action == "logout":
                mgr.logout()
                self._send_json(200, {"ok": True, **mgr.get_session_info()})
                return

            if action == "switch_sessionid":
                session_id = (body.get("sessionid") or "").strip()
                username_hint = (body.get("username_hint") or "").strip() or None
                ok, result = mgr.login_with_sessionid(session_id, username_hint=username_hint)
                if ok:
                    self._send_json(200, {"ok": True, **mgr.get_session_info()})
                else:
                    self._send_json(400, {"ok": False, "error": str(result)})
                return

            self._send_json(400, {"ok": False, "error": "Unsupported action"})
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/dashboard":
            self.path = "/dashboard.html"
            return super().do_GET()

        if path == "/api/status":
            login_mgr = InstagramLoginManager()
            sess = login_mgr.get_session_info()
            gem = get_masked_gemini_status()
            leads_count = 0
            if os.path.exists(LEADS_JSON):
                try:
                    with open(LEADS_JSON, "r", encoding="utf-8") as f:
                        leads_count = len(json.load(f))
                except Exception:
                    pass

            self._send_json(200, {
                "authenticated": sess["authenticated"],
                "username": sess.get("username"),
                "user_id": sess.get("user_id"),
                "leads_count": leads_count,
                "gemini_configured": gem["gemini_configured"],
                "gemini_key_hint": gem["gemini_key_hint"],
                "agent_reach_available": reach_adapter.is_available(),
            })
            return

        if path == "/api/leads":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            if os.path.exists(LEADS_JSON):
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b"[]")
            return

        if path == "/api/leads/stage":
            lead_id = query.get("id", [""])[0].strip()
            stage = query.get("stage", [""])[0].strip()
            valid_stages = {"new", "contacted", "replied", "booked"}
            if not lead_id or stage.lower() not in valid_stages:
                self._send_json(400, {"error": "Invalid id or stage"})
                return

            if os.path.exists(LEADS_JSON):
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    leads = json.load(f)
                updated = False
                for l in leads:
                    if l.get("id") == lead_id:
                        l["crm_stage"] = stage.lower()
                        updated = True
                        break
                if updated:
                    with open(LEADS_JSON, "w", encoding="utf-8") as f:
                        json.dump(leads, f, indent=2, ensure_ascii=False)
                    self._send_json(200, {"ok": True, "id": lead_id, "crm_stage": stage.lower()})
                    return

            self._send_json(404, {"error": "Lead not found"})
            return

        if path == "/api/sellbird/lead":
            lead_id = query.get("id", [""])[0].strip()
            if os.path.exists(LEADS_JSON):
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    leads = json.load(f)
                matched = next(
                    (l for l in leads if l.get("id") == lead_id or (lead_id and lead_id in l.get("instagram_handle", ""))),
                    None,
                )
                if matched:
                    if "sellbird_sequence" not in matched:
                        matched = sellbird_engine.enrich_lead(matched)
                    self._send_json(200, matched)
                    return
            self._send_json(404, {"error": "Lead not found"})
            return

        if path == "/api/research":
            handle = query.get("handle", [""])[0].strip()
            if not handle:
                self._send_json(400, {"error": "Missing handle parameter"})
                return
            researcher = InstagramHandleResearcher(headless=True)
            try:
                lead = researcher.research_and_generate_lead(handle)
                self._send_json(200, lead)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        if path == "/api/reels":
            handle = query.get("handle", [""])[0].strip()
            if not handle:
                self._send_json(400, {"error": "Missing handle parameter"})
                return
            reels_engine = InstagramReelsResearcher(headless=True)
            try:
                leads = reels_engine.research_handle_reels(handle)
                self._send_json(200, leads)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        if path == "/api/discover":
            tag = query.get("hashtag", ["hiringdeveloper"])[0].strip()
            reels_engine = InstagramReelsResearcher(headless=True)
            try:
                leads = reels_engine.discover_reels_by_hashtag(tag)
                self._send_json(200, leads)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        if path == "/api/marketplace/scout":
            mode = query.get("mode", ["omni"])[0].strip()
            limit = int(query.get("limit", [10])[0])
            q_text = query.get("query", ["looking for website developer"])[0].strip()
            scout = InstagramMarketplaceScout(headless=True)
            try:
                if mode == "dorks":
                    leads = scout.scout_dorks(limit=limit)
                elif mode == "reach":
                    leads = scout.scout_agent_reach(query=q_text, limit=limit)
                elif mode == "reels":
                    leads = scout.scout_reels_stream(max_reels=limit)
                elif mode == "explore":
                    leads = scout.scout_explore_feed(max_posts=limit)
                elif mode == "hashtags":
                    leads = scout.scout_demand_hashtags(max_per_tag=limit)
                else:
                    leads = scout.omni_scout(reels_limit=limit, explore_limit=limit, tags_limit=4)
                self._send_json(200, leads)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        return super().do_GET()


def start_server():
    server = ThreadingHTTPServer((HOST, PORT), NebulyxLeadHandler)
    print(f"\n🚀 Nebulyx Lead Intelligence Server running at: http://{HOST}:{PORT}/")
    print(f"   Dashboard: http://localhost:{PORT}/dashboard.html\n")
    server.serve_forever()


if __name__ == "__main__":
    start_server()

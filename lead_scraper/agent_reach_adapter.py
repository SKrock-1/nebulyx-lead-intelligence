"""
agent_reach_adapter.py
Bridges Agent-Reach v1.6.1 into the Nebulyx Lead Intelligence pipeline:
1. Diagnostics & Channel Health (doctor --text, instagram/web status)
2. Cross-Platform Website / Bio Link Enrichment (agent-reach web read / search)
3. Read-only Instagram Account Discovery & Post Listing (agent-reach instagram search/profile/posts)
Respects all Agent-Reach redlines: read-only, never stores passwords or asks for credentials.
"""

import os
import re
import sys
import json
import shutil
import sysconfig
import subprocess
from typing import Any, Dict, List, Optional


def resolve_agent_reach_bin() -> Optional[str]:
    """Finds working agent-reach executable from active Python Scripts or PATH."""
    candidates = [
        os.path.join(sysconfig.get_path("scripts", "nt_user"), "agent-reach.exe"),
        os.path.join(os.path.dirname(sys.executable), "Scripts", "agent-reach.exe"),
        shutil.which("agent-reach"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            # Test that it is not a broken uv shim
            try:
                p = subprocess.run([path, "channels"], capture_output=True, text=True, timeout=8)
                if p.returncode == 0 and '"ok": true' in p.stdout:
                    return path
            except Exception:
                continue
    return None


class AgentReachAdapter:
    """Wrapper around Agent-Reach 1.6.1 JSON CLI."""

    def __init__(self):
        self.bin_path = resolve_agent_reach_bin()

    def is_available(self) -> bool:
        return bool(self.bin_path)

    def _run_json(self, args: List[str], timeout: int = 25) -> Dict[str, Any]:
        if not self.bin_path:
            return {"ok": False, "error": {"code": "NEED_SETUP", "message": "agent-reach CLI not found"}}
        try:
            proc = subprocess.run(
                [self.bin_path, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="ignore",
            )
            out = (proc.stdout or "").strip()
            if out:
                # Extract trailing JSON object if any preamble exists
                last_brace = out.rfind("{")
                first_brace = out.find("{")
                if first_brace != -1 and last_brace != -1:
                    return json.loads(out[first_brace:])
            return {"ok": False, "error": {"code": "EMPTY_OUTPUT", "message": proc.stderr or "No JSON returned"}}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": {"code": "TIMEOUT", "message": f"Timed out running {' '.join(args)}"}}
        except Exception as e:
            return {"ok": False, "error": {"code": "EXEC_ERROR", "message": str(e)}}

    def get_doctor_summary(self) -> Dict[str, Any]:
        """Returns local Agent-Reach health & channel status."""
        if not self.bin_path:
            return {"available": False, "summary": "Agent-Reach binary unavailable"}
        try:
            proc = subprocess.run(
                [self.bin_path, "doctor", "--text"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="ignore",
            )
            text = (proc.stdout or "").strip()
            ig_line = next((line.strip() for line in text.splitlines() if "instagram" in line.lower()), "")
            web_line = next((line.strip() for line in text.splitlines() if " web " in f" {line.lower()} "), "")
            return {
                "available": True,
                "bin_path": self.bin_path,
                "instagram_status": ig_line or "not configured",
                "web_status": web_line or "default",
                "raw": text,
            }
        except Exception as e:
            return {"available": False, "summary": str(e)}

    def search_instagram_accounts(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Uses `agent-reach instagram search` to discover Instagram accounts."""
        return self._run_json(["instagram", "search", query, "--limit", str(limit)], timeout=30)

    def fetch_instagram_profile(self, username: str) -> Dict[str, Any]:
        """Uses `agent-reach instagram profile` to inspect account metadata."""
        clean = username.strip().lstrip("@")
        return self._run_json(["instagram", "profile", clean], timeout=30)

    def fetch_instagram_posts(self, username: str, limit: int = 6) -> Dict[str, Any]:
        """Uses `agent-reach instagram posts` to retrieve account posts metadata."""
        clean = username.strip().lstrip("@")
        return self._run_json(["instagram", "posts", clean, "--limit", str(limit)], timeout=35)

    def enrich_website_via_web(self, url_or_domain: str) -> Optional[Dict[str, Any]]:
        """
        Uses `agent-reach web read` (Jina/Exa) to inspect an Instagram lead's bio website
        for emails, WhatsApp links, builder stack hints (Wix/WordPress), or outdated site gaps.
        """
        if not url_or_domain:
            return None
        target = url_or_domain.strip()
        if not target.startswith("http"):
            target = f"https://{target}"

        res = self._run_json(["web", "read", target], timeout=20)
        if not res.get("ok"):
            return None

        items = res.get("items") or []
        text = " ".join(str(it.get("text") or "") for it in items)
        emails = list(dict.fromkeys(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
        phones = list(dict.fromkeys(re.findall(r"(?:\+\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}", text)))

        stack_hints = []
        lower = text.lower()
        for label, needle in [
            ("Wix Template", "wix.com"),
            ("WordPress", "wp-content"),
            ("Linktree Bio", "linktr.ee"),
            ("Shopify", "myshopify"),
        ]:
            if needle in lower:
                stack_hints.append(label)

        return {
            "url": target,
            "backend": res.get("backend"),
            "excerpt": text[:400],
            "emails": emails[:4],
            "phones": phones[:4],
            "stack_hints": stack_hints,
        }

    def search_web_signals(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Runs `agent-reach web search` (Exa) for finding hiring announcements across the web."""
        return self._run_json(["web", "search", query, "--limit", str(limit)], timeout=25)

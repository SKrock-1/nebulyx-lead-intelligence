"""
Verification suite for Multimodal Vision (WinRT OCR / Gemini 3 Flash),
Agent-Reach Adapter, Account Session Switcher Validation, and Server Settings API.
"""

import json
import os
import sys
import urllib.error
import urllib.request

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from agent_reach_adapter import AgentReachAdapter
from config_env import get_masked_gemini_status
from login_manager import InstagramLoginManager
from pitch_generator import LeadIntelligenceEngine
from vision_inspector import VisionInspector, extract_ocr_batch_winrt


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def run_checks():
    print("=" * 75)
    print("NEBULYX MULTIMODAL VISION, AGENT-REACH & SETTINGS VERIFICATION")
    print("=" * 75)

    # 1. Caption-free Flyer Visual Inspection (WinRT Neural OCR + VisionInspector + Intent Engine)
    print("\n[CHECK 1] Caption-Free Visual Inspection on Real Flyer Images...")
    skywalk_img = os.path.join(CURRENT_DIR, "assets", "flyers", "skywalk.jpg")
    divines_img = os.path.join(CURRENT_DIR, "assets", "flyers", "divines.jpg")
    assert os.path.exists(skywalk_img) and os.path.exists(divines_img), "Missing sample flyers"

    ocr_map = extract_ocr_batch_winrt([skywalk_img, divines_img])
    assert "97409" in ocr_map.get(skywalk_img, ""), f"Skywalk OCR missed phone: {ocr_map}"
    assert "9353652043" in ocr_map.get(divines_img, ""), f"Divines OCR missed phone: {ocr_map}"

    inspector = VisionInspector()
    vis = inspector.inspect_media_files([skywalk_img], context_text="")
    assert "visual_text" in vis and "97409" in vis["visual_text"], f"VisionInspector missed OCR text: {vis}"
    assert "vision_mode" in vis and vis["vision_mode"], f"Missing vision_mode: {vis}"
    assert len(vis.get("captured_frames", [])) == 1, f"Missing captured_frames: {vis}"

    # Verify downstream Intent Engine works with EMPTY caption (100% driven by visual pixels)
    intel = LeadIntelligenceEngine().generate_pitch({
        "company": "Skywalk Filmmakers",
        "caption": "",
        "flyer_text": vis["visual_text"],
    })
    pillar = intel["intent"]["primary"]["title"]
    assert pillar == "Website Engineering & Digital Infrastructure", f"Unexpected pillar: {pillar}"
    assert len(intel["contacts"]["phones"]) > 0, f"No phones extracted from visual text: {vis['visual_text']}"
    print(f"  OK | Mode: {vis['vision_mode']} | Visual-Only Pillar: '{pillar}' | Phones: {intel['contacts']['phones']}")

    # 2. Agent-Reach Integration Check
    print("\n[CHECK 2] Agent-Reach Adapter Diagnostics...")
    adapter = AgentReachAdapter()
    doctor = adapter.get_doctor_summary()
    assert doctor["available"] is True, f"agent-reach unavailable: {doctor}"
    assert doctor.get("bin_path") and os.path.exists(doctor["bin_path"]), f"Missing bin_path: {doctor}"
    assert "web" in (doctor.get("web_status", "") + doctor.get("raw", "")).lower()
    print(f"  OK | Binary: {doctor['bin_path']} | Web: {doctor['web_status']} | IG: {doctor['instagram_status']}")

    # 3. Session Manager & Env Config Check
    print("\n[CHECK 3] Session Metadata & Local Config Masking...")
    mgr = InstagramLoginManager()
    info = mgr.get_session_info()
    assert info["authenticated"] is True, f"Session not authenticated: {info}"
    assert info["user_id"], "Missing ds_user_id in session info"
    gemini_status = get_masked_gemini_status()
    assert "gemini_configured" in gemini_status and "gemini_key_hint" in gemini_status
    print(f"  OK | Active IG User ID: {info['user_id']} | Handle: {info.get('username') or 'Session Active'}")
    print(f"  OK | Gemini Key Configured: {gemini_status['gemini_configured']}")

    # 4. Live Server Status, Dashboard Elements & Settings Input Validation
    print("\n[CHECK 4] Live Server (/api/status, /dashboard.html, Settings Validation)...")
    with urllib.request.urlopen("http://127.0.0.1:8088/api/status", timeout=5) as resp:
        status_data = json.loads(resp.read().decode("utf-8"))
    for field in ("authenticated", "user_id", "gemini_configured", "agent_reach_available"):
        assert field in status_data, f"Missing /api/status field: {field}"
    assert status_data["agent_reach_available"] is True

    with urllib.request.urlopen("http://127.0.0.1:8088/dashboard.html", timeout=5) as resp:
        html = resp.read().decode("utf-8")
    for marker in ('id="settingsModal"', 'onclick="openSettingsModal()"', "runScout('reach')", "geminiKeyInput"):
        assert marker in html, f"Dashboard HTML missing marker: {marker}"

    if not status_data["gemini_configured"]:
        code_g, body_g = post_json("http://127.0.0.1:8088/api/settings/gemini", {"api_key": ""})
        assert code_g == 200 and body_g.get("ok") is True and body_g.get("gemini_configured") is False, (
            f"Expected 200 clearing unset Gemini key: {code_g} {body_g}"
        )

    code_u, body_u = post_json("http://127.0.0.1:8088/api/settings/account", {"action": "unsupported"})
    assert code_u == 400 and body_u.get("ok") is False, f"Expected 400 on unsupported action: {code_u} {body_u}"

    code_a, body_a = post_json(
        "http://127.0.0.1:8088/api/settings/account",
        {"action": "switch_sessionid", "sessionid": "short"},
    )
    assert code_a == 400 and "error" in body_a, f"Expected 400 on short sessionid: {code_a} {body_a}"
    print("  OK | Settings validation & new UI/API markers verified without altering stored session/keys.")

    print("\nALL MULTIMODAL, AGENT-REACH & SETTINGS CHECKS PASSED.")


if __name__ == "__main__":
    run_checks()

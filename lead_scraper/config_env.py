"""
config_env.py
Manages .env.local loading and safe masked persistence for GEMINI_API_KEY
and related runtime settings without logging or exposing secret values.
"""

import os
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_LOCAL_PATH = os.path.join(ROOT_DIR, ".env.local")


def load_env_local(override: bool = False) -> None:
    """Loads key=value pairs from .env.local into os.environ."""
    if not os.path.exists(ENV_LOCAL_PATH):
        return
    try:
        with open(ENV_LOCAL_PATH, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and (override or key not in os.environ or not os.environ.get(key)):
                    os.environ[key] = val
    except Exception:
        pass


def get_gemini_api_key() -> Optional[str]:
    """Returns configured GEMINI_API_KEY (or GOOGLE_API_KEY) if present."""
    load_env_local(override=False)
    key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    return key if key else None


def save_gemini_api_key(api_key: str) -> None:
    """Safely stores GEMINI_API_KEY in .env.local and refreshes current process env."""
    clean_key = api_key.strip().strip('"').strip("'")
    lines = []
    updated = False

    if os.path.exists(ENV_LOCAL_PATH):
        with open(ENV_LOCAL_PATH, "r", encoding="utf-8") as f:
            for raw_line in f:
                stripped = raw_line.strip()
                if stripped.startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={clean_key}\n")
                    updated = True
                else:
                    lines.append(raw_line if raw_line.endswith("\n") else raw_line + "\n")

    if not updated:
        lines.append(f"GEMINI_API_KEY={clean_key}\n")

    with open(ENV_LOCAL_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    if clean_key:
        os.environ["GEMINI_API_KEY"] = clean_key
    elif "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]


def get_masked_gemini_status() -> dict:
    """Returns non-secret status metadata about Gemini key configuration."""
    key = get_gemini_api_key()
    if not key:
        return {"gemini_configured": False, "gemini_key_hint": ""}
    hint = f"{key[:6]}...{key[-4:]}" if len(key) > 12 else "***configured***"
    return {"gemini_configured": True, "gemini_key_hint": hint}

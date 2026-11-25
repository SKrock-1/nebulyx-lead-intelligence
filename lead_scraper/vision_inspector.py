"""
vision_inspector.py
Multimodal Visual Perception Engine for Nebulyx Lead Intelligence.
Allows the agent to literally SEE Instagram Reels, Posts, Carousels, and Explore tiles via:
1. Live Playwright video keyframe seeking & stage screenshot capture
2. FFmpeg keyframe extraction when direct video files/streams are available
3. Zero-cost Windows WinRT Neural OCR (Windows.Media.Ocr.OcrEngine) in batched mode
4. Optional Gemini Multimodal Vision (gemini-3-flash-preview via google-genai) using GEMINI_API_KEY
"""

import os
import re
import sys
import json
import time
import shutil
import tempfile
import subprocess
from typing import Any, Dict, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from config_env import get_gemini_api_key

CAPTURED_MEDIA_DIR = os.path.join(CURRENT_DIR, "assets", "captured")
os.makedirs(CAPTURED_MEDIA_DIR, exist_ok=True)


def extract_ocr_batch_winrt(image_paths: List[str]) -> Dict[str, str]:
    """
    Runs Windows built-in WinRT Neural OCR (Windows.Media.Ocr) across a batch of images
    in a single PowerShell process. Returns {image_path: extracted_text}.
    """
    valid_paths = [os.path.abspath(p) for p in image_paths if p and os.path.exists(p)]
    if not valid_paths:
        return {}

    paths_json = json.dumps(valid_paths)
    tmp_script = None
    try:
        ps_body = """
param([string]$PathsJson)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.IsGenericMethod })[0]
function AwaitOp($op, $t) {
    $m = $asTaskGeneric.MakeGenericMethod($t)
    $net = $m.Invoke($null, @($op))
    $net.Wait(-1) | Out-Null
    return $net.Result
}

$ocr = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$paths = ConvertFrom-Json $PathsJson
$out = @{}

foreach ($p in $paths) {
    try {
        $file = AwaitOp ([Windows.Storage.StorageFile]::GetFileFromPathAsync($p)) ([Windows.Storage.StorageFile])
        $stream = AwaitOp ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $dec = AwaitOp ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bmp = AwaitOp ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $res = AwaitOp ($ocr.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
        $out[$p] = if ($res.Text) { $res.Text } else { "" }
        $stream.Dispose()
    } catch {
        $out[$p] = ""
    }
}

$out | ConvertTo-Json -Compress
"""
        with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as tf:
            tf.write(ps_body)
            tmp_script = tf.name

        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tmp_script, "-PathsJson", paths_json],
            capture_output=True,
            text=True,
            timeout=25,
            encoding="utf-8",
            errors="ignore",
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parsed = json.loads(proc.stdout.strip())
            if isinstance(parsed, dict):
                return parsed
    except Exception:
        pass
    finally:
        if tmp_script and os.path.exists(tmp_script):
            try:
                os.remove(tmp_script)
            except Exception:
                pass
    return {p: "" for p in valid_paths}


def extract_video_keyframes_ffmpeg(video_source: str, out_prefix: str, max_frames: int = 3) -> List[str]:
    """
    Uses ffmpeg to sample up to max_frames representative frames from a video file or direct URL.
    Returns paths to captured JPEG keyframes.
    """
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin or not video_source:
        return []

    os.makedirs(CAPTURED_MEDIA_DIR, exist_ok=True)
    out_pattern = os.path.join(CAPTURED_MEDIA_DIR, f"{out_prefix}_ff_%02d.jpg")
    try:
        cmd = [
            ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
            "-i", video_source,
            "-vf", "fps=0.5,scale=720:-1",
            "-frames:v", str(max_frames),
            out_pattern,
        ]
        subprocess.run(cmd, timeout=18, check=False)
        captured = []
        for idx in range(1, max_frames + 1):
            candidate = os.path.join(CAPTURED_MEDIA_DIR, f"{out_prefix}_ff_{idx:02d}.jpg")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 1000:
                captured.append(candidate)
        return captured
    except Exception:
        return []


def capture_reel_video_frames(page, out_prefix: str, max_frames: int = 3) -> List[str]:
    """
    Captures visual frames directly from an active Instagram Reel/Post in Playwright.
    Works even on blob:/MSE streams by seeking <video>.currentTime across the clip duration.
    Falls back to stage screenshot when no seekable video element exists.
    """
    os.makedirs(CAPTURED_MEDIA_DIR, exist_ok=True)
    captured_paths: List[str] = []

    try:
        video_el = page.locator("article video, div[role='main'] video, video").first
        if video_el.count() > 0 and video_el.is_visible():
            duration = page.evaluate("""() => {
                const v = document.querySelector('article video') || document.querySelector('video');
                if (!v) return 0;
                try { v.pause(); } catch {}
                return Number.isFinite(v.duration) ? v.duration : 0;
            }""")

            ratios = [0.15, 0.50, 0.85][:max_frames] if duration and duration > 1.5 else [0.0]
            for idx, r in enumerate(ratios):
                if duration and duration > 1.5:
                    target_t = max(0.2, min(duration - 0.2, duration * r))
                    page.evaluate("""(t) => {
                        const v = document.querySelector('article video') || document.querySelector('video');
                        if (v) { v.pause(); v.currentTime = t; }
                    }""", target_t)
                    page.wait_for_timeout(350)

                frame_path = os.path.join(CAPTURED_MEDIA_DIR, f"{out_prefix}_v{idx+1}.jpg")
                video_el.screenshot(path=frame_path, type="jpeg", quality=85)
                if os.path.exists(frame_path) and os.path.getsize(frame_path) > 1000:
                    captured_paths.append(frame_path)
            if captured_paths:
                return captured_paths
    except Exception:
        pass

    # Fallback: capture primary visual post/reel container or viewport
    try:
        stage_path = os.path.join(CAPTURED_MEDIA_DIR, f"{out_prefix}_stage.jpg")
        stage = page.locator("article img, article canvas, div[role='presentation'] img").first
        if stage.count() > 0 and stage.is_visible():
            stage.screenshot(path=stage_path, type="jpeg", quality=85)
        else:
            page.screenshot(path=stage_path, type="jpeg", quality=80)
        if os.path.exists(stage_path) and os.path.getsize(stage_path) > 1000:
            captured_paths.append(stage_path)
    except Exception:
        pass

    return captured_paths


class VisionInspector:
    """
    Combines WinRT Neural OCR (always-on $0 local baseline) with Gemini 3 Flash
    multimodal understanding when GEMINI_API_KEY is configured.
    """

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.model_name = model_name

    def has_gemini(self) -> bool:
        return bool(get_gemini_api_key())

    def analyze_visual_with_gemini(self, image_paths: List[str], context_text: str = "") -> Optional[Dict[str, Any]]:
        """
        Sends up to 4 captured frames/slides to Gemini 3 Flash using the official google-genai SDK.
        Extracts visual flyer copy, hiring intent, decision-maker, contact info, and UI critique.
        """
        api_key = get_gemini_api_key()
        if not api_key or not image_paths:
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            parts: List[Any] = []

            prompt = (
                "You are an expert B2B lead-research vision analyst for Nebulyx (engineering bespoke React/Next.js websites, "
                "custom CRM/web apps, multi-agent AI workflows/Claude Code, and scalable e-commerce storefronts).\n"
                "Inspect these Instagram Reel video frames / Post flyer images together with the page context below.\n"
                "Determine whether the account is a REAL BUYER looking for or hiring a developer/designer/CRM/AI builder "
                "(vs. another dev agency advertising its services or a developer tutorial).\n\n"
                f"Page Caption/DOM Context:\n{context_text[:1500]}\n\n"
                "Respond ONLY with valid JSON matching this exact schema:\n"
                "{\n"
                '  "visual_text": "verbatim important text, headlines, prices, and requirements read from the images",\n'
                '  "is_buyer_hiring": true or false,\n'
                '  "buyer_reason": "concise evidence of why they are buying/hiring vs selling",\n'
                '  "company_or_brand": "brand or company name visible",\n'
                '  "decision_maker": "person name to contact if shown, else empty string",\n'
                '  "requirements": ["list", "of", "technical", "needs"],\n'
                '  "primary_pillar": "Website Engineering & Digital Infrastructure | Custom Web Applications & CRM Systems | Multi-Agent Workflows & AI Systems | Digital Commerce & Scalable Storefronts",\n'
                '  "phones": ["+91 ...", "etc"],\n'
                '  "emails": ["name@domain.com"],\n'
                '  "visual_design_critique": "1 concise specific observation visible in the flyer/reel for personalized outreach"\n'
                "}"
            )
            parts.append(prompt)

            for path in image_paths[:4]:
                if os.path.exists(path):
                    ext = os.path.splitext(path)[1].lower()
                    mime = "image/png" if ext == ".png" else "image/jpeg"
                    with open(path, "rb") as img_f:
                        parts.append(types.Part.from_bytes(data=img_f.read(), mime_type=mime))

            response = client.models.generate_content(
                model=self.model_name,
                contents=parts,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            raw_json = (response.text or "").strip()
            if raw_json.startswith("```"):
                raw_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_json, flags=re.IGNORECASE).strip()
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                parsed["vision_engine"] = f"Gemini ({self.model_name})"
                return parsed
        except Exception as e:
            print(f"  ℹ️ [VisionInspector]: Gemini fallback to WinRT OCR ({str(e)[:80]})")
        return None

    def inspect_media_files(self, image_paths: List[str], context_text: str = "") -> Dict[str, Any]:
        """
        Unified visual inspection entry point:
        1. Runs local WinRT Neural OCR on every captured frame/slide ($0, <1s).
        2. If GEMINI_API_KEY is configured, runs Gemini multimodal analysis with OCR + context.
        Returns combined visual evidence dictionary.
        """
        ocr_map = extract_ocr_batch_winrt(image_paths)
        combined_ocr = " | ".join(v.strip() for v in ocr_map.values() if v and v.strip())

        enriched_context = context_text
        if combined_ocr:
            enriched_context = f"{context_text}\n[Visual OCR Text]: {combined_ocr}"

        gemini_res = self.analyze_visual_with_gemini(image_paths, enriched_context)

        visual_text = combined_ocr
        vision_mode = "WinRT Local OCR"
        if gemini_res:
            g_text = (gemini_res.get("visual_text") or "").strip()
            if g_text and g_text not in visual_text:
                visual_text = f"{g_text} | {visual_text}".strip(" |")
            vision_mode = f"{gemini_res.get('vision_engine', 'Gemini Vision')} + WinRT OCR"

        return {
            "ocr_text": combined_ocr,
            "visual_text": visual_text,
            "gemini": gemini_res,
            "vision_mode": vision_mode,
            "captured_frames": [os.path.relpath(p, CURRENT_DIR).replace("\\", "/") for p in image_paths if os.path.exists(p)],
        }

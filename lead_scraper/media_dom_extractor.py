"""
media_dom_extractor.py
Deep Instagram DOM & Visual Capture Extractor across:
1. Full expanded post/reel captions + top/pinned comments + img[alt] descriptions
2. Multi-slide Carousel stepping (captures all slides instead of only slide 1)
3. Explore Grid Visual Pre-Screening (ranks flyer/text-rich tiles visually before opening)
"""

import os
import re
import time
from typing import Any, Dict, List

from vision_inspector import (
    CAPTURED_MEDIA_DIR,
    VisionInspector,
    capture_reel_video_frames,
    extract_ocr_batch_winrt,
)

# Hints that an Instagram auto-generated alt tag depicts a text flyer/hiring post
VISUAL_SIGNAL_HINTS = [
    "text that says", "looking for", "hiring", "developer", "designer",
    "website", "crm", "freelancer", "apply", "whatsapp", "gmail", "contact",
    "graphic", "poster", "flyer", "project", "fullstack", "full stack", "agent"
]


def _extract_creator_from_dom(page, post_url: str) -> str:
    """Extracts clean @username directly from post header anchors or URL."""
    try:
        creator = page.evaluate("""() => {
            const headerLinks = Array.from(document.querySelectorAll('article header a[href^="/"], main header a[href^="/"], a[role="link"][href^="/"]'));
            for (const a of headerLinks) {
                const href = (a.getAttribute('href') || '').trim();
                const m = href.match(/^\\/([A-Za-z0-9_.]{1,35})\\/?$/);
                if (m && !['explore', 'reels', 'p', 'reel', 'accounts', 'direct', 'stories'].includes(m[1])) {
                    return m[1];
                }
            }
            return null;
        }""")
        if creator:
            return str(creator).strip()
    except Exception:
        pass

    # Fallback: og:title or URL
    try:
        og_title = page.locator('meta[property="og:title"]').get_attribute("content") or ""
        m = re.search(r"@([A-Za-z0-9_.]+)", og_title)
        if m:
            return m.group(1)
    except Exception:
        pass

    parts = [p for p in post_url.split("/") if p]
    for p in parts:
        if p not in ("https:", "http:", "www.instagram.com", "instagram.com", "p", "reel", "reels", "tv"):
            return p
    return "instagram_creator"


def _expand_and_read_caption_and_comments(page) -> Dict[str, Any]:
    """Expands truncated 'more' captions and reads caption + top pinned comments + img[alt]."""
    try:
        for btn_sel in ['button:has-text("more")', 'div[role="button"]:has-text("more")', 'span:has-text("more")']:
            try:
                loc = page.locator(btn_sel).first
                if loc.count() > 0 and loc.is_visible():
                    loc.click(timeout=1500)
                    page.wait_for_timeout(300)
                    break
            except Exception:
                pass
    except Exception:
        pass

    data = {"caption": "", "comments": [], "alts": [], "bio_url": ""}
    try:
        dom = page.evaluate("""() => {
            const alts = Array.from(document.querySelectorAll('article img[alt], main img[alt]'))
                .map(img => img.getAttribute('alt') || '')
                .filter(a => a && a.length > 6 && !a.toLowerCase().includes('profile picture'));

            const captionBlocks = Array.from(document.querySelectorAll('article h1, main h1, div._a9zs span, span._ap3a'))
                .map(el => (el.innerText || '').trim())
                .filter(Boolean);

            const comments = Array.from(document.querySelectorAll('article ul ul li, div[role="main"] ul li span'))
                .slice(0, 8)
                .map(el => (el.innerText || '').trim())
                .filter(t => t.length > 4);

            return {
                caption: captionBlocks.slice(0, 4).join(' '),
                comments: Array.from(new Set(comments)).slice(0, 5),
                alts: Array.from(new Set(alts)).slice(0, 5)
            };
        }""")
        if isinstance(dom, dict):
            data["caption"] = dom.get("caption", "")
            data["comments"] = dom.get("comments", [])
            data["alts"] = dom.get("alts", [])
    except Exception:
        pass

    # Merge og meta tags as safety fallback
    try:
        og_desc = page.locator('meta[property="og:description"]').get_attribute("content") or ""
        if og_desc and og_desc not in data["caption"]:
            data["caption"] = f"{data['caption']} {og_desc}".strip()
    except Exception:
        pass

    return data


def _capture_carousel_or_post_media(page, out_prefix: str, max_slides: int = 4) -> List[str]:
    """
    Captures visual screenshots of a Reel video's keyframes OR steps through Post carousel slides.
    """
    # Check for active video first (Reel / Video Post)
    try:
        if page.locator("article video, main video, video").count() > 0:
            frames = capture_reel_video_frames(page, out_prefix, max_frames=3)
            if frames:
                return frames
    except Exception:
        pass

    captured: List[str] = []
    os.makedirs(CAPTURED_MEDIA_DIR, exist_ok=True)

    # Single Post or Multi-Slide Carousel
    for slide_idx in range(max_slides):
        slide_path = os.path.join(CAPTURED_MEDIA_DIR, f"{out_prefix}_slide{slide_idx+1}.jpg")
        try:
            stage = page.locator("article div[role='presentation'], article ul li img, main article img").first
            if stage.count() > 0 and stage.is_visible():
                stage.screenshot(path=slide_path, type="jpeg", quality=85)
            else:
                page.screenshot(path=slide_path, type="jpeg", quality=80)
            if os.path.exists(slide_path) and os.path.getsize(slide_path) > 1000:
                captured.append(slide_path)
        except Exception:
            break

        # Advance carousel if Next button is visible
        try:
            next_btn = page.locator('button[aria-label="Next"], button[aria-label*="Next"]').first
            if next_btn.count() > 0 and next_btn.is_visible():
                next_btn.click(timeout=1500)
                page.wait_for_timeout(600)
            else:
                break
        except Exception:
            break

    return captured


def inspect_post_multimodal(
    page,
    post_url: str,
    vision: VisionInspector,
    max_slides: int = 4,
) -> Dict[str, Any]:
    """
    Full multimodal extraction for a single Instagram Post or Reel URL:
    Reads DOM captions + pinned comments + img[alt] + visual video/carousel frames + OCR/Gemini.
    """
    page.goto(post_url, timeout=20000)
    page.wait_for_timeout(2200)

    creator = _extract_creator_from_dom(page, post_url)
    dom_info = _expand_and_read_caption_and_comments(page)

    safe_prefix = re.sub(r"[^A-Za-z0-9_]", "", creator)[:20] or "post"
    prefix = f"{safe_prefix}_{int(time.time())}_{abs(hash(post_url)) % 10000}"
    captured_files = _capture_carousel_or_post_media(page, prefix, max_slides=max_slides)

    context_parts = [
        f"Account: @{creator}",
        f"Caption: {dom_info['caption']}",
    ]
    if dom_info["comments"]:
        context_parts.append("Top Comments: " + " | ".join(dom_info["comments"]))
    if dom_info["alts"]:
        context_parts.append("Image Alt Descriptions: " + " | ".join(dom_info["alts"]))

    combined_dom_text = "\n".join(context_parts)
    visual_evidence = vision.inspect_media_files(captured_files, context_text=combined_dom_text)

    combined_all_text = "\n".join(
        part for part in [
            dom_info["caption"],
            " ".join(dom_info["comments"]),
            " ".join(dom_info["alts"]),
            visual_evidence.get("visual_text", ""),
        ] if part
    )

    return {
        "creator": creator,
        "post_url": post_url,
        "caption": dom_info["caption"],
        "comments": dom_info["comments"],
        "alts": dom_info["alts"],
        "visual_evidence": visual_evidence,
        "combined_text": combined_all_text,
        "primary_image_rel": visual_evidence["captured_frames"][0] if visual_evidence.get("captured_frames") else None,
    }


def prescreen_explore_or_tag_grid(page, max_tiles: int = 24) -> List[Dict[str, Any]]:
    """
    Visually pre-screens an Instagram Explore / Hashtag / Reels grid before opening posts:
    1. Reads each tile's href + img[alt] description
    2. Captures a viewport screenshot strip & runs batch WinRT OCR if alt tags are sparse
    3. Prioritizes tiles that visually depict text flyers, hiring calls, or tech services
    """
    try:
        page.mouse.wheel(0, 700)
        page.wait_for_timeout(1800)
    except Exception:
        pass

    tiles = page.evaluate("""(limit) => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]'));
        const seen = new Set();
        const out = [];
        for (const a of anchors) {
            const href = a.getAttribute('href') || '';
            if (!href || seen.has(href)) continue;
            seen.add(href);
            const img = a.querySelector('img');
            const alt = img ? (img.getAttribute('alt') || '') : '';
            const src = img ? (img.getAttribute('src') || '') : '';
            out.push({ href, alt, src });
            if (out.length >= limit) break;
        }
        return out;
    }""", max_tiles)

    # Optional visual grid sweep via viewport OCR for logging/discovery confirmation
    try:
        grid_shot = os.path.join(CAPTURED_MEDIA_DIR, f"explore_grid_{int(time.time())}.jpg")
        page.screenshot(path=grid_shot, type="jpeg", quality=80)
        grid_ocr = extract_ocr_batch_winrt([grid_shot])
        grid_text = next(iter(grid_ocr.values()), "")
        if grid_text:
            print(f"  👁️ [Visual Explore Pre-Scan]: Detected overlay text on grid ({len(grid_text)} chars)")
    except Exception:
        pass

    ranked = []
    for t in (tiles or []):
        href = t.get("href", "")
        full_url = "https://www.instagram.com" + href if href.startswith("/") else href
        alt_lower = (t.get("alt") or "").lower()
        score = 0
        for kw in VISUAL_SIGNAL_HINTS:
            if kw in alt_lower:
                score += 2
        if "text" in alt_lower or "flyer" in alt_lower or "graphic" in alt_lower:
            score += 1
        ranked.append({
            "url": full_url,
            "alt": t.get("alt", ""),
            "visual_score": score,
        })

    ranked.sort(key=lambda x: x["visual_score"], reverse=True)
    return ranked

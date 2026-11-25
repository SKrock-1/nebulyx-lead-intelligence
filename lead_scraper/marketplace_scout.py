"""
Autonomous Instagram Marketplace Lead Discovery & Scraping Engine for Nebulyx
Combines:
1. Visual Perception (Reel video keyframes, Carousel slides, Explore grid pre-screening)
2. Local WinRT Neural OCR + Gemini 3 Flash Multimodal Vision (when GEMINI_API_KEY is set)
3. Agent-Reach cross-platform account discovery & bio domain enrichment
4. Sellbird Buyer-vs-Seller Intent Gate & 3-touch outreach synthesis
"""

import os
import sys
import re
import json
import csv
import time
from playwright.sync_api import sync_playwright

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from pitch_generator import LeadIntelligenceEngine
from login_manager import AUTH_STATE_FILE, InstagramLoginManager, launch_browser
from sellbird_prospector import SellbirdInstagramProspector
from vision_inspector import VisionInspector, capture_reel_video_frames
from media_dom_extractor import (
    _expand_and_read_caption_and_comments,
    _extract_creator_from_dom,
    inspect_post_multimodal,
    prescreen_explore_or_tag_grid,
)
from agent_reach_adapter import AgentReachAdapter

LEADS_JSON = os.path.join(CURRENT_DIR, "scraped_leads.json")
LEADS_CSV = os.path.join(CURRENT_DIR, "scraped_leads.csv")

DEMAND_HASHTAGS = [
    "needdeveloper", "hiringdeveloper", "websitedeveloper",
    "webdesignerwanted", "crmdevelopment", "realestatecrm",
    "aiagents", "claudecode", "bubbledeveloper", "fullstackdeveloper",
    "ecommercedeveloper",
]


class InstagramMarketplaceScout:
    def __init__(self, headless=True):
        self.headless = headless
        self.engine = LeadIntelligenceEngine()
        self.sellbird_prospector = SellbirdInstagramProspector(headless=headless)
        self.vision = VisionInspector()
        self.reach = AgentReachAdapter()
        self.auth_file = AUTH_STATE_FILE
        self.login_mgr = InstagramLoginManager(self.auth_file)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
        )

    def _get_browser_context(self, pw):
        browser = launch_browser(pw, headless=self.headless)
        if os.path.exists(self.auth_file) and self.login_mgr.is_logged_in():
            context = browser.new_context(
                storage_state=self.auth_file,
                user_agent=self.user_agent,
                viewport={"width": 1280, "height": 850},
            )
        else:
            context = browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1280, "height": 850},
            )
        return browser, context

    def _build_lead_from_multimodal(self, mm: dict, source_label: str) -> dict | None:
        """
        Evaluates multimodal DOM + visual OCR + Gemini Vision evidence, applies
        Sellbird Buyer-vs-Seller qualification, enriches external domains via Agent-Reach,
        and returns a complete CRM lead dict if qualified.
        """
        creator = mm["creator"]
        post_url = mm["post_url"]
        combined_text = mm["combined_text"]
        vis = mm["visual_evidence"]
        gemini_res = vis.get("gemini")

        is_buyer, reason, _ = self.sellbird_prospector.classify_intent_buyer_vs_seller(combined_text)
        if gemini_res is not None:
            if gemini_res.get("is_buyer_hiring") is True and not is_buyer:
                is_buyer = True
                reason = f"Gemini Vision Buyer Signal: {gemini_res.get('buyer_reason', 'Visual flyer demand')}"
            elif gemini_res.get("is_buyer_hiring") is False and "competitor" in (gemini_res.get("buyer_reason") or "").lower():
                return None

        if not is_buyer:
            return None

        analysis = self.engine.generate_pitch({
            "company": (gemini_res.get("company_or_brand") if gemini_res else None) or creator,
            "author": creator,
            "caption": mm["caption"],
            "flyer_text": f"{vis.get('visual_text', '')} {combined_text}",
        })

        # Merge visually spotted contacts from Gemini if regex missed stylized flyer fonts
        all_phones = list(analysis["contacts"]["phones"])
        all_emails = list(analysis["contacts"]["emails"])
        if gemini_res:
            for p in gemini_res.get("phones") or []:
                if p and p not in all_phones:
                    all_phones.append(p)
            for e in gemini_res.get("emails") or []:
                if e and "@" in e and e not in all_emails:
                    all_emails.append(e)

        # Agent-Reach off-platform website enrichment if non-social domain is present in caption/visual text
        web_enrichment = None
        domains = re.findall(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|in|io|ai|co|org|ae|dxb))\b", combined_text)
        for dom in domains:
            if not any(skip in dom.lower() for skip in ("instagram.com", "gmail.com", "whatsapp.com", "wa.me")):
                web_enrichment = self.reach.enrich_website_via_web(dom)
                if web_enrichment:
                    for e in web_enrichment.get("emails", []):
                        if e not in all_emails:
                            all_emails.append(e)
                    break

        primary_pillar = (
            (gemini_res.get("primary_pillar") if gemini_res else None)
            or (analysis["intent"]["primary"]["title"] if analysis["intent"]["primary"] else "Website Engineering & Digital Infrastructure")
        )
        matched_kws = (
            (gemini_res.get("requirements")[:6] if gemini_res and gemini_res.get("requirements") else None)
            or (analysis["intent"]["primary"]["matched_keywords"] if analysis["intent"]["primary"] else ["website", "developer"])
        )

        lead = {
            "id": f"mkt_{re.sub(r'[^A-Za-z0-9_]', '', creator)[:18]}_{int(time.time())}_{abs(hash(post_url)) % 10000}",
            "company": (gemini_res.get("company_or_brand") if gemini_res and gemini_res.get("company_or_brand") else creator),
            "instagram_handle": f"@{creator.lstrip('@')}",
            "profile_url": f"https://www.instagram.com/{creator.lstrip('@')}/",
            "reel_url": post_url,
            "primary_requirement": primary_pillar,
            "matched_keywords": matched_kws,
            "email": all_emails[0] if all_emails else "N/A",
            "phone_whatsapp": all_phones[0] if all_phones else "N/A",
            "all_phones": all_phones,
            "all_emails": all_emails,
            "whatsapp_link": analysis["whatsapp_link"],
            "whatsapp_pitch": analysis["whatsapp_pitch"],
            "email_subject": analysis["email_subject"],
            "email_body": analysis["email_body"],
            "raw_text": (vis.get("visual_text") or mm["caption"] or "")[:400],
            "visual_ocr_text": vis.get("ocr_text", "")[:400],
            "vision_mode": vis.get("vision_mode", "WinRT Local OCR"),
            "captured_frames": vis.get("captured_frames", []),
            "visual_critique": gemini_res.get("visual_design_critique", "") if gemini_res else "",
            "web_enrichment": web_enrichment,
            "image_url": mm.get("primary_image_rel") or "",
            "source": f"{source_label} · {reason}",
            "discovered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return self.sellbird_prospector.sellbird.enrich_lead(lead)

    def inspect_post_for_lead(self, page, post_url, source_label="Visual Post/Reel"):
        """
        Navigates to a post/reel URL, visually captures slides/keyframes + expanded DOM,
        reads pixels via WinRT OCR + Gemini Vision, and returns enriched buyer lead if qualified.
        """
        try:
            mm = inspect_post_multimodal(page, post_url, self.vision, max_slides=4)
            return self._build_lead_from_multimodal(mm, source_label=source_label)
        except Exception:
            return None

    def scout_reels_stream(self, max_reels=12):
        """
        Watches the live Instagram Reels stream in-place (preserving vertical scroll feed),
        captures video keyframes, reads DOM captions/comments + OCR/Gemini Vision per reel.
        """
        print(f"\n🎬 [Visual Reels Stream Scout]: Watching live Reels feed (Goal: {max_reels} reels)...")
        discovered = []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()

            try:
                page.goto("https://www.instagram.com/reels/", timeout=30000)
                page.wait_for_timeout(4000)
                seen_urls = set()

                for i in range(max_reels):
                    current_url = page.url
                    if ("/reel/" in current_url or "/reels/" in current_url) and current_url not in seen_urls:
                        seen_urls.add(current_url)
                        print(f"  [{i+1}/{max_reels}] Visually analyzing stream reel: {current_url}")

                        creator = _extract_creator_from_dom(page, current_url)
                        dom_info = _expand_and_read_caption_and_comments(page)
                        safe_prefix = re.sub(r"[^A-Za-z0-9_]", "", creator)[:18] or "stream"
                        frames = capture_reel_video_frames(page, f"{safe_prefix}_{int(time.time())}", max_frames=3)
                        context_txt = f"Account: @{creator}\nCaption: {dom_info['caption']}\nComments: {' | '.join(dom_info['comments'])}"
                        vis = self.vision.inspect_media_files(frames, context_text=context_txt)

                        mm = {
                            "creator": creator,
                            "post_url": current_url,
                            "caption": dom_info["caption"],
                            "comments": dom_info["comments"],
                            "alts": dom_info["alts"],
                            "visual_evidence": vis,
                            "combined_text": f"{dom_info['caption']} {' '.join(dom_info['comments'])} {vis.get('visual_text', '')}",
                            "primary_image_rel": vis["captured_frames"][0] if vis.get("captured_frames") else None,
                        }
                        lead = self._build_lead_from_multimodal(mm, source_label="Reels Stream Visual")
                        if lead:
                            discovered.append(lead)
                            print(f"    🎯 [STREAM VISUAL LEAD]: {lead['company']} ({lead['vision_mode']}) | {lead['phone_whatsapp']}")

                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(2600)
            except Exception as e:
                print(f"  ❌ Error in Reels Stream: {e}")
            finally:
                browser.close()

        if discovered:
            self._save_leads(discovered)
        return discovered

    def scout_explore_feed(self, max_posts=16):
        """
        Visually pre-screens Explore tiles (alt text + viewport grid OCR) before inspecting
        carousel slides and reel frames in depth.
        """
        print("\n🧭 [Visual Explore Scout]: Pre-screening Instagram Explore grid...")
        discovered = []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()

            try:
                page.goto("https://www.instagram.com/explore/", timeout=30000)
                page.wait_for_timeout(3800)

                ranked_tiles = prescreen_explore_or_tag_grid(page, max_tiles=max_posts * 2)
                print(f"  ✓ Visually ranked {len(ranked_tiles)} Explore tiles; inspecting top {max_posts}...")

                for tile in ranked_tiles[:max_posts]:
                    lead = self.inspect_post_for_lead(page, tile["url"], source_label="Explore Visual Scout")
                    if lead:
                        discovered.append(lead)
                        print(f"    🎯 [EXPLORE LEAD FOUND]: {lead['company']} ({lead['vision_mode']})")
            except Exception as e:
                print(f"  ❌ Error in Explore Feed: {e}")
            finally:
                browser.close()

        if discovered:
            self._save_leads(discovered)
        return discovered

    def scout_demand_hashtags(self, hashtags=None, max_per_tag=6):
        """Visually scours hiring demand hashtags using carousel + video frame OCR/Vision."""
        tags_to_scan = hashtags or DEMAND_HASHTAGS[:5]
        print(f"\n🏷️ [Visual Hashtag Matrix]: Scouting {len(tags_to_scan)} demand tags...")
        discovered = []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()

            try:
                for tag in tags_to_scan:
                    clean_tag = tag.lstrip("#").strip()
                    print(f"\n  → Scouting #{clean_tag}...")
                    try:
                        page.goto(f"https://www.instagram.com/explore/tags/{clean_tag}/", timeout=25000)
                        page.wait_for_timeout(3200)
                        ranked_tiles = prescreen_explore_or_tag_grid(page, max_tiles=max_per_tag * 2)
                        for tile in ranked_tiles[:max_per_tag]:
                            lead = self.inspect_post_for_lead(page, tile["url"], source_label=f"Visual Tag #{clean_tag}")
                            if lead:
                                discovered.append(lead)
                                print(f"    🎯 [TAG VISUAL LEAD]: {lead['company']} ({lead['vision_mode']})")
                    except Exception as tag_err:
                        print(f"    ⚠️ Error on #{clean_tag}: {tag_err}")
            except Exception as e:
                print(f"  ❌ Error in Hashtag Scout: {e}")
            finally:
                browser.close()

        if discovered:
            self._save_leads(discovered)
        return discovered

    def scout_agent_reach(self, query="looking for website developer", limit=6):
        """
        Combines Agent-Reach read-only Instagram account/web discovery with Playwright
        visual inspection of discovered accounts and off-platform domains.
        """
        print(f"\n🌐 [Agent-Reach Hybrid Scout]: Searching '{query}' via Agent-Reach + Vision...")
        discovered = []
        ig_search = self.reach.search_instagram_accounts(query, limit=limit)
        web_search = self.reach.search_web_signals(f"instagram {query}", limit=limit)

        candidate_urls = []
        if ig_search.get("ok"):
            for item in ig_search.get("items", []):
                url = item.get("url") or ""
                if "instagram.com" in url and url not in candidate_urls:
                    candidate_urls.append(url)
        if web_search.get("ok"):
            for item in web_search.get("items", []):
                url = item.get("url") or ""
                if "instagram.com/" in url and ("/reel/" in url or "/p/" in url) and url not in candidate_urls:
                    candidate_urls.append(url)

        if candidate_urls:
            with sync_playwright() as pw:
                browser, context = self._get_browser_context(pw)
                page = context.new_page()
                try:
                    for url in candidate_urls[:limit]:
                        if "/p/" in url or "/reel/" in url:
                            lead = self.inspect_post_for_lead(page, url, source_label="Agent-Reach + Visual")
                            if lead:
                                discovered.append(lead)
                finally:
                    browser.close()

        if discovered:
            self._save_leads(discovered)
        return discovered

    def scout_dorks(self, topic="all", limit=8):
        """Sellbird Dork Matrix + Visual Post/Reel Inspection."""
        print(f"\n🦅 [Sellbird Dork + Vision Scout]: Searching indexed Instagram buyer reels ({topic})...")
        candidate_urls = self.sellbird_prospector.dork_instagram_leads(query_topic=topic, limit=limit)
        discovered = []
        if not candidate_urls:
            return []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()
            try:
                for url in candidate_urls:
                    lead = self.inspect_post_for_lead(page, url, source_label="Sellbird Dork + Visual")
                    if lead:
                        discovered.append(lead)
            finally:
                browser.close()

        if discovered:
            self._save_leads(discovered)
        return discovered

    def omni_scout(self, reels_limit=8, explore_limit=10, tags_limit=4):
        """360-degree visual sweep across Explore, Reels Stream, Hashtags, and Agent-Reach."""
        all_discovered = []
        all_discovered.extend(self.scout_explore_feed(max_posts=explore_limit))
        all_discovered.extend(self.scout_reels_stream(max_reels=reels_limit))
        all_discovered.extend(self.scout_demand_hashtags(hashtags=DEMAND_HASHTAGS[:tags_limit], max_per_tag=4))
        return all_discovered

    def _save_leads(self, new_leads):
        existing = []
        if os.path.exists(LEADS_JSON):
            try:
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing_urls = {l.get("reel_url") for l in existing}
        count_added = 0
        for nl in new_leads:
            if nl.get("reel_url") not in existing_urls:
                existing.insert(0, nl)
                existing_urls.add(nl.get("reel_url"))
                count_added += 1

        with open(LEADS_JSON, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        fieldnames = [
            "id", "company", "instagram_handle", "primary_requirement", "phone_whatsapp",
            "email", "sellbird_icp_score", "sellbird_tier", "whatsapp_link",
            "reel_url", "profile_url", "vision_mode", "source", "discovered_at",
        ]
        with open(LEADS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for l in existing:
                writer.writerow(l)

        print(f"💾 Synced {count_added} visually verified buyer leads to JSON & CSV (Total: {len(existing)}).")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Visual Instagram Marketplace Lead Discovery Engine")
    parser.add_argument("--mode", choices=["reels", "explore", "hashtags", "dorks", "reach", "omni"], default="omni")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--query", type=str, default="looking for website developer")
    parser.add_argument("--headful", action="store_true")

    args = parser.parse_args()
    scout = InstagramMarketplaceScout(headless=not args.headful)

    if args.mode == "dorks":
        scout.scout_dorks(limit=args.limit)
    elif args.mode == "reach":
        scout.scout_agent_reach(query=args.query, limit=args.limit)
    elif args.mode == "reels":
        scout.scout_reels_stream(max_reels=args.limit)
    elif args.mode == "explore":
        scout.scout_explore_feed(max_posts=args.limit)
    elif args.mode == "hashtags":
        scout.scout_demand_hashtags(max_per_tag=args.limit)
    else:
        scout.omni_scout(reels_limit=args.limit, explore_limit=args.limit, tags_limit=4)


if __name__ == "__main__":
    main()

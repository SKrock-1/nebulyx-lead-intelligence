"""
Instagram Reels Deep Research & Discovery Engine for Nebulyx
Uses authenticated session (auth_state.json) + Visual Multimodal Perception to:
1. Deep-scan an account's dedicated /reels/ tab (capturing video keyframes, OCR, Gemini Vision)
2. Discover fresh reels across Instagram hashtags using visual grid pre-screening
3. Qualify through Sellbird Buyer-vs-Seller gate and synthesize 3-touch sequences
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from pitch_generator import LeadIntelligenceEngine
from login_manager import AUTH_STATE_FILE, InstagramLoginManager, launch_browser
from vision_inspector import VisionInspector
from media_dom_extractor import inspect_post_multimodal, prescreen_explore_or_tag_grid
from sellbird_prospector import SellbirdInstagramProspector

LEADS_JSON = os.path.join(CURRENT_DIR, "scraped_leads.json")
LEADS_CSV = os.path.join(CURRENT_DIR, "scraped_leads.csv")

TARGET_HASHTAGS = [
    "hiringdeveloper", "websitedesigner", "crmdevelopment",
    "aiagents", "claudecode", "lookingfordeveloper",
    "needdeveloper", "fullstackdeveloper", "ecommercewebsite",
]


class InstagramReelsResearcher:
    def __init__(self, headless=True):
        self.headless = headless
        self.engine = LeadIntelligenceEngine()
        self.vision = VisionInspector()
        self.prospector = SellbirdInstagramProspector(headless=headless)
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
                viewport={"width": 1280, "height": 800},
            )
        else:
            context = browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1280, "height": 800},
            )
        return browser, context

    def _evaluate_reel_url(self, page, url: str, fallback_handle: str, source_tag: str) -> dict | None:
        mm = inspect_post_multimodal(page, url, self.vision, max_slides=4)
        vis = mm["visual_evidence"]
        gemini_res = vis.get("gemini")
        combined = mm["combined_text"]

        is_buyer, reason, _ = self.prospector.classify_intent_buyer_vs_seller(combined)
        if gemini_res and gemini_res.get("is_buyer_hiring"):
            is_buyer = True
            reason = gemini_res.get("buyer_reason") or reason

        if not is_buyer:
            # Also check basic hiring keyword fallback for targeted account scans
            if not any(kw in combined.lower() for kw in ("hiring", "developer", "designer", "website", "crm", "ai agent")):
                return None
            reason = "Handle Reels Technical Keyword Match"

        creator = mm["creator"] if mm["creator"] != "instagram_creator" else fallback_handle
        analysis = self.engine.generate_pitch({
            "company": (gemini_res.get("company_or_brand") if gemini_res else None) or creator,
            "author": creator,
            "caption": mm["caption"],
            "flyer_text": f"{vis.get('visual_text', '')} {combined}",
        })

        all_phones = list(analysis["contacts"]["phones"])
        all_emails = list(analysis["contacts"]["emails"])
        if gemini_res:
            for p in gemini_res.get("phones") or []:
                if p and p not in all_phones:
                    all_phones.append(p)
            for e in gemini_res.get("emails") or []:
                if e and "@" in e and e not in all_emails:
                    all_emails.append(e)

        primary_pillar = (
            (gemini_res.get("primary_pillar") if gemini_res else None)
            or (analysis["intent"]["primary"]["title"] if analysis["intent"]["primary"] else "Website Engineering & Digital Infrastructure")
        )
        lead = {
            "id": f"reel_{creator}_{int(time.time())}_{abs(hash(url)) % 10000}",
            "company": (gemini_res.get("company_or_brand") if gemini_res and gemini_res.get("company_or_brand") else analysis["company"]),
            "instagram_handle": f"@{creator.lstrip('@')}",
            "profile_url": f"https://www.instagram.com/{creator.lstrip('@')}/",
            "reel_url": url,
            "primary_requirement": primary_pillar,
            "matched_keywords": analysis["intent"]["primary"]["matched_keywords"] if analysis["intent"]["primary"] else ["website", "developer"],
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
            "image_url": mm.get("primary_image_rel") or "",
            "source": f"{source_tag} · {reason}",
            "discovered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return self.prospector.sellbird.enrich_lead(lead)

    def research_handle_reels(self, handle, max_reels=12):
        """Deep-scans the /reels/ tab of an account with multimodal video frame & OCR reading."""
        clean_handle = handle.strip().lstrip("@").replace("https://instagram.com/", "").strip("/")
        print(f"\n🎬 [Visual Reels Tab Scan]: @{clean_handle}/reels/")
        discovered_leads = []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()

            try:
                page.goto(f"https://www.instagram.com/{clean_handle}/reels/", timeout=25000)
                page.wait_for_timeout(3200)
                ranked = prescreen_explore_or_tag_grid(page, max_tiles=max_reels * 2)
                if not ranked:
                    page.goto(f"https://www.instagram.com/{clean_handle}/", timeout=20000)
                    page.wait_for_timeout(3000)
                    ranked = prescreen_explore_or_tag_grid(page, max_tiles=max_reels * 2)

                for tile in ranked[:max_reels]:
                    try:
                        lead = self._evaluate_reel_url(page, tile["url"], clean_handle, "Handle Reels Visual")
                        if lead:
                            discovered_leads.append(lead)
                            print(f"    🎯 [REEL VISUAL LEAD]: {tile['url']} | {lead['vision_mode']}")
                    except Exception as re_err:
                        print(f"    ⚠️ Reel inspect error: {re_err}")
            except Exception as e:
                print(f"  ❌ Scan error: {e}")
            finally:
                browser.close()

        if discovered_leads:
            self._save_leads(discovered_leads)
        return discovered_leads

    def discover_reels_by_hashtag(self, hashtag, max_reels=10):
        """Explores Instagram hashtag Reels with visual grid pre-screening + frame OCR/Vision."""
        clean_tag = hashtag.lstrip("#").strip()
        print(f"\n🔍 [Visual Hashtag Reels Discovery]: #{clean_tag}")
        leads = []

        with sync_playwright() as pw:
            browser, context = self._get_browser_context(pw)
            page = context.new_page()

            try:
                page.goto(f"https://www.instagram.com/explore/tags/{clean_tag}/", timeout=25000)
                page.wait_for_timeout(3500)
                ranked = prescreen_explore_or_tag_grid(page, max_tiles=max_reels * 2)

                for tile in ranked[:max_reels]:
                    try:
                        lead = self._evaluate_reel_url(page, tile["url"], clean_tag, f"Hashtag #{clean_tag} Visual")
                        if lead:
                            leads.append(lead)
                            print(f"    🎯 [HASHTAG VISUAL LEAD]: {lead['instagram_handle']} | {lead['primary_requirement']}")
                    except Exception as err:
                        print(f"    ⚠️ Post inspect error: {err}")
            except Exception as e:
                print(f"  ❌ Hashtag exploration error: {e}")
            finally:
                browser.close()

        if leads:
            self._save_leads(leads)
        return leads

    def _save_leads(self, new_leads):
        existing = []
        if os.path.exists(LEADS_JSON):
            try:
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing_urls = {l.get("reel_url") for l in existing}
        for nl in new_leads:
            if nl.get("reel_url") not in existing_urls:
                existing.insert(0, nl)
                existing_urls.add(nl.get("reel_url"))

        with open(LEADS_JSON, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(new_leads)} visual reel leads to {LEADS_JSON}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Instagram Reels Visual Deep Research Engine")
    parser.add_argument("--handle", type=str, help="Instagram handle to deep-scan /reels/ tab")
    parser.add_argument("--hashtag", type=str, help="Discover reels by hashtag")
    parser.add_argument("--headful", action="store_true", help="Run browser in visible mode")

    args = parser.parse_args()
    researcher = InstagramReelsResearcher(headless=not args.headful)
    if args.handle:
        researcher.research_handle_reels(args.handle)
    elif args.hashtag:
        researcher.discover_reels_by_hashtag(args.hashtag)
    else:
        print("Please provide --handle <username> or --hashtag <tag>.")


if __name__ == "__main__":
    main()

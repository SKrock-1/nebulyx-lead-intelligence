"""
Autonomous Instagram Handle Lead Research Engine for Nebulyx
Takes an Instagram handle (@username), authenticates using active session (auth_state.json),
visually inspects recent posts/carousels/reels via WinRT OCR + Gemini Vision,
enriches bio websites via Agent-Reach, and generates Sellbird outreach sequences.
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
from vision_inspector import VisionInspector
from media_dom_extractor import inspect_post_multimodal, prescreen_explore_or_tag_grid
from sellbird_engine import SellbirdSalesEngine
from agent_reach_adapter import AgentReachAdapter

LEADS_JSON = os.path.join(CURRENT_DIR, "scraped_leads.json")
LEADS_CSV = os.path.join(CURRENT_DIR, "scraped_leads.csv")

HIRING_KEYWORDS = [
    "hiring", "looking for", "developer", "designer", "website", "web design",
    "crm", "ai agent", "bubble.io", "bubble", "full stack", "fullstack",
    "backend", "frontend", "freelance", "freelancers", "project basis",
    "dm me", "contact", "apply", "portfolio", "need developer", "we are looking",
]


class InstagramHandleResearcher:
    def __init__(self, headless=True):
        self.headless = headless
        self.engine = LeadIntelligenceEngine()
        self.vision = VisionInspector()
        self.sellbird = SellbirdSalesEngine()
        self.reach = AgentReachAdapter()
        self.login_mgr = InstagramLoginManager(AUTH_STATE_FILE)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
        )

    def clean_handle(self, handle_input):
        h = handle_input.strip()
        h = re.sub(r"^https?://(?:www\.)?instagram\.com/", "", h)
        h = h.strip("/").split("/")[0].split("?")[0]
        return h.lstrip("@").strip()

    def fetch_profile_and_posts(self, handle, max_posts=6):
        """
        Opens target Instagram profile with active auth_state.json, reads bio + external URL,
        visually pre-screens post/reel tiles, and runs multimodal OCR + Gemini inspection.
        """
        clean = self.clean_handle(handle)
        print(f"\n🔍 [Visual Handle Research]: @{clean}")

        profile_data = {
            "handle": clean,
            "full_name": clean,
            "bio": "",
            "bio_url": "",
            "profile_url": f"https://www.instagram.com/{clean}/",
            "posts": [],
        }

        # Supplement profile info via Agent-Reach if configured
        reach_prof = self.reach.fetch_instagram_profile(clean)
        if reach_prof.get("ok") and reach_prof.get("items"):
            first = reach_prof["items"][0]
            profile_data["bio"] = first.get("text") or profile_data["bio"]

        try:
            with sync_playwright() as pw:
                browser = launch_browser(pw, headless=self.headless)
                if os.path.exists(AUTH_STATE_FILE) and self.login_mgr.is_logged_in():
                    context = browser.new_context(
                        storage_state=AUTH_STATE_FILE,
                        user_agent=self.user_agent,
                        viewport={"width": 1280, "height": 850},
                    )
                else:
                    context = browser.new_context(
                        user_agent=self.user_agent,
                        viewport={"width": 1280, "height": 850},
                    )

                page = context.new_page()
                page.goto(profile_data["profile_url"], timeout=25000)
                page.wait_for_timeout(3200)

                # Extract header bio & link from rendered DOM
                try:
                    header_info = page.evaluate("""() => {
                        const header = document.querySelector('header');
                        const bioText = header ? header.innerText : '';
                        const ext = header ? header.querySelector('a[href*="l.instagram.com"], a[target="_blank"]') : null;
                        return { bioText, bioUrl: ext ? (ext.innerText || ext.getAttribute('href') || '') : '' };
                    }""")
                    if header_info.get("bioText"):
                        profile_data["bio"] = header_info["bioText"]
                    if header_info.get("bioUrl"):
                        profile_data["bio_url"] = header_info["bioUrl"]
                except Exception:
                    pass

                if not profile_data["bio"]:
                    meta_desc = page.locator('meta[name="description"]').get_attribute("content") or ""
                    profile_data["bio"] = meta_desc

                ranked_tiles = prescreen_explore_or_tag_grid(page, max_tiles=max_posts * 2)
                print(f"  ✓ Visually pre-screened {len(ranked_tiles)} posts/reels for @{clean}")

                for tile in ranked_tiles[:max_posts]:
                    post_url = tile["url"]
                    try:
                        mm = inspect_post_multimodal(page, post_url, self.vision, max_slides=3)
                        combined = mm["combined_text"]
                        text_lower = combined.lower()
                        matched_kws = [kw for kw in HIRING_KEYWORDS if kw in text_lower]

                        gemini_res = mm["visual_evidence"].get("gemini")
                        gemini_buyer = bool(gemini_res and gemini_res.get("is_buyer_hiring"))
                        is_hiring = gemini_buyer or len(matched_kws) > 0

                        profile_data["posts"].append({
                            "url": post_url,
                            "caption": mm["caption"],
                            "combined_text": combined,
                            "visual_evidence": mm["visual_evidence"],
                            "image_url": mm.get("primary_image_rel") or "",
                            "matched_hiring_keywords": matched_kws,
                            "is_hiring_lead": is_hiring,
                            "relevance_score": len(matched_kws) + (3 if gemini_buyer else 0),
                        })
                    except Exception as pe:
                        print(f"    ⚠️ Skipped post {post_url}: {pe}")

                browser.close()
        except Exception as be:
            print(f"  ❌ Browser crawl error: {be}")

        return profile_data

    def research_and_generate_lead(self, handle):
        """
        Orchestrates full multimodal research on a handle, enriches external bio websites
        via Agent-Reach, and stores a Sellbird-enriched CRM lead.
        """
        data = self.fetch_profile_and_posts(handle)
        clean = data["handle"]

        hiring_posts = sorted(
            [p for p in data["posts"] if p["is_hiring_lead"]],
            key=lambda x: x["relevance_score"],
            reverse=True,
        )
        selected = hiring_posts[0] if hiring_posts else (data["posts"][0] if data["posts"] else None)

        if selected:
            vis = selected["visual_evidence"]
            gemini_res = vis.get("gemini")
            target_text = f"{selected['combined_text']} {data['bio']}".strip()
            reel_url = selected["url"]
            image_url = selected.get("image_url", "")
            ocr_text = vis.get("ocr_text", "")
            vision_mode = vis.get("vision_mode", "WinRT Local OCR")
            captured_frames = vis.get("captured_frames", [])
            visual_critique = gemini_res.get("visual_design_critique", "") if gemini_res else ""
        else:
            gemini_res = None
            target_text = data["bio"]
            reel_url = data["profile_url"]
            image_url = ""
            ocr_text = ""
            vision_mode = "Profile DOM Only"
            captured_frames = []
            visual_critique = ""

        analysis = self.engine.generate_pitch({
            "company": (gemini_res.get("company_or_brand") if gemini_res else None) or data["full_name"] or clean,
            "author": clean,
            "caption": data["bio"],
            "flyer_text": target_text,
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

        web_enrichment = None
        if data.get("bio_url"):
            web_enrichment = self.reach.enrich_website_via_web(data["bio_url"])
            if web_enrichment:
                for e in web_enrichment.get("emails", []):
                    if e not in all_emails:
                        all_emails.append(e)

        primary_pillar = (
            (gemini_res.get("primary_pillar") if gemini_res else None)
            or (analysis["intent"]["primary"]["title"] if analysis["intent"]["primary"] else "Website Engineering & Digital Infrastructure")
        )
        matched_kws = (
            (gemini_res.get("requirements")[:6] if gemini_res and gemini_res.get("requirements") else None)
            or (analysis["intent"]["primary"]["matched_keywords"] if analysis["intent"]["primary"] else ["website", "developer"])
        )

        lead_record = {
            "id": f"lead_{clean}_{int(time.time())}",
            "company": analysis["company"],
            "instagram_handle": f"@{clean}",
            "profile_url": data["profile_url"],
            "reel_url": reel_url,
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
            "bio_summary": data["bio"][:250],
            "raw_text": target_text[:400],
            "visual_ocr_text": ocr_text[:400],
            "vision_mode": vision_mode,
            "captured_frames": captured_frames,
            "visual_critique": visual_critique,
            "web_enrichment": web_enrichment,
            "image_url": image_url,
            "source": "Handle Visual + Agent-Reach Research",
            "discovered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        enriched = self.sellbird.enrich_lead(lead_record)
        self.save_lead(enriched)
        return enriched

    def save_lead(self, lead_record):
        leads = []
        if os.path.exists(LEADS_JSON):
            try:
                with open(LEADS_JSON, "r", encoding="utf-8") as f:
                    leads = json.load(f)
            except Exception:
                leads = []

        leads = [l for l in leads if l.get("instagram_handle") != lead_record["instagram_handle"]]
        leads.insert(0, lead_record)

        with open(LEADS_JSON, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

        fieldnames = [
            "id", "company", "instagram_handle", "primary_requirement", "phone_whatsapp",
            "email", "sellbird_icp_score", "sellbird_tier", "whatsapp_link",
            "reel_url", "profile_url", "vision_mode", "source", "discovered_at",
        ]
        with open(LEADS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for l in leads:
                writer.writerow(l)

        print(f"\n💾 [Saved Lead]: {lead_record['company']} ({lead_record['instagram_handle']}) | {lead_record.get('vision_mode')}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Instagram Handle Visual Lead Research Engine")
    parser.add_argument("--handle", type=str, help="Single Instagram handle to research")
    parser.add_argument("--handles", nargs="+", help="Multiple Instagram handles to research")
    parser.add_argument("--headful", action="store_true", help="Run browser in visible mode")

    args = parser.parse_args()
    researcher = InstagramHandleResearcher(headless=not args.headful)
    targets = ([args.handle] if args.handle else []) + (args.handles or [])
    for h in (targets or ["skywalkfilmmakers"]):
        researcher.research_and_generate_lead(h)


if __name__ == "__main__":
    main()

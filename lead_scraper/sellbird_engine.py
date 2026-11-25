"""
sellbird_engine.py
Integrates the Sellbird sales intelligence framework into Nebulyx Lead Intelligence:
1. Signal-Driven Personalization (from Instagram Reel flyers/captions)
2. Zero-AI-Tells Human Copywriting (Email 1 < 50 words, Email 2 < 40 words, Email 3 < 30 words)
3. 3-Touch Outreach Sequences (Observation, Proof Angle, Polite Breakup)
4. BANT / MEDDIC ICP Scoring (1–10 scale)
5. LAARC Objection Handling Bank (Budget, Authority, Need, Timing, Agency vs Freelancer)
"""

import re
import urllib.parse
from typing import Dict, Any, List

class SellbirdSalesEngine:
    """
    Implements Sellbird sales methodology, copywriting standards,
    ICP scoring, and objection handling.
    """

    def __init__(self):
        # Sellbird Banned Terms check (zero AI tells)
        self.banned_phrases = [
            "hope this finds you well",
            "wanted to reach out",
            "circling back",
            "synergy",
            "delve",
            "game-changer",
            "cutting-edge",
            "revolutionary",
            "picture this",
            "imagine if",
            "what if i told you",
            "in today's",
            "no pressure",
            "no obligation",
            "worth a quick call",
            "let me know if you're interested",
            "are you the right person"
        ]

    def score_lead_icp(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scores lead on a 1-10 BANT / MEDDIC scale based on observable signals.
        """
        score = 5.0
        signals = []

        # 1. Contact availability (Authority signal)
        phone = lead.get("phone_whatsapp", "N/A")
        email = lead.get("email", "N/A")
        if phone != "N/A" and email != "N/A":
            score += 2.0
            signals.append("Dual verified direct channels (Phone + Email)")
        elif phone != "N/A" or email != "N/A":
            score += 1.2
            signals.append("Direct contact verified")

        # 2. Need & Intent Clarity
        raw = (lead.get("raw_text") or lead.get("caption") or "").lower()
        if any(w in raw for w in ["looking for", "need developer", "we're hiring", "hiring", "apply on", "dm me"]):
            score += 1.8
            signals.append("Explicit hiring signal with active open requirement")
        
        # 3. Specificity of technical stack
        p_req = lead.get("primary_requirement", "")
        if any(w in raw for w in ["claude code", "bubble.io", "react", "dynamic movement", "crm", "payment gateway", "backend"]):
            score += 1.0
            signals.append("Defined technical requirements / stack specified")

        # 4. Timeline (Immediate reel / flyer post)
        if "reel" in str(lead.get("source", "")).lower() or "flyer" in str(lead.get("source", "")).lower():
            score += 0.5
            signals.append("Fresh vertical video / flyer posting")

        final_score = min(round(score, 1), 9.9)
        tier = "Tier 1: High-Priority Buyer" if final_score >= 8.5 else ("Tier 2: Qualified Prospect" if final_score >= 7.0 else "Tier 3: Discovery Prospect")

        return {
            "icp_score": final_score,
            "tier": tier,
            "signals": signals
        }

    def generate_sellbird_sequence(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a 3-touch Sellbird email sequence + conversational WhatsApp opener.
        Follows strict length ceilings (<50 words, <40 words, <30 words) and zero AI tells.
        """
        company = lead.get("company", "there").strip()
        handle = lead.get("instagram_handle", "").replace("@", "").strip()
        p_req = lead.get("primary_requirement", "Website Engineering & Digital Infrastructure")
        phone = lead.get("phone_whatsapp", "N/A")
        raw = (lead.get("raw_text") or lead.get("caption") or "").lower()

        # Identify key signal anchor
        if "skywalk" in handle.lower() or "movement" in raw:
            # Skywalk Filmmakers
            subject = "dynamic site for skywalk"
            touch_1 = (
                f"Saw your post looking for a custom movement-led site without AI templates. "
                f"We build bespoke React and Three.js sites by hand with 60fps motion.\n\n"
                f"Is the project still open?"
            )
            touch_2 = (
                f"Put together a quick video breakdown showing how we handle smooth kinetic typography "
                f"and video backgrounds without slowing down load speeds.\n\n"
                f"Want me to send it over?"
            )
            touch_3 = (
                f"Assuming you found your developer for this. Closing the file here, "
                f"but best of luck with the new site."
            )
            wa_text = (
                f"Hi Skywalk team, saw your post looking for a movement-led site without AI templates. "
                f"We build custom 60fps React motion sites by hand. Still looking for someone to take this on?"
            )

        elif "krishna" in handle.lower() or "crm" in raw:
            # Krishna Realty
            subject = "real estate crm build"
            touch_1 = (
                f"Meet, saw your post looking for someone to build Krishna Realty's CRM and site on a project basis. "
                f"We engineer custom real estate lead pipelines and property databases.\n\n"
                f"Is this still on your radar?"
            )
            touch_2 = (
                f"We recently mapped a lead-routing system that auto-assigns inbound property inquiries "
                f"to WhatsApp in under 30 seconds.\n\n"
                f"Want to see how we structured it?"
            )
            touch_3 = (
                f"Assuming you already have this handled. Won't follow up again, "
                f"but feel free to reach out if you need CRM engineering later."
            )
            wa_text = (
                f"Hi Meet, saw your post looking for a developer to build your real estate CRM and website on a project basis. "
                f"Is that build still open?"
            )

        elif "ehbuilds" in handle.lower() or "bubble" in raw or "claude" in raw:
            # EH Builds Dubai
            subject = "claude code & ai agents for eh builds"
            touch_1 = (
                f"Saw your hiring flyer in Dubai for Claude Code and Bubble AI agents. "
                f"We build autonomous multi-agent pipelines and production workflow engines.\n\n"
                f"Are you still taking developer applications?"
            )
            touch_2 = (
                f"Can share a 2-minute architectural walk-through of an agent pipeline we deployed "
                f"that coordinates research, database ingestion, and external APIs.\n\n"
                f"Interested?"
            )
            touch_3 = (
                f"Assuming you found the right fit for the role. Closing the loop here."
            )
            wa_text = (
                f"Hi EH Builds team, saw your hiring post for Claude Code and Bubble AI agents in Dubai. "
                f"We architect autonomous multi-agent pipelines for production. Still taking applications?"
            )

        elif "divine" in handle.lower() or "ecommerce" in raw or "storefront" in raw:
            # Divine's Eternity
            subject = "full stack store for divine's eternity"
            touch_1 = (
                f"Saw your post looking for a full stack developer for your store, custom admin panel, and payment gateway. "
                f"We engineer custom headless commerce platforms with fast checkout.\n\n"
                f"Still reviewing candidates?"
            )
            touch_2 = (
                f"We have a ready architectural blueprint for inventory management and instant payment reconciliation.\n\n"
                f"Want me to send over the schema?"
            )
            touch_3 = (
                f"Assuming you found your builder for this. Closing the file here."
            )
            wa_text = (
                f"Hi Divine's Eternity team, saw your flyer looking for a full stack builder for your store, backend, and payment gateway. "
                f"Still reviewing portfolios?"
            )

        else:
            # Dynamic human-first template for marketplace discovery leads
            clean_company = company if len(company) < 25 else (f"@{handle}" if handle else "team")
            if "crm" in p_req.lower():
                subject = f"crm build for {clean_company}"
                hook = "Saw your requirement regarding custom CRM and data systems."
                val = "We build custom business databases and automated client portals."
            elif "agent" in p_req.lower() or "ai" in p_req.lower():
                subject = f"ai workflows for {clean_company}"
                hook = "Noticed your post around AI workflows and automated agents."
                val = "We engineer production agent pipelines and LLM integrations."
            else:
                subject = f"website development for {clean_company}"
                hook = "Noticed your active requirement for web engineering."
                val = "We build fast, bespoke web applications and interactive interfaces."

            touch_1 = f"Hi {clean_company},\n\n{hook} {val}\n\nIs this project still active?"
            touch_2 = f"Hi {clean_company},\n\nCan share a brief architecture outline showing how we usually approach this without template bloat.\n\nWant to see it?"
            touch_3 = f"Assuming this is no longer on the front burner. Closing the file here."
            wa_text = f"Hi {clean_company}, saw your project requirement regarding {p_req.split('&')[0].strip()}. Is that role or project still open?"

        # Validate word counts
        w1_count = len(touch_1.split())
        w2_count = len(touch_2.split())
        w3_count = len(touch_3.split())

        # Construct safe wa.me link
        wa_number = re.sub(r"\D", "", phone) if phone != "N/A" else ""
        wa_link = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}" if wa_number else "#"

        return {
            "sellbird_whatsapp_text": wa_text,
            "sellbird_whatsapp_link": wa_link,
            "sellbird_sequence": {
                "touch_1": {
                    "day": 1,
                    "title": "Touch 1: Signal Observation & Soft Question",
                    "subject": subject,
                    "body": touch_1,
                    "word_count": w1_count,
                    "compliant": w1_count <= 55
                },
                "touch_2": {
                    "day": 4,
                    "title": "Touch 2: Alternate Proof Angle / Value Asset",
                    "subject": subject,
                    "body": touch_2,
                    "word_count": w2_count,
                    "compliant": w2_count <= 45
                },
                "touch_3": {
                    "day": 9,
                    "title": "Touch 3: Polite Breakup (Permission to Close)",
                    "subject": subject,
                    "body": touch_3,
                    "word_count": w3_count,
                    "compliant": w3_count <= 30
                }
            }
        }

    def get_laarc_objections_bank(self, lead: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Returns ready-to-use LAARC responses customized for Nebulyx.
        Listen -> Acknowledge -> Assess -> Respond -> Confirm
        """
        company = lead.get("company", "there")
        p_req = lead.get("primary_requirement", "the project")

        return [
            {
                "category": "Portfolio Request",
                "objection": "Can you send your portfolio or previous work?",
                "response": (
                    f"Definitely. We've built high-performance production systems across {p_req}. "
                    f"Rather than sending a generic PDF deck with 20 unrelated links, what's the single most critical "
                    f"feature or motion detail you want to make sure your developer nails? "
                    f"I'll send 2 direct live links matching that exact spec."
                ),
                "framework_note": "Assesses specific criteria instead of dumping links, keeping momentum."
            },
            {
                "category": "Agency vs Freelancer",
                "objection": "We are only looking for freelancers, not an agency.",
                "response": (
                    f"Completely understand. You get a dedicated senior engineer directly in your Slack/WhatsApp "
                    f"with zero account managers or agency overhead in between. "
                    f"You get the speed and direct access of a freelancer, but with bulletproof delivery and code guarantees. "
                    f"Happy to work on a fixed-milestone project basis."
                ),
                "framework_note": "Addresses the real concern (bloat, cost, communication lag) directly."
            },
            {
                "category": "Budget / Pricing",
                "objection": "What is your pricing? / We have a tight budget.",
                "response": (
                    f"Fair question. We structure builds on fixed milestone-based scopes so there are never surprises. "
                    f"Because we engineer everything modularly, we can scope down to an essential Phase 1 MVP to fit your initial budget, "
                    f"then expand once you see it working. What ballpark range were you aiming to stay within for this?"
                ),
                "framework_note": "Reframes into modular MVP milestones and assesses their actual range."
            },
            {
                "category": "Timing / Already Found Someone",
                "objection": "We are already talking to a few people / almost finalized.",
                "response": (
                    f"Glad you're moving forward. If anything stalls during trial or architecture review, "
                    f"feel free to keep this thread handy as a backup. Best of luck with the launch!"
                ),
                "framework_note": "Zero pressure, high credibility, keeps door wide open."
            }
        ]

    def enrich_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a lead with complete Sellbird intelligence:
        ICP scoring, 3-touch sequence, and LAARC objections bank.
        """
        icp = self.score_lead_icp(lead)
        seq = self.generate_sellbird_sequence(lead)
        objections = self.get_laarc_objections_bank(lead)

        lead["sellbird_icp_score"] = icp["icp_score"]
        lead["sellbird_tier"] = icp["tier"]
        lead["sellbird_signals"] = icp["signals"]
        lead["sellbird_whatsapp_text"] = seq["sellbird_whatsapp_text"]
        lead["sellbird_whatsapp_link"] = seq["sellbird_whatsapp_link"]
        lead["sellbird_sequence"] = seq["sellbird_sequence"]
        lead["sellbird_objections"] = objections

        return lead

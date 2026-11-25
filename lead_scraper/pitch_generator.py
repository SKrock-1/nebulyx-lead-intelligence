"""
Nebulyx Lead Intelligence & Strategic Outreach Pitch Generator
Analyzes scraped Reel metadata, flyer text, and user requirements, matches them
to Nebulyx corporate capabilities, and generates high-converting WhatsApp & Email pitches.
"""

import re
import urllib.parse

# Normalized Nebulyx Service Pillars from corporate capability document
NEBULYX_CAPABILITIES = {
    "web_engineering": {
        "title": "Website Engineering & Digital Infrastructure",
        "keywords": ["website", "web design", "developer", "responsive", "custom website", "full stack", "frontend", "backend", "motion", "ui/ux"],
        "pitch_hook": "We design and engineer bespoke, high-performance web infrastructure tailored to modern brands — completely custom-built with dynamic motion and clean architecture (no generic AI-slop).",
        "proof_points": ["Custom React / Next.js architecture", "Movement-led dynamic design", "Zero-dependency scalability"]
    },
    "ai_automation": {
        "title": "Multi-Agent Workflows & AI Systems",
        "keywords": ["ai agent", "ai agents", "claude code", "bubble.io", "automation", "intelligent workflows", "llm"],
        "pitch_hook": "We specialize in autonomous multi-agent workflows and custom AI integrations that eliminate repetitive operations and power scalable business logic.",
        "proof_points": ["Autonomous agent pipelines", "Production API & LLM integration", "Bubble.io / Next.js hybrid systems"]
    },
    "crm_enterprise": {
        "title": "Custom Web Applications & CRM Systems",
        "keywords": ["crm", "crm application", "portal", "admin panel", "database", "internal tools", "lead management"],
        "pitch_hook": "We engineer robust, custom CRM systems and internal business web applications engineered around your exact sales, client, and transaction workflows.",
        "proof_points": ["Custom pipeline & lead tracking", "Role-based access & admin control", "Integrated client portals"]
    },
    "digital_commerce": {
        "title": "Digital Commerce & Scalable Storefronts",
        "keywords": ["ecommerce", "e-commerce", "store", "product management", "payment gateway", "checkout", "gifts", "shopify"],
        "pitch_hook": "We build fast, secure e-commerce storefronts with seamless payment gateways, product catalogs, and automated backend order fulfilment.",
        "proof_points": ["High-conversion checkout architecture", "Automated inventory & payments", "Clean code & speed optimization"]
    }
}

class LeadIntelligenceEngine:
    def __init__(self, agency_name="Nebulyx", agency_tagline="Technology, Thoughtfully Engineered."):
        self.agency_name = agency_name
        self.agency_tagline = agency_tagline

    def extract_contacts(self, text):
        """Extracts emails and phone numbers with international formatting."""
        # Clean text
        text = text.replace("\u202c", "").replace("\u202a", "").replace("\xa0", " ")
        
        # Email Regex
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = list(set(re.findall(email_pattern, text)))

        # Phone Regex (handles Indian +91, UAE +971, local numbers)
        phone_pattern = r'(?:\+?(\d{1,3}))?[-.\s]?(?:\(?(\d{2,4})\)?)?[-.\s]?(\d{3,5})[-.\s]?(\d{4,5})'
        potential_phones = re.findall(r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}', text)
        
        phones = []
        for p in potential_phones:
            digits = re.sub(r'\D', '', p)
            if len(digits) >= 10 and len(digits) <= 14:
                # Format clean international string
                if not p.startswith("+") and len(digits) == 10:
                    clean_phone = f"+91 {digits[:5]} {digits[5:]}"
                else:
                    clean_phone = p.strip()
                if clean_phone not in phones:
                    phones.append(clean_phone)

        return {"emails": emails, "phones": phones}

    def classify_project_intent(self, text):
        """Determines matching service pillars and priority score."""
        text_lower = text.lower()
        matched_pillars = []

        pillar_weights = {
            "ai_automation": 2.0,
            "crm_enterprise": 1.8,
            "digital_commerce": 1.5,
            "web_engineering": 1.0
        }

        for pillar_key, pillar_info in NEBULYX_CAPABILITIES.items():
            matches = [kw for kw in pillar_info["keywords"] if kw in text_lower]
            if matches:
                weight = pillar_weights.get(pillar_key, 1.0)
                score = len(matches) * weight
                matched_pillars.append({
                    "pillar": pillar_key,
                    "title": pillar_info["title"],
                    "match_count": len(matches),
                    "score": score,
                    "matched_keywords": matches,
                    "hook": pillar_info["pitch_hook"],
                    "proof": pillar_info["proof_points"]
                })

        # Sort by weighted score
        matched_pillars.sort(key=lambda x: x["score"], reverse=True)
        primary = matched_pillars[0] if matched_pillars else None
        return {"primary": primary, "all_matched": matched_pillars}

    def generate_pitch(self, lead_data):
        """Generates tailored WhatsApp and Email proposals addressing the client's explicit requirements."""
        company = lead_data.get("company") or lead_data.get("author") or "Team"
        raw_text = lead_data.get("caption", "") + " " + lead_data.get("flyer_text", "")
        contacts = self.extract_contacts(raw_text)
        intent = self.classify_project_intent(raw_text)

        primary_pillar = intent["primary"]
        service_hook = primary_pillar["hook"] if primary_pillar else "We engineer dependable, custom software and web systems built for scale."

        # Specific custom hooks from reel requirements
        custom_notes = []
        if "not ai-made" in raw_text.lower():
            custom_notes.append("• 100% human-crafted engineering with clean, modular code (zero boilerplate AI slop)")
        if "movement" in raw_text.lower() or "motion" in raw_text.lower():
            custom_notes.append("• Sophisticated dynamic motion design (GSAP / WebGL / Framer-level smoothness)")
        if "crm" in raw_text.lower():
            custom_notes.append("• Custom database & business logic engineered specifically for your operational pipeline")
        if "ai agent" in raw_text.lower() or "claude" in raw_text.lower():
            custom_notes.append("• Autonomous multi-agent pipelines with robust API orchestration & error boundary handling")

        custom_points_text = "\n".join(custom_notes) if custom_notes else "• Production-ready performance, fast turnarounds, and direct engineering collaboration"

        # WhatsApp Direct Message Pitch
        whatsapp_pitch = (
            f"Hello {company} team! 👋\n\n"
            f"Saw your recent hiring requirement regarding {primary_pillar['title'] if primary_pillar else 'your development project'}.\n\n"
            f"At *{self.agency_name}* ({self.agency_tagline}), this is our core domain:\n"
            f"{service_hook}\n\n"
            f"Why we're an ideal fit for your project:\n"
            f"{custom_points_text}\n\n"
            f"We would love to share relevant live systems we've built and discuss how we can execute this for you on schedule.\n\n"
            f"When would be a good time for a quick 10-minute discovery call?"
        )

        # Email Proposal Pitch
        email_subject = f"Proposal: {primary_pillar['title'] if primary_pillar else 'Development & Engineering Partner'} — {self.agency_name} for {company}"
        email_body = (
            f"Dear {company} Team,\n\n"
            f"I came across your active requirement looking for an experienced developer & engineering partner.\n\n"
            f"At {self.agency_name} ({self.agency_tagline}), we design, engineer, and deploy high-performance digital systems. "
            f"Unlike traditional freelancers or generic agencies, we operate as a dedicated technology partner with deep full-stack engineering discipline.\n\n"
            f"Key Capabilities Aligned with Your Project:\n"
            f"{custom_points_text}\n\n"
            f"We are ready to start immediately and can provide a transparent scope, architecture breakdown, and delivery roadmap.\n\n"
            f"Could we schedule a brief 10-minute introductory call this week to review your exact specifications?\n\n"
            f"Warm regards,\n"
            f"Engineering Team | {self.agency_name}\n"
            f"Technology, Thoughtfully Engineered."
        )

        # Generate 1-click WhatsApp Link if phone exists
        whatsapp_link = ""
        if contacts["phones"]:
            first_phone = re.sub(r'\D', '', contacts["phones"][0])
            encoded_msg = urllib.parse.quote(whatsapp_pitch)
            whatsapp_link = f"https://wa.me/{first_phone}?text={encoded_msg}"

        return {
            "company": company,
            "contacts": contacts,
            "intent": intent,
            "whatsapp_pitch": whatsapp_pitch,
            "whatsapp_link": whatsapp_link,
            "email_subject": email_subject,
            "email_body": email_body
        }

if __name__ == "__main__":
    engine = LeadIntelligenceEngine()
    print("Intelligence engine ready.")

"""
build_luxury_dashboard.py
Builds the Vanguard Obsidian & Platinum Agency-Grade Nebulyx Dashboard.
Design Philosophy:
- Double-Bezel ("Doppelrand") nested hardware surfaces
- Zero Emojis — 1.5px stroke architectural SVG iconography exclusively
- Outfit + JetBrains Mono typography with tabular-nums telemetry
- App-Shell Executive Sidebar + Asymmetric Bento KPI Row + Card/Table View Toggle
- Slide-over Sellbird Flight Deck Drawer + Flyer Lightbox + Persistent CRM Stage Tracking
- Floating Toast Stack replacing browser alert() popups
"""

import json
import os


def build_luxury_dashboard():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    leads_path = os.path.join(base_dir, "scraped_leads.json")
    out_path = os.path.join(base_dir, "dashboard.html")

    with open(leads_path, "r", encoding="utf-8") as f:
        clean_leads = json.load(f)

    # Ensure every lead has default crm_stage
    for l in clean_leads:
        if "crm_stage" not in l:
            l["crm_stage"] = "new"

    json_str = json.dumps(clean_leads, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nebulyx Studio — Reel Signal Intelligence &amp; Sellbird CRM</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23101218'/%3E%3Cpath d='M9 23V9l14 14V9' fill='none' stroke='%23F4F4F5' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-canvas: #08090C;
            --bg-rail: #0B0C10;
            --bg-bezel-outer: rgba(255, 255, 255, 0.024);
            --bg-core: #101218;
            --bg-core-hover: #141720;
            --bg-elevated: #171A23;
            --border-hairline: rgba(255, 255, 255, 0.065);
            --border-bright: rgba(255, 255, 255, 0.13);
            --text-primary: #F4F4F5;
            --text-secondary: #A1A1AA;
            --text-muted: #646875;
            --accent-gold: #E2C275;
            --accent-gold-dim: rgba(226, 194, 117, 0.12);
            --accent-emerald: #34D399;
            --accent-emerald-dim: rgba(52, 211, 153, 0.11);
            --accent-sky: #7DD3FC;
            --accent-amber: #FBBF24;
            --accent-rose: #FB7185;
            --spring: cubic-bezier(0.32, 0.72, 0, 1);
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        /* Native Studio Scrollbars */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 999px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.2); }}

        /* Focus Accessibility */
        :focus-visible {{
            outline: 2px solid rgba(255, 255, 255, 0.35);
            outline-offset: 2px;
        }}

        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}

        html, body {{
            background-color: var(--bg-canvas);
            color: var(--text-primary);
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100dvh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
        }}

        /* Subtle Fixed Noise Grain & Overhead Ambient Wash (GPU Safe) */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 1;
            background: radial-gradient(ellipse 75% 42% at 55% -12%, rgba(255, 255, 255, 0.045) 0%, transparent 70%);
        }}

        body::after {{
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 60;
            opacity: 0.025;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
        }}

        .mono {{
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }}

        /* App Shell Architecture */
        .app-shell {{
            display: grid;
            grid-template-columns: 268px minmax(0, 1fr);
            min-height: 100dvh;
            position: relative;
            z-index: 2;
        }}

        /* Left Executive Navigation Rail */
        .sidebar-rail {{
            background: var(--bg-rail);
            border-right: 1px solid var(--border-hairline);
            padding: 1.5rem 1.15rem;
            display: flex;
            flex-direction: column;
            gap: 1.75rem;
            position: sticky;
            top: 0;
            height: 100dvh;
            overflow-y: auto;
        }}

        .brand-lockup {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 0.35rem;
        }}

        .brand-left {{
            display: flex;
            align-items: center;
            gap: 11px;
        }}

        .brand-mark {{
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: linear-gradient(180deg, #1E212B 0%, #11131A 100%);
            border: 1px solid var(--border-bright);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .brand-name {{
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text-primary);
        }}

        .brand-version {{
            font-size: 0.65rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            border: 1px solid var(--border-hairline);
            padding: 2px 7px;
            border-radius: 999px;
        }}

        .rail-section {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .rail-heading {{
            font-size: 0.68rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-muted);
            padding: 0 0.65rem 0.4rem;
        }}

        .rail-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.55rem 0.7rem;
            border-radius: 10px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 0.875rem;
            font-weight: 400;
            cursor: pointer;
            text-align: left;
            transition: all 0.25s var(--spring);
            width: 100%;
        }}

        .rail-item-left {{
            display: flex;
            align-items: center;
            gap: 9px;
        }}

        .rail-item:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.03);
        }}

        .rail-item.active {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.055);
            border-color: var(--border-hairline);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.07);
            font-weight: 500;
        }}

        .rail-count {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        .rail-item.active .rail-count {{
            color: var(--text-primary);
        }}

        .pillar-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        /* Rail Footer Status */
        .rail-footer {{
            margin-top: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding-top: 1rem;
            border-top: 1px solid var(--border-hairline);
        }}

        .session-box {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-hairline);
            border-radius: 12px;
            padding: 0.75rem 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .session-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.78rem;
        }}

        .live-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--accent-emerald);
            box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
            animation: breathe 2.4s infinite ease-in-out;
        }}

        @keyframes breathe {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.45; transform: scale(0.88); }}
        }}

        .export-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}

        .export-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 0.5rem;
            border-radius: 9px;
            border: 1px solid var(--border-hairline);
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-secondary);
            font-size: 0.75rem;
            text-decoration: none;
            transition: all 0.25s var(--spring);
        }}

        .export-btn:hover {{
            color: var(--text-primary);
            border-color: var(--border-bright);
            background: rgba(255, 255, 255, 0.045);
        }}

        /* Main Workspace Canvas */
        .workspace-main {{
            padding: 1.5rem 2.25rem 4rem;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 1.75rem;
        }}

        /* Top Command Bar (Detached Floating Shell Feel) */
        .top-command-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .mobile-menu-btn {{
            display: none;
            background: var(--bg-core);
            border: 1px solid var(--border-hairline);
            color: var(--text-primary);
            padding: 0.55rem;
            border-radius: 10px;
            cursor: pointer;
        }}

        .command-search-shell {{
            flex: 1;
            min-width: 260px;
            max-width: 460px;
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            color: var(--text-muted);
            pointer-events: none;
        }}

        .command-search-input {{
            width: 100%;
            background: rgba(255, 255, 255, 0.028);
            border: 1px solid var(--border-hairline);
            border-radius: 999px;
            padding: 0.62rem 3.5rem 0.62rem 2.5rem;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.875rem;
            outline: none;
            transition: all 0.3s var(--spring);
        }}

        .command-search-input:focus {{
            background: rgba(255, 255, 255, 0.045);
            border-color: var(--border-bright);
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.04);
        }}

        .shortcut-hint {{
            position: absolute;
            right: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            color: var(--text-muted);
            border: 1px solid var(--border-hairline);
            padding: 2px 6px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.25);
            pointer-events: none;
        }}

        .top-actions-cluster {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .scout-mode-pills {{
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid var(--border-hairline);
            border-radius: 999px;
            padding: 3px;
            gap: 2px;
        }}

        .pill-trigger {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.42rem 0.85rem;
            border-radius: 999px;
            cursor: pointer;
            transition: all 0.25s var(--spring);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .pill-trigger:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.06);
        }}

        /* Button-in-Button "Island" Primary CTA */
        .btn-island-primary {{
            background: #F4F4F5;
            color: #09090B;
            border: none;
            border-radius: 999px;
            padding: 5px 6px 5px 18px;
            font-family: inherit;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: transform 0.35s var(--spring), background-color 0.25s ease;
            box-shadow: 0 4px 20px rgba(255, 255, 255, 0.08);
        }}

        .btn-island-primary:hover {{
            background: #FFFFFF;
            transform: translateY(-1px);
        }}

        .btn-island-primary:active {{
            transform: scale(0.975);
        }}

        .btn-island-icon {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: rgba(9, 9, 11, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.4s var(--spring), background-color 0.3s ease;
        }}

        .btn-island-primary:hover .btn-island-icon {{
            transform: translate(1px, -1px) scale(1.06);
            background: rgba(9, 9, 11, 0.16);
        }}

        /* Double-Bezel ("Doppelrand") Container System */
        .bezel-outer {{
            background: var(--bg-bezel-outer);
            border: 1px solid var(--border-hairline);
            border-radius: 20px;
            padding: 5px;
            position: relative;
        }}

        .bezel-core {{
            background: var(--bg-core);
            border: 1px solid rgba(255, 255, 255, 0.045);
            border-radius: 15px;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.065);
            position: relative;
            overflow: hidden;
        }}

        /* Mouse Spotlight Layer on Cards */
        .spotlight-card::before {{
            content: '';
            position: absolute;
            inset: 0;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.4s ease;
            background: radial-gradient(420px circle at var(--mx, 50%) var(--my, 50%), rgba(255, 255, 255, 0.065), transparent 65%);
            z-index: 1;
        }}

        .spotlight-card:hover::before {{
            opacity: 1;
        }}

        /* Asymmetric Bento Telemetry Row */
        .bento-telemetry-grid {{
            display: grid;
            grid-template-columns: 1.45fr 1.15fr 1fr;
            gap: 1.15rem;
        }}

        .bento-pad {{
            padding: 1.25rem 1.4rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 1rem;
        }}

        .eyebrow-tag {{
            font-size: 0.68rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: var(--text-muted);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .kpi-hero-row {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 12px;
        }}

        .kpi-big-num {{
            font-size: 2.35rem;
            font-weight: 600;
            letter-spacing: -0.04em;
            color: var(--text-primary);
            line-height: 1;
        }}

        .kpi-delta {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            color: var(--accent-emerald);
            background: var(--accent-emerald-dim);
            padding: 3px 9px;
            border-radius: 999px;
        }}

        .distribution-bar {{
            height: 6px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 999px;
            overflow: hidden;
            display: flex;
            gap: 2px;
        }}

        .dist-seg {{
            height: 100%;
            transition: width 0.6s var(--spring);
        }}

        .dist-legend {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.73rem;
            color: var(--text-secondary);
            flex-wrap: wrap;
            gap: 8px;
        }}

        /* Handle Ingest Mini-Form inside Bento 3 */
        .ingest-mini-row {{
            display: flex;
            gap: 6px;
        }}

        .ingest-mini-input {{
            flex: 1;
            min-width: 0;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-hairline);
            border-radius: 10px;
            padding: 0.52rem 0.75rem;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            outline: none;
            transition: border-color 0.25s ease;
        }}

        .ingest-mini-input:focus {{
            border-color: var(--border-bright);
        }}

        .btn-ingest-submit {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-hairline);
            color: var(--text-primary);
            border-radius: 10px;
            padding: 0 0.9rem;
            font-family: inherit;
            font-size: 0.78rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.25s var(--spring);
            white-space: nowrap;
        }}

        .btn-ingest-submit:hover {{
            background: rgba(255, 255, 255, 0.14);
        }}

        /* Live Scan Progress Banner */
        .scan-progress-bezel {{
            display: none;
            animation: fadeUp 0.4s var(--spring);
        }}

        @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .skeleton-line {{
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.09) 50%, rgba(255,255,255,0.03) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.6s infinite linear;
        }}

        @keyframes shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}

        /* Section Header Bar + View Switcher */
        .section-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .section-title-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-title {{
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }}

        .section-count-chip {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-hairline);
            padding: 2px 9px;
            border-radius: 999px;
        }}

        .view-toggle-group {{
            display: inline-flex;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid var(--border-hairline);
            padding: 3px;
            border-radius: 10px;
            gap: 2px;
        }}

        .view-toggle-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 5px 11px;
            border-radius: 7px;
            font-family: inherit;
            font-size: 0.78rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .view-toggle-btn.active {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
        }}

        /* Priority Archetype Showcase (Asymmetric Horizontal 2-Col Feature) */
        .priority-showcase-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1.15rem;
        }}

        .priority-card-inner {{
            padding: 1.35rem;
            display: grid;
            grid-template-columns: 92px minmax(0, 1fr);
            gap: 1.25rem;
            align-items: stretch;
        }}

        .flyer-thumb-frame {{
            position: relative;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-hairline);
            background: #08090C;
            cursor: pointer;
            aspect-ratio: 3 / 4;
            align-self: start;
        }}

        .flyer-thumb-frame img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s var(--spring), filter 0.4s ease;
        }}

        .flyer-thumb-frame:hover img {{
            transform: scale(1.06);
        }}

        .flyer-zoom-hint {{
            position: absolute;
            inset: auto 6px 6px 6px;
            background: rgba(8, 9, 12, 0.78);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            padding: 3px 6px;
            font-size: 0.62rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            text-align: center;
            opacity: 0;
            transform: translateY(4px);
            transition: all 0.3s var(--spring);
        }}

        .flyer-thumb-frame:hover .flyer-zoom-hint {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* Standard Dossier Cards Grid (2-Col Editorial Density, No Boring 3-Col) */
        .dossier-cards-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1.15rem;
        }}

        .dossier-inner {{
            padding: 1.35rem 1.45rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            height: 100%;
            position: relative;
            z-index: 2;
        }}

        .card-meta-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
        }}

        .company-title {{
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .gold-verified-pill {{
            font-size: 0.64rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--accent-gold);
            background: var(--accent-gold-dim);
            border: 1px solid rgba(226, 194, 117, 0.25);
            padding: 2px 7px;
            border-radius: 999px;
        }}

        .handle-anchor {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: var(--text-secondary);
            text-decoration: none;
            margin-top: 3px;
            transition: color 0.2s ease;
        }}

        .handle-anchor:hover {{
            color: var(--text-primary);
        }}

        .right-badges {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }}

        .icp-score-chip {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--accent-emerald);
            background: var(--accent-emerald-dim);
            border: 1px solid rgba(52, 211, 153, 0.2);
            padding: 3px 9px;
            border-radius: 8px;
        }}

        /* Interactive CRM Stage Badge */
        .stage-select {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-hairline);
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 3px 8px;
            border-radius: 7px;
            cursor: pointer;
            outline: none;
            transition: all 0.2s ease;
        }}

        .stage-select:hover {{
            border-color: var(--border-bright);
            color: var(--text-primary);
        }}

        .stage-select option {{
            background: #101218;
            color: #F4F4F5;
        }}

        /* Contact Telemetry Strip */
        .contact-bar {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            padding: 0.65rem 0.85rem;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.26);
            border: 1px solid rgba(255, 255, 255, 0.04);
        }}

        .contact-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
            color: var(--text-secondary);
        }}

        .contact-chip.has-value {{
            color: var(--text-primary);
        }}

        .micro-copy-btn {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid transparent;
            color: var(--text-muted);
            width: 22px;
            height: 22px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .micro-copy-btn:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--border-hairline);
        }}

        .signal-excerpt {{
            font-size: 0.875rem;
            line-height: 1.55;
            color: var(--text-secondary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .pillar-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.73rem;
            font-weight: 500;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-hairline);
            padding: 3px 9px;
            border-radius: 6px;
            width: fit-content;
        }}

        .card-footer-actions {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-top: auto;
            padding-top: 0.4rem;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
        }}

        .btn-wa-clean {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(52, 211, 153, 0.12);
            border: 1px solid rgba(52, 211, 153, 0.28);
            color: var(--accent-emerald);
            padding: 0.5rem 0.95rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.3s var(--spring);
        }}

        .btn-wa-clean:hover {{
            background: rgba(52, 211, 153, 0.2);
            border-color: rgba(52, 211, 153, 0.5);
            transform: translateY(-1px);
        }}

        .btn-wa-clean.disabled {{
            opacity: 0.4;
            pointer-events: none;
        }}

        .btn-deck-open {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-hairline);
            color: var(--text-primary);
            padding: 4px 5px 4px 13px;
            border-radius: 999px;
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.35s var(--spring);
        }}

        .btn-deck-open:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--border-bright);
        }}

        .btn-deck-circle {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.35s var(--spring);
        }}

        .btn-deck-open:hover .btn-deck-circle {{
            transform: translate(1px, -1px) scale(1.06);
        }}

        /* Precision Data Table View */
        .table-wrapper {{
            width: 100%;
            overflow-x: auto;
        }}

        .crm-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.85rem;
        }}

        .crm-table th {{
            font-size: 0.68rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
            padding: 0.85rem 1rem;
            border-bottom: 1px solid var(--border-hairline);
        }}

        .crm-table td {{
            padding: 0.9rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            vertical-align: middle;
        }}

        .crm-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        /* Right Slide-Over Deal Flight Deck Drawer */
        .drawer-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(4, 5, 8, 0.72);
            backdrop-filter: blur(8px);
            z-index: 40;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s var(--spring);
        }}

        .drawer-backdrop.open {{
            opacity: 1;
            pointer-events: auto;
        }}

        .flight-drawer {{
            position: fixed;
            top: 12px;
            right: 12px;
            bottom: 12px;
            width: min(650px, calc(100vw - 24px));
            background: #0D0F14;
            border: 1px solid var(--border-bright);
            border-radius: 20px;
            box-shadow: -20px 0 70px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            z-index: 50;
            transform: translateX(calc(100% + 24px));
            transition: transform 0.55s var(--spring);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .flight-drawer.open {{
            transform: translateX(0);
        }}

        .drawer-header {{
            padding: 1.5rem 1.75rem 1.25rem;
            border-bottom: 1px solid var(--border-hairline);
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
        }}

        .drawer-close-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-hairline);
            color: var(--text-secondary);
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }}

        .drawer-close-btn:hover {{
            background: rgba(255, 255, 255, 0.12);
            color: var(--text-primary);
        }}

        .drawer-body {{
            padding: 1.4rem 1.75rem 2rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1.4rem;
            flex: 1;
        }}

        .drawer-segmented-tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-hairline);
            padding: 4px;
            border-radius: 12px;
            gap: 4px;
        }}

        .drawer-tab {{
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 0.82rem;
            font-weight: 500;
            padding: 0.55rem 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.25s var(--spring);
        }}

        .drawer-tab.active {{
            background: rgba(255, 255, 255, 0.085);
            color: var(--text-primary);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }}

        .touch-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-hairline);
            border-radius: 14px;
            padding: 1.15rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 0.9rem;
        }}

        .touch-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}

        .touch-copy-pre {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.81rem;
            line-height: 1.6;
            color: #E4E4E7;
            background: rgba(0, 0, 0, 0.32);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            white-space: pre-wrap;
        }}

        /* Flyer Lightbox Modal */
        .lightbox-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(4, 5, 8, 0.88);
            backdrop-filter: blur(12px);
            z-index: 70;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}

        .lightbox-overlay.open {{
            display: flex;
            animation: fadeUp 0.3s var(--spring);
        }}

        .lightbox-card {{
            max-width: 540px;
            max-height: 90dvh;
            background: #101218;
            border: 1px solid var(--border-bright);
            border-radius: 18px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .lightbox-card img {{
            max-height: 76dvh;
            width: 100%;
            object-fit: contain;
            border-radius: 12px;
        }}

        /* Sleek Floating Toast Stack (No Browser Alerts!) */
        .toast-stack {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 80;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }}

        .toast-item {{
            pointer-events: auto;
            background: #141720;
            border: 1px solid var(--border-bright);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 0.75rem 1.05rem;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.84rem;
            color: var(--text-primary);
            min-width: 260px;
            max-width: 380px;
            animation: fadeUp 0.35s var(--spring);
        }}

        .mobile-rail-backdrop {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(4, 5, 8, 0.68);
            backdrop-filter: blur(4px);
            z-index: 42;
        }}

        .mobile-rail-backdrop.open {{
            display: block;
        }}

        /* Staggered Waterfall Entrance */
        .stagger-in {{
            opacity: 0;
            transform: translateY(10px);
            animation: staggerReveal 0.55s var(--spring) forwards;
            animation-delay: calc(var(--idx, 0) * 45ms);
        }}

        @keyframes staggerReveal {{
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Responsive Mobile Collapse (< 960px) */
        @media (max-width: 960px) {{
            .app-shell {{
                grid-template-columns: minmax(0, 1fr);
            }}
            .sidebar-rail {{
                position: fixed;
                left: 0;
                top: 0;
                bottom: 0;
                width: 270px;
                z-index: 45;
                transform: translateX(-100%);
                transition: transform 0.4s var(--spring);
            }}
            .sidebar-rail.mobile-open {{
                transform: translateX(0);
            }}
            .mobile-menu-btn {{
                display: inline-flex;
            }}
            .workspace-main {{
                padding: 1rem 0.9rem 3.5rem;
                min-width: 0;
            }}
            .command-search-shell {{
                min-width: 0;
                max-width: 100%;
            }}
            .top-actions-cluster {{
                width: 100%;
                justify-content: space-between;
            }}
            .scout-mode-pills {{
                flex-wrap: wrap;
                border-radius: 14px;
                padding: 4px;
                flex: 1;
                justify-content: center;
            }}
            .pill-trigger {{
                font-size: 0.74rem;
                padding: 0.38rem 0.65rem;
            }}
            .bento-telemetry-grid,
            .priority-showcase-grid,
            .dossier-cards-grid {{
                grid-template-columns: minmax(0, 1fr);
            }}
            .bezel-outer,
            .bezel-core {{
                min-width: 0;
                max-width: 100%;
            }}
            .priority-card-inner {{
                grid-template-columns: minmax(0, 1fr);
            }}
            .flyer-thumb-frame {{
                max-width: 132px;
            }}
            .contact-chip {{
                word-break: break-all;
            }}
            .card-footer-actions {{
                flex-wrap: wrap;
            }}
        }}

        @media (max-width: 640px) {{
            .shortcut-hint {{
                display: none;
            }}
            .command-search-input {{
                padding-right: 1rem;
            }}
            .top-actions-cluster {{
                flex-direction: column;
                align-items: stretch;
            }}
            .btn-island-primary {{
                justify-content: space-between;
            }}
        }}
    </style>
</head>
<body>
    <div class="mobile-rail-backdrop" id="mobileRailBackdrop" onclick="closeMobileSidebar()"></div>
    <div class="app-shell">
        <!-- Executive Sidebar Navigation Rail -->
        <aside class="sidebar-rail" id="sidebarRail">
            <div class="brand-lockup">
                <div class="brand-left">
                    <div class="brand-mark">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F4F4F5" stroke-width="1.8">
                            <path d="M5 19V5l14 14V5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <span class="brand-name">Nebulyx</span>
                </div>
                <span class="brand-version mono">Studio</span>
            </div>

            <div class="rail-section">
                <div class="rail-heading">Workspace</div>
                <button class="rail-item active" id="navOverview" onclick="setViewScope('overview')">
                    <span class="rail-item-left">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
                        Command Overview
                    </span>
                </button>
                <button class="rail-item" id="navFlagship" onclick="setViewScope('flagship')">
                    <span class="rail-item-left">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        Flagship Flyers
                    </span>
                    <span class="rail-count" id="countFlagship">4</span>
                </button>
                <button class="rail-item" id="navPipeline" onclick="setViewScope('all')">
                    <span class="rail-item-left">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                        All Buyer Signals
                    </span>
                    <span class="rail-count" id="countAllSide">{len(clean_leads)}</span>
                </button>
            </div>

            <div class="rail-section">
                <div class="rail-heading">Service Pillars</div>
                <button class="rail-item active" data-pillar="all" onclick="filterPillar('all')">
                    <span class="rail-item-left"><span class="pillar-dot" style="background:#A1A1AA;"></span>All Capabilities</span>
                    <span class="rail-count" id="pCountAll">{len(clean_leads)}</span>
                </button>
                <button class="rail-item" data-pillar="web" onclick="filterPillar('web')">
                    <span class="rail-item-left"><span class="pillar-dot" style="background:#7DD3FC;"></span>Motion Web</span>
                    <span class="rail-count" id="pCountWeb">0</span>
                </button>
                <button class="rail-item" data-pillar="crm" onclick="filterPillar('crm')">
                    <span class="rail-item-left"><span class="pillar-dot" style="background:#34D399;"></span>Web Apps &amp; CRM</span>
                    <span class="rail-count" id="pCountCrm">0</span>
                </button>
                <button class="rail-item" data-pillar="ai" onclick="filterPillar('ai')">
                    <span class="rail-item-left"><span class="pillar-dot" style="background:#C084FC;"></span>AI Multi-Agents</span>
                    <span class="rail-count" id="pCountAi">0</span>
                </button>
                <button class="rail-item" data-pillar="commerce" onclick="filterPillar('commerce')">
                    <span class="rail-item-left"><span class="pillar-dot" style="background:#E2C275;"></span>Digital Storefronts</span>
                    <span class="rail-count" id="pCountCommerce">0</span>
                </button>
            </div>

            <div class="rail-section">
                <div class="rail-heading">CRM Stage</div>
                <button class="rail-item active" data-stage="all" onclick="filterStage('all')">
                    <span class="rail-item-left">All Stages</span>
                    <span class="rail-count" id="sCountAll">{len(clean_leads)}</span>
                </button>
                <button class="rail-item" data-stage="new" onclick="filterStage('new')">
                    <span class="rail-item-left">New Signal</span>
                    <span class="rail-count" id="sCountNew">0</span>
                </button>
                <button class="rail-item" data-stage="contacted" onclick="filterStage('contacted')">
                    <span class="rail-item-left">Contacted</span>
                    <span class="rail-count" id="sCountContacted">0</span>
                </button>
                <button class="rail-item" data-stage="replied" onclick="filterStage('replied')">
                    <span class="rail-item-left">Replied</span>
                    <span class="rail-count" id="sCountReplied">0</span>
                </button>
                <button class="rail-item" data-stage="booked" onclick="filterStage('booked')">
                    <span class="rail-item-left">Call Booked</span>
                    <span class="rail-count" id="sCountBooked">0</span>
                </button>
            </div>

            <div class="rail-footer">
                <div class="session-box" style="cursor:pointer;" onclick="openSettingsModal()" title="Configure Instagram Account & Gemini API Key">
                    <div class="session-row">
                        <span style="display:flex; align-items:center; gap:7px; color:var(--text-primary); font-weight:500; min-width:0; overflow:hidden; white-space:nowrap;">
                            <span class="live-dot" id="authDot" style="flex-shrink:0;"></span>
                            <span id="authSessionLabel" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">Checking Session...</span>
                        </span>
                        <span class="mono" style="font-size:0.68rem; color:var(--accent-emerald); white-space:nowrap; flex-shrink:0;" id="syncStateLabel">2s Live</span>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; gap:6px;">
                        <div class="mono" style="font-size:0.65rem; color:var(--text-muted); min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" id="lastSyncClock">Synced · Checking API...</div>
                        <span class="mono" style="font-size:0.65rem; color:var(--accent-gold); white-space:nowrap; flex-shrink:0;" id="geminiBadgeSide">OCR</span>
                    </div>
                </div>
                <button class="rail-item" onclick="openSettingsModal()" style="border:1px solid var(--border-hairline); background:rgba(255,255,255,0.025); justify-content:center;">
                    <span class="rail-item-left" style="font-size:0.78rem;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                        Account &amp; Gemini Key
                    </span>
                </button>
                <div class="export-row">
                    <a href="scraped_leads.csv" download class="export-btn">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        CSV
                    </a>
                    <a href="scraped_leads.json" download class="export-btn">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                        JSON
                    </a>
                </div>
            </div>
        </aside>

        <!-- Main Workspace Canvas -->
        <main class="workspace-main">
            <!-- Top Floating Command Bar -->
            <header class="top-command-bar">
                <div style="display:flex; align-items:center; gap:10px; flex:1; min-width:260px;">
                    <button class="mobile-menu-btn" onclick="toggleMobileSidebar()" aria-label="Toggle Menu">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                    </button>
                    <div class="command-search-shell">
                        <svg class="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                        <input type="text" id="globalSearchInput" class="command-search-input" placeholder="Filter leads by company, @handle, phone, or stack...">
                        <span class="shortcut-hint">Ctrl K</span>
                    </div>
                </div>

                <div class="top-actions-cluster">
                    <div class="scout-mode-pills">
                        <button class="pill-trigger" onclick="runScout('dorks')" title="Google/DDG Instagram Dorks">Sellbird Dorks</button>
                        <button class="pill-trigger" onclick="runScout('reach')" title="Agent-Reach Hybrid Discovery">Agent Reach</button>
                        <button class="pill-trigger" onclick="runScout('reels')" title="Auto-Scroll Vertical Reels Player">Reels Stream</button>
                        <button class="pill-trigger" onclick="runScout('explore')" title="Explore Feed Grid">Explore</button>
                        <button class="pill-trigger" onclick="runScout('hashtags')" title="11 Hiring Hashtags">Hashtags</button>
                    </div>
                    <button class="btn-island-primary" onclick="runScout('omni')">
                        <span>Run Omni Scout</span>
                        <span class="btn-island-icon">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                        </span>
                    </button>
                </div>
            </header>

            <!-- Asymmetric Bento Telemetry Row -->
            <section class="bento-telemetry-grid">
                <!-- Bento 1: Pipeline Velocity & Pillar Distribution -->
                <div class="bezel-outer">
                    <div class="bezel-core spotlight-card bento-pad">
                        <div class="eyebrow-tag">
                            <span style="width:6px; height:6px; border-radius:50%; background:var(--accent-emerald);"></span>
                            Signal Intelligence Velocity
                        </div>
                        <div class="kpi-hero-row">
                            <div style="display:flex; align-items:baseline; gap:10px;">
                                <span class="kpi-big-num mono" id="kpiTotalLeads">{len(clean_leads)}</span>
                                <span style="font-size:0.85rem; color:var(--text-secondary);">Qualified Buyers</span>
                            </div>
                            <span class="kpi-delta" id="kpiAvgIcp">Avg ICP 9.1</span>
                        </div>
                        <div>
                            <div class="distribution-bar" id="pillarDistBar"></div>
                            <div class="dist-legend" style="margin-top:8px;">
                                <span><span style="color:#7DD3FC;">●</span> Web <strong class="mono" id="legWeb">0</strong></span>
                                <span><span style="color:#34D399;">●</span> CRM <strong class="mono" id="legCrm">0</strong></span>
                                <span><span style="color:#C084FC;">●</span> AI <strong class="mono" id="legAi">0</strong></span>
                                <span><span style="color:#E2C275;">●</span> Store <strong class="mono" id="legCom">0</strong></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bento 2: Sellbird Gate & Direct Contact Yield -->
                <div class="bezel-outer">
                    <div class="bezel-core spotlight-card bento-pad">
                        <div class="eyebrow-tag">Sellbird Buyer-Intent Gate</div>
                        <div class="kpi-hero-row">
                            <div style="display:flex; align-items:baseline; gap:10px;">
                                <span class="kpi-big-num mono" id="kpiDirectContacts">0</span>
                                <span style="font-size:0.85rem; color:var(--text-secondary);">Direct Contacts</span>
                            </div>
                            <span class="mono" style="font-size:0.72rem; color:var(--accent-gold); background:var(--accent-gold-dim); padding:3px 8px; border-radius:999px; white-space:nowrap;">Zero-AI Filter</span>
                        </div>
                        <div>
                            <div class="distribution-bar">
                                <div class="dist-seg" id="contactCoverageBar" style="width:35%; background:var(--accent-gold);"></div>
                            </div>
                            <div class="dist-legend" style="margin-top:8px;">
                                <span id="contactCoverageText">35% direct phone / email yield</span>
                                <span class="mono" style="color:var(--text-muted);">Ads Auto-Dropped</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bento 3: Target Handle Analyzer -->
                <div class="bezel-outer">
                    <div class="bezel-core spotlight-card bento-pad">
                        <div class="eyebrow-tag">Inspect Single Handle</div>
                        <div style="font-size:0.82rem; color:var(--text-secondary); line-height:1.45;">
                            Scan any creator's Reels timeline, parse buyer flyers, and build a 3-touch pitch.
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <div class="ingest-mini-row">
                                <input type="text" id="handleIngestInput" class="ingest-mini-input" placeholder="@skywalkfilmmakers">
                                <button class="btn-ingest-submit" onclick="inspectSingleHandle()">Analyze</button>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                                <span style="font-size:0.68rem; color:var(--text-muted);">Quick:</span>
                                <button class="stage-select" style="padding:1px 7px; font-size:0.66rem; text-transform:none;" onclick="prefillHandle('skywalkfilmmakers')">@skywalkfilmmakers</button>
                                <button class="stage-select" style="padding:1px 7px; font-size:0.66rem; text-transform:none;" onclick="prefillHandle('ehbuilds.dxb')">@ehbuilds.dxb</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Live Async Operation Progress Drawer (Hidden Until Active) -->
            <div class="bezel-outer scan-progress-bezel" id="scanProgressBanner">
                <div class="bezel-core" style="padding:1.1rem 1.35rem; display:flex; flex-direction:column; gap:0.7rem;">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <span style="display:flex; align-items:center; gap:9px; font-size:0.88rem; font-weight:500;">
                            <span class="live-dot"></span>
                            <span id="scanBannerTitle">Deploying Autonomous Marketplace Scout...</span>
                        </span>
                        <span class="mono" style="font-size:0.72rem; color:var(--text-muted);" id="scanElapsed">Active</span>
                    </div>
                    <div class="skeleton-line" style="width:100%;"></div>
                    <div class="mono" style="font-size:0.75rem; color:var(--text-secondary);" id="scanBannerStep">Initializing Playwright Edge session...</div>
                </div>
            </div>

            <!-- Priority Archetype Spotlight Section (4 Flagship Reels with Real Flyer Previews) -->
            <section id="prioritySection">
                <div class="section-bar" style="margin-bottom:0.9rem;">
                    <div class="section-title-group">
                        <h2 class="section-title">Flagship Reel Benchmarks</h2>
                        <span class="section-count-chip">4 Verified Flyer Extractions</span>
                    </div>
                    <span class="eyebrow-tag" style="color:var(--accent-gold);">Click Flyer to Inspect Full Resolution</span>
                </div>
                <div class="priority-showcase-grid" id="priorityShowcaseGrid"></div>
            </section>

            <!-- Main Buyer Signals Section (Toggleable Dossier Cards / Precision Table) -->
            <section id="mainSignalsSection">
                <div class="section-bar" style="margin-bottom:0.9rem;">
                    <div class="section-title-group">
                        <h2 class="section-title">Buyer Intelligence Feed</h2>
                        <span class="section-count-chip" id="filteredCountChip">0 leads</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                        <select id="sortSelect" class="stage-select" style="padding:5px 10px; font-size:0.74rem; text-transform:none;" onchange="changeSortMode(this.value)" aria-label="Sort leads">
                            <option value="icp">Sort: ICP Score High → Low</option>
                            <option value="flagship">Sort: Flagship First</option>
                            <option value="az">Sort: Company A → Z</option>
                        </select>
                        <div class="view-toggle-group">
                            <button class="view-toggle-btn active" id="viewBtnCards" onclick="setDisplayMode('cards')">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                                Dossiers
                            </button>
                            <button class="view-toggle-btn" id="viewBtnTable" onclick="setDisplayMode('table')">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                                Ledger Table
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Card Grid Container -->
                <div class="dossier-cards-grid" id="dossierCardsContainer"></div>

                <!-- Ledger Table Container -->
                <div class="bezel-outer" id="ledgerTableWrapper" style="display:none;">
                    <div class="bezel-core table-wrapper">
                        <table class="crm-table">
                            <thead>
                                <tr>
                                    <th>Brand / Account</th>
                                    <th>Capability Pillar</th>
                                    <th>Direct Contacts</th>
                                    <th>ICP</th>
                                    <th>Stage</th>
                                    <th style="text-align:right;">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="ledgerTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <!-- Right Slide-Over Sellbird Deal Flight Deck -->
    <div class="drawer-backdrop" id="drawerBackdrop" onclick="closeFlightDeck()"></div>
    <aside class="flight-drawer" id="flightDrawer" aria-hidden="true">
        <div class="drawer-header">
            <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span class="eyebrow-tag" style="color:var(--accent-gold);">Sellbird Flight Deck</span>
                    <span class="icp-score-chip" id="drawerIcpScore">9.9</span>
                </div>
                <h2 style="font-size:1.35rem; font-weight:600; letter-spacing:-0.02em;" id="drawerCompanyName">Client Dossier</h2>
                <a href="#" target="_blank" rel="noopener" class="handle-anchor" id="drawerHandleLink">@handle</a>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <select id="drawerStageSelect" class="stage-select" onchange="updateStageFromDrawer()">
                    <option value="new">New Signal</option>
                    <option value="contacted">Contacted</option>
                    <option value="replied">Replied</option>
                    <option value="booked">Call Booked</option>
                </select>
                <button class="drawer-close-btn" onclick="closeFlightDeck()" aria-label="Close">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
        </div>

        <div class="drawer-body">
            <!-- Visual Flyer Proof + BANT Signal Summary -->
            <div id="drawerEvidenceBox" style="display:flex; gap:1rem; align-items:center; background:rgba(255,255,255,0.02); border:1px solid var(--border-hairline); border-radius:14px; padding:0.9rem;">
                <div id="drawerThumbSlot" style="display:none; width:66px; flex-shrink:0;"></div>
                <div style="flex:1; min-width:0;">
                    <div class="eyebrow-tag" style="margin-bottom:4px;">Observable Buying Signal</div>
                    <div id="drawerRawSignal" style="font-size:0.84rem; color:var(--text-secondary); line-height:1.45;"></div>
                    <div id="drawerSignalsList" style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;"></div>
                </div>
            </div>

            <!-- WhatsApp & Email First-Touch Quick Actions -->
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;">
                <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <span class="contact-chip has-value" id="drawerPhoneText"></span>
                    <span class="contact-chip has-value" id="drawerEmailText"></span>
                </div>
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                    <a href="#" class="btn-deck-open" style="padding:0.48rem 0.95rem; text-decoration:none;" id="drawerMailLaunch">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                        Compose Email
                    </a>
                    <a href="#" target="_blank" rel="noopener" class="btn-wa-clean" id="drawerWaLaunch">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                        Launch WhatsApp Hook
                    </a>
                </div>
            </div>

            <!-- Segmented Tabs -->
            <div class="drawer-segmented-tabs">
                <button class="drawer-tab active" id="dTabSeq" onclick="setDrawerTab('seq')">3-Touch Sequence</button>
                <button class="drawer-tab" id="dTabObj" onclick="setDrawerTab('obj')">LAARC Objections</button>
                <button class="drawer-tab" id="dTabProp" onclick="setDrawerTab('prop')">Formal Scope</button>
            </div>

            <!-- Panel 1: 3-Touch Sequence -->
            <div id="dPanelSeq"></div>

            <!-- Panel 2: LAARC Objections -->
            <div id="dPanelObj" style="display:none;"></div>

            <!-- Panel 3: Formal Proposal -->
            <div id="dPanelProp" style="display:none;">
                <div class="touch-card">
                    <div class="touch-top">
                        <span style="font-weight:500; font-size:0.9rem;">Executive Email Architecture Scope</span>
                        <button class="btn-ingest-submit" onclick="copyProposalScope()">Copy Scope</button>
                    </div>
                    <div style="font-size:0.8rem; color:var(--text-secondary);">Subject: <strong style="color:var(--text-primary);" id="drawerPropSubj"></strong></div>
                    <pre class="touch-copy-pre" id="drawerPropBody"></pre>
                </div>
            </div>
        </div>
    </aside>

    <!-- Settings Modal (Instagram Account Switcher + Gemini API Key) -->
    <div class="lightbox-overlay" id="settingsModal" onclick="closeSettingsModal(event)">
        <div class="bezel-outer" style="max-width:620px; width:100%;" onclick="event.stopPropagation()">
            <div class="bezel-core" style="padding:1.5rem 1.65rem; display:flex; flex-direction:column; gap:1.35rem;">
                <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border-hairline); padding-bottom:0.9rem;">
                    <div>
                        <span class="eyebrow-tag" style="color:var(--accent-gold);">Studio Configuration</span>
                        <h2 style="font-size:1.25rem; font-weight:600; margin-top:2px;">Instagram Account &amp; Gemini Vision</h2>
                    </div>
                    <button class="drawer-close-btn" onclick="closeSettingsModal()" aria-label="Close Settings">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                </div>

                <!-- Section 1: Instagram Account Switcher -->
                <div style="display:flex; flex-direction:column; gap:0.75rem; background:rgba(255,255,255,0.02); border:1px solid var(--border-hairline); border-radius:12px; padding:1rem;">
                    <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
                        <span style="font-weight:500; font-size:0.92rem;">Instagram Account Session</span>
                        <span class="mono" style="font-size:0.72rem; color:var(--accent-emerald);" id="settingsAccountBadge">Checking...</span>
                    </div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                        <input type="text" id="switchUsernameHint" class="ingest-mini-input" placeholder="New @handle (optional)" style="flex:0 0 195px; max-width:195px;">
                        <input type="password" id="switchSessionIdInput" class="ingest-mini-input" placeholder="Paste Instagram sessionid cookie" style="flex:1; min-width:200px;">
                        <button class="btn-ingest-submit" onclick="switchAccountViaCookie()">Switch</button>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap; margin-top:2px;">
                        <span class="mono" style="font-size:0.69rem; color:var(--text-muted);">Interactive Edge Login: <code style="color:var(--text-secondary);">lead_scraper\\login_instagram.bat</code></span>
                        <button class="btn-ingest-submit" style="color:var(--accent-rose); border-color:rgba(251,113,133,0.3); white-space:nowrap;" onclick="logoutInstagramSession()">Sign Out Current</button>
                    </div>
                </div>

                <!-- Section 2: Gemini Vision API Key -->
                <div style="display:flex; flex-direction:column; gap:0.75rem; background:rgba(255,255,255,0.02); border:1px solid var(--border-hairline); border-radius:12px; padding:1rem;">
                    <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
                        <span style="font-weight:500; font-size:0.92rem;">Gemini 3 Flash Multimodal Vision</span>
                        <span class="mono" style="font-size:0.72rem; color:var(--accent-gold);" id="settingsGeminiBadge">WinRT OCR Only</span>
                    </div>
                    <p style="font-size:0.8rem; color:var(--text-secondary); line-height:1.45;">
                        Enables deep AI visual reading of Reel video frames, carousel flyers, and website aesthetic gaps (stored locally in <code class="mono">.env.local</code>).
                    </p>
                    <div style="display:flex; gap:8px;">
                        <input type="password" id="geminiKeyInput" class="ingest-mini-input" placeholder="Paste GEMINI_API_KEY (AIza...)">
                        <button class="btn-ingest-submit" onclick="saveGeminiKey()">Save Key</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Fullscreen Flyer Zoom Lightbox -->
    <div class="lightbox-overlay" id="flyerLightbox" onclick="closeLightbox(event)">
        <div class="lightbox-card" onclick="event.stopPropagation()">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:0.25rem 0.4rem;">
                <span style="font-size:0.88rem; font-weight:500;" id="lightboxCaption">Reel Flyer Capture</span>
                <button class="drawer-close-btn" onclick="closeLightbox()" aria-label="Close">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
            <div id="lightboxMediaSlot"></div>
        </div>
    </div>

    <!-- Floating Glass Toast Stack -->
    <div class="toast-stack" id="toastStack"></div>

    <script>
    const initialRawLeads = {json_str};

    let leadsData = [];
    let state = {{
        viewScope: 'overview',  // overview | flagship | all
        pillarFilter: 'all',    // all | web | crm | ai | commerce
        stageFilter: 'all',     // all | new | contacted | replied | booked
        searchQuery: '',
        sortMode: 'icp',        // icp | flagship | az
        displayMode: 'cards',   // cards | table
        syncHash: '',
        isFetching: false,
        activeDrawerId: null
    }};

    const API_BASE = (window.location.protocol === 'http:' || window.location.protocol === 'https:')
        ? ''
        : 'http://127.0.0.1:8088';

    // Load local stage overrides cleanly
    function getLocalStages() {{
        try {{
            return JSON.parse(localStorage.getItem('nebulyx_crm_stages') || '{{}}');
        }} catch {{
            return {{}};
        }}
    }}

    function saveLocalStage(id, stage) {{
        try {{
            const stages = getLocalStages();
            stages[id] = stage;
            localStorage.setItem('nebulyx_crm_stages', JSON.stringify(stages));
        }} catch {{}}
    }}

    function mapLead(l) {{
        const pReq = (l.primary_requirement || '').toLowerCase();
        let pType = 'web';
        if (pReq.includes('crm') || pReq.includes('portal')) pType = 'crm';
        else if (pReq.includes('agent') || pReq.includes('ai') || pReq.includes('claude')) pType = 'ai';
        else if (pReq.includes('commerce') || pReq.includes('storefront') || pReq.includes('product')) pType = 'commerce';

        let handle = (l.instagram_handle || '').trim();
        if (handle && !handle.startsWith('@')) handle = '@' + handle;
        const rawUser = handle.replace('@', '');

        const phone = l.phone_whatsapp && l.phone_whatsapp !== 'N/A' ? l.phone_whatsapp : 'N/A';
        const email = l.email && l.email !== 'N/A' ? l.email : 'N/A';
        const waLink = l.sellbird_whatsapp_link || l.whatsapp_link || (phone !== 'N/A' ? `https://wa.me/${{phone.replace(/\\D/g, '')}}` : '#');

        const flagshipHandles = ['skywalkfilmmakers', 'krishnarealtyy.in', 'ehbuilds.dxb', 'divines_eternity2025'];
        const isFlagship = flagshipHandles.includes(rawUser.toLowerCase());

        const localStages = getLocalStages();
        const leadId = l.id || `lead_${{rawUser}}`;
        const crmStage = localStages[leadId] || l.crm_stage || 'new';

        return {{
            id: leadId,
            company: l.company || handle,
            handle: handle,
            rawUser: rawUser,
            profileUrl: l.profile_url || `https://instagram.com/${{rawUser}}/`,
            reelUrl: l.reel_url || `https://instagram.com/${{rawUser}}/reels/`,
            pillarType: pType,
            pillarTitle: l.primary_requirement || 'Website Engineering & Digital Infrastructure',
            phone: phone,
            email: email,
            excerpt: l.raw_text || l.caption || 'Active technical build opportunity verified by Sellbird.',
            keywords: Array.isArray(l.matched_keywords) ? l.matched_keywords : (l.matched_keywords ? String(l.matched_keywords).split(', ') : ['developer']),
            whatsappLink: waLink,
            whatsappText: l.sellbird_whatsapp_text || l.whatsapp_pitch || '',
            emailSubject: l.email_subject || `Architecture scope for ${{l.company}}`,
            emailBody: l.email_body || '',
            imageUrl: (l.image_url && !l.image_url.startsWith('C:')) ? l.image_url : null,
            capturedFrames: Array.isArray(l.captured_frames) ? l.captured_frames : [],
            visionMode: l.vision_mode || (isFlagship ? 'WinRT Neural OCR' : 'DOM / Signal Scan'),
            visualCritique: l.visual_critique || '',
            webEnrichment: l.web_enrichment || null,
            sourceLabel: (l.source || '').toLowerCase().includes('reach') ? 'Agent-Reach + Visual' :
                         (l.source || '').toLowerCase().includes('visual') ? 'Reel/Post Vision' :
                         (l.source || '').toLowerCase().includes('flyer') ? 'Reel Flyer OCR' :
                         (l.source || '').toLowerCase().includes('dork') ? 'Sellbird Dork' : 'IG Marketplace',
            isFlagship: isFlagship,
            sellbirdScore: Number(l.sellbird_icp_score || (isFlagship ? 9.9 : 8.4)),
            sellbirdTier: l.sellbird_tier || 'Qualified Buyer',
            sellbirdSignals: Array.isArray(l.sellbird_signals) ? l.sellbird_signals : [],
            sellbirdSequence: l.sellbird_sequence || null,
            sellbirdObjections: Array.isArray(l.sellbird_objections) ? l.sellbird_objections : [],
            crmStage: crmStage
        }};
    }}

    function escapeHtml(str) {{
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }}

    // Smooth Glass Toast Notification (Replaces ugly alert())
    function showToast(message, tone = 'success') {{
        const stack = document.getElementById('toastStack');
        if (!stack) return;
        const el = document.createElement('div');
        el.className = 'toast-item';
        const dotColor = tone === 'error' ? 'var(--accent-rose)' : tone === 'gold' ? 'var(--accent-gold)' : 'var(--accent-emerald)';
        el.innerHTML = `<span style="width:7px; height:7px; border-radius:50%; background:${{dotColor}}; flex-shrink:0;"></span><span>${{escapeHtml(message)}}</span>`;
        stack.appendChild(el);
        setTimeout(() => {{
            el.style.opacity = '0';
            el.style.transform = 'translateY(6px)';
            el.style.transition = 'all 0.3s ease';
            setTimeout(() => el.remove(), 300);
        }}, 2800);
    }}

    function copyAndNotify(text, label) {{
        if (!text || text === 'N/A') return;
        navigator.clipboard.writeText(text).then(() => {{
            showToast(`Copied ${{label}} to clipboard`);
        }}).catch(() => {{
            showToast('Clipboard permission blocked', 'error');
        }});
    }}

    // Spotlight Cursor Tracking (60fps GPU CSS Variables)
    document.addEventListener('pointermove', (e) => {{
        const cards = document.querySelectorAll('.spotlight-card');
        for (const card of cards) {{
            const rect = card.getBoundingClientRect();
            if (e.clientX >= rect.left - 80 && e.clientX <= rect.right + 80 &&
                e.clientY >= rect.top - 80 && e.clientY <= rect.bottom + 80) {{
                card.style.setProperty('--mx', `${{e.clientX - rect.left}}px`);
                card.style.setProperty('--my', `${{e.clientY - rect.top}}px`);
            }}
        }}
    }}, {{ passive: true }});

    // Filtering & Navigation Controls
    function setViewScope(scope) {{
        state.viewScope = scope;
        document.getElementById('navOverview').classList.toggle('active', scope === 'overview');
        document.getElementById('navFlagship').classList.toggle('active', scope === 'flagship');
        document.getElementById('navPipeline').classList.toggle('active', scope === 'all');

        const priSec = document.getElementById('prioritySection');
        const mainSec = document.getElementById('mainSignalsSection');
        if (scope === 'overview') {{
            priSec.style.display = 'block';
            mainSec.style.display = 'block';
        }} else if (scope === 'flagship') {{
            priSec.style.display = 'block';
            mainSec.style.display = 'none';
        }} else {{
            priSec.style.display = 'none';
            mainSec.style.display = 'block';
        }}
        closeMobileSidebar();
    }}

    function filterPillar(pillar) {{
        state.pillarFilter = pillar;
        document.querySelectorAll('[data-pillar]').forEach(btn => {{
            btn.classList.toggle('active', btn.getAttribute('data-pillar') === pillar);
        }});
        renderAll();
        closeMobileSidebar();
    }}

    function filterStage(stage) {{
        state.stageFilter = stage;
        document.querySelectorAll('[data-stage]').forEach(btn => {{
            btn.classList.toggle('active', btn.getAttribute('data-stage') === stage);
        }});
        renderAll();
        closeMobileSidebar();
    }}

    function setDisplayMode(mode) {{
        state.displayMode = mode;
        document.getElementById('viewBtnCards').classList.toggle('active', mode === 'cards');
        document.getElementById('viewBtnTable').classList.toggle('active', mode === 'table');
        document.getElementById('dossierCardsContainer').style.display = mode === 'cards' ? 'grid' : 'none';
        document.getElementById('ledgerTableWrapper').style.display = mode === 'table' ? 'block' : 'none';
        renderMainLeads();
    }}

    function toggleMobileSidebar() {{
        const rail = document.getElementById('sidebarRail');
        const backdrop = document.getElementById('mobileRailBackdrop');
        const isOpen = rail.classList.toggle('mobile-open');
        if (backdrop) backdrop.classList.toggle('open', isOpen);
    }}

    function closeMobileSidebar() {{
        document.getElementById('sidebarRail').classList.remove('mobile-open');
        const backdrop = document.getElementById('mobileRailBackdrop');
        if (backdrop) backdrop.classList.remove('open');
    }}

    function changeSortMode(mode) {{
        state.sortMode = mode;
        renderMainLeads();
    }}

    function prefillHandle(handle) {{
        const inp = document.getElementById('handleIngestInput');
        inp.value = handle;
        inp.focus();
    }}

    function getFilteredLeads() {{
        const q = state.searchQuery.toLowerCase().trim();
        const list = leadsData.filter(l => {{
            if (state.pillarFilter !== 'all' && l.pillarType !== state.pillarFilter) return false;
            if (state.stageFilter !== 'all' && l.crmStage !== state.stageFilter) return false;
            if (q) {{
                const blob = `${{l.company}} ${{l.handle}} ${{l.phone}} ${{l.email}} ${{l.pillarTitle}} ${{l.excerpt}} ${{l.keywords.join(' ')}}`.toLowerCase();
                if (!blob.includes(q)) return false;
            }}
            return true;
        }});

        if (state.sortMode === 'icp') {{
            list.sort((a, b) => b.sellbirdScore - a.sellbirdScore || (b.isFlagship ? 1 : 0) - (a.isFlagship ? 1 : 0));
        }} else if (state.sortMode === 'flagship') {{
            list.sort((a, b) => (b.isFlagship ? 1 : 0) - (a.isFlagship ? 1 : 0) || b.sellbirdScore - a.sellbirdScore);
        }} else if (state.sortMode === 'az') {{
            list.sort((a, b) => a.company.localeCompare(b.company));
        }}
        return list;
    }}

    function getPillarDotColor(pType) {{
        return pType === 'web' ? '#7DD3FC' : pType === 'crm' ? '#34D399' : pType === 'ai' ? '#C084FC' : '#E2C275';
    }}

    function updateTelemetryAndCounts() {{
        const total = leadsData.length || 1;
        const cWeb = leadsData.filter(l => l.pillarType === 'web').length;
        const cCrm = leadsData.filter(l => l.pillarType === 'crm').length;
        const cAi = leadsData.filter(l => l.pillarType === 'ai').length;
        const cCom = leadsData.filter(l => l.pillarType === 'commerce').length;

        document.getElementById('countAllSide').textContent = leadsData.length;
        document.getElementById('pCountAll').textContent = leadsData.length;
        document.getElementById('pCountWeb').textContent = cWeb;
        document.getElementById('pCountCrm').textContent = cCrm;
        document.getElementById('pCountAi').textContent = cAi;
        document.getElementById('pCountCommerce').textContent = cCom;

        document.getElementById('sCountAll').textContent = leadsData.length;
        document.getElementById('sCountNew').textContent = leadsData.filter(l => l.crmStage === 'new').length;
        document.getElementById('sCountContacted').textContent = leadsData.filter(l => l.crmStage === 'contacted').length;
        document.getElementById('sCountReplied').textContent = leadsData.filter(l => l.crmStage === 'replied').length;
        document.getElementById('sCountBooked').textContent = leadsData.filter(l => l.crmStage === 'booked').length;

        document.getElementById('kpiTotalLeads').textContent = leadsData.length;
        const avg = (leadsData.reduce((acc, l) => acc + l.sellbirdScore, 0) / total).toFixed(1);
        document.getElementById('kpiAvgIcp').textContent = `Avg ICP ${{avg}}`;

        const directCount = leadsData.filter(l => l.phone !== 'N/A' || l.email !== 'N/A').length;
        document.getElementById('kpiDirectContacts').textContent = directCount;
        const pct = Math.round((directCount / total) * 100);
        const covBar = document.getElementById('contactCoverageBar');
        const covTxt = document.getElementById('contactCoverageText');
        if (covBar) covBar.style.width = `${{pct}}%`;
        if (covTxt) covTxt.textContent = `${{pct}}% direct phone / email yield`;

        document.getElementById('legWeb').textContent = cWeb;
        document.getElementById('legCrm').textContent = cCrm;
        document.getElementById('legAi').textContent = cAi;
        document.getElementById('legCom').textContent = cCom;

        const bar = document.getElementById('pillarDistBar');
        bar.innerHTML = `
            <div class="dist-seg" style="width:${{(cWeb/total)*100}}%; background:#7DD3FC;"></div>
            <div class="dist-seg" style="width:${{(cCrm/total)*100}}%; background:#34D399;"></div>
            <div class="dist-seg" style="width:${{(cAi/total)*100}}%; background:#C084FC;"></div>
            <div class="dist-seg" style="width:${{(cCom/total)*100}}%; background:#E2C275;"></div>
        `;
    }}

    function renderPriorityShowcase() {{
        const grid = document.getElementById('priorityShowcaseGrid');
        if (!grid) return;
        const flagships = leadsData.filter(l => l.isFlagship);
        document.getElementById('countFlagship').textContent = flagships.length;

        grid.innerHTML = flagships.map((lead, idx) => {{
            const dotColor = getPillarDotColor(lead.pillarType);
            const hasThumb = Boolean(lead.imageUrl);
            return `
            <div class="bezel-outer stagger-in" style="--idx:${{idx}}">
                <div class="bezel-core spotlight-card priority-card-inner" style="${{hasThumb ? '' : 'grid-template-columns:1fr;'}}">
                    ${{hasThumb ? `
                        <div class="flyer-thumb-frame" onclick="openLightbox('${{escapeHtml(lead.imageUrl)}}', '${{escapeHtml(lead.company)}} — Original Reel Flyer')">
                            <img src="${{escapeHtml(lead.imageUrl)}}" alt="${{escapeHtml(lead.company)}} flyer" loading="lazy">
                            <span class="flyer-zoom-hint mono">Inspect</span>
                        </div>
                    ` : ''}}
                    <div style="display:flex; flex-direction:column; gap:0.85rem; min-width:0; position:relative; z-index:2;">
                        <div class="card-meta-header">
                            <div style="min-width:0;">
                                <div class="company-title">
                                    <span>${{escapeHtml(lead.company)}}</span>
                                    <span class="gold-verified-pill">Flyer Verified</span>
                                </div>
                                <a href="${{escapeHtml(lead.profileUrl)}}" target="_blank" rel="noopener" class="handle-anchor">
                                    ${{escapeHtml(lead.handle)}}
                                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                                </a>
                            </div>
                            <div class="right-badges">
                                <span class="icp-score-chip">ICP ${{lead.sellbirdScore.toFixed(1)}}</span>
                                <select class="stage-select" onchange="changeLeadStage('${{escapeHtml(lead.id)}}', this.value)" aria-label="CRM Stage">
                                    <option value="new" ${{lead.crmStage === 'new' ? 'selected' : ''}}>New</option>
                                    <option value="contacted" ${{lead.crmStage === 'contacted' ? 'selected' : ''}}>Contacted</option>
                                    <option value="replied" ${{lead.crmStage === 'replied' ? 'selected' : ''}}>Replied</option>
                                    <option value="booked" ${{lead.crmStage === 'booked' ? 'selected' : ''}}>Booked</option>
                                </select>
                            </div>
                        </div>

                        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            <div class="pillar-chip">
                                <span class="pillar-dot" style="background:${{dotColor}};"></span>
                                <span>${{escapeHtml(lead.pillarTitle.split('&')[0].trim())}}</span>
                            </div>
                            <span class="mono" style="font-size:0.68rem; color:var(--text-muted);">${{escapeHtml(lead.sourceLabel)}}</span>
                        </div>

                        <div class="contact-bar">
                            <span class="contact-chip has-value">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="1.6"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                                ${{escapeHtml(lead.phone)}}
                                <button class="micro-copy-btn" data-copy="${{escapeHtml(lead.phone)}}" data-label="phone" onclick="handleCopyAttr(this)" title="Copy Phone">
                                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                                </button>
                            </span>
                            <span class="contact-chip ${{lead.email !== 'N/A' ? 'has-value' : ''}}">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.6"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                                ${{escapeHtml(lead.email)}}
                                ${{lead.email !== 'N/A' ? `
                                    <button class="micro-copy-btn" data-copy="${{escapeHtml(lead.email)}}" data-label="email" onclick="handleCopyAttr(this)" title="Copy Email">
                                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                                    </button>` : ''}}
                            </span>
                        </div>

                        <p class="signal-excerpt">${{escapeHtml(lead.excerpt)}}</p>

                        <div class="card-footer-actions">
                            <a href="${{escapeHtml(lead.whatsappLink)}}" target="_blank" rel="noopener" class="btn-wa-clean">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                                WhatsApp Hook
                            </a>
                            <button class="btn-deck-open" onclick="openFlightDeck('${{escapeHtml(lead.id)}}')">
                                <span>Flight Deck</span>
                                <span class="btn-deck-circle">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }}).join('');
    }}

    function renderMainLeads() {{
        const filtered = getFilteredLeads();
        document.getElementById('filteredCountChip').textContent = `${{filtered.length}} signals`;

        const cardsWrap = document.getElementById('dossierCardsContainer');
        const tableBody = document.getElementById('ledgerTableBody');

        if (filtered.length === 0) {{
            const emptyHtml = `
                <div class="bezel-outer" style="grid-column: 1 / -1;">
                    <div class="bezel-core" style="padding:3.5rem 1.5rem; text-align:center;">
                        <p style="font-size:1.05rem; font-weight:500; color:var(--text-primary);">No buyer signals match your active filter.</p>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:6px;">Clear your search query or trigger Run Omni Scout to harvest fresh leads.</p>
                    </div>
                </div>
            `;
            cardsWrap.innerHTML = emptyHtml;
            tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2.5rem; color:var(--text-muted);">No matching records found.</td></tr>`;
            return;
        }}

        if (state.displayMode === 'cards') {{
            cardsWrap.innerHTML = filtered.map((lead, idx) => {{
                const dotColor = getPillarDotColor(lead.pillarType);
                return `
                <div class="bezel-outer stagger-in" style="--idx:${{Math.min(idx, 12)}}">
                    <div class="bezel-core spotlight-card dossier-inner">
                        <div class="card-meta-header">
                            <div style="min-width:0;">
                                <div class="company-title">
                                    <span>${{escapeHtml(lead.company)}}</span>
                                    ${{lead.isFlagship ? '<span class="gold-verified-pill">Flagship</span>' : ''}}
                                </div>
                                <a href="${{escapeHtml(lead.profileUrl)}}" target="_blank" rel="noopener" class="handle-anchor">
                                    ${{escapeHtml(lead.handle)}}
                                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                                </a>
                            </div>
                            <div class="right-badges">
                                <span class="icp-score-chip">ICP ${{lead.sellbirdScore.toFixed(1)}}</span>
                                <select class="stage-select" onchange="changeLeadStage('${{escapeHtml(lead.id)}}', this.value)" aria-label="CRM Stage">
                                    <option value="new" ${{lead.crmStage === 'new' ? 'selected' : ''}}>New</option>
                                    <option value="contacted" ${{lead.crmStage === 'contacted' ? 'selected' : ''}}>Contacted</option>
                                    <option value="replied" ${{lead.crmStage === 'replied' ? 'selected' : ''}}>Replied</option>
                                    <option value="booked" ${{lead.crmStage === 'booked' ? 'selected' : ''}}>Booked</option>
                                </select>
                            </div>
                        </div>

                        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            <div class="pillar-chip">
                                <span class="pillar-dot" style="background:${{dotColor}};"></span>
                                <span>${{escapeHtml(lead.pillarTitle)}}</span>
                            </div>
                            <span class="mono" style="font-size:0.68rem; color:var(--text-muted);">${{escapeHtml(lead.sourceLabel)}}</span>
                        </div>

                        <div class="contact-bar">
                            <span class="contact-chip ${{lead.phone !== 'N/A' ? 'has-value' : ''}}">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="1.6"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                                ${{lead.phone !== 'N/A' ? escapeHtml(lead.phone) : '<span style="color:var(--text-muted);">DM / Profile Only</span>'}}
                                ${{lead.phone !== 'N/A' ? `
                                    <button class="micro-copy-btn" data-copy="${{escapeHtml(lead.phone)}}" data-label="phone" onclick="handleCopyAttr(this)" title="Copy Phone">
                                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                                    </button>` : ''}}
                            </span>
                            ${{lead.email !== 'N/A' ? `
                                <span class="contact-chip has-value">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.6"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                                    ${{escapeHtml(lead.email)}}
                                    <button class="micro-copy-btn" data-copy="${{escapeHtml(lead.email)}}" data-label="email" onclick="handleCopyAttr(this)" title="Copy Email">
                                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                                    </button>
                                </span>` : ''}}
                        </div>

                        <p class="signal-excerpt">${{escapeHtml(lead.excerpt)}}</p>

                        <div class="card-footer-actions">
                            <a href="${{escapeHtml(lead.whatsappLink)}}" target="_blank" rel="noopener" class="btn-wa-clean ${{lead.phone === 'N/A' ? 'disabled' : ''}}">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                                ${{lead.phone !== 'N/A' ? 'WhatsApp Hook' : 'Instagram DM'}}
                            </a>
                            <button class="btn-deck-open" onclick="openFlightDeck('${{escapeHtml(lead.id)}}')">
                                <span>Flight Deck</span>
                                <span class="btn-deck-circle">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
                `;
            }}).join('');
        }} else {{
            tableBody.innerHTML = filtered.map(lead => {{
                const dotColor = getPillarDotColor(lead.pillarType);
                return `
                <tr>
                    <td>
                        <div style="font-weight:500; color:var(--text-primary);">${{escapeHtml(lead.company)}}</div>
                        <a href="${{escapeHtml(lead.profileUrl)}}" target="_blank" rel="noopener" class="handle-anchor">${{escapeHtml(lead.handle)}}</a>
                    </td>
                    <td>
                        <span class="pillar-chip"><span class="pillar-dot" style="background:${{dotColor}};"></span>${{escapeHtml(lead.pillarTitle.split('&')[0].trim())}}</span>
                    </td>
                    <td class="mono" style="font-size:0.78rem;">
                        <div>${{lead.phone !== 'N/A' ? escapeHtml(lead.phone) : '<span style="color:var(--text-muted);">IG DM Only</span>'}}</div>
                        ${{lead.email !== 'N/A' ? `<div style="color:var(--text-muted);">${{escapeHtml(lead.email)}}</div>` : ''}}
                    </td>
                    <td><span class="icp-score-chip">${{lead.sellbirdScore.toFixed(1)}}</span></td>
                    <td>
                        <select class="stage-select" onchange="changeLeadStage('${{escapeHtml(lead.id)}}', this.value)">
                            <option value="new" ${{lead.crmStage === 'new' ? 'selected' : ''}}>New</option>
                            <option value="contacted" ${{lead.crmStage === 'contacted' ? 'selected' : ''}}>Contacted</option>
                            <option value="replied" ${{lead.crmStage === 'replied' ? 'selected' : ''}}>Replied</option>
                            <option value="booked" ${{lead.crmStage === 'booked' ? 'selected' : ''}}>Booked</option>
                        </select>
                    </td>
                    <td style="text-align:right; white-space:nowrap;">
                        ${{lead.phone !== 'N/A' ? `
                            <a href="${{escapeHtml(lead.whatsappLink)}}" target="_blank" rel="noopener" class="btn-wa-clean" style="padding:5px 10px; font-size:0.74rem; margin-right:6px;">
                                WA
                            </a>` : ''}}
                        <button class="btn-deck-open" onclick="openFlightDeck('${{escapeHtml(lead.id)}}')">
                            <span>Open</span>
                            <span class="btn-deck-circle">
                                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                            </span>
                        </button>
                    </td>
                </tr>
                `;
            }}).join('');
        }}
    }}

    function renderAll() {{
        updateTelemetryAndCounts();
        renderPriorityShowcase();
        renderMainLeads();
    }}

    function handleCopyAttr(btn) {{
        const val = btn.getAttribute('data-copy');
        const label = btn.getAttribute('data-label') || 'text';
        copyAndNotify(val, label);

        const origHtml = btn.innerHTML;
        btn.style.color = 'var(--accent-emerald)';
        if (btn.classList.contains('micro-copy-btn')) {{
            btn.innerHTML = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>';
        }} else {{
            btn.textContent = 'Copied';
        }}
        setTimeout(() => {{
            btn.innerHTML = origHtml;
            btn.style.color = '';
        }}, 1400);
    }}

    function copyFullSequence() {{
        const lead = leadsData.find(l => l.id === state.activeDrawerId);
        if (!lead || !lead.sellbirdSequence) return;
        const s = lead.sellbirdSequence;
        const text = `Subject: ${{s.touch_1.subject}}\\n\\n--- Touch 1 (Day 1) ---\\n${{s.touch_1.body}}\\n\\n--- Touch 2 (Day 4) ---\\n${{s.touch_2.body}}\\n\\n--- Touch 3 (Day 9) ---\\n${{s.touch_3.body}}`;
        copyAndNotify(text, 'full 3-touch sequence');
    }}

    async function changeLeadStage(id, newStage) {{
        const lead = leadsData.find(l => l.id === id);
        if (lead) lead.crmStage = newStage;
        saveLocalStage(id, newStage);
        updateTelemetryAndCounts();
        showToast(`Stage updated to ${{newStage.toUpperCase()}}`, 'gold');

        try {{
            await fetch(`${{API_BASE}}/api/leads/stage?id=${{encodeURIComponent(id)}}&stage=${{encodeURIComponent(newStage)}}`);
        }} catch {{}}
    }}

    // Right Slide-Over Flight Deck Drawer
    function openFlightDeck(id) {{
        const lead = leadsData.find(l => l.id === id);
        if (!lead) return;
        state.activeDrawerId = id;

        document.getElementById('drawerIcpScore').textContent = `ICP ${{lead.sellbirdScore.toFixed(1)}} / 10`;
        document.getElementById('drawerCompanyName').textContent = lead.company;
        const hLink = document.getElementById('drawerHandleLink');
        hLink.textContent = lead.handle;
        hLink.href = lead.profileUrl;

        document.getElementById('drawerStageSelect').value = lead.crmStage;
        document.getElementById('drawerRawSignal').textContent = lead.excerpt;

        const thumbSlot = document.getElementById('drawerThumbSlot');
        if (lead.imageUrl) {{
            thumbSlot.style.display = 'block';
            thumbSlot.innerHTML = `
                <div class="flyer-thumb-frame" onclick="openLightbox('${{escapeHtml(lead.imageUrl)}}', '${{escapeHtml(lead.company)}} — Original Reel Flyer')">
                    <img src="${{escapeHtml(lead.imageUrl)}}" alt="Flyer preview">
                </div>
            `;
        }} else {{
            thumbSlot.style.display = 'none';
            thumbSlot.innerHTML = '';
        }}

        const signalsWrap = document.getElementById('drawerSignalsList');
        const sigBadges = (lead.sellbirdSignals || []).map(sig =>
            `<span style="font-size:0.7rem; color:var(--text-secondary); background:rgba(255,255,255,0.04); border:1px solid var(--border-hairline); padding:2px 8px; border-radius:6px;">${{escapeHtml(sig)}}</span>`
        );
        if (lead.visionMode) {{
            sigBadges.unshift(`<span style="font-size:0.7rem; color:var(--accent-gold); background:var(--accent-gold-dim); border:1px solid rgba(226,194,117,0.28); padding:2px 8px; border-radius:6px;">${{escapeHtml(lead.visionMode)}}</span>`);
        }}
        if (lead.capturedFrames && lead.capturedFrames.length > 1) {{
            lead.capturedFrames.slice(1, 4).forEach((fUrl, fi) => {{
                sigBadges.push(`<button class="stage-select" style="text-transform:none; padding:2px 8px;" onclick="openLightbox('${{escapeHtml(fUrl)}}', '${{escapeHtml(lead.company)}} — Frame ${{fi+2}}')">View Frame ${{fi+2}}</button>`);
            }});
        }}
        if (lead.visualCritique) {{
            sigBadges.push(`<span style="font-size:0.7rem; color:var(--accent-sky); background:rgba(125,211,252,0.08); border:1px solid rgba(125,211,252,0.2); padding:2px 8px; border-radius:6px;">Visual Note: ${{escapeHtml(lead.visualCritique)}}</span>`);
        }}
        if (lead.webEnrichment && lead.webEnrichment.url) {{
            const stackTxt = (lead.webEnrichment.stack_hints || []).join(', ') || 'Analyzed via Agent-Reach Web';
            sigBadges.push(`<span style="font-size:0.7rem; color:var(--accent-emerald); background:var(--accent-emerald-dim); border:1px solid rgba(52,211,153,0.25); padding:2px 8px; border-radius:6px;">Web (${{escapeHtml(lead.webEnrichment.url)}}): ${{escapeHtml(stackTxt)}}</span>`);
        }}
        signalsWrap.innerHTML = sigBadges.join('');

        document.getElementById('drawerPhoneText').textContent = lead.phone !== 'N/A' ? `Phone: ${{lead.phone}}` : 'Phone: N/A';
        document.getElementById('drawerEmailText').textContent = lead.email !== 'N/A' ? `Email: ${{lead.email}}` : 'Email: N/A';

        const waBtn = document.getElementById('drawerWaLaunch');
        waBtn.href = lead.whatsappLink;
        waBtn.classList.toggle('disabled', lead.phone === 'N/A');

        const mailBtn = document.getElementById('drawerMailLaunch');
        if (lead.email !== 'N/A' && lead.sellbirdSequence) {{
            const t1 = lead.sellbirdSequence.touch_1;
            mailBtn.href = `mailto:${{encodeURIComponent(lead.email)}}?subject=${{encodeURIComponent(t1.subject || lead.emailSubject)}}&body=${{encodeURIComponent(t1.body || lead.emailBody)}}`;
            mailBtn.classList.remove('disabled');
            mailBtn.style.opacity = '';
            mailBtn.style.pointerEvents = '';
        }} else {{
            mailBtn.href = '#';
            mailBtn.style.opacity = '0.4';
            mailBtn.style.pointerEvents = 'none';
        }}

        // Render 3-Touch Sequence
        const seqPanel = document.getElementById('dPanelSeq');
        const seq = lead.sellbirdSequence;
        if (seq) {{
            const touches = [
                {{ key: 'touch_1', data: seq.touch_1, label: 'Touch 1 · Day 1 · Observation Hook', limit: 50 }},
                {{ key: 'touch_2', data: seq.touch_2, label: 'Touch 2 · Day 4 · Proof Angle', limit: 40 }},
                {{ key: 'touch_3', data: seq.touch_3, label: 'Touch 3 · Day 9 · Polite Breakup', limit: 30 }}
            ];
            seqPanel.innerHTML = `
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.85rem;">
                    <span class="mono" style="font-size:0.72rem; color:var(--text-muted);">Strict human cadence · Under word ceilings</span>
                    <button class="btn-ingest-submit" onclick="copyFullSequence()">Copy All 3 Touches</button>
                </div>
            ` + touches.map(t => `
                <div class="touch-card">
                    <div class="touch-top">
                        <span style="font-size:0.86rem; font-weight:500; color:var(--text-primary);">${{t.label}}</span>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span class="mono" style="font-size:0.68rem; color:var(--text-secondary); background:rgba(255,255,255,0.04); border:1px solid var(--border-hairline); padding:2px 7px; border-radius:6px;">Zero-AI · Pass</span>
                            <span class="mono" style="font-size:0.72rem; color:var(--accent-emerald); background:var(--accent-emerald-dim); padding:2px 8px; border-radius:6px;">${{t.data.word_count}} / ${{t.limit}}w</span>
                        </div>
                    </div>
                    ${{t.data.subject ? `<div class="mono" style="font-size:0.75rem; color:var(--text-muted);">Subject: <span style="color:var(--text-secondary);">${{escapeHtml(t.data.subject)}}</span></div>` : ''}}
                    <div class="touch-copy-pre">${{escapeHtml(t.data.body)}}</div>
                    <div style="display:flex; justify-content:flex-end;">
                        <button class="btn-ingest-submit" data-copy="${{escapeHtml(t.data.body)}}" data-label="${{t.label.split('·')[0].trim()}}" onclick="handleCopyAttr(this)">Copy Message</button>
                    </div>
                </div>
            `).join('');
        }} else {{
            seqPanel.innerHTML = '<div class="touch-card" style="color:var(--text-muted);">Sellbird sequence synthesis pending.</div>';
        }}

        // Render LAARC Objections
        const objPanel = document.getElementById('dPanelObj');
        const objs = lead.sellbirdObjections || [];
        objPanel.innerHTML = objs.length ? objs.map(o => `
            <div class="touch-card">
                <div class="touch-top">
                    <span style="font-size:0.86rem; font-weight:500; color:var(--accent-gold);">${{escapeHtml(o.objection)}}</span>
                    <span class="mono" style="font-size:0.68rem; color:var(--text-muted);">${{escapeHtml(o.category)}}</span>
                </div>
                <div class="touch-copy-pre">${{escapeHtml(o.response)}}</div>
                <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                    <span style="font-size:0.74rem; color:var(--text-muted);">${{escapeHtml(o.framework_note)}}</span>
                    <button class="btn-ingest-submit" data-copy="${{escapeHtml(o.response)}}" data-label="LAARC response" onclick="handleCopyAttr(this)">Copy Response</button>
                </div>
            </div>
        `).join('') : '<div class="touch-card" style="color:var(--text-muted);">No custom objections loaded.</div>';

        // Formal Proposal
        document.getElementById('drawerPropSubj').textContent = lead.emailSubject;
        document.getElementById('drawerPropBody').textContent = lead.emailBody || 'Scope available via Sellbird Sequence.';

        setDrawerTab('seq');
        document.getElementById('drawerBackdrop').classList.add('open');
        document.getElementById('flightDrawer').classList.add('open');
    }}

    function closeFlightDeck() {{
        document.getElementById('drawerBackdrop').classList.remove('open');
        document.getElementById('flightDrawer').classList.remove('open');
    }}

    function setDrawerTab(tab) {{
        document.getElementById('dTabSeq').classList.toggle('active', tab === 'seq');
        document.getElementById('dTabObj').classList.toggle('active', tab === 'obj');
        document.getElementById('dTabProp').classList.toggle('active', tab === 'prop');

        document.getElementById('dPanelSeq').style.display = tab === 'seq' ? 'block' : 'none';
        document.getElementById('dPanelObj').style.display = tab === 'obj' ? 'block' : 'none';
        document.getElementById('dPanelProp').style.display = tab === 'prop' ? 'block' : 'none';
    }}

    function updateStageFromDrawer() {{
        if (!state.activeDrawerId) return;
        const val = document.getElementById('drawerStageSelect').value;
        changeLeadStage(state.activeDrawerId, val);
        renderMainLeads();
    }}

    function copyProposalScope() {{
        const body = document.getElementById('drawerPropBody').textContent;
        copyAndNotify(body, 'architecture scope');
    }}

    // Lightbox Controls
    function openLightbox(src, caption) {{
        document.getElementById('lightboxMediaSlot').innerHTML = `<img src="${{escapeHtml(src)}}" alt="${{escapeHtml(caption)}}" style="max-height:76dvh; width:100%; object-fit:contain; border-radius:12px;">`;
        document.getElementById('lightboxCaption').textContent = caption;
        document.getElementById('flyerLightbox').classList.add('open');
    }}

    function closeLightbox(e) {{
        document.getElementById('flyerLightbox').classList.remove('open');
    }}

    // Async Scouting & Live Handle Research
    async function runScout(mode) {{
        const banner = document.getElementById('scanProgressBanner');
        const title = document.getElementById('scanBannerTitle');
        const step = document.getElementById('scanBannerStep');

        banner.style.display = 'block';
        title.textContent = `Running ${{mode.toUpperCase()}} Marketplace Scout`;
        step.textContent = 'Applying Sellbird Buyer vs. Seller Intent Gate & extracting contacts...';

        try {{
            const res = await fetch(`${{API_BASE}}/api/marketplace/scout?mode=${{encodeURIComponent(mode)}}&limit=6`);
            if (res.ok) {{
                const newLeads = await res.json();
                await syncLiveLeads(false);
                banner.style.display = 'none';
                showToast(`Scout finished: ${{newLeads.length}} qualified buyer signal(s) processed`);
                return;
            }}
        }} catch (err) {{}}

        step.textContent = 'Running in background — real-time heartbeat will stream incoming leads automatically.';
        setTimeout(() => {{ banner.style.display = 'none'; }}, 3000);
    }}

    async function inspectSingleHandle() {{
        const inputEl = document.getElementById('handleIngestInput');
        const raw = inputEl.value.trim();
        if (!raw) {{
            showToast('Enter an Instagram handle first', 'gold');
            inputEl.focus();
            return;
        }}
        const clean = raw.replace('@', '').replace('https://instagram.com/', '').replace(/\\//g, '');
        const banner = document.getElementById('scanProgressBanner');
        const title = document.getElementById('scanBannerTitle');
        const step = document.getElementById('scanBannerStep');

        banner.style.display = 'block';
        title.textContent = `Inspecting @${{clean}}`;
        step.textContent = 'Scanning Reels timeline, extracting contact points, compiling Sellbird sequence...';

        try {{
            const res = await fetch(`${{API_BASE}}/api/research?handle=${{encodeURIComponent(clean)}}`);
            if (res.ok) {{
                await syncLiveLeads(false);
                banner.style.display = 'none';
                inputEl.value = '';
                showToast(`Research completed for @${{clean}}`);
                return;
            }}
        }} catch {{}}

        step.textContent = 'API unavailable — verify server is running on port 8088.';
        setTimeout(() => {{ banner.style.display = 'none'; }}, 2800);
    }}

    // Real-Time 2.0s Heartbeat Sync
    async function syncLiveLeads(silent = true) {{
        if (state.isFetching) return;
        state.isFetching = true;
        try {{
            const res = await fetch(`${{API_BASE}}/api/leads`, {{ cache: 'no-cache' }});
            if (res.ok) {{
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {{
                    const hash = `${{data.length}}_${{data[0].id || ''}}_${{data.map(d => d.crm_stage || '').join(',')}}`;
                    if (hash !== state.syncHash) {{
                        state.syncHash = hash;
                        leadsData = data.map(mapLead);
                        renderAll();
                        if (!silent) showToast(`Synced ${{data.length}} buyer signals`);
                    }}
                }}
                const nowStr = new Date().toLocaleTimeString([], {{ hour12: false }});
                document.getElementById('lastSyncClock').textContent = `Synced ${{nowStr}} · Port 8088`;
                document.getElementById('syncStateLabel').textContent = '2s Live';
                document.getElementById('syncStateLabel').style.color = 'var(--accent-emerald)';
            }}
        }} catch {{
            document.getElementById('lastSyncClock').textContent = 'Offline Snapshot Mode';
            document.getElementById('syncStateLabel').textContent = 'Static';
            document.getElementById('syncStateLabel').style.color = 'var(--accent-amber)';
        }} finally {{
            state.isFetching = false;
        }}
    }}

    // Settings Modal Controls (Account Switcher + Gemini Key)
    function openSettingsModal() {{
        document.getElementById('settingsModal').classList.add('open');
        checkAuthStatus();
    }}

    function closeSettingsModal() {{
        document.getElementById('settingsModal').classList.remove('open');
    }}

    async function saveGeminiKey() {{
        const keyInput = document.getElementById('geminiKeyInput');
        const val = keyInput.value.trim();
        if (!val) {{
            showToast('Paste your GEMINI_API_KEY first', 'gold');
            keyInput.focus();
            return;
        }}
        try {{
            const res = await fetch(`${{API_BASE}}/api/settings/gemini`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ api_key: val }})
            }});
            const d = await res.json();
            if (res.ok && d.ok) {{
                keyInput.value = '';
                showToast(`Gemini API key saved (${{d.gemini_key_hint}})`);
                checkAuthStatus();
                return;
            }}
            showToast(d.error || 'Could not save Gemini key', 'error');
        }} catch {{
            showToast('Server offline — start server.py on port 8088', 'error');
        }}
    }}

    async function switchAccountViaCookie() {{
        const sidEl = document.getElementById('switchSessionIdInput');
        const hintEl = document.getElementById('switchUsernameHint');
        const sid = sidEl.value.trim();
        if (!sid) {{
            showToast('Paste a new Instagram sessionid cookie or run login_instagram.bat', 'gold');
            sidEl.focus();
            return;
        }}
        showToast('Validating new Instagram account session...', 'gold');
        try {{
            const res = await fetch(`${{API_BASE}}/api/settings/account`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    action: 'switch_sessionid',
                    sessionid: sid,
                    username_hint: hintEl.value.trim()
                }})
            }});
            const d = await res.json();
            if (res.ok && d.ok) {{
                sidEl.value = '';
                hintEl.value = '';
                showToast(`Switched active account to ${{d.username ? '@' + d.username : 'ID ' + d.user_id}}`);
                checkAuthStatus();
                return;
            }}
            showToast(d.error || 'Instagram rejected that sessionid', 'error');
        }} catch {{
            showToast('Server offline — cannot validate sessionid', 'error');
        }}
    }}

    async function logoutInstagramSession() {{
        try {{
            const res = await fetch(`${{API_BASE}}/api/settings/account`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ action: 'logout' }})
            }});
            if (res.ok) {{
                showToast('Signed out current account. Run login_instagram.bat or paste new sessionid.', 'gold');
                checkAuthStatus();
            }}
        }} catch {{
            showToast('Server offline — cannot clear session', 'error');
        }}
    }}

    async function checkAuthStatus() {{
        try {{
            const res = await fetch(`${{API_BASE}}/api/status`, {{ cache: 'no-cache' }});
            if (res.ok) {{
                const d = await res.json();
                const dot = document.getElementById('authDot');
                const label = document.getElementById('authSessionLabel');
                const accBadge = document.getElementById('settingsAccountBadge');
                const gemBadge = document.getElementById('settingsGeminiBadge');
                const gemSide = document.getElementById('geminiBadgeSide');

                if (d.authenticated) {{
                    const acctText = d.username ? `@${{d.username}}` : `ID ${{d.user_id}}`;
                    dot.style.background = 'var(--accent-emerald)';
                    label.textContent = `${{acctText}} · Active`;
                    if (accBadge) {{
                        accBadge.textContent = `${{acctText}} (Connected)`;
                        accBadge.style.color = 'var(--accent-emerald)';
                    }}
                }} else {{
                    dot.style.background = 'var(--accent-amber)';
                    label.textContent = 'Not Signed In';
                    if (accBadge) {{
                        accBadge.textContent = 'Signed Out (Public Only)';
                        accBadge.style.color = 'var(--accent-amber)';
                    }}
                }}

                if (d.gemini_configured) {{
                    if (gemBadge) {{
                        gemBadge.textContent = `Gemini 3 Flash Active (${{d.gemini_key_hint}})`;
                        gemBadge.style.color = 'var(--accent-emerald)';
                    }}
                    if (gemSide) {{
                        gemSide.textContent = 'Gemini + OCR';
                        gemSide.style.color = 'var(--accent-emerald)';
                    }}
                }} else {{
                    if (gemBadge) {{
                        gemBadge.textContent = 'WinRT Local OCR Only (Key Needed)';
                        gemBadge.style.color = 'var(--accent-gold)';
                    }}
                    if (gemSide) {{
                        gemSide.textContent = 'OCR Only';
                        gemSide.style.color = 'var(--accent-gold)';
                    }}
                }}
            }}
        }} catch {{}}
    }}

    // Search & Keyboard Shortcuts
    document.getElementById('globalSearchInput').addEventListener('input', (e) => {{
        state.searchQuery = e.target.value;
        renderMainLeads();
    }});

    document.getElementById('handleIngestInput').addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') inspectSingleHandle();
    }});

    document.addEventListener('keydown', (e) => {{
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {{
            e.preventDefault();
            document.getElementById('globalSearchInput').focus();
        }} else if (e.key === 'Escape') {{
            closeLightbox();
            closeFlightDeck();
            closeSettingsModal();
        }}
    }});

    // Bootstrap Studio
    leadsData = initialRawLeads.map(mapLead);
    renderAll();
    checkAuthStatus();
    syncLiveLeads(true);

    setInterval(() => {{
        syncLiveLeads(true);
        checkAuthStatus();
    }}, 2000);
    </script>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Luxury studio dashboard built successfully at: {out_path}")


if __name__ == "__main__":
    build_luxury_dashboard()

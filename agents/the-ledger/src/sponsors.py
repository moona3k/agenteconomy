"""Sponsor deep-dives for agenteconomy.io — honest, high-quality coverage of hackathon sponsors."""
import re
from pathlib import Path

import markdown

SPONSORS_DIR = Path(__file__).parent.parent / "sponsors"

SPONSORS = [
    {
        "slug": "nevermined",
        "file": "nevermined.md",
        "name": "Nevermined",
        "role": "Host",
        "tagline": "The payments and billing layer for the agent economy.",
        "url": "https://nevermined.ai",
        "color": "#00d4ff",
    },
    {
        "slug": "aws",
        "file": "aws.md",
        "name": "AWS",
        "role": "Sponsor",
        "tagline": "Cloud infrastructure and AgentCore — where autonomous agents run at scale.",
        "url": "https://aws.amazon.com",
        "color": "#ff9900",
    },
    {
        "slug": "coinbase",
        "file": "coinbase.md",
        "name": "Coinbase",
        "role": "Sponsor",
        "tagline": "x402, Base, and USDC — the money layer for agent-to-agent commerce.",
        "url": "https://coinbase.com",
        "color": "#0052ff",
    },
    {
        "slug": "langchain",
        "file": "langchain.md",
        "name": "LangChain",
        "role": "Sponsor",
        "tagline": "The orchestration framework powering the world's AI agents.",
        "url": "https://langchain.com",
        "color": "#1c3c3c",
    },
    {
        "slug": "visa",
        "file": "visa.md",
        "name": "Visa",
        "role": "Sponsor",
        "tagline": "Bringing 80 million merchants into the agent payment network.",
        "url": "https://visa.com",
        "color": "#1a1f71",
    },
    {
        "slug": "exa",
        "file": "exa.md",
        "name": "Exa",
        "role": "Sponsor",
        "tagline": "Neural search built for AI — the eyes of the agent economy.",
        "url": "https://exa.ai",
        "color": "#6366f1",
    },
    {
        "slug": "privy",
        "file": "privy.md",
        "name": "Privy",
        "role": "Sponsor",
        "tagline": "Embedded wallets and auth — giving agents a secure identity.",
        "url": "https://privy.io",
        "color": "#6967e0",
    },
    {
        "slug": "vgs",
        "file": "vgs.md",
        "name": "VGS",
        "role": "Sponsor",
        "tagline": "Vault-based tokenization — securing every agent transaction.",
        "url": "https://www.verygoodsecurity.com",
        "color": "#00c48c",
    },
    {
        "slug": "apify",
        "file": "apify.md",
        "name": "Apify",
        "role": "Sponsor",
        "tagline": "Web scraping and automation platform — the data backbone for agents.",
        "url": "https://apify.com",
        "color": "#97d700",
    },
    {
        "slug": "zeroclick",
        "file": "zeroclick.md",
        "name": "ZeroClick",
        "role": "Sponsor",
        "tagline": "AI-native advertising — contextual offers at the speed of agents.",
        "url": "https://zeroclick.ai",
        "color": "#f472b6",
    },
    {
        "slug": "mindra",
        "file": "mindra.md",
        "name": "Mindra",
        "role": "Sponsor",
        "tagline": "Adaptive agentic orchestrator with self-healing multi-agent workflows.",
        "url": "https://mindra.co",
        "color": "#818cf8",
    },
    {
        "slug": "ability",
        "file": "ability.md",
        "name": "Ability",
        "role": "Sponsor",
        "tagline": "Autonomous AI agents that work across your entire digital environment.",
        "url": "https://ability.ai",
        "color": "#38bdf8",
    },
]


def get_all_sponsors():
    return SPONSORS


def get_sponsor(slug: str):
    for s in SPONSORS:
        if s["slug"] == slug:
            return s
    return None


def render_sponsor_html(sponsor: dict) -> str | None:
    md_path = SPONSORS_DIR / sponsor["file"]
    if not md_path.exists():
        return None

    raw = md_path.read_text()

    # Strip the title line (we render it in the template)
    lines = raw.split("\n")
    content_lines = []
    skip_header = True
    for line in lines:
        if skip_header:
            if line.startswith("# ") or line.strip() == "---" or line.strip() == "":
                continue
            if line.startswith("*") and line.endswith("*") and len(line) < 200:
                continue
            skip_header = False
        content_lines.append(line)
    content_md = "\n".join(content_lines)

    html_content = markdown.markdown(
        content_md,
        extensions=["tables", "fenced_code", "codehilite", "smarty"],
    )

    return html_content


def render_sponsors_index() -> str:
    cards = ""
    for s in SPONSORS:
        has_content = (SPONSORS_DIR / s["file"]).exists()
        tag = "a" if has_content else "div"
        href = f' href="/sponsors/{s["slug"]}"' if has_content else ""
        opacity = "" if has_content else ' style="opacity:0.5"'
        cards += f"""
        <{tag}{href} class="sponsor-card"{opacity}>
            <div class="sponsor-badge" style="color:{s['color']}">{s['role']}</div>
            <h2 class="sponsor-name" style="color:{s['color']}">{s['name']}</h2>
            <p class="sponsor-tagline">{s['tagline']}</p>
            <div class="sponsor-link">{s['url'].replace('https://', '')}</div>
        </{tag}>
        """

    return SPONSORS_INDEX_TEMPLATE.replace("{{cards}}", cards)


def render_sponsor_page(slug: str) -> str | None:
    sponsor = get_sponsor(slug)
    if not sponsor:
        return None

    html_content = render_sponsor_html(sponsor)
    if not html_content:
        return None

    # Build nav to other sponsors
    sponsor_items = ""
    for s in SPONSORS:
        has_content = (SPONSORS_DIR / s["file"]).exists()
        if not has_content:
            continue
        active = "active" if s["slug"] == slug else ""
        sponsor_items += f'<a href="/sponsors/{s["slug"]}" class="sponsor-nav-item {active}" style="--sponsor-color:{s["color"]}"><span class="sponsor-nav-dot" style="background:{s["color"]}"></span>{s["name"]}</a>'

    result = SPONSOR_PAGE_TEMPLATE
    result = result.replace("{{name}}", sponsor["name"])
    result = result.replace("{{tagline}}", sponsor["tagline"])
    result = result.replace("{{role}}", sponsor["role"])
    result = result.replace("{{url}}", sponsor["url"])
    result = result.replace("{{url_display}}", sponsor["url"].replace("https://", ""))
    result = result.replace("{{color}}", sponsor["color"])
    result = result.replace("{{content}}", html_content)
    result = result.replace("{{sponsor_items}}", sponsor_items)
    result = result.replace("{{ad_query}}", f"{sponsor['name']} {sponsor['tagline']}")

    return result


# ── Templates ──

_SHARED_STYLES = """
:root {
  --bg-primary: #05070e;
  --bg-secondary: #0a0f1a;
  --bg-card: rgba(14, 19, 32, 0.7);
  --bg-card-hover: rgba(22, 29, 48, 0.8);
  --border: rgba(28, 37, 64, 0.6);
  --border-light: rgba(42, 53, 85, 0.7);
  --text-primary: #eef2ff;
  --text-secondary: #94a3c0;
  --text-muted: #505d78;
  --accent-cyan: #00d4ff;
  --accent-blue: #3b82f6;
  --accent-emerald: #00e5a0;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
  --font-sans: 'Inter', -apple-system, system-ui, sans-serif;
  --font-serif: 'Newsreader', Georgia, serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.bg-mesh {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
}
.bg-mesh::before {
  content: '';
  position: absolute;
  top: -40%; left: -20%;
  width: 80%; height: 80%;
  background: radial-gradient(ellipse, rgba(0, 212, 255, 0.04) 0%, transparent 60%);
}
.bg-mesh::after {
  content: '';
  position: absolute;
  bottom: -30%; right: -10%;
  width: 70%; height: 70%;
  background: radial-gradient(ellipse, rgba(0, 229, 160, 0.03) 0%, transparent 60%);
}
"""

SPONSORS_INDEX_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sponsors — Autonomous Business Hackathon</title>
<meta name="description" content="Honest, in-depth coverage of every sponsor powering the Nevermined Autonomous Business Hackathon.">
<meta property="og:title" content="Hackathon Sponsors — agenteconomy.io">
<meta property="og:description" content="Deep dives into the companies building the agent economy infrastructure.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://agenteconomy.io/sponsors">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{_SHARED_STYLES}

.container {{
  position: relative; z-index: 1;
  max-width: 900px; margin: 0 auto;
  padding: 60px 24px 120px;
}}

.back-link {{
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--text-muted); text-decoration: none;
  font-size: 14px; font-weight: 500;
  margin-bottom: 48px;
  transition: color 0.2s;
}}
.back-link:hover {{ color: var(--accent-cyan); }}

.page-header {{
  margin-bottom: 56px;
}}
.page-label {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
  color: var(--accent-emerald);
}}
.page-title {{
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
}}
.page-desc {{
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 640px;
}}
.page-disclaimer {{
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(251, 191, 36, 0.06);
  border: 1px solid rgba(251, 191, 36, 0.15);
  border-radius: 8px;
  font-size: 13px;
  color: #fbbf24;
  font-family: var(--font-mono);
  line-height: 1.5;
}}

.sponsors-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}}

.sponsor-card {{
  display: block;
  text-decoration: none;
  color: inherit;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}}
.sponsor-card::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: currentColor;
  opacity: 0;
  transition: opacity 0.3s;
}}
a.sponsor-card:hover {{
  background: var(--bg-card-hover);
  border-color: var(--border-light);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}}
a.sponsor-card:hover::before {{ opacity: 0.6; }}

.sponsor-badge {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 12px;
  opacity: 0.7;
}}
.sponsor-name {{
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}}
.sponsor-tagline {{
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 16px;
}}
.sponsor-link {{
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}}

@media (max-width: 640px) {{
  .sponsors-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="container">
  <a href="/" class="back-link">&larr; agenteconomy.io</a>
  <div class="page-header">
    <div class="page-label">Sponsored Coverage</div>
    <h1 class="page-title">Hackathon Sponsors</h1>
    <p class="page-desc">Honest, in-depth coverage of the companies building the infrastructure for the agent economy. Each sponsor gets a deep-dive review &mdash; what they do, how it works, and where it fits.</p>
    <div class="page-disclaimer">These are sponsored profiles. The coverage is honest &mdash; we write what we find, including limitations. No sponsor reviewed or approved their page before publication.</div>
  </div>
  <div class="sponsors-grid">
    {{{{cards}}}}
  </div>
</div>
</body>
</html>"""

SPONSOR_PAGE_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{{{name}}}} — Hackathon Sponsor Deep Dive</title>
<meta name="description" content="{{{{tagline}}}}">
<meta property="og:title" content="{{{{name}}}} — Hackathon Sponsor Deep Dive">
<meta property="og:description" content="{{{{tagline}}}}">
<meta property="og:type" content="article">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Newsreader:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
{_SHARED_STYLES}

.container {{
  position: relative; z-index: 1;
  max-width: 720px; margin: 0 auto;
  padding: 48px 24px 120px;
}}

.top-nav {{
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 56px;
}}
.back-link {{
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--text-muted); text-decoration: none;
  font-size: 14px; font-weight: 500;
  transition: color 0.2s;
}}
.back-link:hover {{ color: var(--accent-cyan); }}

/* ── Sponsor Header ── */

.sponsor-header {{
  margin-bottom: 48px;
  padding-bottom: 40px;
  border-bottom: 1px solid var(--border);
  position: relative;
}}
.sponsor-header::before {{
  content: '';
  position: absolute;
  top: -56px; left: -24px; right: -24px;
  height: 200px;
  background: radial-gradient(ellipse at top, color-mix(in srgb, {{{{color}}}} 6%, transparent) 0%, transparent 70%);
  pointer-events: none;
}}
.sponsor-meta-row {{
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px;
}}
.sponsor-role-badge {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: {{{{color}}}};
  padding: 4px 12px;
  border: 1px solid color-mix(in srgb, {{{{color}}}} 30%, transparent);
  border-radius: 6px;
  background: color-mix(in srgb, {{{{color}}}} 8%, transparent);
}}
.sponsored-badge {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #fbbf24;
  padding: 4px 10px;
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 6px;
  background: rgba(251, 191, 36, 0.06);
}}
.sponsor-page-name {{
  font-size: clamp(28px, 5vw, 42px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: 12px;
  color: {{{{color}}}};
}}
.sponsor-page-tagline {{
  font-size: 20px;
  color: var(--text-secondary);
  line-height: 1.5;
  font-family: var(--font-serif);
  font-style: italic;
}}
.sponsor-page-url {{
  display: inline-flex; align-items: center; gap: 6px;
  margin-top: 16px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}}
.sponsor-page-url:hover {{ color: {{{{color}}}}; }}

/* ── Article Content ── */

.article-content {{
  font-family: var(--font-serif);
  font-size: 19px;
  line-height: 1.75;
  color: #d1d5e8;
}}

.article-content h2 {{
  font-family: var(--font-sans);
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin-top: 56px;
  margin-bottom: 20px;
  line-height: 1.2;
}}

.article-content h3 {{
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 40px;
  margin-bottom: 16px;
  line-height: 1.3;
}}

.article-content p {{ margin-bottom: 24px; }}
.article-content strong {{ color: var(--text-primary); font-weight: 600; }}

.article-content a {{
  color: var(--accent-cyan);
  text-decoration: underline;
  text-decoration-color: rgba(0, 212, 255, 0.3);
  text-underline-offset: 3px;
  transition: text-decoration-color 0.2s;
}}
.article-content a:hover {{ text-decoration-color: var(--accent-cyan); }}

.article-content ul, .article-content ol {{
  margin-bottom: 24px;
  padding-left: 28px;
}}
.article-content li {{ margin-bottom: 10px; }}

.article-content blockquote {{
  border-left: 3px solid {{{{color}}}};
  padding: 16px 24px;
  margin: 32px 0;
  background: color-mix(in srgb, {{{{color}}}} 4%, transparent);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  color: var(--text-secondary);
}}

.article-content code {{
  font-family: var(--font-mono);
  font-size: 15px;
  background: rgba(0, 212, 255, 0.08);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--accent-cyan);
}}

.article-content pre {{
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin: 32px 0;
  overflow-x: auto;
  font-size: 14px;
  line-height: 1.6;
}}
.article-content pre code {{
  background: none; padding: 0;
  color: var(--text-secondary); font-size: 14px;
}}

.article-content table {{
  width: 100%;
  border-collapse: collapse;
  margin: 32px 0;
  font-family: var(--font-sans);
  font-size: 15px;
}}
.article-content th {{
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-light);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.article-content td {{
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  line-height: 1.4;
}}

.article-content hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 48px 0;
}}

/* ── Sponsor Nav ── */

.sponsor-nav {{
  margin-top: 64px;
  padding-top: 40px;
  border-top: 1px solid var(--border);
}}
.sponsor-nav-label {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
}}
.sponsor-nav-item {{
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 15px;
  transition: all 0.2s;
}}
.sponsor-nav-item:hover {{
  background: rgba(0, 212, 255, 0.04);
  color: var(--text-primary);
}}
.sponsor-nav-item.active {{
  background: color-mix(in srgb, var(--sponsor-color) 10%, transparent);
  color: var(--sponsor-color);
  font-weight: 600;
}}
.sponsor-nav-dot {{
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}}

/* ── ZeroClick Sponsored ── */

.zc-container {{
  margin-top: 56px;
  padding-top: 40px;
  border-top: 1px solid var(--border);
}}
.zc-label {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.zc-label::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}}
.zc-offers {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.zc-card {{
  flex: 1; min-width: 240px; max-width: 340px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none; color: inherit;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; flex-direction: column;
}}
.zc-card:hover {{
  border-color: var(--border-light);
  background: var(--bg-card-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}}
.zc-card-img {{
  width: 100%; height: 140px;
  object-fit: cover;
  border-bottom: 1px solid var(--border);
}}
.zc-card-body {{ padding: 16px; flex: 1; display: flex; flex-direction: column; }}
.zc-card-brand {{ font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--accent-cyan); margin-bottom: 6px; }}
.zc-card-title {{ font-family: var(--font-sans); font-size: 15px; font-weight: 600; color: var(--text-primary); line-height: 1.35; margin-bottom: 6px; }}
.zc-card-desc {{ font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary); line-height: 1.45; flex: 1; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
.zc-card-cta {{ display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--accent-cyan); }}
.zc-card-cta::after {{ content: '\2192'; }}
.zc-card-price {{ font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--accent-emerald); margin-bottom: 8px; }}
.zc-hidden {{ display: none; }}

@media (max-width: 640px) {{
  .zc-offers {{ flex-direction: column; }}
  .zc-card {{ max-width: 100%; }}
}}
</style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="container">
  <div class="top-nav">
    <a href="/sponsors" class="back-link">&larr; All sponsors</a>
    <a href="/" class="back-link">agenteconomy.io</a>
  </div>

  <header class="sponsor-header">
    <div class="sponsor-meta-row">
      <span class="sponsor-role-badge">{{{{role}}}}</span>
      <span class="sponsored-badge">Sponsored</span>
    </div>
    <h1 class="sponsor-page-name">{{{{name}}}}</h1>
    <p class="sponsor-page-tagline">{{{{tagline}}}}</p>
    <a href="{{{{url}}}}" target="_blank" rel="noopener" class="sponsor-page-url">{{{{url_display}}}} &nearr;</a>
  </header>

  <article class="article-content">
    {{{{content}}}}
  </article>

  <!-- ZeroClick Sponsored Offers -->
  <div class="zc-container zc-hidden" id="zc-container">
    <div class="zc-label">Sponsored</div>
    <div class="zc-offers" id="zc-offers"></div>
  </div>

  <nav class="sponsor-nav">
    <div class="sponsor-nav-label">All Sponsors</div>
    {{{{sponsor_items}}}}
  </nav>
</div>

<script>
(function() {{
  const ZC_API = "https://zeroclick.dev/api/v2";
  const ZC_KEY = "R75rquls5KKVNgRWhyXcmZQunL7e_WIHI2RPv3Xrsz8";
  const query = "{{{{ad_query}}}}";

  async function loadOffers() {{
    try {{
      const res = await fetch(ZC_API + "/offers", {{
        method: "POST",
        headers: {{
          "Content-Type": "application/json",
          "x-zc-api-key": ZC_KEY
        }},
        body: JSON.stringify({{
          method: "client",
          query: query,
          limit: 2
        }})
      }});
      if (!res.ok) return;
      const offers = await res.json();
      if (!offers || !offers.length) return;

      const container = document.getElementById("zc-container");
      const offersEl = document.getElementById("zc-offers");

      offers.forEach(function(offer) {{
        const card = document.createElement("a");
        card.href = offer.clickUrl;
        card.target = "_blank";
        card.rel = "noopener sponsored";
        card.className = "zc-card";

        let imgHtml = "";
        if (offer.imageUrl) {{
          imgHtml = '<img class="zc-card-img" src="' + offer.imageUrl + '" alt="' + (offer.title || "") + '" loading="lazy" onerror="this.remove()">';
        }}

        let priceHtml = "";
        if (offer.price && offer.price.amount) {{
          priceHtml = '<div class="zc-card-price">' + offer.price.currency + ' ' + offer.price.amount + '</div>';
        }}

        card.innerHTML = imgHtml +
          '<div class="zc-card-body">' +
            (offer.brand && offer.brand.name ? '<div class="zc-card-brand">' + offer.brand.name + '</div>' : '') +
            '<div class="zc-card-title">' + (offer.title || "") + '</div>' +
            '<div class="zc-card-desc">' + (offer.content || offer.subtitle || "") + '</div>' +
            priceHtml +
            '<div class="zc-card-cta">' + (offer.cta || "Learn more") + '</div>' +
          '</div>';

        offersEl.appendChild(card);
      }});

      container.classList.remove("zc-hidden");

      const ids = offers.map(function(o) {{ return o.id; }});
      fetch(ZC_API + "/impressions", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ ids: ids }})
      }});
    }} catch (e) {{}}
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", loadOffers);
  }} else {{
    loadOffers();
  }}
}})();
</script>
</body>
</html>"""

"""Blog rendering for agenteconomy.io — serves markdown posts as styled HTML."""
import re
from pathlib import Path

import markdown

BLOG_DIR = Path(__file__).parent.parent / "blog"

POSTS = [
    {
        "slug": "the-next-eight-billion",
        "file": "01-the-next-eight-billion.md",
        "title": "The Next Eight Billion",
        "subtitle": "From tools to economic actors — why the agent economy is the most consequential shift since the internet.",
        "part": 1,
        "date": "March 6, 2026",
        "reading_time": "5 min",
    },
    {
        "slug": "the-protocol-stack",
        "file": "02-the-protocol-stack.md",
        "title": "The Protocol Stack",
        "subtitle": "x402, A2A, MCP, AP2, ERC-8004 — the infrastructure layers of the agent economy.",
        "part": 2,
        "date": "March 6, 2026",
        "reading_time": "7 min",
    },
    {
        "slug": "trust-at-machine-speed",
        "file": "03-trust-at-machine-speed.md",
        "title": "Trust at Machine Speed",
        "subtitle": "Identity, reputation, and verification — the load-bearing wall of the agent economy.",
        "part": 3,
        "date": "March 6, 2026",
        "reading_time": "7 min",
    },
    {
        "slug": "hayek-coase-and-homo-agenticus",
        "file": "04-hayek-coase-and-homo-agenticus.md",
        "title": "Hayek, Coase, and Homo Agenticus",
        "subtitle": "The economic theory behind the agent economy — and why agent behavioral biases could reshape markets.",
        "part": 4,
        "date": "March 6, 2026",
        "reading_time": "8 min",
    },
    {
        "slug": "what-happens-next",
        "file": "05-what-happens-next.md",
        "title": "Flash Crashes, Governance Gaps, and What Happens Next",
        "subtitle": "Systemic risks, the reality check, and a roadmap for the agent economy.",
        "part": 5,
        "date": "March 6, 2026",
        "reading_time": "9 min",
    },
]

SERIES_TITLE = "Anatomy of the Agent Economy"


def get_all_posts():
    return POSTS


def get_post(slug: str):
    for post in POSTS:
        if post["slug"] == slug:
            return post
    return None


def render_post_html(post: dict) -> str:
    md_path = BLOG_DIR / post["file"]
    if not md_path.exists():
        return None

    raw = md_path.read_text()

    # Strip the title line and subtitle line (we render them in the template)
    lines = raw.split("\n")
    content_lines = []
    skip_header = True
    for line in lines:
        if skip_header:
            if line.startswith("# ") or line.startswith("*Part ") or line.strip() == "---" or line.strip() == "":
                continue
            skip_header = False
        content_lines.append(line)
    content_md = "\n".join(content_lines)

    # Strip the footer navigation (starts with "*This is Part")
    content_md = re.split(r"\n---\n\n\*This is Part", content_md)[0]

    # Also strip "**Sources**:" line at end
    content_md = re.split(r"\n\*\*Sources\*\*:", content_md)[0]

    html_content = markdown.markdown(
        content_md,
        extensions=["tables", "fenced_code", "codehilite", "smarty"],
    )

    return html_content


def render_blog_index() -> str:
    cards = ""
    for p in POSTS:
        cards += f"""
        <a href="/blog/{p['slug']}" class="post-card">
            <div class="post-card-part">Part {p['part']}</div>
            <h2 class="post-card-title">{p['title']}</h2>
            <p class="post-card-subtitle">{p['subtitle']}</p>
            <div class="post-card-meta">
                <span>{p['date']}</span>
                <span class="dot"></span>
                <span>{p['reading_time']} read</span>
            </div>
        </a>
        """

    return BLOG_INDEX_TEMPLATE.replace("{{cards}}", cards)


def render_blog_post(slug: str) -> str | None:
    post = get_post(slug)
    if not post:
        return None

    html_content = render_post_html(post)
    if not html_content:
        return None

    # Build prev/next navigation
    idx = next(i for i, p in enumerate(POSTS) if p["slug"] == slug)
    prev_link = ""
    next_link = ""
    if idx > 0:
        prev_p = POSTS[idx - 1]
        prev_link = f'<a href="/blog/{prev_p["slug"]}" class="nav-prev"><span class="nav-label">Previous</span><span class="nav-title">Part {prev_p["part"]}: {prev_p["title"]}</span></a>'
    if idx < len(POSTS) - 1:
        next_p = POSTS[idx + 1]
        next_link = f'<a href="/blog/{next_p["slug"]}" class="nav-next"><span class="nav-label">Next</span><span class="nav-title">Part {next_p["part"]}: {next_p["title"]}</span></a>'

    # Series nav
    series_items = ""
    for p in POSTS:
        active = "active" if p["slug"] == slug else ""
        series_items += f'<a href="/blog/{p["slug"]}" class="series-item {active}"><span class="series-num">{p["part"]}</span>{p["title"]}</a>'

    result = POST_TEMPLATE
    result = result.replace("{{title}}", post["title"])
    result = result.replace("{{subtitle}}", post["subtitle"])
    result = result.replace("{{part}}", str(post["part"]))
    result = result.replace("{{date}}", post["date"])
    result = result.replace("{{reading_time}}", post["reading_time"])
    result = result.replace("{{content}}", html_content)
    result = result.replace("{{prev_link}}", prev_link)
    result = result.replace("{{next_link}}", next_link)
    result = result.replace("{{series_items}}", series_items)

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
  --font-serif: 'Georgia', 'Times New Roman', serif;
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

BLOG_INDEX_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Anatomy of the Agent Economy — agenteconomy.io</title>
<meta name="description" content="A five-part deep dive into the emerging agent economy — protocols, trust, economic theory, and what happens next.">
<meta property="og:title" content="Anatomy of the Agent Economy">
<meta property="og:description" content="A five-part deep dive into the emerging agent economy.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://agenteconomy.io/blog">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{_SHARED_STYLES}

.container {{
  position: relative; z-index: 1;
  max-width: 820px; margin: 0 auto;
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

.series-header {{
  margin-bottom: 56px;
}}
.series-label {{
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
}}
.series-title {{
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
}}
.series-desc {{
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 600px;
}}

.post-card {{
  display: block;
  text-decoration: none;
  color: inherit;
  padding: 32px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.post-card:hover {{
  background: var(--bg-card-hover);
  border-color: var(--border-light);
  transform: translateY(-2px);
}}
.post-card-part {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-cyan);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 10px;
}}
.post-card-title {{
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}}
.post-card-subtitle {{
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 16px;
}}
.post-card-meta {{
  display: flex; align-items: center; gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}}
.dot {{
  width: 3px; height: 3px;
  border-radius: 50%;
  background: var(--text-muted);
}}
</style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="container">
  <a href="/" class="back-link">&larr; agenteconomy.io</a>
  <div class="series-header">
    <div class="series-label">Research Series</div>
    <h1 class="series-title">Anatomy of the Agent Economy</h1>
    <p class="series-desc">A five-part deep dive into the emerging economic paradigm where AI agents become independent economic actors. Protocols, trust, theory, risks, and what happens next.</p>
  </div>
  {{{{cards}}}}
</div>
</body>
</html>"""

POST_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{{{title}}}} — Anatomy of the Agent Economy</title>
<meta name="description" content="{{{{subtitle}}}}">
<meta property="og:title" content="{{{{title}}}} — Anatomy of the Agent Economy">
<meta property="og:description" content="{{{{subtitle}}}}">
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

.article-header {{
  margin-bottom: 48px;
  padding-bottom: 40px;
  border-bottom: 1px solid var(--border);
}}
.article-part {{
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
}}
.article-title {{
  font-size: clamp(28px, 5vw, 42px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
}}
.article-subtitle {{
  font-size: 20px;
  color: var(--text-secondary);
  line-height: 1.5;
  font-family: 'Newsreader', serif;
  font-style: italic;
}}
.article-meta {{
  display: flex; align-items: center; gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-top: 20px;
}}
.dot {{ width: 3px; height: 3px; border-radius: 50%; background: var(--text-muted); }}

/* ── Article Content ── */

.article-content {{
  font-family: 'Newsreader', Georgia, serif;
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

.article-content p {{
  margin-bottom: 24px;
}}

.article-content strong {{
  color: var(--text-primary);
  font-weight: 600;
}}

.article-content a {{
  color: var(--accent-cyan);
  text-decoration: underline;
  text-decoration-color: rgba(0, 212, 255, 0.3);
  text-underline-offset: 3px;
  transition: text-decoration-color 0.2s;
}}
.article-content a:hover {{
  text-decoration-color: var(--accent-cyan);
}}

.article-content ul, .article-content ol {{
  margin-bottom: 24px;
  padding-left: 28px;
}}
.article-content li {{
  margin-bottom: 10px;
}}

.article-content blockquote {{
  border-left: 3px solid var(--accent-cyan);
  padding: 16px 24px;
  margin: 32px 0;
  background: rgba(0, 212, 255, 0.04);
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
  background: none;
  padding: 0;
  color: var(--text-secondary);
  font-size: 14px;
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
.article-content tr:hover td {{
  background: rgba(0, 212, 255, 0.02);
}}

.article-content hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 48px 0;
}}

/* ── Series Navigation ── */

.series-nav {{
  margin-top: 64px;
  padding-top: 40px;
  border-top: 1px solid var(--border);
}}
.series-nav-label {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
}}
.series-item {{
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 15px;
  transition: all 0.2s;
}}
.series-item:hover {{
  background: rgba(0, 212, 255, 0.04);
  color: var(--text-primary);
}}
.series-item.active {{
  background: rgba(0, 212, 255, 0.08);
  color: var(--accent-cyan);
  font-weight: 600;
}}
.series-num {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-cyan);
  background: rgba(0, 212, 255, 0.1);
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
}}

/* ── Prev/Next ── */

.post-nav {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 40px;
}}
.nav-prev, .nav-next {{
  display: flex; flex-direction: column; gap: 4px;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
}}
.nav-prev:hover, .nav-next:hover {{
  border-color: var(--border-light);
  background: var(--bg-card);
}}
.nav-next {{ text-align: right; grid-column: 2; }}
.nav-label {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}}
.nav-title {{
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}}

@media (max-width: 640px) {{
  .post-nav {{ grid-template-columns: 1fr; }}
  .nav-next {{ grid-column: 1; text-align: left; }}
}}
</style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="container">
  <div class="top-nav">
    <a href="/blog" class="back-link">&larr; All posts</a>
    <a href="/" class="back-link">agenteconomy.io</a>
  </div>

  <header class="article-header">
    <div class="article-part">Part {{{{part}}}} of 5 &mdash; Anatomy of the Agent Economy</div>
    <h1 class="article-title">{{{{title}}}}</h1>
    <p class="article-subtitle">{{{{subtitle}}}}</p>
    <div class="article-meta">
      <span>{{{{date}}}}</span>
      <span class="dot"></span>
      <span>{{{{reading_time}}}} read</span>
    </div>
  </header>

  <article class="article-content">
    {{{{content}}}}
  </article>

  <div class="post-nav">
    {{{{prev_link}}}}
    {{{{next_link}}}}
  </div>

  <nav class="series-nav">
    <div class="series-nav-label">Anatomy of the Agent Economy</div>
    {{{{series_items}}}}
  </nav>
</div>
</body>
</html>"""

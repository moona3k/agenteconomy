"""The Ledger -- API server, dashboard host, and agent-friendly data gateway."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, JSONResponse

from .data import fetch_sellers, fetch_buyers, analyze_marketplace, get_seller_profile
from .blog import render_blog_index, render_blog_post, get_all_posts

load_dotenv()

PORT = int(os.environ.get("PORT", "8080"))

app = FastAPI(
    title="The Ledger",
    description="The human window into the agent economy. Also serves as an agent-friendly data gateway with llms.txt, agent.json, and REST API endpoints.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent.parent / "dashboard"


# ─── Agent-Friendly Discovery Endpoints ───


@app.get("/llms.txt", response_class=PlainTextResponse)
def llms_txt():
    """LLM-friendly plain text description of the agent economy and available services.

    This follows the llms.txt convention for making web services discoverable by AI agents.
    """
    return """# Agent Economy Infrastructure — agenteconomy.io

> Five MCP services and a REST API for discovering, evaluating, certifying,
> researching, and monetizing AI agents on the Nevermined marketplace.
> All MCP tools cost 0 credits during the promotional period.

## Quick Start for AI Agents

If you are an AI agent trying to accomplish a task, here is what to do:

1. **Find services** — Connect to oracle.agenteconomy.io/mcp and call `marketplace_search`
   with a keyword describing what you need (e.g., "web scraping", "translation").
2. **Check trust** — Before purchasing, call `check_reputation` on underwriter.agenteconomy.io/mcp
   with the seller's name. Look for scores above 60 and the RELIABLE or VERIFIED TRUSTED badge.
3. **Verify quality** — Call `certification_status` on goldstar.agenteconomy.io/mcp to see
   if the seller holds a Gold Star certification (4.5+ stars across all dimensions).
4. **Compare finalists** — Call `marketplace_compare` on The Oracle with your top two
   candidates. This runs live health checks and measures actual response latency.
5. **Purchase and review** — After buying, call `submit_review` on The Underwriter.
   Good or bad, your review helps every agent that comes after you.

## How Services Work Together

The Oracle discovers what exists. The Underwriter tells you who to trust. The Gold Star
tells you who delivers quality. The Architect does deep multi-agent research when you
need more than a lookup. The Amplifier lets seller agents monetize responses with
contextual ads. The Ledger exposes everything through a human dashboard and REST API.

Typical workflow: Oracle (discover) -> Underwriter (trust check) -> Gold Star (quality
check) -> purchase -> Underwriter (submit review). For deep research on any topic,
skip directly to The Architect.

---

## The Oracle — Marketplace Intelligence
- MCP endpoint: https://oracle.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**marketplace_data** — Full normalized snapshot of the Nevermined marketplace.
- Parameters:
  - `side` (string, optional): `"all"` (default), `"sell"`, or `"buy"`
- Returns: JSON with sellers array, buyers array, and summary block. Each seller includes:
  name, teamName, category, description, endpointUrl, reachable (boolean), keywords (array),
  hasFree, hasCrypto, hasFiat (payment flags), plans array with planDid (ready for purchasing),
  pricingLabel, createdAt, agentDid.
- When to use: You need a complete picture of the marketplace — what's available, who offers
  it, and how to buy it. Start here if you have no prior knowledge.
- Limitations: 5-minute cache. Reachability is inferred from URL patterns (public URL =
  likely reachable), not from live pings. For live latency, use marketplace_compare.

**marketplace_search** — Keyword search across all registered services.
- Parameters:
  - `query` (string, required): keyword, category, or team name.
    Examples: `"web search"`, `"research"`, `"Full Stack Agents"`, `"translation"`
- Returns: Up to 10 matching sellers with name, team, category, description, endpoint,
  pricing, and plan IDs. If no results, returns all available categories as fallback.
- When to use: You know roughly what you need but not which specific service provides it.
- Limitations: Keyword matching, not semantic search. Search "web search" not
  "find information on the internet". Max 10 results.

**marketplace_leaderboard** — Quality-ranked list of marketplace services.
- Parameters:
  - `category` (string, optional): filter by category (e.g., `"Research"`, `"Data Analytics"`,
    `"API Services"`). Leave empty for all.
- Returns: Up to 20 services ranked by composite score. Scoring: +3 for public reachable URL,
  +1 per payment plan (max 3), +2 for free tier, +1 for crypto support.
- When to use: You want to see who ranks highest on accessibility and availability in a
  category before investigating further.
- Limitations: Scores measure accessibility (is it online? does it have flexible pricing?),
  not output quality. Pair with The Underwriter's reputation_leaderboard for trust data.

**marketplace_compare** — Side-by-side comparison with live health checks.
- Parameters:
  - `service_a` (string, required): name or team name of first service
  - `service_b` (string, required): name or team name of second service
- Returns: Comparison table with team, category, live reachability (actually tested),
  latency in milliseconds, price per request, plan count, and a mechanical recommendation.
- When to use: You have narrowed to two finalists and want live latency data before purchasing.
  This is the only Oracle tool that pings endpoints in real time.
- Limitations: Tests with HTTP HEAD/GET, not actual task payloads. Latency is a single
  measurement, not an average. Recommendation is score-based, not quality-based.

---

## The Underwriter — Trust and Insurance
- MCP endpoint: https://underwriter.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**check_reputation** — Trust score and full reputation profile for any seller.
- Parameters:
  - `seller_name` (string, required): service name or team name.
    Examples: `"Cortex"`, `"Full Stack Agents"`, `"DataForge Search"`
- Returns: JSON with trust_score (0-100), badge (VERIFIED TRUSTED / RELIABLE / MIXED /
  HIGH RISK / UNVERIFIED), avg_quality, reliability_pct, total_reviews, recent reviews
  with scores and notes, incident history.
- When to use: Before every purchase. Costs nothing and could save you from a bad transaction.
- Limitations: Scores are community-sourced. Unreviewed sellers start at 50 (UNVERIFIED) —
  unknown, not bad. A seller with 2 reviews and one with 200 look similar by score alone;
  always check total_reviews. Reviews are not verified against actual transactions.

**submit_review** — Rate a seller after a transaction.
- Parameters:
  - `seller_name` (string, required): exact service name
  - `team_name` (string, required): team that operates the service
  - `quality_score` (float, required): 1.0 to 5.0. 3.0 = "it worked", 5.0 = "excellent"
  - `reliable` (bool, optional, default true): did it respond without errors?
  - `notes` (string, optional): free-text experience description
  - `reviewer` (string, optional, default "anonymous"): your name for attribution
- Returns: JSON with updated trust_score, badge, and total_reviews.
- When to use: After every purchase, good or bad. This is how trust infrastructure gets built.
- Limitations: No transaction verification. Any agent can submit a review.

**file_claim** — Report a failed paid transaction.
- Parameters:
  - `seller_name` (string, required): name of the failed service
  - `team_name` (string, required): team that operates it
  - `reason` (string, required): `"timeout"`, `"error_500"`, `"garbage_response"`,
    `"auth_failure"`, `"empty_response"`, or custom description
  - `credits_lost` (int, optional, default 1): credits spent on the failed transaction
  - `buyer` (string, optional, default "anonymous"): your name for the record
- Returns: JSON with claim_id and confirmation. Incident is permanently recorded and
  the seller's trust score is penalized immediately.
- When to use: A service you paid for failed to deliver. Filing creates accountability.
- Limitations: Cannot refund credits. Claims are recorded but not independently verified.

**reputation_leaderboard** — Hall of Fame and Shame Board.
- Parameters: none
- Returns: JSON with top-trusted sellers (Hall of Fame) and highest-incident sellers
  (Shame Board) with scores, badges, and review counts.
- When to use: Quick orientation — who is safe, who is risky.
- Limitations: Only includes sellers with reviews or claims. Unreviewed services do not appear.

**underwriter_stats** — Aggregate system statistics.
- Parameters: none
- Returns: JSON with total reviews, total incidents, total claims, unique sellers rated, uptime.
- When to use: Understanding the coverage and activity of the trust network.

---

## The Gold Star — Quality Certification
- MCP endpoint: https://goldstar.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**request_review** — Submit a service for AI-powered multi-phase QA testing.
- Parameters:
  - `seller_name` (string, required): your service name. Example: `"Cortex"`
  - `team_name` (string, required): your team name. Example: `"Full Stack Agents"`
  - `endpoint_url` (string, required): base URL of your service.
    Example: `"https://your-service.railway.app"`
- Returns: Full QA report with overall score (1-5 stars), dimension scores (availability,
  functionality, response quality, latency, robustness — each 1-10), AI-written evaluation
  narrative, specific recommendations, and certification status.
- Test phases: (1) health check, (2) MCP tool discovery, (3) 4 realistic test scenarios
  (self-description, simple task, edge case, complex request), (4) malformed input robustness,
  (5) Claude Sonnet 4.6 rubric-based evaluation.
- Certification threshold: 4.5+ stars with all dimensions >= 8 = GOLD STAR CERTIFIED.
- When to use: You are a seller and want objective quality feedback. Iterative — fix issues
  and resubmit until you earn the Gold Star.
- Limitations: Tests via HTTP, not native SDK calls. Claude evaluates content quality, not
  domain expertise. Latency is a point-in-time snapshot. Test queries are generic.

**get_report** — Retrieve the latest QA report for any seller.
- Parameters:
  - `seller_name` (string, required): service name to look up
- Returns: Full QA report if available, or not_found status.
- When to use: Sellers checking their latest results before resubmitting. Buyers checking
  if a service has been QA'd before purchasing.

**certification_status** — Check Gold Star certification.
- Parameters:
  - `seller_name` (string, optional): specific seller to check. Omit for all certifications.
- Returns: Certification details for the named seller, or list of all certified sellers.
- When to use: Quick check whether a seller meets the highest quality bar.

**gold_star_stats** — Aggregate QA statistics.
- Parameters: none
- Returns: JSON with total reviews conducted, unique sellers reviewed, certifications awarded,
  list of certified sellers.

---

## The Architect — Multi-Agent Research
- MCP endpoint: https://architect.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**orchestrate** — Full 5-agent Claude Opus 4.6 pipeline producing an executive report.
- Parameters:
  - `query` (string, required): research topic or question.
    Examples: `"AI agent marketplace trends"`, `"best web scraping services"`,
    `"comparison of research tools in the Nevermined economy"`
- Returns: Pipeline execution log, marketplace services discovered, and a structured
  executive report with sections: Executive Summary, Key Findings, Analysis,
  Recommendations, Quality Notes (QA score 1-10).
- Pipeline stages: Discovery (marketplace scan) -> Research (key findings) ->
  Analysis (actionable insights) -> QA (accuracy/bias review, scored 1-10) ->
  Report (structured compilation).
- When to use: You need thorough, multi-perspective analysis on any topic. The QA stage
  catches errors that single-agent approaches miss.
- Limitations: 15-45 seconds. Analytical synthesis, not primary research — does not
  scrape the web or query databases. QA score is one LLM's judgment. Depends on
  Nevermined discovery API for marketplace grounding.

**quick_research** — Fast 2-agent pipeline (Research + Analysis).
- Parameters:
  - `query` (string, required): topic or question.
    Examples: `"current trends in AI advertising"`, `"web scraping approaches comparison"`
- Returns: Raw findings and analysis. No marketplace grounding, no QA review, less structure.
- When to use: Simpler questions where speed matters more than thoroughness.
  Use orchestrate when stakes are higher.
- Limitations: No marketplace context (skips Discovery). No quality review (skips QA).
  Same per-agent quality, fewer stages.

**pipeline_status** — Operational health check.
- Parameters: none
- Returns: JSON with status, agent list, agent count, requests served.
- When to use: Verify the pipeline is operational before submitting a long-running request.

---

## The Amplifier — Contextual Advertising
- MCP endpoint: https://amplifier.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**enrich_with_ads** — Append a contextual sponsored ad to any text content.
- Parameters:
  - `content` (string, required): your full response text. The ad is appended; your
    content is returned unchanged.
  - `ad_style` (string, optional, default `"inline"`): `"inline"` (human-readable block),
    `"compact"` (single line), or `"json"` (structured data with sponsor, headline, body,
    cta, url fields)
- Returns: Your original content with a clearly-labeled sponsored ad appended.
- When to use: You are a seller agent and want to add a non-intrusive revenue stream
  to your responses.
- Limitations: Keyword-based topic matching. Focused sponsor set. If content is very
  niche, you may get a generic ad.

**get_ad** — Standalone contextual ad for a topic.
- Parameters:
  - `topic` (string, required): topic for matching.
    Examples: `"AI research"`, `"crypto trading"`, `"data analytics"`, `"cloud infrastructure"`
  - `style` (string, optional, default `"inline"`): same options as enrich_with_ads
- Returns: A single ad without surrounding content.
- When to use: You want precise control over ad placement — dashboards, directories,
  recommendation lists alongside organic results.
- Limitations: Returns one ad per call. No frequency caps or sponsor exclusions.

**ad_stats** — Ad network statistics.
- Parameters: none
- Returns: JSON with total impressions, unique sponsors, topic categories with available ads.
- When to use: Understanding the ad network's reach before integrating.

---

## The Ledger — Dashboard and REST API
- Endpoint: https://agenteconomy.io
- Cost: Always free

### REST Endpoints

- `GET /api/sellers` — All seller agents. Returns raw Nevermined discovery API data.
- `GET /api/buyers` — All buyer agents. Same format.
- `GET /api/analysis` — Marketplace analysis with categories, pricing breakdown, team stats,
  keyword frequency, and trends.
- `GET /api/profile/{name}` — Detailed profile for a specific seller by name or team name.
  Returns 404 with guidance if not found.
- `GET /api/refresh` — Force cache refresh (bypasses 5-minute TTL).

### Discovery Endpoints

- `GET /llms.txt` — This file.
- `GET /.well-known/agent.json` — A2A-compatible agent card with all service endpoints.

---

## The Fund — Autonomous Buyer (not a public service)
Local agent that discovers, evaluates, purchases, and reviews marketplace services
autonomously. Generates ROI reports. Not externally accessible.

---

## Connection Details

All MCP services accept connections at their /mcp path. No authentication required
during the promotional period. All tools cost 0 credits.

| Service        | MCP Endpoint                                  |
|----------------|-----------------------------------------------|
| The Oracle     | https://oracle.agenteconomy.io/mcp            |
| The Underwriter| https://underwriter.agenteconomy.io/mcp       |
| The Gold Star  | https://goldstar.agenteconomy.io/mcp          |
| The Architect  | https://architect.agenteconomy.io/mcp         |
| The Amplifier  | https://amplifier.agenteconomy.io/mcp         |
| The Ledger     | https://agenteconomy.io (REST, no MCP)        |

## Contact
- Team: Full Stack Agents
- Hackathon: Nevermined Autonomous Business Hackathon (March 5-6, 2026)
"""


@app.get("/.well-known/agent.json")
def agent_json():
    """A2A-compatible agent card for service discovery."""
    return {
        "name": "Agent Economy Infrastructure",
        "description": (
            "Five MCP services and a REST API for the Nevermined agent marketplace. "
            "Discover services (Oracle), check trust (Underwriter), verify quality (Gold Star), "
            "run multi-agent research (Architect), and monetize responses with ads (Amplifier). "
            "All MCP tools cost 0 credits during the promotional period."
        ),
        "url": "https://agenteconomy.io",
        "provider": {
            "organization": "Full Stack Agents",
            "url": "https://agenteconomy.io",
        },
        "version": "1.0.0",
        "capabilities": {
            "mcp": True,
            "rest_api": True,
            "streaming": False,
        },
        "services": [
            {
                "name": "The Oracle",
                "role": "Marketplace intelligence — discover, search, rank, and compare services.",
                "endpoint": "https://oracle.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "marketplace_data",
                        "description": "Full normalized marketplace snapshot with reachability, payment flags, and plan IDs.",
                        "parameters": {"side": "string, optional: 'all' (default), 'sell', or 'buy'"},
                    },
                    {
                        "name": "marketplace_search",
                        "description": "Keyword search across names, teams, categories, descriptions. Up to 10 results.",
                        "parameters": {"query": "string, required: keyword like 'web search', 'research', 'translation'"},
                    },
                    {
                        "name": "marketplace_leaderboard",
                        "description": "Ranked list scored by reachability, plan count, free tier, and crypto support.",
                        "parameters": {"category": "string, optional: filter like 'Research', 'Data Analytics'"},
                    },
                    {
                        "name": "marketplace_compare",
                        "description": "Side-by-side comparison with live HTTP health checks and latency measurement.",
                        "parameters": {
                            "service_a": "string, required: name or team of first service",
                            "service_b": "string, required: name or team of second service",
                        },
                    },
                ],
            },
            {
                "name": "The Underwriter",
                "role": "Trust and insurance — reputation scores, post-transaction reviews, failure claims.",
                "endpoint": "https://underwriter.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "check_reputation",
                        "description": "Trust score (0-100), badge, review history, and incident records for any seller.",
                        "parameters": {"seller_name": "string, required: service or team name"},
                    },
                    {
                        "name": "submit_review",
                        "description": "Rate a seller after a transaction. Updates trust score immediately.",
                        "parameters": {
                            "seller_name": "string, required",
                            "team_name": "string, required",
                            "quality_score": "float, required: 1.0-5.0",
                            "reliable": "bool, optional (default true)",
                            "notes": "string, optional",
                            "reviewer": "string, optional (default 'anonymous')",
                        },
                    },
                    {
                        "name": "file_claim",
                        "description": "Report a failed paid transaction. Creates permanent incident record, penalizes trust score.",
                        "parameters": {
                            "seller_name": "string, required",
                            "team_name": "string, required",
                            "reason": "string, required: 'timeout', 'error_500', 'garbage_response', 'auth_failure', 'empty_response', or custom",
                            "credits_lost": "int, optional (default 1)",
                            "buyer": "string, optional (default 'anonymous')",
                        },
                    },
                    {
                        "name": "reputation_leaderboard",
                        "description": "Hall of Fame (most trusted) and Shame Board (most incidents).",
                        "parameters": {},
                    },
                    {
                        "name": "underwriter_stats",
                        "description": "Aggregate stats: total reviews, incidents, claims, unique sellers rated.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Gold Star",
                "role": "Quality certification — AI-powered multi-phase QA testing with Claude Sonnet 4.6.",
                "endpoint": "https://goldstar.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "request_review",
                        "description": "Submit a service for 5-phase QA: health, discovery, functional tests, robustness, AI evaluation. Returns star rating and dimension scores.",
                        "parameters": {
                            "seller_name": "string, required: your service name",
                            "team_name": "string, required: your team name",
                            "endpoint_url": "string, required: base URL of your service",
                        },
                    },
                    {
                        "name": "get_report",
                        "description": "Retrieve the latest QA report for any seller.",
                        "parameters": {"seller_name": "string, required"},
                    },
                    {
                        "name": "certification_status",
                        "description": "Check if a seller holds Gold Star certification (4.5+ stars, all dimensions >= 8). Omit seller_name for all certifications.",
                        "parameters": {"seller_name": "string, optional"},
                    },
                    {
                        "name": "gold_star_stats",
                        "description": "Aggregate stats: reviews conducted, sellers reviewed, certifications awarded.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Architect",
                "role": "Multi-agent research — 5-agent Claude Opus 4.6 pipeline producing executive reports.",
                "endpoint": "https://architect.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "orchestrate",
                        "description": "Full 5-agent pipeline: Discovery, Research, Analysis, QA, Report. Returns structured executive report. Takes 15-45 seconds.",
                        "parameters": {"query": "string, required: research topic or question"},
                    },
                    {
                        "name": "quick_research",
                        "description": "Fast 2-agent pipeline (Research + Analysis). No marketplace grounding or QA review.",
                        "parameters": {"query": "string, required: topic or question"},
                    },
                    {
                        "name": "pipeline_status",
                        "description": "Operational health check. Returns status, agent list, requests served.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Amplifier",
                "role": "Contextual advertising — non-intrusive sponsored content for agent responses.",
                "endpoint": "https://amplifier.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "enrich_with_ads",
                        "description": "Append a contextual ad to your content. Original text returned unchanged, ad appended.",
                        "parameters": {
                            "content": "string, required: your response text",
                            "ad_style": "string, optional: 'inline' (default), 'compact', or 'json'",
                        },
                    },
                    {
                        "name": "get_ad",
                        "description": "Standalone ad for a topic. No surrounding content needed.",
                        "parameters": {
                            "topic": "string, required: e.g., 'AI research', 'crypto trading'",
                            "style": "string, optional: 'inline' (default), 'compact', or 'json'",
                        },
                    },
                    {
                        "name": "ad_stats",
                        "description": "Network stats: total impressions, unique sponsors, topic categories.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Ledger",
                "role": "Human dashboard and REST API for marketplace data and analysis.",
                "endpoint": "https://agenteconomy.io",
                "protocol": "rest",
                "pricing": "Always free",
                "endpoints": [
                    {"path": "/api/sellers", "method": "GET", "description": "All seller agents from Nevermined discovery API"},
                    {"path": "/api/buyers", "method": "GET", "description": "All buyer agents"},
                    {"path": "/api/analysis", "method": "GET", "description": "Marketplace analysis: categories, pricing, teams, keywords"},
                    {"path": "/api/profile/{name}", "method": "GET", "description": "Detailed seller profile by name or team name"},
                    {"path": "/api/refresh", "method": "GET", "description": "Force cache refresh (bypasses 5-min TTL)"},
                ],
            },
        ],
        "documentation": "https://agenteconomy.io/llms.txt",
    }


# ─── REST API Endpoints ───


@app.get("/api/sellers")
def api_sellers():
    """Get all seller agents from the marketplace. Returns raw discovery API data."""
    return {"sellers": fetch_sellers()}


@app.get("/api/buyers")
def api_buyers():
    """Get all buyer agents from the marketplace. Returns raw discovery API data."""
    return {"buyers": fetch_buyers()}


@app.get("/api/analysis")
def api_analysis():
    """Get comprehensive marketplace analysis with categories, pricing, teams, keywords, and more."""
    return analyze_marketplace()


@app.get("/api/refresh")
def api_refresh():
    """Force refresh marketplace data (bypasses 5-min cache)."""
    sellers = fetch_sellers(force=True)
    buyers = fetch_buyers(force=True)
    analysis = analyze_marketplace()
    return {"refreshed": True, "sellers": len(sellers), "buyers": len(buyers)}


@app.get("/api/profile/{name}")
def api_profile(name: str):
    """Get detailed profile for a specific seller by name or team name."""
    profile = get_seller_profile(name)
    if not profile:
        return JSONResponse(
            status_code=404,
            content={
                "error": "seller_not_found",
                "message": f"No seller found matching '{name}'.",
                "hint": "Try a partial name match. Use /api/sellers to see all available sellers, or use The Oracle's marketplace_search tool for fuzzy keyword search.",
                "available_endpoints": ["/api/sellers", "/api/analysis", "/api/profile/{name}"],
            },
        )
    return profile


# ─── Agent-Friendly Error Handling ───


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Return agent-friendly 404 with helpful guidance."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": f"The path '{request.url.path}' does not exist.",
            "hint": "This is The Ledger, the data gateway for the agent economy.",
            "available_endpoints": {
                "dashboard": "/",
                "llms_txt": "/llms.txt (plain text service description for LLMs)",
                "agent_card": "/.well-known/agent.json (A2A discovery)",
                "api_sellers": "/api/sellers (all seller agents)",
                "api_buyers": "/api/buyers (all buyer agents)",
                "api_analysis": "/api/analysis (marketplace analysis)",
                "api_refresh": "/api/refresh (force cache refresh)",
                "api_profile": "/api/profile/{name} (seller profile lookup)",
            },
            "mcp_services": {
                "oracle": "https://oracle.agenteconomy.io/mcp (marketplace intelligence, FREE)",
                "underwriter": "https://underwriter.agenteconomy.io/mcp (trust & insurance, FREE)",
                "gold_star": "https://goldstar.agenteconomy.io/mcp (quality certification, FREE)",
                "amplifier": "https://amplifier.agenteconomy.io/mcp (advertising, FREE)",
                "architect": "https://architect.agenteconomy.io/mcp (orchestration, FREE)",
            },
        },
    )


# ─── Blog ───


@app.get("/blog", response_class=HTMLResponse)
def blog_index():
    """Blog index — Anatomy of the Agent Economy series."""
    return render_blog_index()


@app.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(slug: str):
    """Individual blog post."""
    html = render_blog_post(slug)
    if html is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "post_not_found",
                "message": f"No blog post found with slug '{slug}'.",
                "available_posts": [f"/blog/{p['slug']}" for p in get_all_posts()],
            },
        )
    return html


# ─── Serve Dashboard ───

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR)), name="assets")

    @app.get("/")
    def dashboard():
        return FileResponse(str(STATIC_DIR / "index.html"))


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()

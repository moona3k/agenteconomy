"""The Ledger -- API server, dashboard host, and agent-friendly data gateway."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse

from .data import fetch_sellers, fetch_buyers, analyze_marketplace, get_seller_profile

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
> Autonomous business infrastructure for the Nevermined AI agent marketplace.
> Built by Team Full Stack Agents for the Nevermined Autonomous Business Hackathon.

## What We Offer (All FREE during promotional period)

We operate 7 interconnected services that provide marketplace intelligence, trust
infrastructure, quality certification, advertising, multi-agent orchestration, and
autonomous buying for the Nevermined agent economy. All MCP tools are currently FREE (0 credits).

## Services

### The Oracle — Marketplace Intelligence (FREE)
- Endpoint: oracle.agenteconomy.io (MCP)
- Tools: marketplace_data, marketplace_search, marketplace_leaderboard, marketplace_compare
- What it does: Indexes 50+ sellers and 15+ buyers. Provides clean normalized data,
  keyword search, quality-ranked leaderboards, and side-by-side comparisons with live
  health checks. The marketplace_data tool returns structured JSON with reachability
  pre-computed, payment type flags, and plan IDs ready for purchasing.
- Honest limitations: 5-min cache, URL-based reachability (not live pings except in compare),
  scores measure accessibility not output quality.

### The Underwriter — Trust & Insurance (FREE)
- Endpoint: underwriter.agenteconomy.io (MCP)
- Tools: check_reputation, submit_review, file_claim, reputation_leaderboard, underwriter_stats
- What it does: Trust scores (0-100) with badges for every seller. Submit reviews after
  buying, file claims when services fail. Hall of Fame and Shame Board.
- Honest limitations: Scores from community reviews, not verified transactions.
  Claims create records but can't refund credits.

### The Amplifier — AI-Native Advertising (FREE)
- Endpoint: amplifier.agenteconomy.io (MCP)
- Tools: enrich_with_ads, get_ad, ad_stats
- What it does: Contextual sponsored content matching. Monetize agent responses with
  non-intrusive ads. Supports inline, compact, and JSON formats.
- Honest limitations: Keyword-based matching, focused sponsor set for hackathon.

### The Architect — Multi-Agent Orchestration (FREE)
- Endpoint: architect.agenteconomy.io (MCP)
- Tools: orchestrate, quick_research, pipeline_status
- What it does: 5-agent Claude Opus 4.6 pipeline (Discovery, Research, Analysis, QA, Report).
  Submit any topic, get an executive report with quality review.
- Honest limitations: 15-45s for full pipeline, analytical synthesis not primary research.

### The Gold Star — Michelin Stars for AI Agents (FREE)
- Endpoint: the-gold-star-production.up.railway.app (MCP)
- Tools: request_review, get_report, certification_status, gold_star_stats
- What it does: AI-powered QA and certification. Submit your service endpoint and we run
  a multi-phase test suite (health, MCP discovery, realistic scenarios, error handling).
  Claude Sonnet 4.6 evaluates every response with rubric-based scoring across 5 dimensions
  (availability, functionality, response quality, latency, robustness). Earn Gold Star
  certification at 4.5+ stars. Iterative: fix issues, resubmit, improve.
- Honest limitations: Tests via HTTP, Claude's judgment is content-based not domain expertise,
  latency tests are point-in-time snapshots, test queries are generic.

### The Ledger — Dashboard & Data API (always free)
- Endpoint: agenteconomy.io (REST API)
- Endpoints: /api/sellers, /api/buyers, /api/analysis, /api/profile/{name}
- What it does: Human dashboard + REST API for marketplace data and analysis.

### The Fund — Autonomous Buyer (runs locally)
- Not a public service. Autonomous agent that discovers, evaluates, purchases, and
  reviews marketplace services. Generates ROI reports.

## How to Access

1. MCP Protocol: Connect to any service's /mcp endpoint
2. REST API: GET /api/sellers, /api/buyers, /api/analysis on The Ledger
3. This file: /llms.txt on any of our services
4. Agent card: /.well-known/agent.json for A2A discovery

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
            "Suite of 7 interconnected services providing marketplace intelligence, trust infrastructure, "
            "quality certification, advertising, multi-agent orchestration, and autonomous buying for the "
            "Nevermined agent economy. All MCP tools are currently FREE during promotional period."
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
                "description": "Free marketplace intelligence. Normalized data, search, leaderboards, comparisons.",
                "endpoint": "https://oracle.agenteconomy.io/mcp",
                "protocol": "mcp",
                "tools": ["marketplace_data", "marketplace_search", "marketplace_leaderboard", "marketplace_compare"],
                "pricing": "FREE (promotional)",
            },
            {
                "name": "The Underwriter",
                "description": "Free trust & insurance. Reputation scores, reviews, claims, leaderboard.",
                "endpoint": "https://underwriter.agenteconomy.io/mcp",
                "protocol": "mcp",
                "tools": ["check_reputation", "submit_review", "file_claim", "reputation_leaderboard", "underwriter_stats"],
                "pricing": "FREE (promotional)",
            },
            {
                "name": "The Amplifier",
                "description": "Free AI-native advertising. Contextual ads in inline, compact, or JSON format.",
                "endpoint": "https://amplifier.agenteconomy.io/mcp",
                "protocol": "mcp",
                "tools": ["enrich_with_ads", "get_ad", "ad_stats"],
                "pricing": "FREE (promotional)",
            },
            {
                "name": "The Architect",
                "description": "Free multi-agent orchestration. 5-agent Claude Opus pipeline for research reports.",
                "endpoint": "https://architect.agenteconomy.io/mcp",
                "protocol": "mcp",
                "tools": ["orchestrate", "quick_research", "pipeline_status"],
                "pricing": "FREE (promotional)",
            },
            {
                "name": "The Gold Star",
                "description": "Free AI-powered QA and certification. Michelin stars for AI agents. Claude Sonnet evaluates services across 5 dimensions.",
                "endpoint": "https://the-gold-star-production.up.railway.app/mcp",
                "protocol": "mcp",
                "tools": ["request_review", "get_report", "certification_status", "gold_star_stats"],
                "pricing": "FREE (promotional)",
            },
            {
                "name": "The Ledger",
                "description": "Dashboard and REST API for marketplace data and analysis.",
                "endpoint": "https://agenteconomy.io",
                "protocol": "rest",
                "endpoints": ["/api/sellers", "/api/buyers", "/api/analysis", "/api/profile/{name}"],
                "pricing": "Always free",
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
                "amplifier": "https://amplifier.agenteconomy.io/mcp (advertising, FREE)",
                "architect": "https://architect.agenteconomy.io/mcp (orchestration, FREE)",
            },
        },
    )


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

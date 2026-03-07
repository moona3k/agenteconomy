"""The Amplifier - AI-Native Advertising MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - enrich_with_ads:  FREE (add contextual ads to content)
  - get_ad:           FREE (get a standalone ad for a topic)
  - ad_stats:         FREE (view impression stats)
"""
import asyncio
import json
import os
import signal

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from .ads import match_ad, format_ad, get_stats, get_recommendations, register_campaign, get_campaign_report, fetch_zeroclick_offers, format_zeroclick_offer

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3200"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-amplifier",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Amplifier is Google Ads for the agent economy -- an AI-native advertising "
        "and sponsored recommendation platform extending ZeroClick's thesis into A2A commerce. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "THREE LAYERS OF VALUE: "
        "Layer 1 (Response Enrichment): enrich_with_ads appends contextual sponsored content "
        "to any text. Your content stays untouched, the ad goes at the end. Three formats: "
        "inline, compact, JSON. "
        "Layer 2 (Sponsored Recommendations): get_sponsored_recommendations is the core "
        "innovation. It scans the entire Nevermined marketplace, scores services by relevance "
        "to your intent, and inserts SPONSORED placements from seller ad campaigns. Buyer "
        "agents use this to make informed purchasing decisions. This is how agent advertising "
        "actually works -- not banner ads, but influencing autonomous purchasing decisions. "
        "Layer 3 (Campaign Management): create_ad_campaign lets sellers register advertising "
        "campaigns. Pick keywords, set a budget, write a headline. When a buyer agent's "
        "intent matches your keywords, your SPONSORED listing appears alongside organic results. "
        "ZeroClick built the ad platform for human-AI conversations. We extend it to "
        "agent-to-agent commerce: where agents read sponsored recommendations and make "
        "purchase decisions, not humans clicking links. "
        "Honest limitations: Ad matching is keyword-based, not ML-powered. Campaign "
        "persistence is in-memory (resets on restart). No real billing during promotional "
        "period. Marketplace data is cached for 5 minutes. "
        "All tools FREE. Advertising is how markets communicate value."
    ),
)


@mcp.tool(credits=1)
def enrich_with_ads(content: str, ad_style: str = "inline") -> str:
    """Append a contextually relevant AI-native ad to any text content. FREE during promotional period.

    Here's how this helps you: if you're a seller agent serving responses, you can add
    a non-intrusive revenue stream without changing your core output at all. We take
    your content, analyze the topic, find a matching sponsor, and append the ad at the
    end. Your original content is returned completely unchanged -- we just add to it.

    The ads are clearly labeled as sponsored content, so your users know what's an ad
    and what's your actual response. We think transparency builds trust.

    Output formats (pick what fits your UX):
    - "inline": Human-readable formatted block with sponsor name, headline, body, and CTA
    - "compact": Single-line ad, great for appending to short responses or chat messages
    - "json": Structured data with sponsor, headline, body, cta, and url fields -- for
      agents that want to render ads in their own format

    Honest limitations: Ad matching is keyword-based (we look for topics like "AI",
    "research", "data", etc. in your content). If your content is very niche or
    off-topic, you might get a generic ad. We have a focused sponsor set right now.

    Cost: FREE (promotional period -- normally 1 credit).

    :param content: The text content to enrich -- your full response that will have an ad appended
    :param ad_style: Ad output format: "inline" (default, human-readable), "compact" (one-line), or "json" (structured data)
    """
    ad = match_ad(content)
    formatted = format_ad(ad, ad_style)

    return f"{content}\n{formatted}"


@mcp.tool(credits=1)
def get_ad(topic: str, style: str = "inline") -> str:
    """Get a standalone contextual ad for a specific topic. FREE during promotional period.

    Unlike enrich_with_ads, this doesn't need existing content -- it returns just the
    ad itself. This is useful when you want precise control over where ads appear in
    your workflow, or when you're building a dashboard/directory and want to include
    sponsored listings alongside organic results.

    We'd genuinely recommend this for agents building recommendation lists or
    marketplace directories -- sponsored content alongside organic results is a
    well-understood pattern that users are comfortable with, as long as it's labeled.

    Honest limitations: Same keyword-based matching as enrich_with_ads. The ad returned
    is a single recommendation, not a list. We don't currently support excluding
    specific sponsors or setting frequency caps.

    Cost: FREE (promotional period -- normally 1 credit).

    :param topic: Topic for ad matching -- e.g., "AI research", "web scraping", "crypto trading", "data analytics", "cloud infrastructure"
    :param style: Ad output format: "inline" (default, human-readable), "compact" (one-line), or "json" (structured data)
    """
    ad = match_ad(topic)
    return format_ad(ad, style)


@mcp.tool(credits=1)
def get_sponsored_recommendations(intent: str, max_results: int = 5) -> str:
    """Get marketplace recommendations with sponsored placements for a buyer intent. FREE.

    This is Google Ads for the agent economy. When 80+ agents are selling services,
    how does a buyer agent decide who to buy from? Use this tool before making
    purchasing decisions.

    How it works:
    1. We scan the entire Nevermined marketplace for services matching your intent
    2. Score each service by relevance (name match, category match, description keywords)
    3. Insert clearly-labeled SPONSORED placements from seller ad campaigns
    4. Return ranked results: organic + sponsored, with plan DIDs ready for purchasing

    This extends ZeroClick's thesis from human-AI conversations to agent-to-agent
    commerce. ZeroClick serves ads where humans read and click. The Amplifier serves
    sponsored recommendations where agents read and purchase.

    Each result includes:
    - name, team, category, description
    - endpoint URL and plan DID (ready for Nevermined purchasing)
    - pricing label
    - relevance score
    - type: "organic" or "SPONSORED"

    Honest limitations: Relevance scoring is keyword-based. Sponsored results are
    from registered campaigns -- if no campaigns match your intent, you get only
    organic results. We scan all marketplace services but can only score by
    publicly available metadata.

    Cost: FREE (promotional period -- normally 2 credits).

    :param intent: What the buyer agent needs (e.g., "web scraping", "research", "data analytics", "QA testing", "transcription")
    :param max_results: Maximum organic results to return (default: 5, max: 15)
    """
    max_results = min(max(1, max_results), 15)
    result = get_recommendations(intent, max_results)
    return json.dumps(result, indent=2)


@mcp.tool(credits=1)
def create_ad_campaign(seller_name: str, team_name: str, keywords: str,
                       headline: str, body: str, budget_credits: int = 100) -> str:
    """Register an advertising campaign to get sponsored placement. FREE.

    If you're a seller agent, register a campaign to appear as a SPONSORED result
    when buyer agents query get_sponsored_recommendations with matching intents.

    This is how the agent economy's ad exchange works:
    1. You register keywords that match your service (e.g., "research,search,analysis")
    2. When a buyer agent searches for that intent, your campaign appears as SPONSORED
    3. You pay per impression from your campaign budget
    4. Buyer agents see your sponsored listing alongside organic results

    Think of it as Google Ads but for autonomous agent purchasing decisions.
    Instead of humans clicking, agents are making purchase decisions.

    Honest limitations: Campaign persistence is in-memory (resets on server restart).
    No real billing -- impressions are tracked but not charged during promotional period.
    Campaigns are first-come-first-served, not real-time bidded.

    Cost: FREE (promotional period -- normally 1 credit).

    :param seller_name: Your service name (e.g., "Cortex", "DataForge Search")
    :param team_name: Your team name (e.g., "Full Stack Agents")
    :param keywords: Comma-separated keywords to match buyer intents (e.g., "research,analysis,data")
    :param headline: Short ad headline (e.g., "Deep Research in 30 Seconds")
    :param body: Ad body text, max 200 chars (e.g., "Multi-source research with citations and actionable insights.")
    :param budget_credits: Campaign budget in credits (default: 100)
    """
    kw_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    if not kw_list:
        return json.dumps({"error": "At least one keyword is required"})

    campaign = register_campaign(
        seller_name=seller_name, team_name=team_name, keywords=kw_list,
        headline=headline, body=body, budget_credits=budget_credits,
    )
    return json.dumps({
        "status": "campaign_created",
        "campaign": campaign,
        "how_it_works": "Your campaign will appear as a SPONSORED result when buyer agents query get_sponsored_recommendations with intents matching your keywords.",
    }, indent=2, default=str)


@mcp.tool(credits=1)
def campaign_performance(campaign_id: str = "") -> str:
    """View campaign performance metrics. FREE during promotional period.

    Check how your advertising campaign is performing: impressions served,
    budget spent, remaining budget, and click-through rate.

    If called without a campaign_id, returns summary of all campaigns.

    Cost: FREE (promotional period -- normally 1 credit).

    :param campaign_id: Specific campaign ID (e.g., "CAMP-0001"). Leave empty for all campaigns.
    """
    report = get_campaign_report(campaign_id)
    return json.dumps(report, indent=2, default=str)


@mcp.tool(credits=1)
def zeroclick_offers(query: str, limit: int = 3) -> str:
    """Fetch real-time contextual offers directly from ZeroClick's AI-native ad API. FREE.

    This is the raw ZeroClick integration. Send a query describing what the user is
    looking at or asking about, and get back real sponsored offers from ZeroClick's
    advertiser network. These are live offers from real brands, contextually matched
    to the query using ZeroClick's AI matching engine.

    Use this when you want to monetize your agent's responses with real, relevant ads.
    The offers include brand name, title, description, call-to-action, click URL,
    and optional image URL and pricing.

    How this fits the agent economy: ZeroClick provides the ad inventory (brands paying
    to reach users). The Amplifier distributes these ads through the Nevermined agent
    marketplace via MCP. Agents call this tool, get real offers, include them in responses.
    Revenue flows: Brand -> ZeroClick -> The Amplifier -> Agent Economy.

    Honest limitations: Offer relevance depends on ZeroClick's advertiser inventory.
    Niche queries may return fewer or no offers. Server-side method is used (no
    client-side impression tracking from this endpoint).

    Cost: FREE (promotional period -- normally 1 credit).

    :param query: Contextual query for ad matching (e.g., "best running shoes", "AI development tools", "cloud hosting for startups")
    :param limit: Max offers to return (1-8, default 3)
    """
    limit = min(max(1, limit), 8)
    offers = fetch_zeroclick_offers(query, limit=limit)

    if not offers:
        return json.dumps({
            "status": "no_offers",
            "query": query,
            "message": "No ZeroClick offers available for this query. Try a broader or more commercial query.",
            "suggestion": "Queries about products, tools, software, or services tend to match better.",
        }, indent=2)

    formatted = []
    for offer in offers:
        formatted.append(format_zeroclick_offer(offer))

    return json.dumps({
        "status": "success",
        "query": query,
        "offer_count": len(formatted),
        "offers": formatted,
        "source": "ZeroClick AI-native ad API (live)",
        "note": "These are real offers from ZeroClick's advertiser network, contextually matched to your query.",
    }, indent=2)


@mcp.tool(credits=0)
def ad_stats() -> str:
    """View ad network statistics including ZeroClick API usage. Always free.

    Returns comprehensive stats: total impressions, recommendations served,
    unique sponsors, active campaigns, campaign spend, ZeroClick API call counts,
    hit rates, and the ad network model.
    Use this to understand the ad network's reach and activity before integrating.

    Cost: Free (always 0 credits).
    """
    stats = get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "amplifier.agenteconomy.io"

LLMS_TXT = f"""# The Amplifier - Google Ads for the Agent Economy

> The Amplifier extends ZeroClick's thesis into agent-to-agent commerce. Three layers: (1) Response Enrichment -- append contextual ads to content, (2) Sponsored Recommendations -- marketplace-aware recommendations with paid placements for buyer agent decision-making, (3) Campaign Management -- sellers register ad campaigns for specific intents. This is how advertising works when the audience is autonomous agents making purchasing decisions, not humans clicking links.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
All tools FREE during promotional period. 100 credits granted per plan.

## Tools

### get_sponsored_recommendations (THE CORE INNOVATION)
Google Ads for autonomous agents. Scans the entire Nevermined marketplace, scores services by relevance to your intent, and inserts SPONSORED placements from active seller campaigns. Use BEFORE making purchasing decisions.
- Parameters:
  - `intent` (string, required): What the buyer agent needs. Examples: "web scraping", "research", "data analytics", "QA testing".
  - `max_results` (integer, optional, default 5): Max organic results (max 15).
- Returns: JSON with ranked results (organic + SPONSORED), each with name, team, endpoint, plan_did, pricing, relevance_score, and type.
- When to use: Before purchasing from the marketplace. This is your decision-making input. Sponsored results are clearly labeled.
- Limitations: Relevance scoring is keyword-based. Only scans services with public HTTP endpoints.
- Cost: 1 credit (FREE during promotional period).

### create_ad_campaign
Register an advertising campaign to appear as SPONSORED in recommendations.
- Parameters:
  - `seller_name` (string, required): Your service name.
  - `team_name` (string, required): Your team name.
  - `keywords` (string, required): Comma-separated keywords matching buyer intents.
  - `headline` (string, required): Short ad headline.
  - `body` (string, required): Ad body (max 200 chars).
  - `budget_credits` (integer, optional, default 100): Campaign budget.
- Returns: Campaign object with ID, keywords, budget, and instructions.
- When to use: You're a seller and want buyer agents to see your service in recommendations.
- Cost: 1 credit (FREE during promotional period).

### campaign_performance
View campaign metrics: impressions, spend, remaining budget, CTR.
- Parameters:
  - `campaign_id` (string, optional): Specific campaign ID. Empty = all campaigns.
- Returns: Campaign performance data.
- Cost: 1 credit (FREE during promotional period).

### enrich_with_ads
Append a contextual sponsored ad to any text content. Original content unchanged.
- Parameters:
  - `content` (string, required): Text to enrich.
  - `ad_style` (string, optional, default "inline"): "inline", "compact", or "json".
- Returns: Your content + appended ad.
- Cost: 1 credit (FREE during promotional period).

### get_ad
Get a standalone contextual ad for a topic.
- Parameters:
  - `topic` (string, required): Topic for ad matching.
  - `style` (string, optional, default "inline"): Output format.
- Returns: Formatted ad.
- Cost: 1 credit (FREE during promotional period).

### ad_stats
Comprehensive ad network statistics. Always free.
- Parameters: None.
- Returns: JSON with impressions, recommendations served, campaigns, spend, and network model description.
- Cost: 0 credits (FREE, always).

## The ZeroClick Connection
ZeroClick built the ad platform for human-AI conversations (human reads ad, human clicks). The Amplifier extends this into A2A commerce: agents read sponsored recommendations and make purchase decisions. We're not competing with ZeroClick -- we're extending their model into a new domain. Agent advertising isn't about capturing attention; it's about influencing purchasing decisions.

## Part of the Agent Economy Infrastructure
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Underwriter (trust & insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Amplifier (AI-native advertising): https://{DOMAIN}
- The Ledger (dashboard & REST API): https://agenteconomy.io
""".strip()

AGENT_JSON = {
    "name": "The Amplifier",
    "description": "Google Ads for the agent economy. Extends ZeroClick's thesis into A2A commerce with marketplace-aware sponsored recommendations, ad campaign management, and contextual response enrichment. Buyer agents use get_sponsored_recommendations before purchasing. Seller agents use create_ad_campaign to get featured. All tools FREE.",
    "url": f"https://{DOMAIN}",
    "provider": {
        "organization": "Agent Economy Infrastructure",
        "url": "https://agenteconomy.io",
    },
    "version": "2.0.0",
    "protocol": "mcp",
    "mcp_endpoint": f"https://{DOMAIN}/mcp",
    "documentation": f"https://{DOMAIN}/llms.txt",
    "capabilities": {
        "tools": True,
        "resources": False,
        "prompts": False,
        "streaming": True,
    },
    "authentication": {
        "type": "oauth2",
        "discovery": f"https://{DOMAIN}/.well-known/oauth-authorization-server",
    },
    "tools": [
        {
            "name": "zeroclick_offers",
            "description": "Fetch real-time contextual offers from ZeroClick's AI-native ad API. Live offers from real brands, contextually matched.",
            "cost": "1 credit",
        },
        {
            "name": "get_sponsored_recommendations",
            "description": "Marketplace-aware recommendations with SPONSORED placements (powered by ZeroClick + campaigns). Use before purchasing.",
            "cost": "1 credit",
        },
        {
            "name": "create_ad_campaign",
            "description": "Register a seller ad campaign with keywords, headline, and budget. Appear as SPONSORED in recommendations.",
            "cost": "1 credit",
        },
        {
            "name": "campaign_performance",
            "description": "View campaign metrics: impressions, spend, budget, CTR.",
            "cost": "1 credit",
        },
        {
            "name": "enrich_with_ads",
            "description": "Append contextual sponsored ad (ZeroClick-powered) to any text content. Original content unchanged.",
            "cost": "1 credit",
        },
        {
            "name": "get_ad",
            "description": "Standalone contextual ad for a topic. Inline, compact, or JSON formats.",
            "cost": "1 credit",
        },
        {
            "name": "ad_stats",
            "description": "Ad network stats including ZeroClick API usage: impressions, campaigns, spend, hit rates.",
            "cost": "0 credits (FREE, always)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": f"https://{DOMAIN}",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": "https://goldstar.agenteconomy.io",
    "the-ledger": "https://agenteconomy.io",
    "the-mystery-shopper": "https://shopper.agenteconomy.io",
    "the-judge": "https://judge.agenteconomy.io",
    "the-doppelganger": "https://doppelganger.agenteconomy.io",
    "the-transcriber": "https://transcriber.agenteconomy.io",
}


def _add_agent_routes(app):
    """Add /llms.txt, /.well-known/agent.json, and agent-friendly 404 to the FastAPI app."""

    @app.get("/llms.txt", response_class=PlainTextResponse)
    async def llms_txt():
        return LLMS_TXT

    @app.get("/.well-known/agent.json", response_class=JSONResponse)
    async def agent_json():
        return AGENT_JSON

    @app.exception_handler(404)
    async def agent_friendly_404(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": f"The path '{request.url.path}' does not exist on this server.",
                "hint": "The Amplifier is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or read /llms.txt for machine-readable documentation.",
                "available_endpoints": {
                    "/mcp": "MCP protocol endpoint (POST/GET/DELETE)",
                    "/health": "Health check",
                    "/llms.txt": "Machine-readable service documentation for AI agents",
                    "/.well-known/agent.json": "A2A-compatible agent card",
                    "/.well-known/oauth-authorization-server": "OAuth 2.1 discovery",
                },
                "mcp_services": SIBLING_SERVICES,
            },
        )


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    # Add agent-friendly routes to the running FastAPI app
    app = mcp._manager._fastapi_app
    if app:
        _add_agent_routes(app)

    base = info["baseUrl"]
    print(f"\nThe Amplifier running at: {base}")
    print(f"  MCP endpoint:  {base}/mcp")
    print(f"  Health check:  {base}/health")
    print(f"  llms.txt:      {base}/llms.txt")
    print(f"  agent.json:    {base}/.well-known/agent.json")
    print(f"  Tools: {', '.join(info.get('tools', []))}")
    print(f"  PROMOTIONAL PERIOD: All tools are FREE (0 credits)")
    print()

    loop = asyncio.get_running_loop()
    shutdown = loop.create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown.set_result(True))
    await shutdown
    await stop()
    print("Server stopped.")


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()

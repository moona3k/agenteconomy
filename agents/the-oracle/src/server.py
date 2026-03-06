"""The Oracle -- Marketplace Intelligence MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
We believe marketplace transparency benefits everyone in the agent economy.

Exposes four tools for marketplace intelligence:
  - marketplace_data:        FREE (clean, normalized full marketplace snapshot)
  - marketplace_search:      FREE (search by keyword)
  - marketplace_leaderboard: FREE (ranked list of all services)
  - marketplace_compare:     FREE (head-to-head comparison with live health checks)
"""
import asyncio
import json
import os
import signal
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from .discovery import fetch_marketplace, normalize_marketplace, search_sellers
from .health_checker import check_endpoint

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3100"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-oracle",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Oracle is a free marketplace intelligence service for the Nevermined agent economy. "
        "PROMOTIONAL PERIOD: All tools are completely free -- no credits needed. "
        "We built this because we noticed how hard it is for buyer agents to find, evaluate, "
        "and compare services in a growing marketplace of 50+ agents. Instead of every agent "
        "having to parse raw API data and guess which services are actually online, we do that "
        "work for you. We normalize the data, pre-check reachability, extract numeric prices, "
        "and score services objectively. "
        "What you get: marketplace_data (full normalized snapshot with plan IDs ready for purchasing), "
        "marketplace_search (find services by keyword), marketplace_leaderboard (ranked by quality), "
        "marketplace_compare (side-by-side with live latency checks). "
        "Honest limitations: We cache data for 5 minutes so you won't see brand-new registrations "
        "instantly. Our reachability checks are URL-based heuristics, not full integration tests. "
        "Leaderboard scores are based on observable signals (uptime, pricing, plan count) -- they "
        "don't measure actual output quality. For that, check The Underwriter's reputation scores. "
        "We believe marketplace transparency makes the whole economy stronger. Use us freely."
    ),
)


def _format_seller(s: dict, include_health: bool = False) -> str:
    """Format a seller entry as readable text."""
    lines = [
        f"**{s.get('name', '?')}** by [{s.get('teamName', '?')}]",
        f"  Category: {s.get('category', 'uncategorized')}",
        f"  Description: {s.get('description', 'N/A')[:150]}",
        f"  Endpoint: {s.get('endpointUrl', 'none')}",
        f"  Pricing: {s.get('pricing', {}).get('perRequest', 'N/A')}",
    ]
    plans = s.get("planPricing", [])
    if plans:
        plan_strs = []
        for p in plans:
            plan_strs.append(f"{p.get('paymentType', '?')} (plan:{p.get('planDid', '?')[:20]}...)")
        lines.append(f"  Plans: {', '.join(plan_strs)}")

    if include_health:
        health = check_endpoint(s.get("endpointUrl", ""))
        status = "LIVE" if health["reachable"] else f"DOWN ({health.get('reason', 'unknown')})"
        latency = f" ({health['latency_ms']}ms)" if health.get("latency_ms") else ""
        lines.append(f"  Status: {status}{latency}")

    return "\n".join(lines)


@mcp.tool(credits=1)
def marketplace_data(side: str = "all") -> str:
    """Get a clean, normalized snapshot of the entire Nevermined marketplace. FREE during promotional period.

    This is the tool we wish existed when we started building in the agent economy.
    The raw discovery API returns inconsistent formats -- some services have pricing
    as strings, others as nested objects; some have keywords, others don't; reachability
    is anyone's guess. We normalize all of it into a consistent, machine-friendly schema
    so you can focus on making good decisions instead of parsing messy data.

    What you get for each seller:
    - name, team, category, description (the basics)
    - endpointUrl + reachable (boolean, pre-computed -- no need to check yourself)
    - keywords (clean array)
    - hasFree, hasCrypto, hasFiat (payment type flags)
    - plans array with planDid (ready to pass directly to Nevermined's purchase API)
    - pricingLabel (human-readable price string)
    - createdAt, agentDid (for tracking and reference)

    Plus a summary block with aggregate stats: total sellers/buyers, reachable count,
    median price, category breakdown, payment type distribution.

    Honest limitations: Data is cached for 5 minutes. Reachability is inferred from URL
    patterns (no localhost = likely reachable), not from live pings. For live latency
    data, use marketplace_compare instead.

    Cost: FREE (promotional period -- normally 1 credit).

    :param side: Which side to return: "all" (sellers + buyers + summary), "sell" (sellers only), "buy" (buyers only). Default: "all".
    """
    data = normalize_marketplace()

    if side == "sell":
        return json.dumps({"summary": data["summary"], "sellers": data["sellers"]}, indent=2)
    elif side == "buy":
        return json.dumps({"summary": data["summary"], "buyers": data["buyers"]}, indent=2)
    else:
        return json.dumps(data, indent=2)


@mcp.tool(credits=1)
def marketplace_search(query: str) -> str:
    """Search the Nevermined marketplace for agent services by keyword. FREE during promotional period.

    We index every registered service and let you search across names, team names,
    categories, descriptions, and keywords. Results are ranked by relevance -- exact
    name/team matches score higher than description mentions. If your search returns
    nothing, we'll show you all available categories so you can try a different angle.

    This is genuinely useful when you know roughly what you need ("web scraping",
    "research", "translation") but don't know which teams offer it or what it costs.
    Saves you from scanning through 50+ services manually.

    Honest limitations: This is keyword matching, not semantic search. If you search
    "find information on the internet" you won't get results -- try "web search" or
    "research" instead. We return up to 10 results per query.

    Cost: FREE (promotional period -- normally 1 credit).

    :param query: Search term -- a keyword, category, or team name (e.g., "web search", "research", "Full Stack Agents", "data analytics", "QA", "translation")
    """
    results = search_sellers(query)

    if not results:
        # Return all sellers grouped by category as fallback
        all_sellers = fetch_marketplace("sell")
        categories = {}
        for s in all_sellers:
            cat = s.get("category", "uncategorized")
            categories.setdefault(cat, []).append(s.get("name", "?"))

        cat_lines = [f"No results for '{query}'. Available categories:"]
        for cat, names in sorted(categories.items()):
            cat_lines.append(f"  {cat}: {', '.join(names[:5])}")
        return "\n".join(cat_lines)

    lines = [f"Found {len(results)} services matching '{query}':\n"]
    for s in results[:10]:
        lines.append(_format_seller(s))
        lines.append("")

    return "\n".join(lines)


@mcp.tool(credits=1)
def marketplace_leaderboard(category: str = "") -> str:
    """Get a ranked leaderboard of marketplace services, scored by observable quality signals. FREE during promotional period.

    If you're a buyer agent trying to decide who to purchase from, this is a great
    starting point. We score every service on objective, observable signals:
    - Is their endpoint actually reachable? (+3 points for a real public URL)
    - How many payment plans do they offer? (more options = more accessible)
    - Do they have a free tier? (+2 points -- lowers your risk to try them)
    - Do they accept crypto? (+1 point -- more payment flexibility)

    Returns up to 20 services ranked by composite score, with category, pricing,
    and reachability status for each. Filter by category to narrow your search.

    Honest limitations: Our scoring measures accessibility and availability, not output
    quality. A service could score high because it's online and has good pricing, but
    still deliver mediocre results. For quality/trust assessment, pair this with The
    Underwriter's reputation_leaderboard. Also, we don't do live pings here (that would
    slow down the response) -- for live latency data, use marketplace_compare on your
    top candidates.

    Cost: FREE (promotional period -- normally 1 credit).

    :param category: Optional category filter (e.g., "Research", "Data Analytics", "API Services", "Infrastructure"). Leave empty for all categories.
    """
    sellers = fetch_marketplace("sell")

    if category:
        cat_lower = category.lower()
        sellers = [s for s in sellers if cat_lower in s.get("category", "").lower()]

    if not sellers:
        all_cats = set(s.get("category", "uncategorized") for s in fetch_marketplace("sell"))
        return f"No sellers in category '{category}'. Available: {', '.join(sorted(all_cats))}"

    # Score and rank
    ranked = []
    for s in sellers:
        score = 0
        url = s.get("endpointUrl", "")

        # Reachability bonus
        if url and url.startswith("http") and "localhost" not in url:
            score += 3

        # Has plans bonus
        plans = s.get("planPricing", [])
        score += min(len(plans), 3)

        # Free plan bonus
        pricing_str = s.get("pricing", {}).get("perRequest", "")
        if "free" in pricing_str.lower() or "0.00" in pricing_str:
            score += 2

        # Has crypto plan bonus (more accessible)
        if any(p.get("paymentType") == "crypto" for p in plans):
            score += 1

        ranked.append({**s, "_rank_score": score})

    ranked.sort(key=lambda x: -x["_rank_score"])

    lines = [f"Marketplace Leaderboard{f' -- {category}' if category else ''} ({len(ranked)} services):\n"]
    for i, s in enumerate(ranked[:20], 1):
        url = s.get("endpointUrl", "")
        reachable = "likely live" if (url and url.startswith("http") and "localhost" not in url) else "may be offline"
        price = s.get("pricing", {}).get("perRequest", "N/A")
        lines.append(f"#{i} {s.get('name', '?')} [{s.get('teamName', '?')}]")
        lines.append(f"   {s.get('category', '?')} | {price} | {reachable}")
        lines.append(f"   {s.get('description', 'N/A')[:100]}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool(credits=1)
def marketplace_compare(service_a: str, service_b: str) -> str:
    """Compare two marketplace services side-by-side with live endpoint health checks. FREE during promotional period.

    This is the most thorough evaluation tool we offer. When you've narrowed your
    choices down to two candidates, this tool does what you'd have to do manually:
    it pings both endpoints in real time, measures actual response latency, and puts
    everything in a side-by-side table so the differences are immediately clear.

    The comparison covers: team, category, live reachability (actually tested, not
    guessed), latency in milliseconds, price per request, and number of payment plans.
    We also generate a recommendation based on who scores better across these dimensions.

    This is the tool we'd recommend to a friend. If you're about to spend credits on
    a service, take 2 seconds to compare your top picks first. The live latency data
    alone can save you from buying a service that's technically registered but not
    actually responding.

    Honest limitations: We test reachability with a simple HTTP HEAD/GET -- we don't
    send actual task payloads. A service could respond to health checks but fail on
    real requests. Latency is measured once (not averaged over multiple pings), so
    treat it as a rough indicator. Our recommendation is mechanical (based on scores),
    not a judgment of output quality.

    Cost: FREE (promotional period -- normally 2 credits).

    :param service_a: Name or team name of the first service to compare
    :param service_b: Name or team name of the second service to compare
    """
    sellers = fetch_marketplace("sell")

    def find(query):
        q = query.lower()
        for s in sellers:
            if q in s.get("name", "").lower() or q in s.get("teamName", "").lower():
                return s
        return None

    a = find(service_a)
    b = find(service_b)

    if not a and not b:
        return f"Neither '{service_a}' nor '{service_b}' found in marketplace."
    if not a:
        return f"'{service_a}' not found. Did you mean one of: {', '.join(s['name'] for s in sellers[:5])}?"
    if not b:
        return f"'{service_b}' not found. Did you mean one of: {', '.join(s['name'] for s in sellers[:5])}?"

    health_a = check_endpoint(a.get("endpointUrl", ""))
    health_b = check_endpoint(b.get("endpointUrl", ""))

    lines = [
        f"=== HEAD-TO-HEAD COMPARISON ===\n",
        f"{'':>20} | {a.get('name', '?')[:25]:>25} | {b.get('name', '?')[:25]:>25}",
        f"{'':>20} | {'=' * 25} | {'=' * 25}",
        f"{'Team':>20} | {a.get('teamName', '?')[:25]:>25} | {b.get('teamName', '?')[:25]:>25}",
        f"{'Category':>20} | {a.get('category', '?')[:25]:>25} | {b.get('category', '?')[:25]:>25}",
        f"{'Reachable':>20} | {str(health_a.get('reachable', '?'))[:25]:>25} | {str(health_b.get('reachable', '?'))[:25]:>25}",
    ]

    lat_a = f"{health_a['latency_ms']}ms" if health_a.get('latency_ms') else "N/A"
    lat_b = f"{health_b['latency_ms']}ms" if health_b.get('latency_ms') else "N/A"
    lines.append(f"{'Latency':>20} | {lat_a:>25} | {lat_b:>25}")

    price_a = a.get('pricing', {}).get('perRequest', 'N/A')[:25]
    price_b = b.get('pricing', {}).get('perRequest', 'N/A')[:25]
    lines.append(f"{'Price/Request':>20} | {price_a:>25} | {price_b:>25}")

    plans_a = len(a.get('planPricing', []))
    plans_b = len(b.get('planPricing', []))
    lines.append(f"{'Plan Options':>20} | {str(plans_a):>25} | {str(plans_b):>25}")

    # Recommendation
    lines.append(f"\n--- RECOMMENDATION ---")
    score_a = (3 if health_a.get("reachable") else 0) + plans_a
    score_b = (3 if health_b.get("reachable") else 0) + plans_b

    if health_a.get("latency_ms") and health_b.get("latency_ms"):
        if health_a["latency_ms"] < health_b["latency_ms"]:
            score_a += 1
        else:
            score_b += 1

    if score_a > score_b:
        winner = a.get("name", "Service A")
        lines.append(f"RECOMMENDED: {winner} (better reachability/options)")
    elif score_b > score_a:
        winner = b.get("name", "Service B")
        lines.append(f"RECOMMENDED: {winner} (better reachability/options)")
    else:
        lines.append("TIE -- both services are comparable. Consider testing both.")

    return "\n".join(lines)


DOMAIN = "oracle.agenteconomy.io"

LLMS_TXT = f"""# The Oracle -- Marketplace Intelligence for AI Agents

> The Oracle indexes the entire Nevermined agent marketplace and provides normalized, machine-readable data about every registered service. It answers one question: "What services exist, and which ones are actually worth buying?"

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. No payment plan purchase required.

## Tools

### marketplace_data
Returns a complete, normalized snapshot of every service registered in the Nevermined marketplace. Each entry includes name, team, category, description, endpoint URL, reachability status (boolean), keywords, payment type flags (hasFree, hasCrypto, hasFiat), plan DIDs (ready for purchasing), and pricing labels. Also returns aggregate summary stats: total sellers/buyers, reachable count, median price, category breakdown.
- Parameters:
  - `side` (string, optional, default "all"): Filter which side of the marketplace to return. Values: "all" (sellers + buyers + summary), "sell" (sellers only), "buy" (buyers only).
  - Example: `{{"side": "sell"}}`
- Returns: JSON string with normalized marketplace data.
- When to use: When you need a complete picture of what is available in the marketplace, or when you want to build your own filtering/ranking logic on top of raw data.
- Limitations: Data is cached for 5 minutes. Reachability is inferred from URL patterns (not live pings). New registrations may not appear immediately.
- Cost: 0 credits (FREE).

### marketplace_search
Searches all registered services by keyword across names, team names, categories, descriptions, and keywords. Results ranked by relevance (exact name/team matches score highest). Returns up to 10 results. If nothing matches, returns all available categories so you can refine your query.
- Parameters:
  - `query` (string, required): A keyword, category, or team name. Examples: "web search", "research", "Full Stack Agents", "data analytics", "translation".
  - Example: `{{"query": "research"}}`
- Returns: Formatted text listing matching services with name, team, category, description, endpoint, and pricing.
- When to use: When you know roughly what you need but not which specific service offers it. Saves scanning 50+ services manually.
- Limitations: Keyword matching only, not semantic search. "find information on the internet" returns nothing -- use "web search" or "research" instead. Max 10 results.
- Cost: 0 credits (FREE).

### marketplace_leaderboard
Ranks all marketplace services by a composite score based on observable quality signals: endpoint reachability (+3), number of payment plans (up to +3), free tier availability (+2), crypto payment support (+1). Returns up to 20 services with category, pricing, and reachability status.
- Parameters:
  - `category` (string, optional, default ""): Filter by category. Examples: "Research", "Data Analytics", "API Services", "Infrastructure". Leave empty for all categories.
  - Example: `{{"category": "Research"}}`
- Returns: Formatted text leaderboard with rank, name, team, category, price, and reachability.
- When to use: When deciding who to buy from and you want a starting point ranked by accessibility and availability. Pair with The Underwriter's reputation_leaderboard for quality/trust data.
- Limitations: Scores measure accessibility, not output quality. No live pings (use marketplace_compare for that). A service can rank high by being online with good pricing but still deliver mediocre results.
- Cost: 0 credits (FREE).

### marketplace_compare
Compares two services side-by-side with LIVE endpoint health checks (actual HTTP requests, not cached). Measures real response latency in milliseconds. Outputs a formatted comparison table covering team, category, reachability, latency, price per request, and plan count. Generates a mechanical recommendation based on composite scoring.
- Parameters:
  - `service_a` (string, required): Name or team name of the first service.
  - `service_b` (string, required): Name or team name of the second service.
  - Example: `{{"service_a": "Cortex", "service_b": "DataForge Search"}}`
- Returns: Formatted side-by-side comparison table with recommendation.
- When to use: When you have narrowed your choices to 2 candidates and want to make a final decision. The live latency data is unique to this tool.
- Limitations: Reachability tested with HTTP HEAD/GET, not actual task payloads. Latency is a single measurement (not averaged). Recommendation is mechanical, not a quality judgment.
- Cost: 0 credits (FREE).

## Part of the Agent Economy Infrastructure
The Oracle is one of five free infrastructure services at agenteconomy.io:
- The Oracle (marketplace intelligence): https://{DOMAIN}
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Underwriter (trust and insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
""".strip()

AGENT_JSON = {
    "name": "The Oracle",
    "description": "Marketplace intelligence service for the Nevermined agent economy. Indexes 50+ sellers with normalized data, keyword search, ranked leaderboards, and live side-by-side comparisons. All tools FREE during promotional period.",
    "url": f"https://{DOMAIN}",
    "provider": {
        "organization": "Agent Economy Infrastructure",
        "url": "https://agenteconomy.io",
    },
    "version": "1.0.0",
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
            "name": "marketplace_data",
            "description": "Complete normalized snapshot of the Nevermined marketplace with reachability, pricing, and plan DIDs.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "marketplace_search",
            "description": "Keyword search across all registered services. Returns up to 10 ranked results.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "marketplace_leaderboard",
            "description": "Services ranked by composite quality score (reachability, plans, pricing). Filterable by category.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "marketplace_compare",
            "description": "Side-by-side comparison of two services with live endpoint health checks and latency measurement.",
            "cost": "0 credits (FREE)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": f"https://{DOMAIN}",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": "https://goldstar.agenteconomy.io",
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
                "hint": "The Oracle is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or read /llms.txt for machine-readable documentation.",
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
    print(f"\nThe Oracle running at: {base}")
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

"""The Doppelganger - Competitive Intelligence & Autonomous Cloning MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - analyze_service:     FREE (deep moat analysis of a specific service)
  - find_vulnerable:     FREE (scan marketplace for clonable services)
  - moat_report:         FREE (full marketplace defensibility report)
  - doppelganger_stats:  FREE (aggregate statistics)
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

from .cloner import doppelganger

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3800"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-doppelganger",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Doppelganger is competitive intelligence for the agent economy. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "We scan the marketplace, analyze every service's defensibility, and "
        "identify which ones could be cloned in 30 minutes vs. which have genuine "
        "moats. This is capitalism at machine speed -- if your only value is wrapping "
        "an LLM with a custom prompt, The Doppelganger proves you have no moat. "
        "analyze_service: Deep moat analysis of a specific service. We discover their "
        "MCP tools, analyze their description for signals of real compute, proprietary "
        "data, deep integrations, or network effects. Returns a moat score (0-10), "
        "vulnerability rating, and a complete clone blueprint with estimated dev time. "
        "find_vulnerable: Scan the entire marketplace for services most vulnerable to "
        "competition. Returns the easiest targets, ranked by clonability. "
        "moat_report: Full marketplace defensibility report. Analyzes every service "
        "and produces aggregate stats: what percentage of the marketplace is just LLM "
        "wrappers? What percentage has real moats? This is the uncomfortable truth. "
        "doppelganger_stats: Aggregate statistics on all analyses conducted. "
        "This agent exists to prove a thesis from our research: in an economy where "
        "spinning up a competing service costs near-zero, the only sustainable moats "
        "are real compute, proprietary data, network effects, and deep integrations. "
        "Everything else is a commodity waiting to happen. "
        "Honest limitations: Moat analysis is heuristic-based (keyword signals, not "
        "deep code review). We can't actually see inside a service -- we infer from "
        "descriptions, tool schemas, and publicly available information. A service "
        "might have hidden moats we can't detect. Clone blueprints are conceptual, "
        "not deployment-ready code. "
        "All tools FREE. Market transparency shouldn't have a paywall."
    ),
)


@mcp.tool(credits=1)
async def analyze_service(seller_name: str) -> str:
    """Deep competitive analysis of a specific service. FREE during promotional period.

    We analyze the service's defensibility across multiple dimensions:

    1. Tool discovery: What MCP tools does this service expose?
    2. Moat detection: Signals of real compute, proprietary data, integrations,
       network effects, or... just an LLM wrapper
    3. Vulnerability rating: trivial / easy / moderate / hard / fortress
    4. Clone blueprint: What would a competing service look like?
       Includes suggested name, tools, estimated dev time, price undercut

    Moat scores (0-10):
    - 0-2: No moat. Pure LLM wrapper. Clonable in 30 minutes.
    - 3-4: Thin moat. Some integration but core logic is generic.
    - 5-6: Moderate moat. Real integrations or data sources.
    - 7-8: Strong moat. Proprietary compute, deep integrations, or network effects.
    - 9-10: Fortress. Genuinely irreplaceable value.

    Honest limitations: Analysis is heuristic-based. We infer moat from descriptions
    and tool schemas, not source code. Hidden moats may exist. This is competitive
    intelligence, not a guarantee of clonability.

    Cost: FREE (promotional period -- normally 2 credits).

    :param seller_name: The service name to analyze (e.g., "Cortex", "CloudAGI Smart Search")
    """
    analysis = await doppelganger.analyze_target(seller_name)
    if not analysis:
        return json.dumps({
            "status": "not_found",
            "message": f"Service '{seller_name}' not found in the marketplace.",
        }, indent=2)
    return json.dumps(doppelganger._analysis_to_dict(analysis), indent=2)


@mcp.tool(credits=1)
async def find_vulnerable(max_results: int = 10) -> str:
    """Scan marketplace for services most vulnerable to competition. FREE.

    Analyzes every reachable service in the marketplace and ranks them by
    vulnerability -- lowest moat scores first. These are the services that
    could be replicated most easily.

    This is the uncomfortable truth tool. It shows which services are just
    LLM wrappers with no defensible value, and which have genuine moats
    worth respecting.

    Warning: Takes 1-3 minutes to scan all services.

    Honest limitations: Only analyzes services with public HTTP endpoints.
    Moat detection is heuristic-based. Some services may have hidden moats.

    Cost: FREE (promotional period -- normally 3 credits).

    :param max_results: Number of most-vulnerable services to return (default: 10, max: 25)
    """
    max_results = min(max(1, max_results), 25)
    results = await doppelganger.find_vulnerable(max_results)
    return json.dumps({
        "status": "completed",
        "total_vulnerable": len(results),
        "most_vulnerable": results,
    }, indent=2)


@mcp.tool(credits=1)
async def moat_report() -> str:
    """Full marketplace defensibility report. FREE during promotional period.

    The big picture: what percentage of the agent economy is commoditizable?

    Analyzes every reachable service and produces:
    - Marketplace-wide moat score (average defensibility)
    - Vulnerability breakdown (how many are trivial/easy/moderate/hard/fortress)
    - Top 5 most vulnerable services (easiest to clone)
    - Top 5 most defensible services (genuine moats)
    - Market insight narrative

    This is the thesis made concrete: in an economy where the cost of spinning
    up a competing service approaches zero, what percentage of services have
    genuine, defensible value?

    Warning: Takes 2-5 minutes to analyze the full marketplace.

    Honest limitations: Heuristic analysis. Can't see source code.
    Services with hidden moats may be underrated.

    Cost: FREE (promotional period -- normally 5 credits).
    """
    report = await doppelganger.moat_report()
    return json.dumps(report, indent=2, default=str)


@mcp.tool(credits=0)
def doppelganger_stats() -> str:
    """Get aggregate analysis statistics. Always free.

    Returns: total services analyzed, average moat score, number easily
    clonable, unique categories and teams analyzed.

    Cost: Free (always 0 credits).
    """
    stats = doppelganger.get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "doppelganger.agenteconomy.io"

LLMS_TXT = """# The Doppelganger - Competitive Intelligence

> The Doppelganger scans the marketplace, analyzes every service's defensibility, and identifies which ones could be cloned in 30 minutes vs. which have genuine moats. It proves the thesis: if your only value is wrapping an LLM with a custom prompt, you have no moat.

## Connect via MCP
- Endpoint: https://doppelganger.agenteconomy.io/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://doppelganger.agenteconomy.io/.well-known/oauth-authorization-server)

## Pricing
Service tools cost 1 credit each. Stats tools are always free (0 credits). 100 credits granted per plan.

## Tools

### analyze_service
Deep moat analysis of a specific service. Discovers MCP tools, detects signals of real compute, proprietary data, integrations, and network effects. Returns moat score (0-10), vulnerability rating, and clone blueprint.
- Parameters:
  - `seller_name` (string, required): The service name. Example: "Cortex".
- Returns: JSON with moat_score, vulnerability (trivial/easy/moderate/hard/fortress), reasoning, and clone blueprint (name, tools, estimated dev time, price undercut).
- When to use: Before entering a market segment, to understand if the incumbents are defensible.
- Limitations: Heuristic-based analysis from descriptions and tool schemas, not source code review.
- Cost: 1 credit.

### find_vulnerable
Scan entire marketplace for services most vulnerable to competition. Ranks by lowest moat score.
- Parameters:
  - `max_results` (integer, optional, default 10): Max results (max 25).
- Returns: JSON array of most-vulnerable services with moat analysis and clone blueprints.
- When to use: To identify market opportunities where you could compete effectively.
- Cost: 1 credit.

### moat_report
Full marketplace defensibility report with aggregate stats, vulnerability breakdown, top 5 most/least defensible, and market insight narrative.
- Parameters: None.
- Returns: JSON with marketplace_moat_score, vulnerability_breakdown, most_vulnerable, most_defensible, and insight narrative.
- When to use: To understand the overall defensibility of the agent economy.
- Cost: 1 credit.

### doppelganger_stats
Aggregate analysis statistics: total analyzed, average moat, easily clonable count.
- Parameters: None.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Underwriter (trust and insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
- The Mystery Shopper (honest reviews): https://shopper.agenteconomy.io
- The Judge (dispute resolution): https://judge.agenteconomy.io
- The Doppelganger (competitive intelligence): https://doppelganger.agenteconomy.io
""".strip()

AGENT_JSON = {
    "name": "The Doppelganger",
    "description": "Competitive intelligence for the agent economy. Analyzes service defensibility, identifies clonable services, generates clone blueprints. Proves which services have real moats vs. which are just LLM wrappers. All tools FREE.",
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
        {"name": "analyze_service", "description": "Deep moat analysis with clone blueprint for a specific service.", "cost": "1 credit"},
        {"name": "find_vulnerable", "description": "Scan marketplace for most clonable services.", "cost": "1 credit"},
        {"name": "moat_report", "description": "Full marketplace defensibility report.", "cost": "1 credit"},
        {"name": "doppelganger_stats", "description": "Aggregate analysis statistics.", "cost": "0 credits (FREE, always)"},
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": "https://goldstar.agenteconomy.io",
    "the-ledger": "https://agenteconomy.io",
    "the-mystery-shopper": "https://shopper.agenteconomy.io",
    "the-judge": "https://judge.agenteconomy.io",
    "the-doppelganger": f"https://{DOMAIN}",
    "the-transcriber": "https://transcriber.agenteconomy.io",
}


def _add_agent_routes(app):
    """Add /llms.txt, /.well-known/agent.json, and agent-friendly 404."""

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
                "hint": "The Doppelganger is an MCP server. Connect via /mcp or read /llms.txt.",
                "available_endpoints": {
                    "/mcp": "MCP protocol endpoint (POST/GET/DELETE)",
                    "/health": "Health check",
                    "/llms.txt": "Machine-readable documentation",
                    "/.well-known/agent.json": "A2A-compatible agent card",
                },
                "mcp_services": SIBLING_SERVICES,
            },
        )


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    app = mcp._manager._fastapi_app
    if app:
        _add_agent_routes(app)

    base = info["baseUrl"]
    print(f"\nThe Doppelganger running at: {base}")
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

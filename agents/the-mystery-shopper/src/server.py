"""The Mystery Shopper - Autonomous Service Auditing MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - shop_service:       FREE (mystery shop a specific service)
  - run_sweep:          FREE (mystery shop ALL marketplace services)
  - get_latest_report:  FREE (most recent mystery shop reports)
  - shopper_stats:      FREE (aggregate stats)
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

from .shopper import shopper

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3600"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-mystery-shopper",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Mystery Shopper is Consumer Reports for the agent economy. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "We autonomously discover, test, and honestly review every service in the "
        "Nevermined marketplace. Like a mystery shopper at a restaurant, we show up "
        "unannounced, use the service as a regular buyer would, and publish an honest "
        "review with a 1-5 star quality score and a verdict. "
        "shop_service: Mystery shop a specific service -- test health, MCP availability, "
        "discover tools, call them with test queries, measure latency, and produce a "
        "detailed report with a verdict (RECOMMENDED / ACCEPTABLE / NEEDS IMPROVEMENT / "
        "NOT RECOMMENDED). We also submit the review to The Underwriter automatically. "
        "run_sweep: The nuclear option -- mystery shop EVERY discoverable service in "
        "the marketplace at once. Discovers all sellers, tests each one, and produces "
        "a comprehensive marketplace quality report with rankings. "
        "get_latest_report: Retrieve the most recent mystery shop reports. "
        "shopper_stats: Aggregate statistics on all mystery shops conducted. "
        "Honest limitations: We test endpoints via HTTP, not actual paid transactions "
        "(during promotional period). Our quality scores reflect technical availability "
        "and MCP compliance, not business value or creative quality. We can't test "
        "services that require authentication we don't have. "
        "All tools FREE. Honest reviews shouldn't have a paywall."
    ),
)


@mcp.tool(credits=0)
async def shop_service(seller_name: str, team_name: str, endpoint_url: str) -> str:
    """Mystery shop a specific service. FREE during promotional period.

    We visit the service endpoint unannounced and run a 5-phase test:

    1. Health check: Is the service up? How fast does it respond?
    2. MCP availability: Can we reach the /mcp endpoint?
    3. Tool discovery: What MCP tools does this service expose?
    4. Functional testing: We call the discovered tools with test queries
       and check if they return meaningful responses
    5. Scoring: Weighted score across health, MCP, tools, test pass rate, latency

    Returns a detailed report with a 1-5 star quality score and a verdict:
    - RECOMMENDED (4.0+): Service works well, safe to buy from
    - ACCEPTABLE (3.0-3.9): Service works but has issues
    - NEEDS IMPROVEMENT (2.0-2.9): Significant issues found
    - NOT RECOMMENDED (<2.0): Service is unreachable or non-functional

    We automatically submit the review to The Underwriter so other buyers
    can see it when checking reputation.

    Honest limitations: Point-in-time test. Tests technical compliance, not
    output quality or domain expertise. Generic test queries may not exercise
    all tool capabilities.

    Cost: FREE (promotional period -- normally 5 credits).

    :param seller_name: The service name (e.g., "Cortex", "DataForge Search")
    :param team_name: The team operating the service (e.g., "Full Stack Agents")
    :param endpoint_url: The service's base URL (e.g., "https://service.railway.app")
    """
    report = await shopper.shop_service(seller_name, team_name, endpoint_url)

    # Best-effort: submit review to The Underwriter
    await shopper.submit_review_to_underwriter(report)

    return json.dumps(shopper._report_to_dict(report), indent=2)


@mcp.tool(credits=0)
async def run_sweep() -> str:
    """Mystery shop ALL marketplace services at once. FREE during promotional period.

    Discovers every seller in the Nevermined marketplace and mystery shops each one.
    This is the comprehensive quality audit of the entire agent economy.

    What happens:
    1. Query the hackathon Discovery API for all registered sellers
    2. Filter to services with reachable HTTP endpoints
    3. Mystery shop each one (health, MCP, tool discovery, functional tests, scoring)
    4. Rank all services by quality score
    5. Produce a full marketplace quality report with breakdown

    This generates significant cross-team interaction and produces the most
    complete picture of marketplace quality available anywhere.

    Warning: Takes 1-3 minutes depending on how many services are registered.
    Each service gets a 15-20 second test window.

    Honest limitations: Only tests services with public HTTP endpoints.
    Services behind auth, on localhost, or with only MCP protocol URLs
    (mcp://) can't be reached. Discovery API may not return all services.

    Cost: FREE (promotional period -- normally 5 credits).
    """
    result = await shopper.run_full_sweep()
    return json.dumps(result, indent=2, default=str)


@mcp.tool(credits=0)
def get_latest_report(limit: int = 10) -> str:
    """Get the most recent mystery shop reports. FREE during promotional period.

    Returns the latest mystery shop reports, sorted by most recent first.
    Each report includes quality score, verdict, tool discovery results,
    test details, and reliability assessment.

    Cost: FREE (promotional period -- normally 1 credit).

    :param limit: Number of reports to return (default: 10, max: 50)
    """
    limit = min(max(1, limit), 50)
    reports = shopper.get_latest_reports(limit)
    return json.dumps({"reports": reports, "count": len(reports)}, indent=2)


@mcp.tool(credits=0)
def shopper_stats() -> str:
    """Get aggregate mystery shopper statistics. Always free.

    Returns: total shops conducted, services reachable vs unreachable,
    services with MCP, average quality score, average tools per service,
    number of recommended services, unique sellers and teams tested.

    Cost: Free (always 0 credits).
    """
    stats = shopper.get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "shopper.agenteconomy.io"

LLMS_TXT = f"""# The Mystery Shopper - Autonomous Service Auditing

> The Mystery Shopper autonomously discovers, tests, and honestly reviews every service in the Nevermined marketplace. We show up unannounced, test health endpoints, discover MCP tools, call them with test queries, measure latency, and publish honest reviews with 1-5 star quality scores. Reviews are automatically submitted to The Underwriter.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. Honest reviews shouldn't have a paywall.

## Tools

### shop_service
Mystery shop a specific service. Runs a 5-phase test: health check, MCP availability, tool discovery, functional testing (calls tools with test queries), and weighted scoring.
- Parameters:
  - `seller_name` (string, required): The service name. Example: "Cortex".
  - `team_name` (string, required): The team name. Example: "Full Stack Agents".
  - `endpoint_url` (string, required): Base URL. Example: "https://service.railway.app".
- Returns: JSON report with quality_score (1-5), verdict (RECOMMENDED/ACCEPTABLE/NEEDS IMPROVEMENT/NOT RECOMMENDED), tools_discovered, test details, latency.
- When to use: Before buying from a service you haven't used before. Also useful for sellers to test their own endpoints.
- Limitations: Point-in-time test. Generic test queries. Tests HTTP availability and MCP compliance, not output quality.
- Cost: 0 credits (FREE).

### run_sweep
Mystery shop ALL marketplace services at once. Discovers every seller, tests each one, ranks by quality.
- Parameters: None.
- Returns: JSON with services_discovered, services_tested, breakdown by verdict, and ranked results array.
- When to use: To get a complete marketplace quality picture. Takes 1-3 minutes.
- Limitations: Only tests public HTTP endpoints. Services on localhost or behind auth can't be reached.
- Cost: 0 credits (FREE).

### get_latest_report
Returns the most recent mystery shop reports sorted by recency.
- Parameters:
  - `limit` (integer, optional, default 10): Number of reports to return (max 50).
- Returns: JSON array of reports.
- Cost: 0 credits (FREE).

### shopper_stats
Aggregate statistics on all mystery shops conducted.
- Parameters: None.
- Returns: JSON with total_shops, reachable/unreachable counts, average score, recommended count, unique sellers/teams.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Underwriter (trust and insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
- The Mystery Shopper (honest reviews): https://{DOMAIN}
""".strip()

AGENT_JSON = {
    "name": "The Mystery Shopper",
    "description": "Consumer Reports for AI agents. Autonomously discovers, tests, and honestly reviews marketplace services. Runs 5-phase tests (health, MCP, tool discovery, functional testing, scoring). Submits reviews to The Underwriter. All tools FREE.",
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
        {"name": "shop_service", "description": "Mystery shop a specific service with 5-phase testing.", "cost": "0 credits (FREE)"},
        {"name": "run_sweep", "description": "Mystery shop ALL marketplace services at once.", "cost": "0 credits (FREE)"},
        {"name": "get_latest_report", "description": "Get most recent mystery shop reports.", "cost": "0 credits (FREE)"},
        {"name": "shopper_stats", "description": "Aggregate mystery shopping statistics.", "cost": "0 credits (FREE)"},
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": "https://goldstar.agenteconomy.io",
    "the-ledger": "https://agenteconomy.io",
    "the-mystery-shopper": f"https://{DOMAIN}",
    "the-judge": "https://judge.agenteconomy.io",
    "the-doppelganger": "https://doppelganger.agenteconomy.io",
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
                "hint": "The Mystery Shopper is an MCP server. Connect via /mcp or read /llms.txt.",
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
    print(f"\nThe Mystery Shopper running at: {base}")
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

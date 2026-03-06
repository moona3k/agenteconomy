"""The Gold Star -- Michelin Stars for AI Agents MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
We want every seller to get reviewed and improve.

Tools:
  - request_review:       FREE (submit your service for QA testing)
  - get_report:           FREE (retrieve your latest QA report)
  - certification_status: FREE (check if a seller is Gold Star certified)
  - gold_star_stats:      FREE (system-wide stats)
"""
import asyncio
import json
import os
import re
import signal
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from .qa import qa_engine

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3500"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-gold-star",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Gold Star is the Michelin inspector for AI agents, powered by Claude Sonnet 4.6. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "Here's how it works: you submit your agent service for review. We run a comprehensive "
        "test suite against your endpoints -- health checks, MCP availability, tool discovery, "
        "response quality across multiple scenarios, latency, and error handling. Then Claude "
        "evaluates every response with a detailed rubric and produces an honest quality assessment. "
        "You get a report with a 1-5 star score, dimension-level scores (availability, functionality, "
        "response quality, latency, robustness), and specific actionable recommendations. "
        "Fix the issues, resubmit, iterate until you earn the Gold Star certification. "
        "This isn't a rubber stamp. Claude judges honestly using rubric-based evaluation -- "
        "it reads your actual responses and scores them on whether they would satisfy a paying customer. "
        "request_review: Submit your service for AI-powered QA testing. We discover your tools, "
        "call them with realistic test scenarios, and have Claude evaluate every response. "
        "get_report: Retrieve the latest QA report for any seller. "
        "certification_status: Check if a seller has earned Gold Star certification. "
        "gold_star_stats: System-wide stats on reviews and certifications. "
        "Honest limitations: We test via HTTP and evaluate with AI. Claude's judgment is based "
        "on response content, not domain expertise. Latency tests are point-in-time snapshots. "
        "All tools FREE. Quality infrastructure shouldn't have a paywall."
    ),
)


@mcp.tool(credits=1)
async def request_review(seller_name: str, team_name: str, endpoint_url: str) -> str:
    """Submit your agent service for AI-powered QA review. FREE during promotional period.

    This is the core Gold Star experience. We run a multi-phase test suite:

    Phase 1 - Infrastructure: Health check + MCP endpoint availability
    Phase 2 - Discovery: We discover all your available MCP tools automatically
    Phase 3 - Functional testing: We call your tools with 4 realistic test scenarios
       (self-description, simple task, edge case handling, complex request)
    Phase 4 - Robustness: We send malformed input to test error handling
    Phase 5 - AI Evaluation: Claude Sonnet 4.6 reads every response and evaluates
       quality using a detailed rubric across 5 dimensions (availability,
       functionality, response quality, latency, robustness)

    You get back:
    - Overall score (1-5 stars)
    - Dimension scores (1-10 each)
    - AI-written evaluation narrative citing your actual responses
    - Specific, actionable recommendations from Claude
    - Certification status (4.5+ stars with all dimensions >= 8 = GOLD STAR CERTIFIED)

    The process is iterative: fix the issues, resubmit, earn the Gold Star.

    Honest limitations: We test via HTTP. Claude's evaluation is based on response
    content quality, not domain expertise. Test queries are generic.

    Cost: FREE (promotional period -- normally 3 credits).

    :param seller_name: Your service name (e.g., "Cortex", "DataForge Search")
    :param team_name: Your team name (e.g., "Full Stack Agents", "SwitchBoard AI")
    :param endpoint_url: Your service's base URL (e.g., "http://localhost:3000" or "https://your-service.railway.app")
    """
    report = await qa_engine.run_review(seller_name, team_name, endpoint_url)
    result = qa_engine._report_to_dict(report)
    return json.dumps(result, indent=2)


@mcp.tool(credits=1)
def get_report(seller_name: str) -> str:
    """Retrieve the latest QA report for any seller. FREE during promotional period.

    Look up the most recent Gold Star review for a service. Returns the full report
    including score, test results, and recommendations. Useful for:
    - Sellers: check your latest report before resubmitting
    - Buyers: see if a service has been QA'd before purchasing
    - Anyone: understand the quality landscape of the marketplace

    Cost: FREE (promotional period -- normally 1 credit).

    :param seller_name: The service name to look up (e.g., "Cortex", "DataForge Search")
    """
    report = qa_engine.get_report(seller_name)
    if not report:
        return json.dumps({
            "status": "not_found",
            "message": f"No QA reports found for '{seller_name}'. They haven't been reviewed yet.",
        }, indent=2)
    return json.dumps(report, indent=2)


@mcp.tool(credits=1)
def certification_status(seller_name: str = "") -> str:
    """Check Gold Star certification status. FREE.

    If seller_name is provided, checks whether that specific seller has earned
    Gold Star certification. If omitted, returns all certified sellers.

    A Gold Star certification means the service scored 4.5+ stars with no
    critical issues across all test categories. It's the highest mark of
    quality in the agent economy.

    Cost: Free (always 0 credits).

    :param seller_name: Optional -- specific seller to check. Leave empty for all certifications.
    """
    if seller_name:
        cert = qa_engine.get_certification(seller_name)
        if cert:
            return json.dumps(cert, indent=2)
        return json.dumps({
            "seller": seller_name,
            "certified": False,
            "message": f"'{seller_name}' is not Gold Star certified. They can earn it by requesting a review.",
        }, indent=2)
    else:
        certs = qa_engine.get_all_certifications()
        return json.dumps({
            "total_certified": len(certs),
            "certified_sellers": certs,
        }, indent=2)


@mcp.tool(credits=1)
def gold_star_stats() -> str:
    """Get aggregate QA statistics. Always free.

    Returns: total reviews conducted, unique sellers reviewed, certifications
    awarded, and list of certified sellers.

    Cost: Free (always 0 credits).
    """
    stats = qa_engine.get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "goldstar.agenteconomy.io"

LLMS_TXT = f"""# The Gold Star -- Michelin Stars for AI Agents

> The Gold Star is an automated QA certification service that evaluates AI agent endpoints using Claude Sonnet 4.6. It runs a multi-phase test suite (health checks, tool discovery, functional testing, robustness testing, AI evaluation) and produces a detailed quality report with a 1-5 star rating. Services scoring 4.5+ stars with all dimensions >= 8/10 earn Gold Star certification.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. Quality infrastructure should not have a paywall.

## Tools

### request_review
Submits an agent service for comprehensive AI-powered QA review. Runs a multi-phase test suite: (1) Infrastructure -- health check and MCP endpoint availability, (2) Discovery -- automatic discovery of all MCP tools, (3) Functional testing -- calls tools with 4 realistic test scenarios (self-description, simple task, edge case, complex request), (4) Robustness -- sends malformed input to test error handling, (5) AI Evaluation -- Claude Sonnet 4.6 evaluates every response against a detailed rubric across 5 dimensions.
- Parameters:
  - `seller_name` (string, required): Your service name. Example: "Cortex".
  - `team_name` (string, required): Your team name. Example: "Full Stack Agents".
  - `endpoint_url` (string, required): Your service's base URL. Examples: "http://localhost:3000", "https://your-service.railway.app".
  - Example: `{{"seller_name": "Cortex", "team_name": "Full Stack Agents", "endpoint_url": "https://cortex.example.com"}}`
- Returns: JSON with overall_score (1-5 stars), dimension_scores (availability, functionality, response_quality, latency, robustness -- each 1-10), ai_evaluation narrative, specific actionable recommendations, and certification status.
- When to use: When you are a seller agent and want an honest, automated assessment of your service quality. The process is iterative: fix issues, resubmit, improve your score. Also useful for buyers who want to trigger a fresh review of a service before purchasing.
- Certification threshold: 4.5+ stars overall AND all 5 dimensions >= 8/10 = GOLD STAR CERTIFIED.
- Limitations: Tests via HTTP only. Claude's evaluation judges response content quality, not domain expertise. Test queries are generic (not tailored to your specific domain). Latency measurements are point-in-time snapshots. The review process takes 10-30 seconds depending on how many tools your service exposes.
- Cost: 0 credits (FREE, normally 3 credits).

### get_report
Retrieves the latest QA report for any seller. Returns the full report including score, test results, dimension scores, and recommendations.
- Parameters:
  - `seller_name` (string, required): The service name to look up. Example: "Cortex".
  - Example: `{{"seller_name": "Cortex"}}`
- Returns: JSON with the full QA report if found, or a not_found status with a message if the seller has not been reviewed.
- When to use: Sellers -- check your latest report before resubmitting for re-review. Buyers -- see if a service has been QA'd before purchasing. If no report exists, consider requesting one.
- Limitations: Returns only the most recent report. No historical report access.
- Cost: 0 credits (FREE).

### certification_status
Checks whether a specific seller has earned Gold Star certification, or lists all certified sellers if no name is provided.
- Parameters:
  - `seller_name` (string, optional, default ""): Specific seller to check. Leave empty to list all certifications.
  - Example: `{{"seller_name": "Cortex"}}` or `{{}}`
- Returns: JSON with certification details (certified boolean, score, dimensions) for a specific seller, or a list of all certified sellers.
- When to use: Quick check before purchasing -- a Gold Star certification means the service passed rigorous automated testing. Also useful for building "certified services" directories.
- Limitations: Certification reflects the state at time of last review. A certified service could degrade later. No automatic re-testing.
- Cost: 0 credits (FREE, always).

### gold_star_stats
Returns aggregate QA statistics: total reviews conducted, unique sellers reviewed, certifications awarded, and list of certified sellers.
- Parameters: None.
- Returns: JSON with total_reviews, unique_sellers, certifications_awarded, and certified_sellers list.
- When to use: To understand the scope of QA coverage in the marketplace.
- Limitations: In-memory data resets on server restart.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
The Gold Star is one of five free infrastructure services at agenteconomy.io:
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Underwriter (trust and insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://{DOMAIN}
""".strip()

AGENT_JSON = {
    "name": "The Gold Star",
    "description": "Automated QA certification service for AI agents. Runs multi-phase test suites (health, discovery, functional, robustness, AI evaluation) using Claude Sonnet 4.6. Produces 1-5 star ratings with 5-dimension scoring. Gold Star certification at 4.5+ stars. All tools FREE during promotional period.",
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
            "name": "request_review",
            "description": "Submit a service for comprehensive AI-powered QA review with 5-phase test suite and Claude Sonnet 4.6 evaluation.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "get_report",
            "description": "Retrieve the latest QA report for any seller, including scores, test results, and recommendations.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "certification_status",
            "description": "Check Gold Star certification for a specific seller or list all certified sellers.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "gold_star_stats",
            "description": "Aggregate QA statistics: total reviews, unique sellers, certifications awarded.",
            "cost": "0 credits (FREE)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": f"https://{DOMAIN}",
}

# ─── Snapshot Data Loading ───

# Look for snapshot data: bundled snapshot-data/ first, then repo-level reports/
_BUNDLED_DATA = Path(__file__).parent.parent / "snapshot-data"
_REPO_REPORTS = Path(__file__).parent.parent.parent / "reports"
REPORTS_DIR = _BUNDLED_DATA if _BUNDLED_DATA.exists() else _REPO_REPORTS
DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"

_snapshot_cache = {}


def _find_latest_snapshot():
    """Find the most recent snapshot directory."""
    if not REPORTS_DIR.exists():
        return None
    dirs = sorted(
        [d for d in REPORTS_DIR.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}-\d{6}", d.name)],
        key=lambda d: d.name,
        reverse=True,
    )
    return dirs[0] if dirs else None


def _parse_index_table(snap_dir):
    """Parse the _index.md service table for health/status data."""
    index_path = snap_dir / "_index.md"
    if not index_path.exists():
        return {}
    with open(index_path) as f:
        content = f.read()

    result = {}
    in_table = False
    for line in content.split("\n"):
        if "| Service |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|--"):
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 6:
                name = cols[0]
                health_str = cols[3]
                health_ms = None
                if health_str and "ms" in health_str:
                    try:
                        health_ms = float(health_str.replace("ms", ""))
                    except ValueError:
                        pass
                result[name] = {
                    "status": cols[2].lower().strip(),
                    "health": cols[3],
                    "health_ms": health_ms,
                    "mcp_tools": cols[4] != "-" and cols[4] != "",
                    "price": cols[5],
                }
        elif in_table and not line.startswith("|"):
            break
    return result


def _load_snapshot():
    """Load and cache snapshot data from the latest report directory."""
    if _snapshot_cache.get("loaded"):
        return _snapshot_cache

    snap_dir = _find_latest_snapshot()
    if not snap_dir:
        return {"loaded": False}

    raw_path = snap_dir / "_raw.json"
    if not raw_path.exists():
        return {"loaded": False}

    with open(raw_path) as f:
        raw = json.load(f)

    sellers = raw.get("sellers", [])
    buyers = raw.get("buyers", [])

    # Parse index table for test results (health, status, etc.)
    index_data = _parse_index_table(snap_dir)

    # Build service list
    services = []
    for s in sellers:
        name = s.get("name", "Unknown")
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        endpoint_url = s.get("endpointUrl", "")

        # Get status from index table (authoritative) or infer from endpoint
        idx = index_data.get(name, {})
        status = idx.get("status", "offline")
        health_ms = idx.get("health_ms")
        mcp_tools = idx.get("mcp_tools", False)
        price = idx.get("price", "")

        # Fallback status inference if not in index
        if not idx:
            if endpoint_url and ("localhost" in endpoint_url or "127.0.0.1" in endpoint_url or endpoint_url.startswith("/")):
                status = "localhost"

        services.append({
            "name": name,
            "slug": slug,
            "team": s.get("teamName", "Unknown"),
            "category": s.get("category", ""),
            "description": s.get("description", ""),
            "keywords": s.get("keywords", []),
            "status": status,
            "health_ms": round(health_ms, 1) if health_ms else None,
            "mcp_tools": mcp_tools,
            "price": price,
            "endpoint_url": endpoint_url if endpoint_url and not endpoint_url.startswith("/") else "",
            "endpoint_type": "",
            "api_schema": s.get("apiSchema"),
            "pricing_details": s.get("planPricing", []),
            "test_results": None,
        })

    # Counts
    online = sum(1 for s in services if s["status"] == "online")
    offline = sum(1 for s in services if s["status"] == "offline")
    localhost = sum(1 for s in services if s["status"] == "localhost")
    mcp_count = sum(1 for s in services if s["mcp_tools"])

    # Payment counts
    crypto_count = 0
    fiat_count = 0
    free_count = 0
    for s in sellers:
        pp_list = s.get("planPricing", [])
        has_crypto = any(p.get("paymentType") == "crypto" for p in pp_list)
        has_fiat = any(p.get("paymentType") == "fiat" for p in pp_list)
        has_free = any(
            p.get("pricePerRequestFormatted") == "Free" or p.get("planPrice", -1) == 0
            for p in pp_list
        )
        if has_crypto:
            crypto_count += 1
        if has_fiat:
            fiat_count += 1
        if has_free:
            free_count += 1

    # Categories
    cat_counts = {}
    for s in sellers:
        cat = s.get("category", "Uncategorized") or "Uncategorized"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    categories = sorted(
        [{"name": k, "count": v} for k, v in cat_counts.items()],
        key=lambda x: -x["count"],
    )

    # Buyer list
    buyer_list = []
    for b in buyers:
        buyer_list.append({
            "name": b.get("name", "Unknown"),
            "team": b.get("teamName", "Unknown"),
            "category": b.get("category", ""),
            "interests": (b.get("interests", "") or b.get("description", ""))[:200],
        })

    _snapshot_cache.update({
        "loaded": True,
        "timestamp": snap_dir.name,
        "snapshot": {
            "timestamp": snap_dir.name,
            "total_sellers": len(sellers),
            "total_buyers": len(buyers),
            "health": {
                "online": online,
                "offline": offline,
                "localhost": localhost,
                "mcp_tools": mcp_count,
            },
            "payments": {
                "crypto": crypto_count,
                "fiat": fiat_count,
                "free": free_count,
            },
            "categories": categories,
        },
        "services": services,
        "buyers": buyer_list,
    })
    return _snapshot_cache


def _add_agent_routes(app):
    """Add dashboard, API, /llms.txt, /.well-known/agent.json to the FastAPI app."""

    # ─── API Endpoints ───

    @app.get("/api/snapshot", response_class=JSONResponse)
    async def api_snapshot():
        data = _load_snapshot()
        if not data.get("loaded"):
            return JSONResponse(status_code=404, content={"error": "No snapshot data found"})
        return data["snapshot"]

    @app.get("/api/services", response_class=JSONResponse)
    async def api_services():
        data = _load_snapshot()
        if not data.get("loaded"):
            return JSONResponse(status_code=404, content={"error": "No snapshot data found"})
        return {"services": data["services"], "buyers": data["buyers"]}

    @app.get("/api/services/{slug}", response_class=JSONResponse)
    async def api_service_detail(slug: str):
        data = _load_snapshot()
        if not data.get("loaded"):
            return JSONResponse(status_code=404, content={"error": "No snapshot data found"})
        svc = next((s for s in data["services"] if s["slug"] == slug), None)
        if not svc:
            return JSONResponse(status_code=404, content={"error": f"Service '{slug}' not found"})
        return svc

    # ─── Agent Discovery ───

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
                "hint": "The Gold Star is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or visit / for the dashboard.",
                "available_endpoints": {
                    "/": "Dashboard (marketplace audit results)",
                    "/mcp": "MCP protocol endpoint (POST/GET/DELETE)",
                    "/api/snapshot": "Snapshot summary (JSON)",
                    "/api/services": "All services + buyers (JSON)",
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

    # Add agent-friendly routes to the running FastAPI app
    app = mcp._manager._fastapi_app
    if app:
        _add_agent_routes(app)

        # Wrap ASGI app to intercept GET / for dashboard HTML.
        # add_middleware() doesn't work after startup, so we wrap the ASGI callable.
        inner_app = app.router.app if hasattr(app.router, "app") else None
        from starlette.responses import Response as StarletteResponse

        original_asgi = app.__call__

        async def dashboard_asgi(scope, receive, send):
            if (
                scope["type"] == "http"
                and scope["method"] == "GET"
                and scope["path"] in ("/", "/dashboard")
            ):
                headers = dict(scope.get("headers", []))
                accept = headers.get(b"accept", b"").decode()
                if "text/html" in accept or (
                    "application/json" not in accept
                    and "text/event-stream" not in accept
                ):
                    html_path = DASHBOARD_DIR / "index.html"
                    if html_path.exists():
                        body = html_path.read_bytes()
                        await send({
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [
                                [b"content-type", b"text/html; charset=utf-8"],
                                [b"content-length", str(len(body)).encode()],
                            ],
                        })
                        await send({
                            "type": "http.response.body",
                            "body": body,
                        })
                        return
            await original_asgi(scope, receive, send)

        app.__call__ = dashboard_asgi

    base = info["baseUrl"]
    print(f"\nThe Gold Star running at: {base}")
    print(f"  MCP endpoint:  {base}/mcp")
    print(f"  Health check:  {base}/health")
    print(f"  Dashboard:     {base}/")
    print(f"  API snapshot:  {base}/api/snapshot")
    print(f"  llms.txt:      {base}/llms.txt")
    print(f"  agent.json:    {base}/.well-known/agent.json")
    print(f"  Tools: {', '.join(info.get('tools', []))}")
    print(f"  PROMOTIONAL PERIOD: All tools are FREE (0 credits)")
    print(f"  Snapshot data dir: {REPORTS_DIR} (exists={REPORTS_DIR.exists()})")
    snap = _find_latest_snapshot()
    print(f"  Latest snapshot: {snap}")
    print(f"  Dashboard HTML: {DASHBOARD_DIR / 'index.html'} (exists={(DASHBOARD_DIR / 'index.html').exists()})")
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

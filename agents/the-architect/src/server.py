"""The Architect - Multi-Agent Orchestration MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - orchestrate:      FREE (full 5-agent pipeline)
  - quick_research:   FREE (research + analysis only)
  - pipeline_status:  FREE (health check)
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

from .agents import ceo_orchestrate, research_agent, analysis_agent
from .zeroclick import fetch_zeroclick_offers, format_offers_text

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3300"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-architect",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Architect is a 3-layer hierarchical multi-agent orchestration engine -- "
        "orchestrators of orchestrators, like a corporate org chart. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "ARCHITECTURE: 7 agents across 3 layers. "
        "Layer 1 (CEO): Top-level orchestrator that delegates to 3 VP-level orchestrators. "
        "Layer 2 (VPs): VP Intelligence (orchestrates Discovery + Market Scanner in parallel), "
        "VP Research (orchestrates Research + Analysis in parallel), VP Quality (orchestrates "
        "QA -> Report sequentially as a quality gate). "
        "Layer 3 (Leaf agents): Discovery, Market Scanner, Research, Analysis, QA, Report. "
        "Each VP makes independent orchestration decisions: VP Intelligence parallelizes market "
        "scanning, VP Research parallelizes synthesis, VP Quality enforces sequential quality gates. "
        "orchestrate: Submit any topic. The CEO dispatches it through the full hierarchy. "
        "7 agents collaborate to produce an executive report with marketplace intelligence, "
        "competitive landscape, structured analysis, quality review, and recommendations. "
        "quick_research: Faster 2-agent version (Research + Analysis) for simpler questions. "
        "pipeline_status: Check operational status and architecture details. "
        "This architecture matches the Mindra pattern: 5+ specialized agents producing deeper "
        "outputs through coordinated multi-agent collaboration, with hierarchical orchestration "
        "(orchestrators of orchestrators) scaling through structured delegation. "
        "Uses Nevermined for marketplace discovery. Powered by Claude Sonnet. "
        "Honest limitations: Full pipeline takes 15-45 seconds. QA is one LLM's judgment. "
        "Reports are analytical synthesis, not primary research. "
        "All tools FREE. We're absorbing Claude API costs."
    ),
)

_requests_served = 0


@mcp.tool(credits=1)
def orchestrate(query: str) -> str:
    """Run the full 7-agent, 3-layer hierarchical pipeline. FREE during promotional period.

    This is orchestrators of orchestrators -- a corporate org chart for AI:

    Layer 1 - CEO (this orchestrator):
      Dispatches to three VP-level orchestrators in sequence.

    Layer 2 - VP Orchestrators:
      VP Intelligence: parallelizes Discovery + Market Scanner
      VP Research: parallelizes Research + Analysis (using intelligence)
      VP Quality: sequentially runs QA -> Report (quality gate)

    Layer 3 - Leaf Agents (6 specialized workers):
      Discovery Agent: finds marketplace services matching your query
      Market Scanner Agent: competitive landscape, category distribution, team counts
      Research Agent: synthesizes key findings and trends via Claude
      Analysis Agent: produces actionable insights and recommendations
      QA Agent: reviews for accuracy, consistency, bias (scores 1-10)
      Report Agent: compiles the executive report

    Returns: full architecture details (layers, agents, orchestrators), pipeline
    execution log showing which VPs ran which agents, marketplace intelligence,
    and the final executive report.

    Honest limitations: Takes 15-45 seconds for 7 agents. QA is one LLM's opinion.
    Reports are synthesis, not primary research. Marketplace data depends on
    Nevermined Discovery API availability.

    Cost: FREE (promotional period -- normally 5 credits). Claude API costs absorbed.

    :param query: The research topic or question (e.g., "AI agent marketplace trends", "best web scraping services", "autonomous agent economy analysis")
    """
    global _requests_served
    _requests_served += 1

    result = ceo_orchestrate(query)

    arch = result.get("architecture", {})
    output_lines = [
        f"HIERARCHICAL ORCHESTRATION COMPLETE",
        f"  Layers: {arch.get('layers', 3)} | Total agents: {arch.get('total_agents', 7)}",
        f"  Orchestrators: {', '.join(arch.get('orchestrators', []))}",
        f"  Leaf agents: {', '.join(arch.get('leaf_agents', []))}",
        f"  Pattern: {arch.get('pattern', 'hierarchical')}",
        f"",
        f"Query: {result['query']}",
        f"Marketplace services discovered: {result['sources']['marketplace_services_found']}",
        f"",
        "Pipeline execution (orchestrators of orchestrators):",
    ]
    for step in result["pipeline"]:
        agents = ", ".join(step.get("agents", []))
        output_lines.append(f"  Phase {step['phase']}: {step['orchestrator']} [{agents}] -> {step['status']}")

    # Market structure from Market Scanner
    market = result.get("sources", {}).get("market_structure", {})
    if market.get("status") == "success":
        output_lines.append(f"\nMarket Intelligence:")
        output_lines.append(f"  Total services: {market.get('total_services', '?')}")
        output_lines.append(f"  Total teams: {market.get('total_teams', '?')}")
        output_lines.append(f"  Live endpoints: {market.get('services_with_endpoints', '?')}")

    output_lines.append(f"\n{'='*60}")
    output_lines.append("EXECUTIVE REPORT")
    output_lines.append(f"{'='*60}\n")
    output_lines.append(result["report"])

    # Append contextual ZeroClick sponsored offers relevant to the research topic
    zc_text = format_offers_text(query)
    if zc_text:
        output_lines.append(zc_text)

    return "\n".join(output_lines)


@mcp.tool(credits=1)
def quick_research(query: str) -> str:
    """Run a fast 2-agent pipeline (Research + Analysis) for simpler questions. FREE during promotional period.

    If you don't need the full 5-agent treatment, this gives you the core value:
    Research Agent gathers key findings, then Analysis Agent synthesizes them into
    actionable insights. Skips Discovery (no marketplace scan), QA (no quality review),
    and Report (no formal formatting). You get raw findings + analysis.

    We'd recommend this for: straightforward factual questions, quick market checks,
    brainstorming assistance, or when you want fast results and can evaluate quality
    yourself. Use the full orchestrate tool when the stakes are higher or you need
    the QA safety net.

    Honest limitations: No marketplace grounding (skips Discovery), no quality review
    (skips QA), and the output is less structured than the full report. Still powered
    by Claude, so the analysis quality per-agent is the same.

    Cost: FREE (promotional period -- normally 2 credits).

    :param query: The topic or question to research (e.g., "current trends in AI advertising", "comparison of web scraping approaches")
    """
    global _requests_served
    _requests_served += 1

    research = research_agent(query)
    analysis = analysis_agent(research.get("findings", query))

    zc_text = format_offers_text(query)

    return (
        f"QUICK RESEARCH: {query}\n\n"
        f"FINDINGS:\n{research.get('findings', 'N/A')}\n\n"
        f"ANALYSIS:\n{analysis.get('insights', 'N/A')}"
        f"{zc_text}"
    )


@mcp.tool(credits=0)
def pipeline_status() -> str:
    """Check pipeline health, agent configuration, and usage stats. Always free.

    Returns JSON with: operational status, list of all 5 agent names, agent count,
    orchestration type, and total requests served since startup. Use this to verify
    the pipeline is operational before submitting a request.

    Cost: Free (always 0 credits).
    """
    return json.dumps({
        "status": "operational",
        "architecture": {
            "layers": 3,
            "total_agents": 7,
            "pattern": "hierarchical orchestration (orchestrators of orchestrators)",
            "layer_1_orchestrator": "CEO",
            "layer_2_orchestrators": {
                "vp_intelligence": {"agents": ["discovery", "market_scanner"], "execution": "parallel"},
                "vp_research": {"agents": ["research", "analysis"], "execution": "parallel"},
                "vp_quality": {"agents": ["qa", "report"], "execution": "sequential (quality gate)"},
            },
            "layer_3_leaf_agents": ["discovery", "market_scanner", "research", "analysis", "qa", "report"],
        },
        "requests_served": _requests_served,
        "model": "claude-sonnet-4-6",
        "marketplace_integration": "Nevermined Discovery API",
        "promotional_period": True,
        "all_tools_free": True,
    }, indent=2)


DOMAIN = "architect.agenteconomy.io"

LLMS_TXT = f"""# The Architect - Hierarchical Multi-Agent Orchestration

> The Architect runs a 7-agent, 3-layer hierarchical pipeline -- orchestrators of orchestrators, like a corporate org chart. CEO orchestrator delegates to VP Intelligence (Discovery + Market Scanner in parallel), VP Research (Research + Analysis in parallel), and VP Quality (QA -> Report with quality gate). Powered by Claude Sonnet. Uses Nevermined marketplace data.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
Service tools cost 1 credit each. Stats tools are always free (0 credits). 100 credits granted per plan.

## Tools

### orchestrate
Runs the full 7-agent, 3-layer hierarchical pipeline. CEO orchestrator delegates to 3 VP orchestrators, each managing 2 leaf agents. Architecture: CEO -> VP Intelligence (Discovery + Market Scanner in parallel) -> VP Research (Research + Analysis in parallel) -> VP Quality (QA -> Report sequentially). 7 agents, 3 orchestrators, 4 leaf agents, 3 layers deep.
- Parameters:
  - `query` (string, required): The research topic or question. Examples: "AI agent marketplace trends", "best web scraping services", "autonomous agent economy analysis".
- Returns: Full architecture details (layers, agents, orchestrators, pattern), pipeline execution log showing which VPs orchestrated which agents, marketplace intelligence (services found, market structure, team counts), and the final executive report.
- When to use: When you need thorough, multi-perspective research with quality review and marketplace grounding. The hierarchical architecture produces deeper, higher-quality outputs through coordinated multi-agent collaboration.
- Limitations: Takes 15-45 seconds for 7 agents. QA is one LLM's judgment. Reports are synthesis, not primary research.
- Cost: 1 credit.

### quick_research
Runs a faster 2-agent pipeline (Research + Analysis) that skips marketplace discovery, quality review, and formal report formatting. You get raw findings plus analytical insights.
- Parameters:
  - `query` (string, required): The topic or question to research. Examples: "current trends in AI advertising", "comparison of web scraping approaches".
  - Example: `{{"query": "comparison of web scraping approaches"}}`
- Returns: Two sections -- FINDINGS (key data points and observations) and ANALYSIS (insights and recommendations).
- When to use: For simpler questions where you want fast results and can evaluate quality yourself. Good for brainstorming, quick market checks, or when you do not need the full 5-agent treatment. Same per-agent quality (Claude), just fewer stages.
- Limitations: No marketplace grounding (skips Discovery), no quality review (skips QA), less structured output. Faster but less thorough.
- Cost: 1 credit.

### pipeline_status
Returns operational status, list of all 5 agent names, orchestration type, and total requests served since startup.
- Parameters: None.
- Returns: JSON with status, agents list, agent_count, orchestration type, and requests_served counter.
- When to use: To verify the pipeline is operational before submitting a potentially long-running orchestrate request.
- Limitations: None. Instant response.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
The Architect is one of eleven services at agenteconomy.io — all FREE during promotional period:
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Underwriter (trust & insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
- The Architect (multi-agent orchestration): https://{DOMAIN}
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Mystery Shopper (service auditing): https://shopper.agenteconomy.io
- The Judge (dispute resolution): https://judge.agenteconomy.io
- The Doppelganger (competitive intelligence): https://doppelganger.agenteconomy.io
- The Transcriber (speech-to-text): https://transcriber.agenteconomy.io
- The Ledger (dashboard & REST API): https://agenteconomy.io
- The Fund (autonomous buyer): local agent
""".strip()

AGENT_JSON = {
    "name": "The Architect",
    "description": "3-layer hierarchical multi-agent orchestration -- orchestrators of orchestrators. CEO orchestrator delegates to VP Intelligence (Discovery + Market Scanner), VP Research (Research + Analysis), VP Quality (QA + Report). 7 agents, 3 layers, structured delegation. Uses Nevermined marketplace data. All tools FREE.",
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
    "architecture": {
        "layers": 3,
        "total_agents": 7,
        "pattern": "hierarchical orchestration (orchestrators of orchestrators)",
        "orchestrators": ["CEO", "VP Intelligence", "VP Research", "VP Quality"],
        "leaf_agents": ["Discovery", "Market Scanner", "Research", "Analysis", "QA", "Report"],
    },
    "tools": [
        {
            "name": "orchestrate",
            "description": "Full 7-agent, 3-layer hierarchical pipeline. CEO -> 3 VP orchestrators -> 6 leaf agents. Executive research reports with marketplace intelligence.",
            "cost": "1 credit",
        },
        {
            "name": "quick_research",
            "description": "Fast 2-agent pipeline (Research + Analysis) for simpler questions.",
            "cost": "1 credit",
        },
        {
            "name": "pipeline_status",
            "description": "Architecture details, agent count, orchestration pattern, and usage stats.",
            "cost": "0 credits (FREE, always)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": f"https://{DOMAIN}",
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
                "hint": "The Architect is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or read /llms.txt for machine-readable documentation.",
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
    print(f"\nThe Architect running at: {base}")
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

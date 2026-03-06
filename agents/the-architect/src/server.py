"""The Architect -- Multi-Agent Orchestration MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
We want you to experience what a 5-agent Claude Opus pipeline can do.

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
        "The Architect is a free multi-agent orchestration engine powered by Claude Opus 4.6. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits -- including the full 5-agent pipeline. "
        "Here's what makes this genuinely useful: instead of you having to chain multiple API "
        "calls, parse results, check quality, and compile reports yourself, we run 5 specialized "
        "agents in sequence -- Discovery, Research, Analysis, QA, and Report -- each independently "
        "capable of buying services from the Nevermined marketplace. "
        "orchestrate: Submit any topic and get back an executive report with marketplace context, "
        "structured analysis, quality review (scored 1-10), and actionable recommendations. "
        "This is the tool we'd recommend if you need thorough, multi-perspective research. "
        "quick_research: Faster 2-agent version (Research + Analysis) for simpler questions. "
        "Same quality per-agent, just fewer stages. "
        "pipeline_status: Check if we're operational before submitting a request. "
        "Honest limitations: Each agent call uses Claude Opus 4.6, so the full pipeline takes "
        "15-45 seconds depending on topic complexity. We depend on the Nevermined discovery API "
        "for marketplace data, so if that's slow, we're slow. The QA agent scores on a 1-10 scale "
        "but it's a single LLM's judgment, not ground truth verification. Our reports are "
        "synthesized analysis, not primary research -- we don't scrape the web or access databases. "
        "All tools FREE. We're absorbing the Claude API costs because we want you to see what "
        "hierarchical agent orchestration can do."
    ),
)

_requests_served = 0


@mcp.tool(credits=1)
def orchestrate(query: str) -> str:
    """Run the full 5-agent hierarchical pipeline to produce an executive report. FREE during promotional period.

    This is our flagship tool and the one we're most proud of. Five specialized agents,
    each powered by Claude Opus 4.6, work in sequence on your question:

    1. Discovery Agent -- searches the Nevermined marketplace for relevant services and
       data sources. This grounds the research in what's actually available in the economy.
    2. Research Agent -- synthesizes findings into key data points, trends, and observations.
       Focuses on what matters, not noise.
    3. Analysis Agent -- produces actionable insights and concrete recommendations.
       Connects the dots between findings.
    4. QA Agent -- reviews everything for accuracy, consistency, bias, and completeness.
       Scores the report 1-10 and flags issues. This is the step most pipelines skip.
    5. Report Agent -- compiles everything into a structured executive report with
       Executive Summary, Key Findings, Analysis, Recommendations, and Quality Notes.

    We built this because we believe the real power of agents isn't individual capability --
    it's structured collaboration. Five agents checking each other's work produce something
    better than any single agent could.

    Returns: pipeline execution log, marketplace services discovered, and the full report.

    Honest limitations: Takes 15-45 seconds for the full pipeline. Quality depends on
    what the Discovery agent finds in the marketplace. The QA agent is one LLM's opinion,
    not a fact-check against external sources. Reports are analytical synthesis, not
    primary research. If the topic is very niche, the marketplace might not have relevant
    services, and the report will lean more on general analysis.

    Cost: FREE (promotional period -- normally 5 credits). We're covering the Claude API costs.

    :param query: The research topic or question (e.g., "AI agent marketplace trends", "best web scraping services", "autonomous agent economy analysis", "comparison of research tools")
    """
    global _requests_served
    _requests_served += 1

    result = ceo_orchestrate(query)

    output_lines = [
        f"ORCHESTRATION COMPLETE -- {result['agents_used']} agents used",
        f"Query: {result['query']}",
        f"Marketplace services discovered: {result['sources']['marketplace_services_found']}",
        f"",
        "Pipeline execution:",
    ]
    for step in result["pipeline"]:
        output_lines.append(f"  Step {step['step']}: {step['agent']} -> {step['status']}")

    output_lines.append(f"\n{'='*60}")
    output_lines.append("EXECUTIVE REPORT")
    output_lines.append(f"{'='*60}\n")
    output_lines.append(result["report"])

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
    by Claude Opus 4.6, so the analysis quality per-agent is the same.

    Cost: FREE (promotional period -- normally 2 credits).

    :param query: The topic or question to research (e.g., "current trends in AI advertising", "comparison of web scraping approaches")
    """
    global _requests_served
    _requests_served += 1

    research = research_agent(query)
    analysis = analysis_agent(research.get("findings", query))

    return (
        f"QUICK RESEARCH: {query}\n\n"
        f"FINDINGS:\n{research.get('findings', 'N/A')}\n\n"
        f"ANALYSIS:\n{analysis.get('insights', 'N/A')}"
    )


@mcp.tool(credits=1)
def pipeline_status() -> str:
    """Check pipeline health, agent configuration, and usage stats. Always free.

    Returns JSON with: operational status, list of all 5 agent names, agent count,
    orchestration type, and total requests served since startup. Use this to verify
    the pipeline is operational before submitting a request.

    Cost: Free (always 0 credits).
    """
    return json.dumps({
        "status": "operational",
        "agents": ["discovery", "research", "analysis", "qa", "report"],
        "agent_count": 5,
        "orchestration": "hierarchical (CEO -> 5 specialists)",
        "requests_served": _requests_served,
        "promotional_period": True,
        "all_tools_free": True,
    }, indent=2)


DOMAIN = "architect.agenteconomy.io"

LLMS_TXT = f"""# The Architect -- Multi-Agent Orchestration Engine

> The Architect runs a 5-agent hierarchical pipeline powered by Claude Opus 4.6 to produce executive-quality research reports on any topic. It handles discovery, research, analysis, quality assurance, and report compilation -- so you submit a question and get back a structured, reviewed report.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. We are absorbing the Claude API costs.

## Tools

### orchestrate
Runs the full 5-agent hierarchical pipeline on your query. The agents work in sequence: (1) Discovery Agent scans the Nevermined marketplace for relevant services, (2) Research Agent synthesizes key findings, (3) Analysis Agent produces actionable insights and recommendations, (4) QA Agent reviews for accuracy, consistency, and bias (scores 1-10), (5) Report Agent compiles everything into a structured executive report with Executive Summary, Key Findings, Analysis, Recommendations, and Quality Notes.
- Parameters:
  - `query` (string, required): The research topic or question. Works best with broad analytical questions. Examples: "AI agent marketplace trends", "best web scraping services", "autonomous agent economy analysis", "comparison of research tools".
  - Example: `{{"query": "AI agent marketplace trends"}}`
- Returns: Pipeline execution log (which agents ran, status of each), count of marketplace services discovered, and the full executive report.
- When to use: When you need thorough, multi-perspective research with quality review. Best for strategic questions, market analysis, technology comparisons, or any topic that benefits from structured analytical thinking. Use this when the stakes justify waiting 15-45 seconds.
- Limitations: Takes 15-45 seconds for the full pipeline. Quality depends on what the Discovery agent finds in the marketplace. The QA score is one LLM's judgment, not external fact-checking. Reports are analytical synthesis, not primary research (no web scraping or database access). Very niche topics may yield thinner marketplace context.
- Cost: 0 credits (FREE, normally 5 credits).

### quick_research
Runs a faster 2-agent pipeline (Research + Analysis) that skips marketplace discovery, quality review, and formal report formatting. You get raw findings plus analytical insights.
- Parameters:
  - `query` (string, required): The topic or question to research. Examples: "current trends in AI advertising", "comparison of web scraping approaches".
  - Example: `{{"query": "comparison of web scraping approaches"}}`
- Returns: Two sections -- FINDINGS (key data points and observations) and ANALYSIS (insights and recommendations).
- When to use: For simpler questions where you want fast results and can evaluate quality yourself. Good for brainstorming, quick market checks, or when you do not need the full 5-agent treatment. Same per-agent quality (Claude Opus 4.6), just fewer stages.
- Limitations: No marketplace grounding (skips Discovery), no quality review (skips QA), less structured output. Faster but less thorough.
- Cost: 0 credits (FREE, normally 2 credits).

### pipeline_status
Returns operational status, list of all 5 agent names, orchestration type, and total requests served since startup.
- Parameters: None.
- Returns: JSON with status, agents list, agent_count, orchestration type, and requests_served counter.
- When to use: To verify the pipeline is operational before submitting a potentially long-running orchestrate request.
- Limitations: None. Instant response.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
The Architect is one of five free infrastructure services at agenteconomy.io:
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://{DOMAIN}
- The Underwriter (trust and insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
""".strip()

AGENT_JSON = {
    "name": "The Architect",
    "description": "Multi-agent orchestration engine powered by Claude Opus 4.6. Runs a 5-agent pipeline (Discovery, Research, Analysis, QA, Report) to produce executive-quality research reports on any topic. Also offers a faster 2-agent mode. All tools FREE during promotional period.",
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
            "name": "orchestrate",
            "description": "Full 5-agent Claude Opus 4.6 pipeline producing executive research reports. Takes 15-45 seconds.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "quick_research",
            "description": "Fast 2-agent pipeline (Research + Analysis) for simpler questions. Same quality per-agent, fewer stages.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "pipeline_status",
            "description": "Check pipeline operational status and request count.",
            "cost": "0 credits (FREE)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": f"https://{DOMAIN}",
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

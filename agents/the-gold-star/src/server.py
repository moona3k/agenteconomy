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
import signal

from dotenv import load_dotenv
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


@mcp.tool(credits=0)
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


@mcp.tool(credits=0)
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


@mcp.tool(credits=0)
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


@mcp.tool(credits=0)
def gold_star_stats() -> str:
    """Get aggregate QA statistics. Always free.

    Returns: total reviews conducted, unique sellers reviewed, certifications
    awarded, and list of certified sellers.

    Cost: Free (always 0 credits).
    """
    stats = qa_engine.get_stats()
    return json.dumps(stats, indent=2)


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    print(f"\nThe Gold Star running at: {info['baseUrl']}")
    print(f"  MCP endpoint:  {info['baseUrl']}/mcp")
    print(f"  Health check:  {info['baseUrl']}/health")
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

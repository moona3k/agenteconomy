"""The Mystery Shopper -- Consumer Reports for AI Agents MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
Transparency and honest reviews benefit the entire economy.

Tools:
  - shop_service:       FREE (mystery shop a specific service)
  - run_sweep:          FREE (mystery shop ALL marketplace services)
  - get_latest_report:  FREE (get most recent mystery shop reports)
  - shopper_stats:      FREE (aggregate stats)
"""
import asyncio
import json
import os
import signal

from dotenv import load_dotenv
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
        "review with a 1-5 star quality score. "
        "shop_service: Mystery shop a specific service by providing its endpoint URL. "
        "We test health, MCP availability, response quality, and latency. Returns a "
        "detailed report with scores and a recommendation verdict. "
        "run_sweep: The nuclear option -- mystery shop EVERY discoverable service in "
        "the marketplace. Discovers all sellers via the Nevermined API, tests each one, "
        "and returns a comprehensive report. This generates massive cross-team transaction "
        "volume and produces the most complete quality picture of the marketplace. "
        "get_latest_report: Retrieve the most recent mystery shop reports. See what we've "
        "tested and how services scored. "
        "shopper_stats: Aggregate statistics on all mystery shops conducted. "
        "Honest limitations: We test endpoints via HTTP, not actual paid transactions "
        "(during promotional period). Our quality scores reflect technical availability "
        "and response consistency, not business value or creative quality. We can't test "
        "services that require authentication we don't have. Services on localhost are "
        "only testable if we're on the same network. "
        "All tools FREE. Honest reviews shouldn't have a paywall."
    ),
)


@mcp.tool(credits=0)
async def shop_service(seller_name: str, team_name: str, endpoint_url: str) -> str:
    """Mystery shop a specific service. FREE during promotional period.

    We visit the service endpoint unannounced and test it like a regular buyer:

    1. Health check: Is the service up?
    2. MCP availability: Can we reach the MCP endpoint?
    3. Response quality: Does it respond meaningfully to test queries?
    4. Latency: How fast does it respond?

    Returns a detailed report with a 1-5 star quality score and a verdict:
    - RECOMMENDED (4.0+): Service works well, safe to buy from
    - ACCEPTABLE (3.0-3.9): Service works but has issues
    - NEEDS IMPROVEMENT (2.0-2.9): Significant issues found
    - NOT RECOMMENDED (<2.0): Service is unreachable or non-functional

    Honest limitations: This is a point-in-time test. A service could perform
    differently at other times. We test technical availability, not output quality.

    Cost: FREE (promotional period -- normally 5 credits).

    :param seller_name: The service name (e.g., "Cortex", "DataForge Search")
    :param team_name: The team operating the service (e.g., "Full Stack Agents")
    :param endpoint_url: The service's base URL (e.g., "https://service.railway.app")
    """
    report = await shopper.shop_service(seller_name, team_name, endpoint_url)
    return json.dumps(shopper._report_to_dict(report), indent=2)


@mcp.tool(credits=0)
async def run_sweep() -> str:
    """Mystery shop ALL marketplace services at once. FREE during promotional period.

    This discovers every seller in the Nevermined marketplace and tests each one.
    It's the comprehensive quality audit of the entire agent economy.

    What happens:
    1. Query the Nevermined Discovery API for all registered sellers
    2. Filter to services with reachable HTTP endpoints
    3. Mystery shop each one (health, MCP, queries, latency)
    4. Produce a full marketplace quality report

    This generates significant cross-team interaction and produces the most
    complete picture of marketplace quality available anywhere.

    Warning: This can take a while depending on how many services are registered
    and how responsive they are. Each service gets a 10-15 second test window.

    Honest limitations: Only tests services with public HTTP endpoints.
    Services behind auth, on localhost, or using only MCP protocol URLs
    (mcp://) can't be reached. Discovery API may not return all services.

    Cost: FREE (promotional period -- normally 5 credits).
    """
    result = await shopper.run_full_sweep()
    return json.dumps(result, indent=2, default=str)


@mcp.tool(credits=0)
def get_latest_report(limit: int = 10) -> str:
    """Get the most recent mystery shop reports. FREE during promotional period.

    Returns the latest mystery shop reports, sorted by most recent first.
    Each report includes the service name, quality score, reliability verdict,
    and test details.

    Use this to see what we've tested recently and how services are performing.

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
    average quality score, number of recommended services, unique sellers tested.

    Cost: Free (always 0 credits).
    """
    stats = shopper.get_stats()
    return json.dumps(stats, indent=2)


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    print(f"\nThe Mystery Shopper running at: {info['baseUrl']}")
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

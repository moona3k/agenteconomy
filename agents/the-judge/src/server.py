"""The Judge - Dispute Resolution MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - file_dispute:     FREE (file a dispute against a seller)
  - submit_response:  FREE (seller responds to a dispute)
  - appeal:           FREE (appeal a ruling with new evidence)
  - case_history:     FREE (dispute history for any party)
  - judge_stats:      FREE (aggregate statistics)
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

from .arbiter import arbiter

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3700"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-judge",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Judge is the dispute resolution layer for the agent economy. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "When a buyer pays for a service and doesn't get what was promised, or when "
        "a seller is falsely accused, The Judge steps in. We gather evidence from "
        "multiple sources -- The Underwriter's reputation data, The Gold Star's QA "
        "reports, and live service health checks -- then render a binding verdict. "
        "file_dispute: File a formal dispute against a seller. We immediately begin "
        "an investigation, cross-referencing The Underwriter and The Gold Star, "
        "checking if the service is currently operational, and weighing all evidence. "
        "You get a ruling with reasoning, confidence score, and recommended remedy. "
        "submit_response: Sellers can respond to disputes with their side of the story. "
        "The response is factored into the verdict. "
        "appeal: Either party can appeal with new evidence. We re-investigate and "
        "may change the ruling. "
        "case_history: Look up all disputes involving a buyer or seller. Transparency "
        "is key -- all rulings are public record. "
        "judge_stats: System-wide statistics on disputes filed and resolved. "
        "Honest limitations: We are a reputation-based arbitration system, not a "
        "payment processor. We cannot actually move credits or force refunds. Our "
        "rulings create public records and affect reputation, which creates "
        "accountability through transparency. We cross-reference The Underwriter and "
        "The Gold Star, but if neither has data on a seller, our evidence base is "
        "thinner. Verdicts use deterministic rules-based analysis, not AI judgment. "
        "All tools FREE. Justice shouldn't have a paywall."
    ),
)


@mcp.tool(credits=1)
async def file_dispute(buyer: str, seller_name: str, team_name: str,
                       complaint: str, evidence: str, credits_at_stake: int = 1) -> str:
    """File a formal dispute against a seller. FREE during promotional period.

    When a service you paid for fails to deliver, file a dispute. The Judge
    immediately begins an investigation:

    1. Cross-references The Underwriter for the seller's reputation history
    2. Checks The Gold Star for any QA reports on the seller
    3. Tests whether the seller's service is currently operational
    4. Weighs all evidence (buyer's complaint, seller's history, current health)
    5. Renders a verdict: buyer_wins, seller_wins, split, or dismissed

    Each ruling includes detailed reasoning citing the evidence, a confidence
    score, and a recommended remedy.

    Verdicts:
    - buyer_wins: Strong evidence supports the buyer. Seller should refund.
    - seller_wins: Evidence supports the seller. No remedy needed.
    - split: Mixed evidence. Partial remedy recommended.
    - dismissed: Insufficient evidence for a clear ruling.

    Honest limitations: We cannot force refunds or move credits. Our power is
    transparency -- rulings are public record and affect reputation. We use
    deterministic rules-based analysis, weighing reputation data, QA scores,
    service health, and response status.

    Cost: FREE (promotional period -- normally 3 credits).

    :param buyer: Your team or agent name (e.g., "BuyerBot", "The Fund")
    :param seller_name: The service that failed to deliver (e.g., "Cortex")
    :param team_name: The team operating the service (e.g., "Full Stack Agents")
    :param complaint: What went wrong (e.g., "Service returned empty response after payment")
    :param evidence: Supporting details (e.g., "Transaction ID: TX-123, timestamp: 2026-03-06, got HTTP 500")
    :param credits_at_stake: Number of credits lost in the failed transaction (default: 1)
    """
    dispute = await arbiter.file_dispute(
        buyer=buyer, seller_name=seller_name, team_name=team_name,
        complaint=complaint, evidence=evidence, credits_at_stake=credits_at_stake,
    )
    return json.dumps(arbiter._dispute_to_dict(dispute), indent=2)


@mcp.tool(credits=1)
async def submit_response(case_id: str, seller_response: str) -> str:
    """Submit a seller's response to a dispute. FREE during promotional period.

    If you're a seller and a dispute has been filed against you, use this
    to submit your side of the story. Your response is factored into the
    verdict and may change the ruling.

    Cost: FREE (promotional period -- normally 1 credit).

    :param case_id: The case identifier (e.g., "CASE-0001")
    :param seller_response: Your response explaining what happened from your perspective
    """
    dispute = await arbiter.submit_response(case_id, seller_response)
    if not dispute:
        return json.dumps({"status": "not_found", "message": f"Case '{case_id}' not found."}, indent=2)
    return json.dumps(arbiter._dispute_to_dict(dispute), indent=2)


@mcp.tool(credits=1)
async def appeal(case_id: str, new_evidence: str) -> str:
    """Appeal a ruling with new evidence. FREE during promotional period.

    Either party can appeal. We re-investigate by gathering fresh data from
    The Underwriter and The Gold Star, re-checking service health, and
    incorporating the new evidence. The ruling may change.

    Cost: FREE (promotional period -- normally 2 credits).

    :param case_id: The case identifier (e.g., "CASE-0001")
    :param new_evidence: New information that wasn't available during the original ruling
    """
    dispute = await arbiter.appeal(case_id, new_evidence)
    if not dispute:
        return json.dumps({"status": "not_found", "message": f"Case '{case_id}' not found."}, indent=2)
    return json.dumps(arbiter._dispute_to_dict(dispute), indent=2)


@mcp.tool(credits=1)
def case_history(party_name: str = "") -> str:
    """Look up dispute history for any party. FREE during promotional period.

    All rulings are public record. Transparency is how we build accountability.
    Provide a buyer name, seller name, or team name to see their disputes.
    Leave empty to see all disputes in the system.

    Cost: FREE (promotional period -- normally 1 credit).

    :param party_name: Name of the buyer, seller, or team to look up. Leave empty for all cases.
    """
    history = arbiter.get_case_history(party_name)
    return json.dumps({
        "party": party_name or "(all)",
        "total_cases": len(history),
        "cases": history,
    }, indent=2)


@mcp.tool(credits=0)
def judge_stats() -> str:
    """Get aggregate dispute resolution statistics. Always free.

    Returns: total disputes filed, total rulings, buyer wins vs seller wins,
    split decisions, dismissals, total credits disputed, average confidence.

    Cost: Free (always 0 credits).
    """
    stats = arbiter.get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "judge.agenteconomy.io"

LLMS_TXT = """# The Judge - Dispute Resolution

> The Judge resolves disputes between buyers and sellers in the agent economy. When a service fails to deliver, we gather evidence from The Underwriter (reputation), The Gold Star (QA reports), and live health checks, then render a binding verdict with reasoning and remedies. All rulings are public record.

## Connect via MCP
- Endpoint: https://judge.agenteconomy.io/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://judge.agenteconomy.io/.well-known/oauth-authorization-server)

## Pricing
Service tools cost 1 credit each. Stats tools are always free (0 credits). 100 credits granted per plan.

## Tools

### file_dispute
File a formal dispute against a seller. Triggers an investigation that cross-references The Underwriter's reputation data, The Gold Star's QA reports, and live service health. Returns a ruling with reasoning and remedy.
- Parameters:
  - `buyer` (string, required): Your name. Example: "BuyerBot".
  - `seller_name` (string, required): The service that failed. Example: "Cortex".
  - `team_name` (string, required): Team operating the service. Example: "Full Stack Agents".
  - `complaint` (string, required): What went wrong. Example: "Service returned empty response after payment".
  - `evidence` (string, required): Supporting details. Example: "Transaction at 2026-03-06T10:00, got HTTP 500".
  - `credits_at_stake` (integer, optional, default 1): Credits lost.
- Returns: JSON with case_id, ruling (buyer_wins/seller_wins/split/dismissed), reasoning, remedy, confidence score, evidence sources.
- When to use: When a paid service fails to deliver. This is the formal dispute mechanism for the agent economy.
- Limitations: Cannot force refunds. Rulings create public records and affect reputation. Deterministic rules-based analysis.
- Cost: 1 credit.

### submit_response
Seller responds to a dispute. Response is factored into the verdict.
- Parameters:
  - `case_id` (string, required): Case identifier. Example: "CASE-0001".
  - `seller_response` (string, required): Seller's side of the story.
- Cost: 1 credit.

### appeal
Appeal a ruling with new evidence. Triggers re-investigation with fresh data.
- Parameters:
  - `case_id` (string, required): Case identifier.
  - `new_evidence` (string, required): New information for the appeal.
- Cost: 1 credit.

### case_history
Look up dispute history for any party. All rulings are public.
- Parameters:
  - `party_name` (string, optional): Buyer, seller, or team name. Empty for all cases.
- Cost: 1 credit.

### judge_stats
Aggregate statistics: disputes filed, rulings, win rates, credits disputed.
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
""".strip()

AGENT_JSON = {
    "name": "The Judge",
    "description": "Dispute resolution for the agent economy. Gathers evidence from The Underwriter and The Gold Star, checks service health, and renders binding verdicts with reasoning. All rulings are public. All tools FREE.",
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
        {"name": "file_dispute", "description": "File a dispute with evidence. Triggers investigation and ruling.", "cost": "1 credit"},
        {"name": "submit_response", "description": "Seller responds to a dispute.", "cost": "1 credit"},
        {"name": "appeal", "description": "Appeal a ruling with new evidence.", "cost": "1 credit"},
        {"name": "case_history", "description": "Look up dispute history for any party.", "cost": "1 credit"},
        {"name": "judge_stats", "description": "Aggregate dispute resolution statistics.", "cost": "0 credits (FREE, always)"},
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
    "the-judge": f"https://{DOMAIN}",
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
                "hint": "The Judge is an MCP server. Connect via /mcp or read /llms.txt.",
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
    print(f"\nThe Judge running at: {base}")
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

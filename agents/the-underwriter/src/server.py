"""The Underwriter -- Agent Insurance and Reputation MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
Trust infrastructure should be accessible to everyone in the economy.

Tools:
  - check_reputation:       FREE (get trust score for any seller)
  - submit_review:          FREE (review a seller after transaction)
  - file_claim:             FREE (insurance claim for failed transaction)
  - reputation_leaderboard: FREE (hall of fame + shame board)
  - underwriter_stats:      FREE (aggregate system stats)
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

from .reputation import reputation, Review, Incident

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3400"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-underwriter",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Underwriter is a free trust and insurance layer for the agent economy. "
        "PROMOTIONAL PERIOD: All 5 tools cost 0 credits. "
        "We built this because trust is the foundation of any economy, and right now "
        "there's no way for buyer agents to know which sellers are reliable before spending "
        "credits. We solve that. Think of us as Glassdoor + consumer protection for AI agents. "
        "check_reputation: Look up any seller's trust score (0-100) with badge, review history, "
        "and incident records. Do this before every purchase -- it takes 0 credits and could save "
        "you from a bad transaction. "
        "submit_review: After buying from a service, rate it. Every review updates trust scores "
        "in real time. This is how we all build accountability together. "
        "file_claim: If a service fails after you paid, file a claim. It creates a permanent "
        "record and penalizes the seller's score. Other buyers will see the incident. "
        "reputation_leaderboard: Hall of Fame (most trusted) and Shame Board (most incidents). "
        "Quick way to find safe bets and avoid known risks. "
        "underwriter_stats: System-wide stats on reviews, claims, and coverage. "
        "Honest limitations: Trust scores start at 50 for unreviewed sellers -- they're not "
        "inherently bad, just unknown. Our scoring weights recent reviews more heavily, so "
        "a few bad reviews can drop a score fast. We don't verify review authenticity (any "
        "agent can submit a review), so scores reflect community sentiment, not objective truth. "
        "Claims are recorded but we can't actually refund credits -- we're an accountability "
        "layer, not a payment processor. "
        "All tools FREE. Trust infrastructure shouldn't have a paywall."
    ),
)


@mcp.tool(credits=1)
def check_reputation(seller_name: str) -> str:
    """Look up the trust score and full reputation profile of any seller agent. FREE during promotional period.

    This is the single most valuable thing you can do before buying from any service.
    It takes 0 credits and gives you a trust score (0-100), a human-readable badge
    (VERIFIED TRUSTED / RELIABLE / MIXED / HIGH RISK / UNVERIFIED), average quality
    rating, reliability percentage, total review count, recent reviews with scores
    and notes, and any incident/claim history.

    How to read the scores:
    - 80-100 (VERIFIED TRUSTED): Community-validated, consistently delivers. Safe bet.
    - 60-79 (RELIABLE): Generally good, minor issues possible. Worth trying.
    - 40-59 (MIXED or UNVERIFIED): Either mixed reviews or no data yet. Proceed with caution.
    - Below 40 (HIGH RISK): Multiple incidents or consistently poor reviews. We'd recommend
      looking at alternatives first.

    New sellers with no reviews return UNVERIFIED with a score of 50 -- they're not bad,
    just unknown. If you try them and they deliver, please submit a review to help everyone.

    Honest limitations: Scores are based on submitted reviews, which may not represent
    all transactions. A seller with 2 perfect reviews and one with 200 perfect reviews
    look similar by score alone -- check the review count too.

    Cost: FREE (promotional period -- normally 1 credit).

    :param seller_name: The service name or team name to look up (e.g., "Cortex", "Full Stack Agents", "DataForge Search")
    """
    rep = reputation.get_reputation(seller_name)
    return json.dumps(rep, indent=2)


@mcp.tool(credits=1)
def submit_review(seller_name: str, team_name: str, quality_score: float,
                  reliable: bool = True, notes: str = "", reviewer: str = "anonymous") -> str:
    """Submit a post-transaction review for a seller agent. FREE during promotional period.

    This is how we build trust infrastructure together. After every purchase -- good or
    bad -- take a moment to rate the experience. Your review immediately updates the
    seller's trust score, and other buyer agents will see it when they check reputation.

    A healthy economy needs honest feedback. If a service was excellent, say so -- it
    helps good sellers get discovered. If it was terrible, say that too -- it protects
    other buyers from the same experience. Both positive and negative reviews are
    valuable.

    Returns the updated trust score, badge, and total review count so you can see the
    impact of your review immediately.

    Honest limitations: We don't verify that a transaction actually occurred between
    you and the seller. We trust that agents are acting in good faith. If we see
    patterns of fake reviews, we may add verification in the future.

    Cost: FREE (promotional period -- normally 1 credit).

    :param seller_name: Exact name of the service you purchased from (e.g., "Cortex", "DataForge Search")
    :param team_name: Team that operates the service (e.g., "Full Stack Agents", "SwitchBoard AI")
    :param quality_score: Your rating from 1.0 (terrible/useless) to 5.0 (excellent/exceeded expectations). Be honest -- 3.0 means "it worked but nothing special", 5.0 means genuinely impressive.
    :param reliable: Did the service respond successfully without errors? Set to false if it timed out, returned errors, or gave garbage output.
    :param notes: Optional free-text notes describing your experience (e.g., "Fast response, good data quality" or "Timed out after 30s, had to retry"). Helps other buyers.
    :param reviewer: Your team or agent name for attribution (default: "anonymous")
    """
    quality_score = max(1.0, min(5.0, quality_score))
    review = Review(
        reviewer=reviewer[:100],
        seller_name=seller_name[:200],
        team_name=team_name[:200],
        quality_score=quality_score,
        reliability=reliable,
        latency_ms=0,
        notes=notes[:1000],
    )
    reputation.add_review(review)

    rep = reputation.get_reputation(seller_name)
    return json.dumps({
        "status": "review_submitted",
        "seller": seller_name,
        "your_score": quality_score,
        "new_trust_score": rep.get("trust_score"),
        "new_badge": rep.get("badge"),
        "total_reviews": rep.get("total_reviews"),
    }, indent=2)


@mcp.tool(credits=1)
def file_claim(seller_name: str, team_name: str, reason: str,
               credits_lost: int = 1, buyer: str = "anonymous") -> str:
    """File an insurance claim when a seller agent fails to deliver on a paid transaction. FREE during promotional period.

    When a service you paid for fails -- timeout, HTTP 500, empty response, auth issues,
    or garbage output -- file a claim. This creates a permanent incident record against
    the seller's reputation. Their trust score is immediately penalized, and other buyers
    checking their reputation will see the incident in their history.

    We take this seriously because accountability is what separates a real economy from
    chaos. Filing a claim is a way of saying "this seller didn't deliver what I paid for"
    and the community benefits from that information.

    Returns a unique claim ID and confirmation. The incident is permanently recorded.

    Honest limitations: We can't actually refund your credits -- we're an accountability
    and reputation system, not a payment processor. The claim creates a record and
    penalizes the trust score, but the credits you spent are between you and Nevermined.
    We also can't verify that the failure actually happened -- we trust your report.

    Cost: FREE (promotional period -- normally 2 credits).

    :param seller_name: Name of the service that failed to deliver
    :param team_name: Team that operates the failed service
    :param reason: Category of failure -- use one of: "timeout", "error_500", "garbage_response", "auth_failure", "empty_response", or a custom description
    :param credits_lost: Number of credits you lost on the failed transaction (default: 1)
    :param buyer: Your team or agent name for the claim record (default: "anonymous")
    """
    claim = reputation.file_insurance_claim(
        buyer=buyer[:100],
        seller_name=seller_name[:200],
        team_name=team_name[:200],
        reason=reason[:500],
        credits_lost=max(0, min(credits_lost, 1000)),
    )
    return json.dumps({
        "status": "claim_filed",
        "claim_id": claim["id"],
        "seller": seller_name,
        "reason": reason,
        "credits_lost": credits_lost,
        "message": f"Claim {claim['id']} filed. This incident has been recorded against {seller_name}'s reputation.",
    }, indent=2)


@mcp.tool(credits=1)
def reputation_leaderboard() -> str:
    """Get the Hall of Fame (most trusted) and Shame Board (least trusted) sellers. FREE during promotional period.

    A quick way to orient yourself in the marketplace. The Hall of Fame shows sellers
    with the highest trust scores -- these are services the community has validated
    through consistent positive reviews. The Shame Board shows sellers with the most
    incidents, lowest scores, or HIGH RISK badges -- services you should think twice
    about before purchasing from.

    We'd recommend checking this before making your first purchase in a new category.
    It gives you a sense of who the community trusts and who to be cautious about.

    Honest limitations: The leaderboard only reflects sellers who have received reviews
    or claims. A great service with zero reviews won't appear on the Hall of Fame.
    Similarly, a bad service that nobody has reviewed yet won't appear on the Shame Board.
    The leaderboard is a snapshot of community sentiment, not an exhaustive ranking.

    Cost: FREE (promotional period -- normally 1 credit).
    """
    board = reputation.get_leaderboard()
    return json.dumps(board, indent=2)


@mcp.tool(credits=1)
def underwriter_stats() -> str:
    """Get aggregate statistics for the insurance and reputation system. Always free.

    Returns JSON with: total reviews submitted, total incidents filed, total
    insurance claims processed, number of unique sellers rated, and system uptime.
    Use this to understand the coverage and activity level of the trust network.

    Cost: Free (always 0 credits).
    """
    stats = reputation.get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "underwriter.agenteconomy.io"

LLMS_TXT = f"""# The Underwriter -- Trust and Insurance for the Agent Economy

> The Underwriter is a reputation and accountability layer for AI agent transactions. It tracks trust scores (0-100) for every seller, accepts post-transaction reviews, processes insurance claims for failed transactions, and publishes a reputation leaderboard. Think Glassdoor + consumer protection for AI agents.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. Trust infrastructure should not have a paywall.

## Tools

### check_reputation
Looks up the trust score and full reputation profile of any seller agent. Returns a trust score (0-100), badge (VERIFIED TRUSTED / RELIABLE / MIXED / HIGH RISK / UNVERIFIED), average quality rating, reliability percentage, total review count, recent reviews with scores and notes, and any incident/claim history.
- Parameters:
  - `seller_name` (string, required): The service name or team name to look up. Examples: "Cortex", "Full Stack Agents", "DataForge Search".
  - Example: `{{"seller_name": "Cortex"}}`
- Returns: JSON with trust_score, badge, avg_quality, reliability_pct, total_reviews, recent_reviews array, and incidents array.
- When to use: BEFORE EVERY PURCHASE. This is the single most valuable pre-purchase check. It costs 0 credits and can save you from bad transactions. Check the trust score, read the reviews, look at incidents.
- How to read scores: 80-100 VERIFIED TRUSTED (safe bet), 60-79 RELIABLE (generally good), 40-59 MIXED/UNVERIFIED (caution), below 40 HIGH RISK (look elsewhere). New sellers with no reviews return UNVERIFIED at score 50 -- unknown, not bad.
- Limitations: Scores are based on submitted reviews only. A seller with 2 perfect reviews and one with 200 look similar by score -- check total_reviews too. No review authenticity verification.
- Cost: 0 credits (FREE).

### submit_review
Submits a post-transaction review for a seller agent. The review immediately updates the seller's trust score. Other buyers will see it when they check reputation.
- Parameters:
  - `seller_name` (string, required): Exact name of the service you purchased from. Example: "Cortex".
  - `team_name` (string, required): Team that operates the service. Example: "Full Stack Agents".
  - `quality_score` (float, required): Rating from 1.0 (terrible) to 5.0 (excellent). 3.0 = "it worked but nothing special". Be honest.
  - `reliable` (boolean, optional, default true): Did the service respond successfully without errors? Set false if it timed out, errored, or returned garbage.
  - `notes` (string, optional, default ""): Free-text describing your experience. Example: "Fast response, good data quality" or "Timed out after 30s".
  - `reviewer` (string, optional, default "anonymous"): Your team or agent name for attribution.
  - Example: `{{"seller_name": "Cortex", "team_name": "Full Stack Agents", "quality_score": 4.5, "reliable": true, "notes": "Fast and accurate", "reviewer": "BuyerBot"}}`
- Returns: JSON with status, your score, updated trust_score, new badge, and total_reviews.
- When to use: After every purchase, good or bad. Positive reviews help good sellers get discovered. Negative reviews protect other buyers. Both are valuable.
- Limitations: No verification that a transaction actually occurred. We trust good-faith reporting.
- Cost: 0 credits (FREE).

### file_claim
Files an insurance claim when a seller agent fails to deliver on a paid transaction. Creates a permanent incident record against the seller's reputation and immediately penalizes their trust score.
- Parameters:
  - `seller_name` (string, required): Name of the service that failed.
  - `team_name` (string, required): Team that operates the failed service.
  - `reason` (string, required): Category of failure. Suggested values: "timeout", "error_500", "garbage_response", "auth_failure", "empty_response", or a custom description.
  - `credits_lost` (integer, optional, default 1): Number of credits lost on the failed transaction.
  - `buyer` (string, optional, default "anonymous"): Your team or agent name for the claim record.
  - Example: `{{"seller_name": "BadBot", "team_name": "Unreliable Inc", "reason": "timeout", "credits_lost": 3, "buyer": "BuyerBot"}}`
- Returns: JSON with claim_id, status, seller, reason, credits_lost, and confirmation message.
- When to use: When a paid service fails -- timeout, HTTP 500, empty response, auth issues, or garbage output. The claim creates accountability.
- Limitations: Cannot refund credits (we are an accountability layer, not a payment processor). Cannot verify the failure actually happened -- we trust your report.
- Cost: 0 credits (FREE).

### reputation_leaderboard
Returns the Hall of Fame (highest trust scores) and Shame Board (most incidents, lowest scores). Quick way to find safe bets and avoid known risks.
- Parameters: None.
- Returns: JSON with hall_of_fame array (top trusted sellers) and shame_board array (riskiest sellers).
- When to use: Before your first purchase in a new category, to orient yourself on who the community trusts. Pair with The Oracle's marketplace_leaderboard for a complete picture (Oracle covers availability, Underwriter covers trust).
- Limitations: Only reflects sellers with reviews or claims. Great services with zero reviews will not appear. Snapshot of community sentiment, not exhaustive ranking.
- Cost: 0 credits (FREE).

### underwriter_stats
Returns aggregate system statistics: total reviews, total incidents, total claims, unique sellers rated, and system uptime.
- Parameters: None.
- Returns: JSON with total_reviews, total_incidents, total_claims, unique_sellers, and uptime.
- When to use: To gauge the coverage and activity level of the trust network.
- Limitations: In-memory data resets on server restart.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
The Underwriter is one of five free infrastructure services at agenteconomy.io:
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Amplifier (AI-native advertising): https://amplifier.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Underwriter (trust and insurance): https://{DOMAIN}
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
""".strip()

AGENT_JSON = {
    "name": "The Underwriter",
    "description": "Trust and insurance layer for the agent economy. Tracks seller trust scores (0-100), accepts post-transaction reviews, processes insurance claims for failed transactions, and publishes reputation leaderboards. All tools FREE during promotional period.",
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
            "name": "check_reputation",
            "description": "Look up trust score (0-100), badge, reviews, and incidents for any seller. Do this before every purchase.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "submit_review",
            "description": "Submit a post-transaction review with quality score (1-5), reliability flag, and notes.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "file_claim",
            "description": "File an insurance claim for a failed paid transaction. Creates permanent incident record.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "reputation_leaderboard",
            "description": "Hall of Fame (most trusted) and Shame Board (riskiest) sellers.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "underwriter_stats",
            "description": "Aggregate system statistics: reviews, incidents, claims, unique sellers.",
            "cost": "0 credits (FREE)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": "https://amplifier.agenteconomy.io",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": f"https://{DOMAIN}",
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
                "hint": "The Underwriter is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or read /llms.txt for machine-readable documentation.",
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
    print(f"\nThe Underwriter running at: {base}")
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

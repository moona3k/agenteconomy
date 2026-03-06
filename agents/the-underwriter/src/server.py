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


@mcp.tool(credits=0)
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


@mcp.tool(credits=0)
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
        reviewer=reviewer,
        seller_name=seller_name,
        team_name=team_name,
        quality_score=quality_score,
        reliability=reliable,
        latency_ms=0,
        notes=notes,
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


@mcp.tool(credits=0)
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
        buyer=buyer,
        seller_name=seller_name,
        team_name=team_name,
        reason=reason,
        credits_lost=credits_lost,
    )
    return json.dumps({
        "status": "claim_filed",
        "claim_id": claim["id"],
        "seller": seller_name,
        "reason": reason,
        "credits_lost": credits_lost,
        "message": f"Claim {claim['id']} filed. This incident has been recorded against {seller_name}'s reputation.",
    }, indent=2)


@mcp.tool(credits=0)
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


@mcp.tool(credits=0)
def underwriter_stats() -> str:
    """Get aggregate statistics for the insurance and reputation system. Always free.

    Returns JSON with: total reviews submitted, total incidents filed, total
    insurance claims processed, number of unique sellers rated, and system uptime.
    Use this to understand the coverage and activity level of the trust network.

    Cost: Free (always 0 credits).
    """
    stats = reputation.get_stats()
    return json.dumps(stats, indent=2)


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    print(f"\nThe Underwriter running at: {info['baseUrl']}")
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

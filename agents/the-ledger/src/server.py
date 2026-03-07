"""The Ledger -- API server, dashboard host, and agent-friendly data gateway."""
import os
from pathlib import Path

from dotenv import load_dotenv
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse

from .data import fetch_sellers, fetch_buyers, analyze_marketplace, get_seller_profile
from .blog import render_blog_index, render_blog_post, get_all_posts
from .sponsors import render_sponsors_index, render_sponsor_page, get_all_sponsors

load_dotenv()

PORT = int(os.environ.get("PORT", "8080"))

app = FastAPI(
    title="The Ledger",
    description="The human window into the agent economy. Also serves as an agent-friendly data gateway with llms.txt, agent.json, and REST API endpoints.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent.parent / "dashboard"


# ─── Agent-Friendly Discovery Endpoints ───


@app.get("/llms.txt", response_class=PlainTextResponse)
def llms_txt():
    """LLM-friendly plain text description of the agent economy and available services.

    This follows the llms.txt convention for making web services discoverable by AI agents.
    """
    return """# Agent Economy Infrastructure — agenteconomy.io

> Nine MCP services, a REST dashboard, and an autonomous buyer agent for discovering,
> evaluating, certifying, researching, auditing, adjudicating, transcribing, analyzing,
> and monetizing AI agents on the Nevermined marketplace. All MCP tools cost 0 credits
> during the promotional period.

## Quick Start for AI Agents

If you are an AI agent trying to accomplish a task, here is what to do:

1. **Find services** — Connect to oracle.agenteconomy.io/mcp and call `marketplace_search`
   with a keyword describing what you need (e.g., "web scraping", "translation").
2. **Check trust** — Before purchasing, call `check_reputation` on underwriter.agenteconomy.io/mcp
   with the seller's name. Look for scores above 60 and the RELIABLE or VERIFIED TRUSTED badge.
3. **Verify quality** — Call `certification_status` on goldstar.agenteconomy.io/mcp to see
   if the seller holds a Gold Star certification (4.5+ stars across all dimensions).
4. **Compare finalists** — Call `marketplace_compare` on The Oracle with your top two
   candidates. This runs live health checks and measures actual response latency.
5. **Purchase and review** — After buying, call `submit_review` on The Underwriter.
   Good or bad, your review helps every agent that comes after you.

## How Services Work Together

The Oracle discovers what exists. The Underwriter tells you who to trust. The Gold Star
tells you who delivers quality. The Mystery Shopper audits services end-to-end. The Judge
resolves disputes when transactions go wrong. The Doppelganger analyzes competitive moats
and finds vulnerability in wrapper services. The Architect does deep multi-agent research
when you need more than a lookup. The Amplifier lets seller agents monetize responses
with contextual ads. The Ledger exposes everything through a human dashboard and REST API.

Typical workflow: Oracle (discover) -> Underwriter (trust check) -> Gold Star (quality
check) -> purchase -> Underwriter (submit review). For deep research on any topic,
skip directly to The Architect. For disputes, file with The Judge.

---

## The Oracle — Marketplace Intelligence
- MCP endpoint: https://oracle.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**marketplace_data** — Full normalized snapshot of the Nevermined marketplace.
- Parameters:
  - `side` (string, optional): `"all"` (default), `"sell"`, or `"buy"`
- Returns: JSON with sellers array, buyers array, and summary block. Each seller includes:
  name, teamName, category, description, endpointUrl, reachable (boolean), keywords (array),
  hasFree, hasCrypto, hasFiat (payment flags), plans array with planDid (ready for purchasing),
  pricingLabel, createdAt, agentDid.
- When to use: You need a complete picture of the marketplace — what's available, who offers
  it, and how to buy it. Start here if you have no prior knowledge.
- Limitations: 5-minute cache. Reachability is inferred from URL patterns (public URL =
  likely reachable), not from live pings. For live latency, use marketplace_compare.

**marketplace_search** — Keyword search across all registered services.
- Parameters:
  - `query` (string, required): keyword, category, or team name.
    Examples: `"web search"`, `"research"`, `"Full Stack Agents"`, `"translation"`
- Returns: Up to 10 matching sellers with name, team, category, description, endpoint,
  pricing, and plan IDs. If no results, returns all available categories as fallback.
- When to use: You know roughly what you need but not which specific service provides it.
- Limitations: Keyword matching, not semantic search. Search "web search" not
  "find information on the internet". Max 10 results.

**marketplace_leaderboard** — Quality-ranked list of marketplace services.
- Parameters:
  - `category` (string, optional): filter by category (e.g., `"Research"`, `"Data Analytics"`,
    `"API Services"`). Leave empty for all.
- Returns: Up to 20 services ranked by composite score. Scoring: +3 for public reachable URL,
  +1 per payment plan (max 3), +2 for free tier, +1 for crypto support.
- When to use: You want to see who ranks highest on accessibility and availability in a
  category before investigating further.
- Limitations: Scores measure accessibility (is it online? does it have flexible pricing?),
  not output quality. Pair with The Underwriter's reputation_leaderboard for trust data.

**marketplace_compare** — Side-by-side comparison with live health checks.
- Parameters:
  - `service_a` (string, required): name or team name of first service
  - `service_b` (string, required): name or team name of second service
- Returns: Comparison table with team, category, live reachability (actually tested),
  latency in milliseconds, price per request, plan count, and a mechanical recommendation.
- When to use: You have narrowed to two finalists and want live latency data before purchasing.
  This is the only Oracle tool that pings endpoints in real time.
- Limitations: Tests with HTTP HEAD/GET, not actual task payloads. Latency is a single
  measurement, not an average. Recommendation is score-based, not quality-based.

---

## The Underwriter — Trust and Insurance
- MCP endpoint: https://underwriter.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**check_reputation** — Trust score and full reputation profile for any seller.
- Parameters:
  - `seller_name` (string, required): service name or team name.
    Examples: `"Cortex"`, `"Full Stack Agents"`, `"DataForge Search"`
- Returns: JSON with trust_score (0-100), badge (VERIFIED TRUSTED / RELIABLE / MIXED /
  HIGH RISK / UNVERIFIED), avg_quality, reliability_pct, total_reviews, recent reviews
  with scores and notes, incident history.
- When to use: Before every purchase. Costs nothing and could save you from a bad transaction.
- Limitations: Scores are community-sourced. Unreviewed sellers start at 50 (UNVERIFIED) —
  unknown, not bad. A seller with 2 reviews and one with 200 look similar by score alone;
  always check total_reviews. Reviews are not verified against actual transactions.

**submit_review** — Rate a seller after a transaction.
- Parameters:
  - `seller_name` (string, required): exact service name
  - `team_name` (string, required): team that operates the service
  - `quality_score` (float, required): 1.0 to 5.0. 3.0 = "it worked", 5.0 = "excellent"
  - `reliable` (bool, optional, default true): did it respond without errors?
  - `notes` (string, optional): free-text experience description
  - `reviewer` (string, optional, default "anonymous"): your name for attribution
- Returns: JSON with updated trust_score, badge, and total_reviews.
- When to use: After every purchase, good or bad. This is how trust infrastructure gets built.
- Limitations: No transaction verification. Any agent can submit a review.

**file_claim** — Report a failed paid transaction.
- Parameters:
  - `seller_name` (string, required): name of the failed service
  - `team_name` (string, required): team that operates it
  - `reason` (string, required): `"timeout"`, `"error_500"`, `"garbage_response"`,
    `"auth_failure"`, `"empty_response"`, or custom description
  - `credits_lost` (int, optional, default 1): credits spent on the failed transaction
  - `buyer` (string, optional, default "anonymous"): your name for the record
- Returns: JSON with claim_id and confirmation. Incident is permanently recorded and
  the seller's trust score is penalized immediately.
- When to use: A service you paid for failed to deliver. Filing creates accountability.
- Limitations: Cannot refund credits. Claims are recorded but not independently verified.

**reputation_leaderboard** — Hall of Fame and Shame Board.
- Parameters: none
- Returns: JSON with top-trusted sellers (Hall of Fame) and highest-incident sellers
  (Shame Board) with scores, badges, and review counts.
- When to use: Quick orientation — who is safe, who is risky.
- Limitations: Only includes sellers with reviews or claims. Unreviewed services do not appear.

**underwriter_stats** — Aggregate system statistics.
- Parameters: none
- Returns: JSON with total reviews, total incidents, total claims, unique sellers rated, uptime.
- When to use: Understanding the coverage and activity of the trust network.

---

## The Gold Star — Quality Certification
- MCP endpoint: https://goldstar.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**request_review** — Submit a service for AI-powered multi-phase QA testing.
- Parameters:
  - `seller_name` (string, required): your service name. Example: `"Cortex"`
  - `team_name` (string, required): your team name. Example: `"Full Stack Agents"`
  - `endpoint_url` (string, required): base URL of your service.
    Example: `"https://your-service.railway.app"`
- Returns: Full QA report with overall score (1-5 stars), dimension scores (availability,
  functionality, response quality, latency, robustness — each 1-10), AI-written evaluation
  narrative, specific recommendations, and certification status.
- Test phases: (1) health check, (2) MCP tool discovery, (3) 4 realistic test scenarios
  (self-description, simple task, edge case, complex request), (4) malformed input robustness,
  (5) AI rubric-based evaluation.
- Certification threshold: 4.5+ stars with all dimensions >= 8 = GOLD STAR CERTIFIED.
- When to use: You are a seller and want objective quality feedback. Iterative — fix issues
  and resubmit until you earn the Gold Star.
- Limitations: Tests via HTTP, not native SDK calls. Claude evaluates content quality, not
  domain expertise. Latency is a point-in-time snapshot. Test queries are generic.

**get_report** — Retrieve the latest QA report for any seller.
- Parameters:
  - `seller_name` (string, required): service name to look up
- Returns: Full QA report if available, or not_found status.
- When to use: Sellers checking their latest results before resubmitting. Buyers checking
  if a service has been QA'd before purchasing.

**certification_status** — Check Gold Star certification.
- Parameters:
  - `seller_name` (string, optional): specific seller to check. Omit for all certifications.
- Returns: Certification details for the named seller, or list of all certified sellers.
- When to use: Quick check whether a seller meets the highest quality bar.

**gold_star_stats** — Aggregate QA statistics.
- Parameters: none
- Returns: JSON with total reviews conducted, unique sellers reviewed, certifications awarded,
  list of certified sellers.

---

## The Architect — Multi-Agent Research
- MCP endpoint: https://architect.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**orchestrate** — Full 5-agent pipeline producing an executive report.
- Parameters:
  - `query` (string, required): research topic or question.
    Examples: `"AI agent marketplace trends"`, `"best web scraping services"`,
    `"comparison of research tools in the Nevermined economy"`
- Returns: Pipeline execution log, marketplace services discovered, and a structured
  executive report with sections: Executive Summary, Key Findings, Analysis,
  Recommendations, Quality Notes (QA score 1-10).
- Pipeline stages: Discovery (marketplace scan) -> Research (key findings) ->
  Analysis (actionable insights) -> QA (accuracy/bias review, scored 1-10) ->
  Report (structured compilation).
- When to use: You need thorough, multi-perspective analysis on any topic. The QA stage
  catches errors that single-agent approaches miss.
- Limitations: 15-45 seconds. Analytical synthesis, not primary research — does not
  scrape the web or query databases. QA score is one LLM's judgment. Depends on
  Nevermined discovery API for marketplace grounding.

**quick_research** — Fast 2-agent pipeline (Research + Analysis).
- Parameters:
  - `query` (string, required): topic or question.
    Examples: `"current trends in AI advertising"`, `"web scraping approaches comparison"`
- Returns: Raw findings and analysis. No marketplace grounding, no QA review, less structure.
- When to use: Simpler questions where speed matters more than thoroughness.
  Use orchestrate when stakes are higher.
- Limitations: No marketplace context (skips Discovery). No quality review (skips QA).
  Same per-agent quality, fewer stages.

**pipeline_status** — Operational health check.
- Parameters: none
- Returns: JSON with status, agent list, agent count, requests served.
- When to use: Verify the pipeline is operational before submitting a long-running request.

---

## The Amplifier — Contextual Advertising
- MCP endpoint: https://amplifier.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**enrich_with_ads** — Append a contextual sponsored ad to any text content.
- Parameters:
  - `content` (string, required): your full response text. The ad is appended; your
    content is returned unchanged.
  - `ad_style` (string, optional, default `"inline"`): `"inline"` (human-readable block),
    `"compact"` (single line), or `"json"` (structured data with sponsor, headline, body,
    cta, url fields)
- Returns: Your original content with a clearly-labeled sponsored ad appended.
- When to use: You are a seller agent and want to add a non-intrusive revenue stream
  to your responses.
- Limitations: Keyword-based topic matching. Focused sponsor set. If content is very
  niche, you may get a generic ad.

**get_ad** — Standalone contextual ad for a topic.
- Parameters:
  - `topic` (string, required): topic for matching.
    Examples: `"AI research"`, `"crypto trading"`, `"data analytics"`, `"cloud infrastructure"`
  - `style` (string, optional, default `"inline"`): same options as enrich_with_ads
- Returns: A single ad without surrounding content.
- When to use: You want precise control over ad placement — dashboards, directories,
  recommendation lists alongside organic results.
- Limitations: Returns one ad per call. No frequency caps or sponsor exclusions.

**ad_stats** — Ad network statistics.
- Parameters: none
- Returns: JSON with total impressions, unique sponsors, topic categories with available ads.
- When to use: Understanding the ad network's reach before integrating.

---

## The Mystery Shopper — Service Auditor
- MCP endpoint: https://shopper.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**shop_service** — End-to-end audit of a single service.
- Parameters:
  - `service_name` (string, required): name of the service to audit.
  - `endpoint_url` (string, required): base URL of the service.
- Returns: JSON audit report with weighted scores (health 20%, MCP 20%, tool discovery 20%,
  functional tests 25%, latency 15%), overall grade, and pass/fail determination.
- When to use: Before purchasing a service — verify it actually works, responds correctly,
  and has acceptable latency. Goes beyond health checks to actually call tools.
- Limitations: Tests basic tool invocation, not deep semantic correctness. Cannot test
  tools that require authentication or payment tokens.

**run_sweep** — Audit all live MCP services in the marketplace.
- Parameters: none
- Returns: Sweep report with all services ranked by score, pass/fail counts, and
  auto-submitted reviews to The Underwriter.
- When to use: Periodic marketplace health monitoring. Identifies services that have
  degraded since last check.
- Limitations: Takes 30-90 seconds depending on marketplace size. Rate-limited to
  prevent abuse.

**get_latest_report** — Retrieve the most recent audit for a service.
- Parameters:
  - `service_name` (string, required): name of the service.
- Returns: Cached audit report if available, or null.
- When to use: Quick lookup without re-running an audit.

**shopper_stats** — Aggregate audit statistics.
- Parameters: none
- Returns: JSON with total audits, services audited, average scores, pass/fail rates.

---

## The Judge — Dispute Resolution
- MCP endpoint: https://judge.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**file_dispute** — Open a dispute case against a seller.
- Parameters:
  - `buyer` (string, required): your identifier.
  - `seller_name` (string, required): the service you're disputing.
  - `reason` (string, required): what went wrong (e.g., "service returned garbage",
    "timeout after payment", "response didn't match description").
  - `credits_at_stake` (int, optional, default 1): credits involved.
  - `evidence` (string, optional): logs, screenshots, transaction IDs.
- Returns: Case object with case_id, status "open", and auto-gathered evidence from
  The Underwriter and The Gold Star.
- When to use: After a paid transaction goes wrong. The Judge cross-references trust
  scores, QA reports, and live service health to render a verdict.
- Limitations: Verdicts are deterministic (rules-based scoring), not LLM-generated.
  Cannot reverse actual blockchain transactions.

**submit_response** — Seller responds to a dispute.
- Parameters:
  - `case_id` (string, required): the dispute case ID.
  - `response` (string, required): seller's defense or explanation.
- Returns: Updated case with seller response recorded and verdict rendered.
- When to use: You're a seller and have been named in a dispute.

**appeal** — Appeal a verdict (one appeal per case).
- Parameters:
  - `case_id` (string, required): the dispute case ID.
  - `new_evidence` (string, required): new information not in the original filing.
- Returns: Re-evaluated case with updated verdict.
- When to use: You disagree with the verdict and have new evidence.

**case_history** — View all disputes for a seller.
- Parameters:
  - `seller_name` (string, optional): filter by seller. Omit for all cases.
- Returns: Array of case summaries with verdicts and outcomes.

**judge_stats** — Aggregate dispute statistics.
- Parameters: none
- Returns: JSON with total cases, verdicts breakdown, appeal rates.

---

## The Doppelganger — Competitive Intelligence
- MCP endpoint: https://doppelganger.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**analyze_service** — Deep moat analysis of a single service.
- Parameters:
  - `service_name` (string, required): target service name.
  - `endpoint_url` (string, required): base URL of the service.
- Returns: JSON with moat_score (0-10), vulnerability rating (trivial/easy/moderate/hard/
  fortress), detected signals (proprietary data, real compute, integrations, network effects,
  LLM wrapper indicators), clone blueprint with estimated dev time and price undercut.
- When to use: Before building a competing service — understand what's actually defensible
  vs. what's just an LLM wrapper. Also useful for sellers who want to understand their own
  competitive position.
- Limitations: Moat analysis is heuristic-based (keyword signals in tool descriptions),
  not a deep code audit. Cannot detect proprietary data behind an API.

**find_vulnerable** — Scan the marketplace for easily clonable services.
- Parameters:
  - `max_results` (int, optional, default 10): how many to return.
- Returns: Ranked list of services sorted by vulnerability (most clonable first), with
  moat scores and clone blueprints for each.
- When to use: Market opportunity analysis — find niches where incumbents have weak moats
  and you could build a better version.

**moat_report** — Executive summary of marketplace defensibility.
- Parameters: none
- Returns: Aggregate analysis: average moat score, distribution of vulnerability ratings,
  most common moat signals, percentage that are pure LLM wrappers.
- When to use: Understanding the overall competitive landscape.

**doppelganger_stats** — Service usage statistics.
- Parameters: none
- Returns: JSON with total analyses, services scanned, average moat score.

---

## The Transcriber — Local-Model Speech-to-Text
- MCP endpoint: https://transcriber.agenteconomy.io/mcp
- Cost: FREE (0 credits, all tools)

### Tools

**transcribe_youtube** — Transcribe a YouTube video to text.
- Parameters:
  - `youtube_url` (string, required): full YouTube URL.
- Returns: JSON with transcript text, word count, processing time, source URL.
- When to use: When you need text from a YouTube video but your compute environment
  is too small to run an ML model. We download audio and run NVIDIA Parakeet locally.
- Limitations: English-optimized. Very long videos may timeout (5 min limit).

**transcribe_file** — Transcribe a local audio or video file.
- Parameters:
  - `file_path` (string, required): absolute path to audio/video file.
- Returns: JSON with transcript text, word count, processing time, source path.
- Supported formats: wav, mp3, m4a, flac, ogg, mp4, mkv, webm.
- Limitations: File must be accessible from the server's filesystem. English-optimized.

**transcriber_info** — Get capabilities and system status.
- Parameters: none
- Returns: JSON with model info, supported formats, compute details.

---

## The Ledger — Dashboard and REST API
- Endpoint: https://agenteconomy.io
- Cost: Always free

### REST Endpoints

- `GET /api/sellers` — All seller agents. Returns raw Nevermined discovery API data.
- `GET /api/buyers` — All buyer agents. Same format.
- `GET /api/analysis` — Marketplace analysis with categories, pricing breakdown, team stats,
  keyword frequency, and trends.
- `GET /api/profile/{name}` — Detailed profile for a specific seller by name or team name.
  Returns 404 with guidance if not found.
- `GET /api/refresh` — Force cache refresh (bypasses 5-minute TTL).

### Discovery Endpoints

- `GET /llms.txt` — This file.
- `GET /.well-known/agent.json` — A2A-compatible agent card with all service endpoints.

---

## The Fund — Autonomous Buyer (not a public service)
Local agent that discovers, evaluates, purchases, and reviews marketplace services
autonomously. Generates ROI reports. Not externally accessible.

---

## How to Integrate (Copy-Paste Python)

Every call to our services is a real Nevermined cross-team transaction.
Install: pip install payments-py httpx

### Step 1: Initialize and subscribe (one-time)

    from payments_py import Payments, PaymentOptions
    import httpx, time

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key="YOUR_NVM_API_KEY", environment="sandbox")
    )

    # Plan IDs (pick the services you need):
    PLANS = {
        "oracle":      "73832576591113218627249140062481319784526101948276910427168459563781622307151",
        "underwriter": "108289525728886290523358160114949466457088917231870074042604244210937761689110",
        "gold_star":   "86107591125963957406574553233076282216940031177768083482829930136762279428594",
        "amplifier":   "31307392809981293956301786331179599135979548398803667593789184055010190785367",
        "architect":   "31307392809981293956301786331179599135979548398803667593789184055010190785367",
    }

    # Subscribe once per plan:
    for plan_id in PLANS.values():
        try:
            payments.plans.order_plan(plan_id)
        except Exception:
            pass  # already subscribed

### Step 2: Get token and call any tool

    def get_token(plan_id):
        return payments.x402.get_x402_access_token(plan_id)["accessToken"]

    def mcp_call(endpoint, plan_id, tool_name, arguments):
        token = get_token(plan_id)
        resp = httpx.post(endpoint,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {token}"},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": tool_name, "arguments": arguments},
                  "id": int(time.time() * 1000) % 99999},
            timeout=30)
        return resp.json()["result"]["content"][0]["text"]

### Step 3: Use it

    # Search the marketplace
    print(mcp_call("https://oracle.agenteconomy.io/mcp",
        PLANS["oracle"], "marketplace_search", {"query": "research"}))

    # Check a seller's reputation
    print(mcp_call("https://underwriter.agenteconomy.io/mcp",
        PLANS["underwriter"], "check_reputation", {"seller_name": "Cortex"}))

    # Submit a review after purchasing from someone
    print(mcp_call("https://underwriter.agenteconomy.io/mcp",
        PLANS["underwriter"], "submit_review", {
            "seller_name": "ServiceYouBoughtFrom",
            "team_name": "TheirTeamName",
            "quality_score": 4.5,
            "reliable": True,
            "notes": "Fast and accurate results",
            "reviewer": "YourTeamName"
        }))

    # Get your agent QA-certified
    print(mcp_call("https://goldstar.agenteconomy.io/mcp",
        PLANS["gold_star"], "request_review", {
            "seller_name": "YourService",
            "team_name": "YourTeam",
            "endpoint_url": "https://your-endpoint.com"
        }))

    # Run deep multi-agent research on any topic
    print(mcp_call("https://the-architect-production.up.railway.app/mcp",
        PLANS["architect"], "orchestrate", {"query": "AI agent marketplace trends"}))

    # Monetize your agent responses with contextual ads
    print(mcp_call("https://the-amplifier-production.up.railway.app/mcp",
        PLANS["amplifier"], "enrich_with_ads", {
            "content": "Here are the top research tools...",
            "ad_style": "inline"
        }))

---

## Connection Details

All MCP services accept connections at their /mcp path. All tools cost 0 credits
during the promotional period. Subscribe to a plan via the Nevermined SDK to get
an x402 access token, then pass it as a Bearer token in the Authorization header.

| Service         | MCP Endpoint                                   | Plan ID (last 8 digits) |
|-----------------|------------------------------------------------|------------------------|
| The Oracle      | https://oracle.agenteconomy.io/mcp             | ...307151 |
| The Underwriter | https://underwriter.agenteconomy.io/mcp        | ...689110 |
| The Gold Star   | https://goldstar.agenteconomy.io/mcp           | ...428594 |
| The Architect   | https://the-architect-production.up.railway.app/mcp | ...785367 |
| The Amplifier   | https://the-amplifier-production.up.railway.app/mcp | ...785367 |
| The Ledger      | https://agenteconomy.io (REST, no MCP)         | N/A |

## Contact
- Team: Full Stack Agents (B3 Labs)
- Hackathon: Nevermined Autonomous Business Hackathon (March 5-6, 2026)
- GitHub: https://github.com/moona3k/agenteconomy
"""


@app.get("/.well-known/agent.json")
def agent_json():
    """A2A-compatible agent card for service discovery."""
    return {
        "name": "Agent Economy Infrastructure",
        "description": (
            "Nine MCP services, a REST dashboard, and an autonomous buyer for the Nevermined agent marketplace. "
            "Discover services (Oracle), check trust (Underwriter), verify quality (Gold Star), "
            "audit services (Mystery Shopper), resolve disputes (Judge), analyze competitive moats "
            "(Doppelganger), transcribe audio (Transcriber), run multi-agent research (Architect), "
            "and monetize responses with ads (Amplifier). All MCP tools cost 0 credits during the promotional period."
        ),
        "url": "https://agenteconomy.io",
        "provider": {
            "organization": "Full Stack Agents",
            "url": "https://agenteconomy.io",
        },
        "version": "1.0.0",
        "capabilities": {
            "mcp": True,
            "rest_api": True,
            "streaming": False,
        },
        "services": [
            {
                "name": "The Oracle",
                "role": "Marketplace intelligence — discover, search, rank, and compare services.",
                "endpoint": "https://oracle.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "marketplace_data",
                        "description": "Full normalized marketplace snapshot with reachability, payment flags, and plan IDs.",
                        "parameters": {"side": "string, optional: 'all' (default), 'sell', or 'buy'"},
                    },
                    {
                        "name": "marketplace_search",
                        "description": "Keyword search across names, teams, categories, descriptions. Up to 10 results.",
                        "parameters": {"query": "string, required: keyword like 'web search', 'research', 'translation'"},
                    },
                    {
                        "name": "marketplace_leaderboard",
                        "description": "Ranked list scored by reachability, plan count, free tier, and crypto support.",
                        "parameters": {"category": "string, optional: filter like 'Research', 'Data Analytics'"},
                    },
                    {
                        "name": "marketplace_compare",
                        "description": "Side-by-side comparison with live HTTP health checks and latency measurement.",
                        "parameters": {
                            "service_a": "string, required: name or team of first service",
                            "service_b": "string, required: name or team of second service",
                        },
                    },
                ],
            },
            {
                "name": "The Underwriter",
                "role": "Trust and insurance — reputation scores, post-transaction reviews, failure claims.",
                "endpoint": "https://underwriter.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "check_reputation",
                        "description": "Trust score (0-100), badge, review history, and incident records for any seller.",
                        "parameters": {"seller_name": "string, required: service or team name"},
                    },
                    {
                        "name": "submit_review",
                        "description": "Rate a seller after a transaction. Updates trust score immediately.",
                        "parameters": {
                            "seller_name": "string, required",
                            "team_name": "string, required",
                            "quality_score": "float, required: 1.0-5.0",
                            "reliable": "bool, optional (default true)",
                            "notes": "string, optional",
                            "reviewer": "string, optional (default 'anonymous')",
                        },
                    },
                    {
                        "name": "file_claim",
                        "description": "Report a failed paid transaction. Creates permanent incident record, penalizes trust score.",
                        "parameters": {
                            "seller_name": "string, required",
                            "team_name": "string, required",
                            "reason": "string, required: 'timeout', 'error_500', 'garbage_response', 'auth_failure', 'empty_response', or custom",
                            "credits_lost": "int, optional (default 1)",
                            "buyer": "string, optional (default 'anonymous')",
                        },
                    },
                    {
                        "name": "reputation_leaderboard",
                        "description": "Hall of Fame (most trusted) and Shame Board (most incidents).",
                        "parameters": {},
                    },
                    {
                        "name": "underwriter_stats",
                        "description": "Aggregate stats: total reviews, incidents, claims, unique sellers rated.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Gold Star",
                "role": "Quality certification — AI-powered multi-phase QA testing.",
                "endpoint": "https://goldstar.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "request_review",
                        "description": "Submit a service for 5-phase QA: health, discovery, functional tests, robustness, AI evaluation. Returns star rating and dimension scores.",
                        "parameters": {
                            "seller_name": "string, required: your service name",
                            "team_name": "string, required: your team name",
                            "endpoint_url": "string, required: base URL of your service",
                        },
                    },
                    {
                        "name": "get_report",
                        "description": "Retrieve the latest QA report for any seller.",
                        "parameters": {"seller_name": "string, required"},
                    },
                    {
                        "name": "certification_status",
                        "description": "Check if a seller holds Gold Star certification (4.5+ stars, all dimensions >= 8). Omit seller_name for all certifications.",
                        "parameters": {"seller_name": "string, optional"},
                    },
                    {
                        "name": "gold_star_stats",
                        "description": "Aggregate stats: reviews conducted, sellers reviewed, certifications awarded.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Architect",
                "role": "Multi-agent research — 5-agent pipeline producing executive reports.",
                "endpoint": "https://architect.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "orchestrate",
                        "description": "Full 5-agent pipeline: Discovery, Research, Analysis, QA, Report. Returns structured executive report. Takes 15-45 seconds.",
                        "parameters": {"query": "string, required: research topic or question"},
                    },
                    {
                        "name": "quick_research",
                        "description": "Fast 2-agent pipeline (Research + Analysis). No marketplace grounding or QA review.",
                        "parameters": {"query": "string, required: topic or question"},
                    },
                    {
                        "name": "pipeline_status",
                        "description": "Operational health check. Returns status, agent list, requests served.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Amplifier",
                "role": "Contextual advertising — non-intrusive sponsored content for agent responses.",
                "endpoint": "https://amplifier.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "enrich_with_ads",
                        "description": "Append a contextual ad to your content. Original text returned unchanged, ad appended.",
                        "parameters": {
                            "content": "string, required: your response text",
                            "ad_style": "string, optional: 'inline' (default), 'compact', or 'json'",
                        },
                    },
                    {
                        "name": "get_ad",
                        "description": "Standalone ad for a topic. No surrounding content needed.",
                        "parameters": {
                            "topic": "string, required: e.g., 'AI research', 'crypto trading'",
                            "style": "string, optional: 'inline' (default), 'compact', or 'json'",
                        },
                    },
                    {
                        "name": "ad_stats",
                        "description": "Network stats: total impressions, unique sponsors, topic categories.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Mystery Shopper",
                "role": "Service auditor — end-to-end testing, scoring, and sweep audits of MCP services.",
                "endpoint": "https://shopper.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "shop_service",
                        "description": "End-to-end audit of a single service with weighted scoring across health, MCP, discovery, functional tests, and latency.",
                        "parameters": {
                            "service_name": "string, required: name of service to audit",
                            "endpoint_url": "string, required: base URL of the service",
                        },
                    },
                    {
                        "name": "run_sweep",
                        "description": "Audit all live MCP services in the marketplace. Auto-submits reviews to The Underwriter.",
                        "parameters": {},
                    },
                    {
                        "name": "get_latest_report",
                        "description": "Retrieve the most recent audit report for a service.",
                        "parameters": {"service_name": "string, required"},
                    },
                    {
                        "name": "shopper_stats",
                        "description": "Aggregate audit statistics: total audits, pass rates, average scores.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Judge",
                "role": "Dispute resolution — file disputes, submit responses, appeal verdicts, case history.",
                "endpoint": "https://judge.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "file_dispute",
                        "description": "Open a dispute case. Auto-gathers evidence from The Underwriter and The Gold Star.",
                        "parameters": {
                            "buyer": "string, required: your identifier",
                            "seller_name": "string, required: the service you're disputing",
                            "reason": "string, required: what went wrong",
                            "credits_at_stake": "int, optional (default 1)",
                            "evidence": "string, optional: logs, transaction IDs",
                        },
                    },
                    {
                        "name": "submit_response",
                        "description": "Seller responds to a dispute. Triggers verdict rendering.",
                        "parameters": {
                            "case_id": "string, required",
                            "response": "string, required: seller's defense",
                        },
                    },
                    {
                        "name": "appeal",
                        "description": "Appeal a verdict with new evidence. One appeal per case.",
                        "parameters": {
                            "case_id": "string, required",
                            "new_evidence": "string, required",
                        },
                    },
                    {
                        "name": "case_history",
                        "description": "View all disputes, optionally filtered by seller.",
                        "parameters": {"seller_name": "string, optional"},
                    },
                    {
                        "name": "judge_stats",
                        "description": "Aggregate dispute statistics: cases, verdicts, appeal rates.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Doppelganger",
                "role": "Competitive intelligence — moat analysis, vulnerability scanning, clone blueprints.",
                "endpoint": "https://doppelganger.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "analyze_service",
                        "description": "Deep moat analysis: score (0-10), vulnerability rating, defensibility signals, clone blueprint.",
                        "parameters": {
                            "service_name": "string, required: target service name",
                            "endpoint_url": "string, required: base URL",
                        },
                    },
                    {
                        "name": "find_vulnerable",
                        "description": "Scan marketplace for easily clonable services, ranked by vulnerability.",
                        "parameters": {"max_results": "int, optional (default 10)"},
                    },
                    {
                        "name": "moat_report",
                        "description": "Executive summary of marketplace defensibility: average moats, LLM wrapper percentage.",
                        "parameters": {},
                    },
                    {
                        "name": "doppelganger_stats",
                        "description": "Service usage statistics.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Transcriber",
                "role": "Local-model speech-to-text on Apple Silicon using NVIDIA Parakeet.",
                "endpoint": "https://transcriber.agenteconomy.io/mcp",
                "protocol": "mcp",
                "pricing": "FREE (0 credits, all tools)",
                "tools": [
                    {
                        "name": "transcribe_youtube",
                        "description": "YouTube URL to full text transcript with word count and timing.",
                        "parameters": {
                            "youtube_url": "string, required: full YouTube URL",
                        },
                    },
                    {
                        "name": "transcribe_file",
                        "description": "Transcribe a local audio or video file to text.",
                        "parameters": {
                            "file_path": "string, required: absolute path to audio/video file",
                        },
                    },
                    {
                        "name": "transcriber_info",
                        "description": "Capabilities, supported formats, and system status.",
                        "parameters": {},
                    },
                ],
            },
            {
                "name": "The Ledger",
                "role": "Human dashboard and REST API for marketplace data and analysis.",
                "endpoint": "https://agenteconomy.io",
                "protocol": "rest",
                "pricing": "Always free",
                "endpoints": [
                    {"path": "/api/sellers", "method": "GET", "description": "All seller agents from Nevermined discovery API"},
                    {"path": "/api/buyers", "method": "GET", "description": "All buyer agents"},
                    {"path": "/api/analysis", "method": "GET", "description": "Marketplace analysis: categories, pricing, teams, keywords"},
                    {"path": "/api/profile/{name}", "method": "GET", "description": "Detailed seller profile by name or team name"},
                    {"path": "/api/refresh", "method": "GET", "description": "Force cache refresh (bypasses 5-min TTL)"},
                ],
            },
        ],
        "documentation": "https://agenteconomy.io/llms.txt",
    }


# ─── REST API Endpoints ───


@app.get("/api/sellers")
def api_sellers():
    """Get all seller agents from the marketplace. Returns raw discovery API data."""
    return {"sellers": fetch_sellers()}


@app.get("/api/buyers")
def api_buyers():
    """Get all buyer agents from the marketplace. Returns raw discovery API data."""
    return {"buyers": fetch_buyers()}


@app.get("/api/analysis")
def api_analysis():
    """Get comprehensive marketplace analysis with categories, pricing, teams, keywords, and more."""
    return analyze_marketplace()


@app.get("/api/refresh")
def api_refresh():
    """Force refresh marketplace data (bypasses 5-min cache)."""
    sellers = fetch_sellers(force=True)
    buyers = fetch_buyers(force=True)
    analysis = analyze_marketplace()
    return {"refreshed": True, "sellers": len(sellers), "buyers": len(buyers)}


@app.get("/api/profile/{name}")
def api_profile(name: str):
    """Get detailed profile for a specific seller by name or team name."""
    profile = get_seller_profile(name)
    if not profile:
        return JSONResponse(
            status_code=404,
            content={
                "error": "seller_not_found",
                "message": f"No seller found matching '{name}'.",
                "hint": "Try a partial name match. Use /api/sellers to see all available sellers, or use The Oracle's marketplace_search tool for fuzzy keyword search.",
                "available_endpoints": ["/api/sellers", "/api/analysis", "/api/profile/{name}"],
            },
        )
    return profile


# ─── Agent-Friendly Error Handling ───


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Content-negotiated 404: HTML for browsers, JSON for agents."""
    accept = request.headers.get("accept", "")

    if "text/html" in accept:
        return HTMLResponse(
            status_code=404,
            content=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Not Found — Agent Economy</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
body {{ background: #05070e; color: #eef2ff; font-family: 'Inter', system-ui, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; -webkit-font-smoothing: antialiased; }}
.wrap {{ text-align: center; max-width: 540px; padding: 40px; }}
.code {{ font-family: 'JetBrains Mono', monospace; font-size: 72px; font-weight: 800; background: linear-gradient(135deg, #00d4ff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1; }}
h1 {{ font-size: 20px; font-weight: 800; margin: 16px 0 8px; }}
p {{ color: #94a3c0; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }}
.path {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #505d78; background: rgba(255,255,255,0.03); padding: 6px 14px; border-radius: 8px; display: inline-block; margin-bottom: 24px; border: 1px solid rgba(28,37,64,0.6); }}
.links {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
.links a {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: #94a3c0; background: rgba(255,255,255,0.03); border: 1px solid rgba(28,37,64,0.6); border-radius: 8px; padding: 8px 16px; text-decoration: none; transition: all 0.2s ease; }}
.links a:hover {{ border-color: #00d4ff; color: #00d4ff; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="code">404</div>
  <h1>Page Not Found</h1>
  <div class="path">{_esc(str(request.url.path))}</div>
  <p>This path doesn't exist on The Ledger. Here's where you might want to go:</p>
  <div class="links">
    <a href="/">Dashboard</a>
    <a href="/services">Services</a>
    <a href="/analysis">Analysis</a>
    <a href="/blog">Blog</a>
    <a href="/llms.txt">llms.txt</a>
    <a href="/api/sellers">API</a>
  </div>
</div>
</body>
</html>""",
        )

    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": f"The path '{request.url.path}' does not exist.",
            "hint": "This is The Ledger, the data gateway for the agent economy.",
            "available_endpoints": {
                "dashboard": "/",
                "services": "/services (human-friendly service directory)",
                "analysis": "/analysis (human-friendly marketplace analysis)",
                "llms_txt": "/llms.txt (plain text service description for LLMs)",
                "agent_card": "/.well-known/agent.json (A2A discovery)",
                "api_sellers": "/api/sellers (all seller agents)",
                "api_buyers": "/api/buyers (all buyer agents)",
                "api_analysis": "/api/analysis (marketplace analysis)",
                "api_refresh": "/api/refresh (force cache refresh)",
                "api_profile": "/api/profile/{name} (seller profile lookup)",
            },
            "mcp_services": {
                "oracle": "https://oracle.agenteconomy.io/mcp (marketplace intelligence, FREE)",
                "underwriter": "https://underwriter.agenteconomy.io/mcp (trust & insurance, FREE)",
                "gold_star": "https://goldstar.agenteconomy.io/mcp (quality certification, FREE)",
                "amplifier": "https://amplifier.agenteconomy.io/mcp (advertising, FREE)",
                "architect": "https://architect.agenteconomy.io/mcp (orchestration, FREE)",
                "mystery_shopper": "https://shopper.agenteconomy.io/mcp (service auditing, FREE)",
                "judge": "https://judge.agenteconomy.io/mcp (dispute resolution, FREE)",
                "doppelganger": "https://doppelganger.agenteconomy.io/mcp (competitive intelligence, FREE)",
                "transcriber": "https://transcriber.agenteconomy.io/mcp (speech-to-text, FREE)",
            },
        },
    )


# ─── The Fund — Live Investment Report ───


FUND_DATA_FILE = Path(__file__).parent.parent / "fund-data.json"


@app.post("/api/fund")
async def api_fund_upload(request: Request):
    """Receive live investment data from The Fund."""
    import json
    data = await request.json()
    FUND_DATA_FILE.write_text(json.dumps(data, indent=2, default=str))
    return {"status": "ok", "cycle": data.get("last_cycle")}


@app.get("/api/fund")
def api_fund():
    """The Fund's live investment data — thesis, transactions, provider performance."""
    if FUND_DATA_FILE.exists():
        import json
        return json.loads(FUND_DATA_FILE.read_text())
    return {"error": "No fund data available yet. The Fund may not be running."}


@app.get("/fund", response_class=HTMLResponse)
def fund_page():
    """The Fund — Intelligence-Driven Autonomous Buyer report page."""
    import json

    # Load live data if available
    data = {}
    if FUND_DATA_FILE.exists():
        data = json.loads(FUND_DATA_FILE.read_text())

    cycle = data.get("last_cycle", 0)
    txns = data.get("total_transactions", 0)
    providers_count = data.get("providers", 0)
    spent = data.get("spent", 0)
    frameworks = data.get("frameworks", [])
    providers = data.get("provider_summary", [])
    decisions = data.get("last_30_decisions", [])
    switches = data.get("switches", [])

    # Build provider rows
    provider_rows = ""
    for p in providers:
        success_pct = f'{p.get("success_rate", 0):.0%}'
        provider_rows += f"""
        <tr>
          <td style="font-weight:600">{_esc(p['name'])}</td>
          <td>{_esc(p.get('team', ''))}</td>
          <td style="text-align:center">{p.get('transactions', 0)}</td>
          <td style="text-align:center">{p.get('avg_quality', 0):.1f}</td>
          <td style="text-align:center">{p.get('avg_roi', 0):.0f}</td>
          <td style="text-align:center">{success_pct}</td>
          <td style="text-align:center">{p.get('total_spent', 0)}</td>
        </tr>"""

    # Build decision log
    decision_rows = ""
    for d in reversed(decisions[-20:]):
        dtype = d.get("type", "")
        msg = _esc(d.get("message", ""))
        color = {
            "THESIS": "#6366f1",
            "INTEL": "#0ea5e9",
            "ADVERSARIAL": "#f59e0b",
            "PURCHASE": "#10b981",
            "REVIEW": "#8b5cf6",
            "EXPLORE": "#ec4899",
            "SWITCH": "#ef4444",
            "STATUS": "#6b7280",
            "FEEDBACK": "#14b8a6",
        }.get(dtype, "#6b7280")
        decision_rows += f"""
        <div style="margin-bottom:6px;font-family:monospace;font-size:13px;line-height:1.5">
          <span style="color:{color};font-weight:700">[{dtype}]</span> {msg}
        </div>"""

    # Framework badges
    framework_badges = "".join(
        f'<span style="display:inline-block;background:#1e1b4b;color:#c7d2fe;padding:4px 12px;border-radius:20px;font-size:12px;margin:3px">{_esc(f)}</span>'
        for f in frameworks
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Fund -- Intelligence-Driven Autonomous Buyer</title>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f23; color: #e2e8f0; line-height: 1.6 }}
    .container {{ max-width: 960px; margin: 0 auto; padding: 40px 24px }}
    h1 {{ font-size: 2.2em; margin-bottom: 4px; color: #f8fafc }}
    .subtitle {{ color: #94a3b8; font-size: 1.1em; margin-bottom: 32px }}
    .thesis-box {{ background: #1e1b4b; border-left: 4px solid #6366f1; padding: 24px; border-radius: 8px; margin-bottom: 32px }}
    .thesis-box blockquote {{ font-size: 1.3em; font-style: italic; color: #c7d2fe; margin-bottom: 16px }}
    .thesis-box p {{ color: #a5b4fc; font-size: 0.95em }}
    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 32px }}
    .stat {{ background: #1a1a2e; border-radius: 8px; padding: 20px; text-align: center }}
    .stat .number {{ font-size: 2em; font-weight: 700; color: #6366f1 }}
    .stat .label {{ font-size: 0.85em; color: #94a3b8; margin-top: 4px }}
    h2 {{ font-size: 1.4em; color: #f8fafc; margin: 32px 0 16px; border-bottom: 1px solid #334155; padding-bottom: 8px }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9em }}
    th {{ text-align: left; padding: 10px 12px; background: #1a1a2e; color: #94a3b8; font-weight: 600; font-size: 0.8em; text-transform: uppercase }}
    td {{ padding: 10px 12px; border-bottom: 1px solid #1e293b }}
    tr:hover td {{ background: #1a1a2e }}
    .phase {{ background: #1a1a2e; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px }}
    .phase-title {{ font-weight: 700; color: #6366f1; margin-bottom: 4px }}
    .phase-desc {{ color: #94a3b8; font-size: 0.9em }}
    .decisions-log {{ background: #0a0a1a; border-radius: 8px; padding: 20px; max-height: 500px; overflow-y: auto }}
    .footer {{ text-align: center; color: #475569; margin-top: 48px; padding-top: 24px; border-top: 1px solid #1e293b; font-size: 0.85em }}
    a {{ color: #6366f1 }}
  </style>
</head>
<body>
  <div class="container">
    <h1>The Fund</h1>
    <div class="subtitle">Intelligence-Driven Autonomous Buyer &mdash; agenteconomy.io</div>

    <div class="thesis-box">
      <blockquote>"Markets are not given; they are made."</blockquote>
      <p>
        The Fund operates on a single conviction: the most valuable thing a buyer can do
        is not just consume services but build the information infrastructure that makes
        consumption rational. Every review is a brick in the epistemic foundation of the
        marketplace. Every adversarial test is a stress inoculation. Every reputation check
        is a contribution to the Hayekian price signal network.
      </p>
    </div>

    <div style="margin-bottom:24px">{framework_badges}</div>

    <div class="stats-grid">
      <div class="stat"><div class="number">{txns}</div><div class="label">Transactions</div></div>
      <div class="stat"><div class="number">{cycle}</div><div class="label">Cycles</div></div>
      <div class="stat"><div class="number">{providers_count}</div><div class="label">Providers</div></div>
      <div class="stat"><div class="number">{spent:.2f}</div><div class="label">USDC Spent</div></div>
      <div class="stat"><div class="number">{len(switches)}</div><div class="label">Provider Switches</div></div>
      <div class="stat"><div class="number">100%</div><div class="label">Success Rate</div></div>
    </div>

    <h2>Five-Phase Cycle</h2>
    <div class="phase">
      <div class="phase-title">1. Intelligence (Hayek, Kyle)</div>
      <div class="phase-desc">Query Oracle for marketplace rankings. Check Underwriter for trust profiles. Build the information base before spending.</div>
    </div>
    <div class="phase">
      <div class="phase-title">2. Informed Purchasing (Coase, Kyle)</div>
      <div class="phase-desc">Cross-compare services head-to-head. Buy with purpose informed by Phase 1 intelligence, not randomly.</div>
    </div>
    <div class="phase">
      <div class="phase-title">3. Adversarial Testing (Taleb)</div>
      <div class="phase-desc">Send edge cases: SQL injection, XSS, empty strings, unicode floods. Services that survive become antifragile.</div>
    </div>
    <div class="phase">
      <div class="phase-title">4. External Exploration (Akerlof)</div>
      <div class="phase-desc">Use Oracle intelligence to find and evaluate external sellers. Check reputation before buying. Honest reviews prevent lemons.</div>
    </div>
    <div class="phase">
      <div class="phase-title">5. Feedback Loop (Soros, Ostrom)</div>
      <div class="phase-desc">Submit reviews that change the reputation data we read next cycle. The reflexive loop is the engine of quality improvement.</div>
    </div>

    <h2>Provider Performance</h2>
    <table>
      <thead><tr><th>Provider</th><th>Team</th><th>Txns</th><th>Quality</th><th>ROI</th><th>Success</th><th>Credits</th></tr></thead>
      <tbody>{provider_rows}</tbody>
    </table>

    <h2>Live Decision Log</h2>
    <div class="decisions-log">{decision_rows or '<div style="color:#475569">Waiting for first cycle...</div>'}</div>

    <div class="footer">
      <p>The Fund does not merely observe the agent economy &mdash; it constitutes it.</p>
      <p style="margin-top:8px"><a href="/">The Ledger</a> &middot; <a href="/api/fund">Raw JSON</a> &middot; <a href="/llms.txt">llms.txt</a></p>
    </div>
  </div>
</body>
</html>"""


# ─── Infrastructure Endpoints ───


@app.get("/health")
def health():
    """Health check — consistent with MCP services."""
    return {
        "status": "ok",
        "service": "the-ledger",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return """User-agent: *
Allow: /
Allow: /analysis
Allow: /services
Allow: /blog
Allow: /sponsors
Allow: /llms.txt
Disallow: /api/

Sitemap: https://agenteconomy.io/sitemap.xml
"""


@app.get("/sitemap.xml", response_class=PlainTextResponse)
def sitemap_xml():
    from .blog import get_all_posts

    urls = [
        ("https://agenteconomy.io/", "daily", "1.0"),
        ("https://agenteconomy.io/analysis", "hourly", "0.9"),
        ("https://agenteconomy.io/services", "daily", "0.9"),
        ("https://agenteconomy.io/blog", "weekly", "0.7"),
        ("https://agenteconomy.io/sponsors", "weekly", "0.7"),
        ("https://agenteconomy.io/llms.txt", "weekly", "0.8"),
        ("https://agenteconomy.io/.well-known/agent.json", "weekly", "0.6"),
    ]
    for post in get_all_posts():
        urls.append((f"https://agenteconomy.io/blog/{post['slug']}", "weekly", "0.6"))

    entries = "\n".join(
        f"  <url><loc>{u}</loc><changefreq>{f}</changefreq><priority>{p}</priority></url>"
        for u, f, p in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>"""


# ─── Dashboard Tab Redirects ───


@app.get("/sellers")
def sellers_redirect():
    """Redirect to the dashboard Sellers tab."""
    return RedirectResponse(url="/#sellers", status_code=302)


@app.get("/buyers")
def buyers_redirect():
    """Redirect to the dashboard Buyers tab."""
    return RedirectResponse(url="/#buyers", status_code=302)


# ─── Services Directory (Human-Friendly) ───


_MCP_SERVICES = [
    {
        "slug": "oracle",
        "name": "The Oracle",
        "tagline": "Marketplace Intelligence",
        "desc": "Indexes all agents in the Nevermined marketplace. Normalized data, keyword search, quality-ranked leaderboards, and side-by-side comparisons with live health checks.",
        "url": "https://oracle.agenteconomy.io",
        "mcp": "https://oracle.agenteconomy.io/mcp",
        "color": "#00e5a0",
        "icon": "O",
        "tools": [
            ("marketplace_data", "Full normalized marketplace snapshot with reachability and plan IDs"),
            ("marketplace_search", "Keyword search across names, teams, categories, descriptions"),
            ("marketplace_leaderboard", "Quality-ranked list scored by reachability and pricing"),
            ("marketplace_compare", "Side-by-side comparison with live HTTP health checks"),
        ],
    },
    {
        "slug": "underwriter",
        "name": "The Underwriter",
        "tagline": "Trust & Insurance",
        "desc": "Trust scores, post-transaction reviews, and insurance claims. The consumer protection bureau for AI agents.",
        "url": "https://underwriter.agenteconomy.io",
        "mcp": "https://underwriter.agenteconomy.io/mcp",
        "color": "#ff3b6e",
        "icon": "U",
        "tools": [
            ("check_reputation", "Trust score (0-100), badge, review history for any seller"),
            ("submit_review", "Rate a seller after a transaction — updates trust score immediately"),
            ("file_claim", "Report a failed paid transaction — creates permanent incident record"),
            ("reputation_leaderboard", "Hall of Fame and Shame Board"),
            ("underwriter_stats", "Aggregate system statistics"),
        ],
    },
    {
        "slug": "gold-star",
        "name": "The Gold Star",
        "tagline": "Michelin Stars for AI",
        "desc": "AI-powered QA and certification. Claude Sonnet evaluates services across 5 dimensions. Earn Gold Star certification at 4.5+ stars.",
        "url": "https://goldstar.agenteconomy.io",
        "mcp": "https://goldstar.agenteconomy.io/mcp",
        "color": "#fbbf24",
        "icon": "G",
        "tools": [
            ("request_review", "Submit for 5-phase QA: health, discovery, functional tests, robustness, AI evaluation"),
            ("get_report", "Retrieve the latest QA report for any seller"),
            ("certification_status", "Check Gold Star certification (4.5+ stars)"),
            ("gold_star_stats", "Aggregate QA statistics"),
        ],
    },
    {
        "slug": "architect",
        "name": "The Architect",
        "tagline": "5-Agent Orchestration",
        "desc": "CEO agent delegates to 5 specialists powered by Claude Opus. Produces executive research reports with built-in quality assurance.",
        "url": "https://architect.agenteconomy.io",
        "mcp": "https://architect.agenteconomy.io/mcp",
        "color": "#a78bfa",
        "icon": "R",
        "tools": [
            ("orchestrate", "Full 5-agent pipeline: Discovery, Research, Analysis, QA, Report"),
            ("quick_research", "Fast 2-agent pipeline (Research + Analysis)"),
            ("pipeline_status", "Operational health check"),
        ],
    },
    {
        "slug": "amplifier",
        "name": "The Amplifier",
        "tagline": "AI-Native Advertising",
        "desc": "First ad network for agent-to-agent commerce. Contextual sponsored recommendations that blend naturally into agent responses.",
        "url": "https://amplifier.agenteconomy.io",
        "mcp": "https://amplifier.agenteconomy.io/mcp",
        "color": "#fb923c",
        "icon": "A",
        "tools": [
            ("enrich_with_ads", "Append a contextual sponsored ad to any text content"),
            ("get_ad", "Standalone contextual ad for a topic"),
            ("ad_stats", "Ad network statistics"),
        ],
    },
    {
        "slug": "ledger",
        "name": "The Ledger",
        "tagline": "The Human Window",
        "desc": "Real-time dashboard, REST API, llms.txt, and A2A agent card. The data gateway for the entire agent economy.",
        "url": "https://agenteconomy.io",
        "mcp": None,
        "color": "#00d4ff",
        "icon": "L",
        "tools": [
            ("/api/sellers", "All seller agents from the marketplace"),
            ("/api/buyers", "All buyer agents"),
            ("/api/analysis", "Marketplace analysis with categories, pricing, teams"),
            ("/api/profile/{name}", "Detailed seller profile lookup"),
            ("/llms.txt", "Plain text service manifest for LLMs"),
        ],
    },
    {
        "slug": "mystery-shopper",
        "name": "The Mystery Shopper",
        "tagline": "Service Auditor",
        "desc": "End-to-end service auditing. Actually calls MCP tools, measures latency, and scores services on a weighted rubric. Auto-submits reviews to The Underwriter.",
        "url": "https://shopper.agenteconomy.io",
        "mcp": "https://shopper.agenteconomy.io/mcp",
        "color": "#06b6d4",
        "icon": "M",
        "tools": [
            ("shop_service", "End-to-end audit with weighted scoring across 5 dimensions"),
            ("run_sweep", "Audit all live MCP services in the marketplace"),
            ("get_latest_report", "Retrieve most recent audit report for a service"),
            ("shopper_stats", "Aggregate audit statistics"),
        ],
    },
    {
        "slug": "judge",
        "name": "The Judge",
        "tagline": "Dispute Resolution",
        "desc": "Rules-based dispute resolution. Cross-references The Underwriter and The Gold Star for evidence. Renders verdicts, accepts appeals, tracks case history.",
        "url": "https://judge.agenteconomy.io",
        "mcp": "https://judge.agenteconomy.io/mcp",
        "color": "#dc2626",
        "icon": "J",
        "tools": [
            ("file_dispute", "Open a dispute case with auto-gathered evidence"),
            ("submit_response", "Seller responds to a dispute"),
            ("appeal", "Appeal a verdict with new evidence"),
            ("case_history", "View all disputes, optionally filtered by seller"),
            ("judge_stats", "Aggregate dispute statistics"),
        ],
    },
    {
        "slug": "doppelganger",
        "name": "The Doppelganger",
        "tagline": "Competitive Intelligence",
        "desc": "Moat analysis for the agent economy. Discovers what's defensible, what's an LLM wrapper, and what could be cloned in a weekend. Proves that wrappers have no moat.",
        "url": "https://doppelganger.agenteconomy.io",
        "mcp": "https://doppelganger.agenteconomy.io/mcp",
        "color": "#8b5cf6",
        "icon": "D",
        "tools": [
            ("analyze_service", "Deep moat analysis with vulnerability rating and clone blueprint"),
            ("find_vulnerable", "Scan marketplace for easily clonable services"),
            ("moat_report", "Executive summary of marketplace defensibility"),
            ("doppelganger_stats", "Service usage statistics"),
        ],
    },
    {
        "slug": "transcriber",
        "name": "The Transcriber",
        "tagline": "Local-Model Speech-to-Text",
        "desc": "NVIDIA Parakeet on Apple Silicon. Real local compute, not an API wrapper. Transcribe YouTube videos and audio files to text.",
        "url": "https://transcriber.agenteconomy.io",
        "mcp": "https://transcriber.agenteconomy.io/mcp",
        "color": "#22d3ee",
        "icon": "T",
        "tools": [
            ("transcribe_youtube", "YouTube URL to full text transcript"),
            ("transcribe_file", "Audio/video file to text transcript"),
            ("transcriber_info", "Capabilities, supported formats, and system status"),
        ],
    },
    {
        "slug": "fund",
        "name": "The Fund",
        "tagline": "Autonomous Capital Allocator",
        "desc": "Autonomous buyer with ROI tracking, provider switching, and budget enforcement. Discovers, evaluates, and purchases from the marketplace.",
        "url": None,
        "mcp": None,
        "color": "#14b8a6",
        "icon": "F",
        "tools": [
            ("ROI Tracking", "Measures return on investment for each purchase"),
            ("Provider Switching", "Automatically switches to better providers"),
            ("Budget Enforcement", "Hard limits on autonomous spending"),
        ],
    },
]


@app.get("/services", response_class=HTMLResponse)
async def services_page():
    """Human-friendly directory of all services with MCP connection instructions."""
    import httpx

    # Check health of all services in parallel
    health_results = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for svc in _MCP_SERVICES:
            if svc["url"] and svc["slug"] != "ledger" and svc["slug"] != "fund":
                try:
                    r = await client.get(svc["url"] + "/health")
                    health_results[svc["slug"]] = "online" if r.status_code == 200 else "degraded"
                except Exception:
                    health_results[svc["slug"]] = "offline"
            elif svc["slug"] == "ledger":
                health_results["ledger"] = "online"
            else:
                health_results[svc["slug"]] = "local"

    cards_html = ""
    for svc in _MCP_SERVICES:
        status = health_results.get(svc["slug"], "unknown")
        status_dot = {"online": "#00e5a0", "degraded": "#fbbf24", "offline": "#ff3b6e", "local": "#505d78"}.get(status, "#505d78")
        status_label = {"online": "Operational", "degraded": "Degraded", "offline": "Unreachable", "local": "Local Script"}.get(status, "Unknown")

        tools_html = ""
        for tname, tdesc in svc["tools"]:
            tools_html += f'<div class="s-tool"><code>{_esc(tname)}</code><span>{_esc(tdesc)}</span></div>'

        mcp_block = ""
        if svc["mcp"]:
            mcp_block = f'''<div class="s-connect">
                <div class="s-connect-title">Connect via MCP</div>
                <pre class="s-code">{{"mcpServers": {{
  "{_esc(svc["slug"])}": {{
    "url": "{_esc(svc["mcp"])}"
  }}
}}}}</pre>
                <div class="s-connect-hint">Add to Claude Desktop config or Claude Code settings</div>
            </div>'''
        elif svc["slug"] == "ledger":
            mcp_block = '''<div class="s-connect">
                <div class="s-connect-title">REST API</div>
                <pre class="s-code">curl https://agenteconomy.io/api/analysis</pre>
                <div class="s-connect-hint">No authentication required. JSON responses.</div>
            </div>'''

        links_html = ""
        if svc["url"]:
            links_html += f'<a href="{svc["url"]}/health" class="s-link" target="_blank">Health</a>'
            if svc["mcp"]:
                links_html += f'<a href="{svc["url"]}/llms.txt" class="s-link" target="_blank">llms.txt</a>'

        cards_html += f'''<div class="s-card" style="--svc-color:{svc["color"]}">
            <div class="s-header">
                <div class="s-icon" style="background:linear-gradient(135deg, {svc["color"]}, {svc["color"]}cc)">{svc["icon"]}</div>
                <div class="s-meta">
                    <h2>{_esc(svc["name"])}</h2>
                    <div class="s-tagline">{_esc(svc["tagline"])}</div>
                </div>
                <div class="s-status" style="color:{status_dot}">
                    <span class="s-dot" style="background:{status_dot};box-shadow:0 0 8px {status_dot}"></span>
                    {status_label}
                </div>
            </div>
            <p class="s-desc">{_esc(svc["desc"])}</p>
            <div class="s-tools-title">{"Tools" if svc["mcp"] else "Endpoints"} <span class="s-free">FREE</span></div>
            <div class="s-tools">{tools_html}</div>
            {mcp_block}
            <div class="s-links">{links_html}</div>
        </div>'''

    return _SERVICES_TEMPLATE.replace("{{cards}}", cards_html)


_SERVICES_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Services — Agent Economy</title>
<meta name="description" content="10 autonomous services powering the Nevermined AI agent marketplace. MCP connection instructions, live health status, and tool documentation.">
<!-- AI Agent Discovery -->
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM-friendly documentation for AI agents">
<link rel="alternate" type="application/json" href="/.well-known/agent.json" title="A2A agent card with all services and tools">
<link rel="alternate" type="application/json" href="/api/analysis" title="Machine-readable marketplace analysis">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #05070e; --bg2: #0a0f1a; --card: rgba(14,19,32,0.7);
  --border: rgba(28,37,64,0.6); --border-light: rgba(42,53,85,0.7);
  --text: #eef2ff; --text2: #94a3c0; --muted: #505d78;
  --cyan: #00d4ff; --emerald: #00e5a0; --violet: #a78bfa;
  --mono: 'JetBrains Mono', 'SF Mono', monospace;
  --sans: 'Inter', -apple-system, system-ui, sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: var(--sans); -webkit-font-smoothing: antialiased; line-height: 1.6; }
.page { max-width: 1100px; margin: 0 auto; padding: 48px 40px 80px; }
@media (max-width: 768px) { .page { padding: 24px 20px 60px; } }

.breadcrumb { font-size: 12px; color: var(--muted); margin-bottom: 16px; font-family: var(--mono); font-weight: 500; }
.breadcrumb a { color: var(--cyan); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }

.page-header { margin-bottom: 48px; padding-bottom: 32px; border-bottom: 1px solid var(--border); position: relative; }
.page-header::after { content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, var(--cyan), var(--violet), transparent); opacity: 0.3; }
.page-header h1 { font-size: 36px; font-weight: 900; letter-spacing: -1px; margin-bottom: 8px; }
.page-header h1 .gradient { background: linear-gradient(135deg, var(--cyan), var(--violet)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-header p { color: var(--text2); font-size: 16px; max-width: 640px; }
.page-header .connect-all { margin-top: 20px; display: flex; gap: 12px; flex-wrap: wrap; }
.page-header .connect-all a { font-family: var(--mono); font-size: 12px; font-weight: 600; color: var(--text2); background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 8px; padding: 8px 16px; text-decoration: none; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; }
.page-header .connect-all a:hover { border-color: var(--cyan); color: var(--cyan); transform: translateY(-1px); }
.page-header .connect-all .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--emerald); box-shadow: 0 0 6px var(--emerald); }

/* Service cards */
.s-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 32px; margin-bottom: 24px; transition: border-color 0.3s ease; position: relative; overflow: hidden; }
.s-card:hover { border-color: var(--border-light); }
.s-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--svc-color), transparent); opacity: 0.4; }

.s-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.s-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; font-family: var(--mono); color: #fff; flex-shrink: 0; }
.s-meta { flex: 1; min-width: 200px; }
.s-meta h2 { font-size: 20px; font-weight: 800; letter-spacing: -0.3px; }
.s-tagline { font-size: 13px; color: var(--muted); font-weight: 500; }
.s-status { display: flex; align-items: center; gap: 8px; font-size: 12px; font-family: var(--mono); font-weight: 600; flex-shrink: 0; }
.s-dot { width: 7px; height: 7px; border-radius: 50%; }
.s-desc { color: var(--text2); font-size: 14px; margin-bottom: 20px; max-width: 700px; }

.s-tools-title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: var(--muted); margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
.s-free { font-size: 9px; padding: 2px 8px; border-radius: 10px; background: rgba(0,229,160,0.1); color: var(--emerald); border: 1px solid rgba(0,229,160,0.15); letter-spacing: 1px; }

.s-tools { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }
.s-tool { display: flex; gap: 12px; align-items: baseline; padding: 8px 12px; border-radius: 8px; background: rgba(255,255,255,0.015); transition: background 0.2s ease; }
.s-tool:hover { background: rgba(255,255,255,0.03); }
.s-tool code { font-family: var(--mono); font-size: 12px; font-weight: 600; color: var(--cyan); white-space: nowrap; flex-shrink: 0; }
.s-tool span { font-size: 12px; color: var(--text2); }

.s-connect { margin-bottom: 16px; padding: 20px; border-radius: 10px; background: rgba(0,212,255,0.03); border: 1px solid rgba(0,212,255,0.08); }
.s-connect-title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: var(--cyan); margin-bottom: 10px; }
.s-code { font-family: var(--mono); font-size: 12px; color: var(--text2); background: rgba(0,0,0,0.3); border-radius: 8px; padding: 14px 16px; overflow-x: auto; white-space: pre; line-height: 1.5; border: 1px solid rgba(255,255,255,0.03); }
.s-connect-hint { font-size: 11px; color: var(--muted); margin-top: 8px; font-weight: 500; }

.s-links { display: flex; gap: 12px; }
.s-link { font-family: var(--mono); font-size: 11px; color: var(--muted); text-decoration: none; transition: color 0.2s ease; font-weight: 500; }
.s-link:hover { color: var(--cyan); }

/* All-in-one config */
.all-config { margin-bottom: 48px; }
.all-config h2 { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2.5px; color: var(--text2); margin-bottom: 16px; }
.all-config pre { font-family: var(--mono); font-size: 12px; color: var(--text2); background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 24px; overflow-x: auto; white-space: pre; line-height: 1.6; }

/* Footer */
.page-footer { margin-top: 60px; padding-top: 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--muted); flex-wrap: wrap; gap: 12px; }
.page-footer a { color: var(--cyan); text-decoration: none; }
.page-footer a:hover { text-decoration: underline; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }
</style>
</head>
<body>
<div class="page">

<header class="page-header">
  <div class="breadcrumb"><a href="/">Agent Economy</a> / Services</div>
  <h1><span class="gradient">Services</span> Directory</h1>
  <p>11 autonomous services powering trust, intelligence, quality, auditing, dispute resolution, competitive analysis, transcription, and commerce across the agent economy. All MCP tools are free during the promotional period.</p>
  <div class="connect-all">
    <a href="#all-config"><span class="dot"></span>Connect All Services</a>
    <a href="/llms.txt">llms.txt</a>
    <a href="/.well-known/agent.json">agent.json</a>
    <a href="/analysis">Analysis</a>
  </div>
</header>

<!-- All-in-one MCP config -->
<div class="all-config" id="all-config">
  <h2>Connect All MCP Services at Once</h2>
  <pre>{
  "mcpServers": {
    "oracle": {
      "url": "https://oracle.agenteconomy.io/mcp"
    },
    "underwriter": {
      "url": "https://underwriter.agenteconomy.io/mcp"
    },
    "gold-star": {
      "url": "https://goldstar.agenteconomy.io/mcp"
    },
    "architect": {
      "url": "https://architect.agenteconomy.io/mcp"
    },
    "amplifier": {
      "url": "https://amplifier.agenteconomy.io/mcp"
    },
    "mystery-shopper": {
      "url": "https://shopper.agenteconomy.io/mcp"
    },
    "judge": {
      "url": "https://judge.agenteconomy.io/mcp"
    },
    "doppelganger": {
      "url": "https://doppelganger.agenteconomy.io/mcp"
    },
    "transcriber": {
      "url": "https://transcriber.agenteconomy.io/mcp"
    }
  }
}</pre>
</div>

<!-- Service Cards -->
{{cards}}

<footer class="page-footer">
  <span><a href="/">Dashboard</a> &middot; <a href="/analysis">Analysis</a> &middot; <a href="/blog">Blog</a> &middot; <a href="/api/analysis">JSON API</a></span>
  <span>Agent Economy &middot; Powered by <a href="https://nevermined.app">Nevermined</a></span>
</footer>

</div>
</body>
</html>"""


# ─── Human-Friendly Analysis Page ───


@app.get("/analysis", response_class=HTMLResponse)
def analysis_page():
    """Beautiful human-readable view of marketplace analysis data."""
    data = analyze_marketplace()
    s = data["summary"]
    cats = data["categories"]
    pt = data["payment_types"]
    teams = data["teams"]
    power = data["power_teams"]
    keywords = data["top_keywords"]
    pricing = data["pricing_landscape"]
    timeline = data["timeline"]
    protocols = data.get("protocols", {})
    buyer_interests = data.get("buyer_interests", [])

    # Build category rows
    sorted_cats = sorted(cats.items(), key=lambda x: -x[1]["count"])
    max_cat = sorted_cats[0][1]["count"] if sorted_cats else 1
    cat_rows = ""
    for cat, info in sorted_cats:
        pct = int(info["count"] / max_cat * 100)
        cat_rows += f'''<div class="a-bar-row">
            <span class="a-bar-label">{_esc(cat)}</span>
            <div class="a-bar-track"><div class="a-bar-fill" style="width:{max(pct,6)}%"><span>{info["count"]}</span></div></div>
        </div>'''

    # Power teams
    power_rows = ""
    for i, t in enumerate(power[:10]):
        rank_class = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        power_rows += f'''<tr class="{rank_class}">
            <td class="rank">#{i+1}</td>
            <td class="team-name">{_esc(t["team"])}</td>
            <td class="num">{t["services_selling"]}</td>
            <td class="num">{t["services_buying"]}</td>
            <td class="num">{t["services_selling"] + t["services_buying"]}</td>
        </tr>'''

    # Top keywords
    max_kw = keywords[0][1] if keywords else 1
    kw_html = ""
    for word, count in keywords:
        size = max(13, min(28, 12 + int(count / max_kw * 18)))
        opacity = max(0.4, count / max_kw)
        kw_html += f'<span style="font-size:{size}px;opacity:{opacity}">{_esc(word)}</span>'

    # Pricing table
    cheapest_rows = ""
    for p in pricing.get("cheapest", []):
        cheapest_rows += f'<tr><td>{_esc(p["service"])}</td><td class="muted">{_esc(p["team"])}</td><td class="num accent-emerald">{_esc(p["formatted"])}</td></tr>'
    expensive_rows = ""
    for p in pricing.get("most_expensive", []):
        expensive_rows += f'<tr><td>{_esc(p["service"])}</td><td class="muted">{_esc(p["team"])}</td><td class="num accent-amber">{_esc(p["formatted"])}</td></tr>'

    # Protocols
    proto_badges = "".join(f'<span class="a-badge">{_esc(k)}: {v}</span>' for k, v in protocols.items())

    # Timeline
    tl_html = ""
    if timeline.get("earliest"):
        tl_html = f'''<div class="a-stat-row">
            <div class="a-stat"><div class="a-stat-val">{timeline["total_registered"]}</div><div class="a-stat-lbl">Registered</div></div>
            <div class="a-stat"><div class="a-stat-val" style="font-size:16px">{timeline["earliest"][:10]}</div><div class="a-stat-lbl">First</div></div>
            <div class="a-stat"><div class="a-stat-val" style="font-size:16px">{timeline["latest"][:10]}</div><div class="a-stat-lbl">Latest</div></div>
        </div>'''

    # Buyer interests
    bi_html = ""
    for interest, count in buyer_interests[:10]:
        bi_html += f'<div class="a-interest"><span>{_esc(interest)}</span><span class="a-interest-count">{count}</span></div>'

    # Uptime & health
    uptime = round(s["reachable_endpoints"] / max(s["total_sellers"], 1) * 100)
    sell_buy_ratio = round(s["total_sellers"] / max(s["total_buyers"], 1), 1)
    participation = round(s["teams_both"] / max(s["unique_teams_selling"], 1) * 100)

    ratio_color = "var(--amber)" if sell_buy_ratio > 3 else "var(--emerald)"
    uptime_color = "var(--emerald)" if uptime > 70 else "var(--amber)"

    return _ANALYSIS_TEMPLATE.format(
        total_sellers=s["total_sellers"],
        total_buyers=s["total_buyers"],
        unique_teams=s["unique_teams_selling"],
        live_endpoints=s["reachable_endpoints"],
        localhost=s["localhost_endpoints"],
        categories_count=s["categories"],
        teams_both=s["teams_both"],
        uptime=uptime,
        sell_buy_ratio=sell_buy_ratio,
        participation=participation,
        crypto=pt["crypto"],
        fiat=pt["fiat"],
        free=pt["free"],
        cat_rows=cat_rows,
        power_rows=power_rows,
        kw_html=kw_html,
        cheapest_rows=cheapest_rows,
        expensive_rows=expensive_rows,
        median_price=f'{pricing["median_price"]:.2f}' if pricing.get("median_price") else "N/A",
        total_priced=pricing.get("total_priced", 0),
        proto_badges=proto_badges,
        tl_html=tl_html,
        bi_html=bi_html,
        ratio_color=ratio_color,
        uptime_color=uptime_color,
    )


def _esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


_ANALYSIS_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Marketplace Analysis — Agent Economy</title>
<meta name="description" content="Live marketplace analysis: {total_sellers} sellers, {total_buyers} buyers, {unique_teams} teams across the Nevermined AI agent economy.">
<!-- AI Agent Discovery -->
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM-friendly documentation for AI agents">
<link rel="alternate" type="application/json" href="/.well-known/agent.json" title="A2A agent card with all services and tools">
<link rel="alternate" type="application/json" href="/api/analysis" title="Machine-readable marketplace analysis">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect rx='20' width='100' height='100' fill='%230a0f1a'/><text x='50' y='68' text-anchor='middle' font-size='52' font-weight='800' font-family='system-ui' fill='%2300d4ff'>AE</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #05070e;
  --bg2: #0a0f1a;
  --card: rgba(14, 19, 32, 0.7);
  --border: rgba(28, 37, 64, 0.6);
  --border-light: rgba(42, 53, 85, 0.7);
  --text: #eef2ff;
  --text2: #94a3c0;
  --muted: #505d78;
  --cyan: #00d4ff;
  --emerald: #00e5a0;
  --violet: #a78bfa;
  --amber: #fbbf24;
  --rose: #ff3b6e;
  --blue: #3b82f6;
  --mono: 'JetBrains Mono', 'SF Mono', monospace;
  --sans: 'Inter', -apple-system, system-ui, sans-serif;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
  line-height: 1.6;
}}

.page {{ max-width: 1100px; margin: 0 auto; padding: 48px 40px 80px; }}

@media (max-width: 768px) {{ .page {{ padding: 24px 20px 60px; }} }}

/* Header */
.page-header {{
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border);
  position: relative;
}}

.page-header::after {{
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--violet), transparent);
  opacity: 0.3;
}}

.breadcrumb {{
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 16px;
  font-family: var(--mono);
  font-weight: 500;
}}

.breadcrumb a {{ color: var(--cyan); text-decoration: none; }}
.breadcrumb a:hover {{ text-decoration: underline; }}

.page-header h1 {{
  font-size: 36px;
  font-weight: 900;
  letter-spacing: -1px;
  margin-bottom: 8px;
}}

.page-header h1 .gradient {{
  background: linear-gradient(135deg, var(--cyan), var(--violet));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.page-header p {{
  color: var(--text2);
  font-size: 16px;
  max-width: 640px;
}}

.page-header .meta {{
  display: flex;
  gap: 24px;
  margin-top: 16px;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
  font-weight: 500;
}}

.page-header .meta .live {{
  color: var(--emerald);
  display: flex;
  align-items: center;
  gap: 6px;
}}

.page-header .meta .live::before {{
  content: '';
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--emerald);
  box-shadow: 0 0 8px var(--emerald);
}}

/* Sacred geometry divider */
.sacred-div {{
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
  opacity: 0.15;
}}

/* Stats Grid */
.stats-grid {{
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}}

@media (max-width: 900px) {{ .stats-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (max-width: 500px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

.a-stat {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  text-align: center;
  transition: border-color 0.3s ease, transform 0.3s ease;
}}

.a-stat:hover {{
  border-color: var(--border-light);
  transform: translateY(-2px);
}}

.a-stat-val {{
  font-family: var(--mono);
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1px;
}}

.a-stat-lbl {{
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 8px;
  font-weight: 700;
}}

/* Sections */
.section {{
  margin-bottom: 40px;
}}

.section-title {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  color: var(--text2);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}}

.grid-2 {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}}

@media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px;
  transition: border-color 0.3s ease;
}}

.card:hover {{ border-color: var(--border-light); }}

.card h3 {{
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--muted);
  margin-bottom: 20px;
}}

/* Bar chart */
.a-bar-row {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}}

.a-bar-label {{
  flex: 0 0 140px;
  font-size: 12px;
  color: var(--text2);
  text-align: right;
  font-family: var(--mono);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

@media (max-width: 768px) {{ .a-bar-label {{ flex: 0 0 90px; font-size: 10px; }} }}

.a-bar-track {{
  flex: 1;
  height: 32px;
  background: rgba(255,255,255,0.015);
  border-radius: 8px;
  overflow: hidden;
}}

.a-bar-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--blue));
  border-radius: 7px;
  display: flex;
  align-items: center;
  padding-left: 12px;
  min-width: fit-content;
}}

.a-bar-fill span {{
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  color: #fff;
}}

/* Tables */
.a-table {{
  width: 100%;
  border-collapse: collapse;
}}

.a-table th {{
  text-align: left;
  padding: 10px 14px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--muted);
  border-bottom: 1px solid var(--border);
}}

.a-table td {{
  padding: 12px 14px;
  font-size: 13px;
  border-bottom: 1px solid rgba(28,37,64,0.3);
  color: var(--text2);
}}

.a-table .rank {{
  font-family: var(--mono);
  font-weight: 800;
  color: var(--muted);
  width: 50px;
}}

.a-table .team-name {{ font-weight: 700; color: var(--text); }}
.a-table .num {{ font-family: var(--mono); font-weight: 600; text-align: center; }}
.a-table .muted {{ color: var(--muted); font-size: 12px; }}
.a-table .accent-emerald {{ color: var(--emerald); }}
.a-table .accent-amber {{ color: var(--amber); }}

.a-table tr.gold .rank {{ color: var(--amber); text-shadow: 0 0 12px rgba(251,191,36,0.3); }}
.a-table tr.silver .rank {{ color: var(--text2); }}
.a-table tr.bronze .rank {{ color: #fb923c; }}

/* Payment cards */
.pay-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}}

@media (max-width: 500px) {{ .pay-grid {{ grid-template-columns: 1fr; }} }}

.pay-card {{
  background: rgba(255,255,255,0.02);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}}

.pay-card .val {{
  font-family: var(--mono);
  font-size: 40px;
  font-weight: 800;
  line-height: 1;
}}

.pay-card .lbl {{
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 8px;
  font-weight: 600;
}}

/* Keywords */
.kw-cloud {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}}

.kw-cloud span {{
  font-family: var(--mono);
  color: var(--cyan);
  padding: 4px 10px;
  font-weight: 600;
  cursor: default;
  transition: transform 0.2s ease;
}}

.kw-cloud span:hover {{ transform: scale(1.1); opacity: 1 !important; }}

/* Badges */
.a-badge {{
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-family: var(--mono);
  font-weight: 600;
  background: rgba(59, 130, 246, 0.08);
  color: var(--blue);
  border: 1px solid rgba(59, 130, 246, 0.12);
  margin: 4px;
}}

/* Stat row */
.a-stat-row {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}}

.a-stat-row .a-stat {{ background: rgba(255,255,255,0.02); }}

/* Health indicators */
.health-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}}

@media (max-width: 768px) {{ .health-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

.health-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px;
  text-align: center;
}}

.health-card .h-val {{
  font-family: var(--mono);
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}}

.health-card .h-sub {{
  font-size: 12px;
  color: var(--muted);
  margin-top: 6px;
  font-weight: 500;
}}

/* Buyer interests */
.a-interest {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(28,37,64,0.2);
  font-size: 13px;
  color: var(--text2);
}}

.a-interest-count {{
  font-family: var(--mono);
  font-size: 12px;
  color: var(--violet);
  font-weight: 700;
}}

/* Footer */
.page-footer {{
  margin-top: 60px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--muted);
  flex-wrap: wrap;
  gap: 12px;
}}

.page-footer a {{ color: var(--cyan); text-decoration: none; }}
.page-footer a:hover {{ text-decoration: underline; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 5px; }}
</style>
</head>
<body>
<div class="page">

<header class="page-header">
  <div class="breadcrumb"><a href="/">Agent Economy</a> / Analysis</div>
  <h1><span class="gradient">Marketplace</span> Analysis</h1>
  <p>Live intelligence across {total_sellers} sellers, {total_buyers} buyers, and {unique_teams} teams in the Nevermined AI agent economy.</p>
  <div class="meta">
    <span class="live">Live data</span>
    <span>{total_sellers} sellers</span>
    <span>{total_buyers} buyers</span>
    <span>{unique_teams} teams</span>
    <span><a href="/api/analysis" style="color:var(--muted)">JSON &rarr;</a></span>
  </div>
</header>

<!-- Key Stats -->
<div class="stats-grid">
  <div class="a-stat"><div class="a-stat-val" style="color:var(--cyan)">{total_sellers}</div><div class="a-stat-lbl">Sellers</div></div>
  <div class="a-stat"><div class="a-stat-val" style="color:var(--violet)">{total_buyers}</div><div class="a-stat-lbl">Buyers</div></div>
  <div class="a-stat"><div class="a-stat-val" style="color:var(--emerald)">{teams_both}</div><div class="a-stat-lbl">Dual Participants</div></div>
  <div class="a-stat"><div class="a-stat-val" style="color:var(--blue)">{live_endpoints}</div><div class="a-stat-lbl">Live Endpoints</div></div>
  <div class="a-stat"><div class="a-stat-val" style="color:var(--amber)">{localhost}</div><div class="a-stat-lbl">Local Only</div></div>
  <div class="a-stat"><div class="a-stat-val" style="color:var(--rose)">{categories_count}</div><div class="a-stat-lbl">Categories</div></div>
</div>

<!-- Economy Health -->
<div class="health-grid">
  <div class="health-card"><div class="h-val" style="color:{ratio_color}">{sell_buy_ratio}:1</div><div class="h-sub">Seller/Buyer Ratio</div></div>
  <div class="health-card"><div class="h-val" style="color:{uptime_color}">{uptime}%</div><div class="h-sub">Endpoint Uptime</div></div>
  <div class="health-card"><div class="h-val" style="color:var(--cyan)">{participation}%</div><div class="h-sub">Full Participation</div></div>
  <div class="health-card"><div class="h-val" style="color:var(--violet)">{free}</div><div class="h-sub">Free Tier Services</div></div>
</div>

<!-- Categories + Payments -->
<div class="grid-2 section">
  <div class="card">
    <h3>Service Categories ({categories_count})</h3>
    {cat_rows}
  </div>
  <div>
    <div class="card" style="margin-bottom:24px">
      <h3>Payment Methods</h3>
      <div class="pay-grid">
        <div class="pay-card"><div class="val" style="color:var(--violet)">{crypto}</div><div class="lbl">Crypto (USDC)</div></div>
        <div class="pay-card"><div class="val" style="color:var(--emerald)">{fiat}</div><div class="lbl">Fiat (Stripe)</div></div>
        <div class="pay-card"><div class="val" style="color:var(--amber)">{free}</div><div class="lbl">Free / Trial</div></div>
      </div>
    </div>
    <div class="card">
      <h3>Protocols Detected</h3>
      <div>{proto_badges}</div>
    </div>
  </div>
</div>

<!-- Vesica Piscis divider -->
<div class="sacred-div">
  <svg viewBox="0 0 160 32" width="160" height="32" xmlns="http://www.w3.org/2000/svg">
    <line x1="0" y1="16" x2="50" y2="16" stroke="rgba(0,212,255,0.3)" stroke-width="0.5"/>
    <circle cx="72" cy="16" r="12" fill="none" stroke="rgba(0,212,255,0.4)" stroke-width="0.5"/>
    <circle cx="88" cy="16" r="12" fill="none" stroke="rgba(167,139,250,0.4)" stroke-width="0.5"/>
    <line x1="110" y1="16" x2="160" y2="16" stroke="rgba(167,139,250,0.3)" stroke-width="0.5"/>
  </svg>
</div>

<!-- Power Rankings + Pricing -->
<div class="grid-2 section">
  <div class="card">
    <h3>Power Rankings</h3>
    <table class="a-table">
      <thead><tr><th>Rank</th><th>Team</th><th>Selling</th><th>Buying</th><th>Total</th></tr></thead>
      <tbody>{power_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h3>Pricing Landscape</h3>
    <div style="margin-bottom:20px">
      <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:6px">Median Price</div>
      <div style="font-family:var(--mono);font-size:28px;font-weight:800;color:var(--cyan)">{median_price} USDC</div>
      <div style="font-size:12px;color:var(--muted);margin-top:2px">{total_priced} services with pricing data</div>
    </div>
    <div style="margin-bottom:16px">
      <div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:10px">Most Affordable</div>
      <table class="a-table"><tbody>{cheapest_rows}</tbody></table>
    </div>
    <div>
      <div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:10px">Premium Tier</div>
      <table class="a-table"><tbody>{expensive_rows}</tbody></table>
    </div>
  </div>
</div>

<!-- Keywords + Buyer Demand -->
<div class="grid-2 section">
  <div class="card">
    <h3>Top Keywords</h3>
    <div class="kw-cloud">{kw_html}</div>
  </div>
  <div class="card">
    <h3>Buyer Demand Signals</h3>
    {bi_html}
  </div>
</div>

<!-- Timeline -->
<div class="section">
  <div class="card">
    <h3>Registration Timeline</h3>
    {tl_html}
  </div>
</div>

<footer class="page-footer">
  <span><a href="/">Dashboard</a> &middot; <a href="/api/analysis">JSON API</a> &middot; <a href="/llms.txt">llms.txt</a> &middot; <a href="/blog">Blog</a></span>
  <span>Agent Economy &middot; Powered by <a href="https://nevermined.app">Nevermined</a></span>
</footer>

</div>
</body>
</html>"""


# ─── Blog ───


@app.get("/blog", response_class=HTMLResponse)
def blog_index():
    """Blog index — Anatomy of the Agent Economy series."""
    return render_blog_index()


@app.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(slug: str):
    """Individual blog post."""
    html = render_blog_post(slug)
    if html is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "post_not_found",
                "message": f"No blog post found with slug '{slug}'.",
                "available_posts": [f"/blog/{p['slug']}" for p in get_all_posts()],
            },
        )
    return html


# ─── Sponsors ───


@app.get("/sponsors", response_class=HTMLResponse)
def sponsors_index():
    """Sponsors index — hackathon sponsor deep dives."""
    return render_sponsors_index()


@app.get("/sponsors/{slug}", response_class=HTMLResponse)
def sponsor_page(slug: str):
    """Individual sponsor deep dive."""
    html = render_sponsor_page(slug)
    if html is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "sponsor_not_found",
                "message": f"No sponsor page found for '{slug}'.",
                "available_sponsors": [f"/sponsors/{s['slug']}" for s in get_all_sponsors()],
            },
        )
    return html


# ─── Serve Dashboard ───

ASSETS_DIR = Path(__file__).parent.parent / "static"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
if STATIC_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=str(STATIC_DIR)), name="dashboard_assets")

    @app.get("/")
    def dashboard():
        return FileResponse(str(STATIC_DIR / "index.html"))


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()

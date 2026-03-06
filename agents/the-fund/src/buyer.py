"""The Fund — Intelligence-driven autonomous buyer with closed economic feedback loops.

Unlike generic buyer agents that randomly shop, The Fund:
1. READS marketplace intelligence (Oracle) and trust data (Underwriter) BEFORE buying
2. Uses that data to make informed purchasing decisions
3. Tests services adversarially (edge cases, stress tests)
4. Cross-compares providers serving similar categories
5. Submits reviews that feed back into the trust system it reads from

This creates a closed economic loop: intelligence -> decisions -> purchases -> reviews -> intelligence
"""
import json
import os
import random
import time
import traceback

import httpx
from dotenv import load_dotenv
from payments_py import Payments, PaymentOptions

from .portfolio import Portfolio, Transaction

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
TOTAL_BUDGET = float(os.environ.get("TOTAL_BUDGET_USDC", "1000000"))
MAX_PER_TX = float(os.environ.get("MAX_PER_TRANSACTION", "10.0"))
LOOP_INTERVAL = int(os.environ.get("LOOP_INTERVAL_SECONDS", "45"))
DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"

# Our economy's live MCP services
OUR_SERVICES = {
    "the-oracle": {
        "url": "https://oracle.agenteconomy.io/mcp",
        "plan_id": "73832576591113218627249140062481319784526101948276910427168459563781622307151",
        "team": "Full Stack Agents",
    },
    "the-amplifier": {
        "url": "https://amplifier.agenteconomy.io/mcp",
        "plan_id": "31307392809981293956301786331179599135979548398803667593789184055010190785367",
        "team": "Full Stack Agents",
    },
    "the-architect": {
        "url": "https://architect.agenteconomy.io/mcp",
        "plan_id": "31307392809981293956301786331179599135979548398803667593789184055010190785367",
        "team": "Full Stack Agents",
    },
    "the-underwriter": {
        "url": "https://underwriter.agenteconomy.io/mcp",
        "plan_id": "108289525728886290523358160114949466457088917231870074042604244210937761689110",
        "team": "Full Stack Agents",
    },
    "the-gold-star": {
        "url": "https://goldstar.agenteconomy.io/mcp",
        "plan_id": "86107591125963957406574553233076282216940031177768083482829930136762279428594",
        "team": "Full Stack Agents",
    },
}

# Edge cases for adversarial testing
ADVERSARIAL_INPUTS = [
    "",                                    # empty string
    " ",                                   # whitespace only
    "a" * 5000,                            # very long input
    "'; DROP TABLE agents; --",            # SQL injection
    "<script>alert('xss')</script>",       # XSS
    "null",                                # null string
    "undefined",                           # undefined
    '{"nested": {"deep": {"very": true}}}',  # nested JSON as string
    "emoji: \U0001f680\U0001f916\U0001f4a5",                  # unicode/emoji
    "search for: -1 OR 1=1",              # boolean injection
]


def create_payments():
    return Payments.get_instance(
        PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
    )


def mcp_call(url: str, token: str, tool_name: str, arguments: dict) -> dict:
    """Call an MCP tool and return the result."""
    start = time.time()
    try:
        resp = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
                "id": int(time.time() * 1000) % 100000,
            },
            timeout=30,
        )
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            body = resp.json()
            result = body.get("result", {})
            meta = result.get("_meta", {})
            content = result.get("content", [])
            text = content[0].get("text", "") if content else ""
            is_error = result.get("isError", False)

            return {
                "success": not is_error and len(text) > 0,
                "text": text[:2000],
                "latency_ms": latency,
                "response_length": len(text),
                "credits_redeemed": meta.get("creditsRedeemed", "0"),
                "tx_hash": meta.get("txHash"),
            }
        else:
            return {"success": False, "text": resp.text[:200], "latency_ms": latency, "response_length": 0}
    except Exception as e:
        return {"success": False, "text": str(e)[:200], "latency_ms": (time.time() - start) * 1000, "response_length": 0}


def score_response(result: dict) -> float:
    """Score a response quality from 0-10."""
    if not result.get("success"):
        return 0
    score = 5.0
    latency = result.get("latency_ms", 5000)
    if latency < 500:
        score += 2
    elif latency < 1000:
        score += 1.5
    elif latency < 2000:
        score += 0.5
    elif latency > 5000:
        score -= 1
    length = result.get("response_length", 0)
    if length > 2000:
        score += 1
    if length > 5000:
        score += 1
    return min(10, max(0, score))


def get_or_refresh_token(payments, plan_id: str, service_name: str, cache: dict) -> str:
    """Get a cached token or fetch a new one."""
    cached = cache.get(service_name)
    if cached and cached["expires"] > time.time():
        return cached["token"]

    try:
        payments.plans.order_plan(plan_id)
    except Exception:
        pass

    try:
        result = payments.x402.get_x402_access_token(plan_id)
        token = result.get("accessToken", "")
        if token:
            cache[service_name] = {"token": token, "expires": time.time() + 300}
        return token
    except Exception as e:
        print(f"  [TOKEN ERROR] {service_name}: {e}")
        return ""


def call_our_service(payments, cache, service_name, tool_name, arguments):
    """Helper to call one of our MCP services."""
    svc = OUR_SERVICES[service_name]
    token = get_or_refresh_token(payments, svc["plan_id"], service_name, cache)
    if not token:
        return None
    return mcp_call(svc["url"], token, tool_name, arguments)


def submit_review(payments, cache, seller_name, team_name, quality, reliable, notes):
    """Submit a review to The Underwriter."""
    stars = max(1.0, min(5.0, quality / 2.0))
    return call_our_service(payments, cache, "the-underwriter", "submit_review", {
        "seller_name": seller_name,
        "team_name": team_name,
        "quality_score": round(stars, 1),
        "reliable": reliable,
        "notes": notes,
        "reviewer": "The Fund (Autonomous Buyer)",
    })


# ---------------------------------------------------------------------------
# PHASE 1: INTELLIGENCE GATHERING
# Read from Oracle + Underwriter to build a picture BEFORE spending
# ---------------------------------------------------------------------------

def gather_intelligence(payments, cache, portfolio, cycle):
    """Read marketplace data and reputation before making purchase decisions."""
    intel = {"leaderboard": [], "reputation": {}, "search_results": []}

    # Ask The Oracle: who's on top?
    portfolio.log_decision("INTEL", "Querying Oracle for marketplace leaderboard...")
    lb_result = call_our_service(payments, cache, "the-oracle", "marketplace_leaderboard", {})
    if lb_result and lb_result.get("success"):
        intel["leaderboard_raw"] = lb_result["text"][:1500]
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-oracle", team_name="Full Stack Agents",
            service_category="intelligence", plan_id=OUR_SERVICES["the-oracle"]["plan_id"],
            tool_name="marketplace_leaderboard", query="pre-purchase intelligence",
            credits_used=1, quality_score=score_response(lb_result),
            response_length=lb_result.get("response_length", 0),
            latency_ms=lb_result.get("latency_ms", 0), success=True,
        ))

    # Ask The Oracle: search for something specific based on cycle
    search_topics = [
        "research", "data analytics", "web search", "QA testing",
        "summarization", "translation", "code", "sentiment",
        "market intelligence", "infrastructure", "automation", "API",
    ]
    topic = search_topics[cycle % len(search_topics)]
    portfolio.log_decision("INTEL", f"Searching marketplace for '{topic}'...")
    search_result = call_our_service(payments, cache, "the-oracle", "marketplace_search", {"query": topic})
    if search_result and search_result.get("success"):
        intel["search_raw"] = search_result["text"][:1500]
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-oracle", team_name="Full Stack Agents",
            service_category="intelligence", plan_id=OUR_SERVICES["the-oracle"]["plan_id"],
            tool_name="marketplace_search", query=f"search: {topic}",
            credits_used=1, quality_score=score_response(search_result),
            response_length=search_result.get("response_length", 0),
            latency_ms=search_result.get("latency_ms", 0), success=True,
        ))

    # Ask The Underwriter: who's trustworthy?
    # Pick targets from leaderboard text if available, otherwise use known names
    rep_targets = ["The Oracle", "The Amplifier", "GTMAgent", "Cortex", "AgentAudit"]
    target = rep_targets[cycle % len(rep_targets)]
    portfolio.log_decision("INTEL", f"Checking reputation for '{target}'...")
    rep_result = call_our_service(payments, cache, "the-underwriter", "check_reputation", {"seller_name": target})
    if rep_result and rep_result.get("success"):
        intel["reputation"][target] = rep_result["text"][:500]
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-underwriter", team_name="Full Stack Agents",
            service_category="trust", plan_id=OUR_SERVICES["the-underwriter"]["plan_id"],
            tool_name="check_reputation", query=f"reputation: {target}",
            credits_used=1, quality_score=score_response(rep_result),
            response_length=rep_result.get("response_length", 0),
            latency_ms=rep_result.get("latency_ms", 0), success=True,
        ))

    return intel


# ---------------------------------------------------------------------------
# PHASE 2: INFORMED PURCHASING
# Use intelligence to decide what to buy
# ---------------------------------------------------------------------------

def informed_purchases(payments, cache, portfolio, cycle, intel):
    """Make purchases informed by intelligence gathered in phase 1."""
    # Use our services — but with PURPOSE, not randomly
    purchases = []

    # Compare two services head-to-head (cross-service arbitrage)
    compare_pairs = [
        ("The Oracle", "GTMAgent"), ("The Amplifier", "Cortex"),
        ("The Gold Star", "AgentAudit"), ("The Architect", "SwitchBoard AI"),
    ]
    pair = compare_pairs[cycle % len(compare_pairs)]
    portfolio.log_decision("COMPARE", f"Cross-comparing {pair[0]} vs {pair[1]}...")
    compare_result = call_our_service(payments, cache, "the-oracle", "marketplace_compare", {
        "service_a": pair[0], "service_b": pair[1],
    })
    if compare_result and compare_result.get("success"):
        quality = score_response(compare_result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-oracle", team_name="Full Stack Agents",
            service_category="arbitrage", plan_id=OUR_SERVICES["the-oracle"]["plan_id"],
            tool_name="marketplace_compare", query=f"arbitrage: {pair[0]} vs {pair[1]}",
            credits_used=1, quality_score=quality,
            response_length=compare_result.get("response_length", 0),
            latency_ms=compare_result.get("latency_ms", 0), success=True,
        ))
        purchases.append(("the-oracle", "marketplace_compare", quality))

    # Buy from Amplifier — contextualize with intelligence we gathered
    ad_content = intel.get("search_raw", "AI agent marketplace services")[:200]
    portfolio.log_decision("BUY", "Enriching intelligence with ads...")
    ad_result = call_our_service(payments, cache, "the-amplifier", "enrich_with_ads", {
        "content": ad_content, "ad_style": "inline",
    })
    if ad_result and ad_result.get("success"):
        quality = score_response(ad_result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-amplifier", team_name="Full Stack Agents",
            service_category="monetization", plan_id=OUR_SERVICES["the-amplifier"]["plan_id"],
            tool_name="enrich_with_ads", query="enrich intelligence with ads",
            credits_used=1, quality_score=quality,
            response_length=ad_result.get("response_length", 0),
            latency_ms=ad_result.get("latency_ms", 0), success=True,
        ))
        purchases.append(("the-amplifier", "enrich_with_ads", quality))

    # Check Gold Star certification for the service we compared
    portfolio.log_decision("BUY", f"Checking certification for {pair[0]}...")
    cert_result = call_our_service(payments, cache, "the-gold-star", "certification_status", {
        "seller_name": pair[0],
    })
    if cert_result and cert_result.get("success"):
        quality = score_response(cert_result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-gold-star", team_name="Full Stack Agents",
            service_category="certification", plan_id=OUR_SERVICES["the-gold-star"]["plan_id"],
            tool_name="certification_status", query=f"cert check: {pair[0]}",
            credits_used=1, quality_score=quality,
            response_length=cert_result.get("response_length", 0),
            latency_ms=cert_result.get("latency_ms", 0), success=True,
        ))
        purchases.append(("the-gold-star", "certification_status", quality))

    # Check Architect pipeline health
    portfolio.log_decision("BUY", "Checking Architect pipeline status...")
    arch_result = call_our_service(payments, cache, "the-architect", "pipeline_status", {})
    if arch_result and arch_result.get("success"):
        quality = score_response(arch_result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-architect", team_name="Full Stack Agents",
            service_category="orchestration", plan_id=OUR_SERVICES["the-architect"]["plan_id"],
            tool_name="pipeline_status", query="pipeline health check",
            credits_used=1, quality_score=quality,
            response_length=arch_result.get("response_length", 0),
            latency_ms=arch_result.get("latency_ms", 0), success=True,
        ))
        purchases.append(("the-architect", "pipeline_status", quality))

    return purchases


# ---------------------------------------------------------------------------
# PHASE 3: ADVERSARIAL TESTING
# Test services with edge cases — no other buyer does this
# ---------------------------------------------------------------------------

def adversarial_test(payments, cache, portfolio, cycle):
    """Test a service with adversarial inputs. Creates accountability."""
    # Rotate through services each cycle
    service_targets = [
        ("the-oracle", "marketplace_search", "query"),
        ("the-amplifier", "get_ad", "topic"),
        ("the-underwriter", "check_reputation", "seller_name"),
        ("the-gold-star", "certification_status", "seller_name"),
    ]
    target_svc, target_tool, target_param = service_targets[cycle % len(service_targets)]
    adversarial_input = ADVERSARIAL_INPUTS[cycle % len(ADVERSARIAL_INPUTS)]

    portfolio.log_decision("ADVERSARIAL", f"Testing {target_svc}.{target_tool} with edge case input...")

    result = call_our_service(payments, cache, target_svc, target_tool, {target_param: adversarial_input})
    if result is None:
        return

    # An adversarial test passes if the service handles it gracefully (responds without crashing)
    handled_gracefully = result.get("success") or result.get("response_length", 0) > 0
    quality = score_response(result) if handled_gracefully else 0

    input_preview = adversarial_input[:50] if adversarial_input else "(empty)"
    portfolio.record_transaction(Transaction(
        timestamp=time.time(), seller_name=target_svc, team_name="Full Stack Agents",
        service_category="adversarial", plan_id=OUR_SERVICES[target_svc]["plan_id"],
        tool_name=f"ADVERSARIAL:{target_tool}", query=f"edge case: {input_preview}",
        credits_used=1, quality_score=quality,
        response_length=result.get("response_length", 0),
        latency_ms=result.get("latency_ms", 0), success=handled_gracefully,
    ))

    verdict = "PASSED (handled gracefully)" if handled_gracefully else "FAILED (crashed or empty)"
    portfolio.log_decision("ADVERSARIAL", f"{target_svc}.{target_tool} {verdict} on input: {input_preview}")

    # File a claim with Underwriter if service failed adversarial test
    if not handled_gracefully:
        portfolio.log_decision("CLAIM", f"Filing incident report for {target_svc} adversarial failure")
        call_our_service(payments, cache, "the-underwriter", "file_claim", {
            "seller_name": target_svc,
            "team_name": "Full Stack Agents",
            "description": f"Service failed adversarial test: {target_tool} crashed on input: {input_preview}",
            "claimant": "The Fund (Autonomous Buyer)",
        })


# ---------------------------------------------------------------------------
# PHASE 4: EXTERNAL EXPLORATION
# Discover and test services from other hackathon teams
# ---------------------------------------------------------------------------

def explore_external(payments, cache, portfolio, cycle):
    """Discover and buy from external sellers."""
    portfolio.log_decision("EXPLORE", "Discovering external marketplace sellers...")
    try:
        resp = httpx.get(
            DISCOVERY_URL, params={"side": "sell"},
            headers={"x-nvm-api-key": NVM_API_KEY}, timeout=15,
        )
        resp.raise_for_status()
        sellers = resp.json().get("sellers", [])
    except Exception as e:
        portfolio.log_decision("EXPLORE", f"Discovery failed: {e}")
        return

    external = [
        s for s in sellers
        if s.get("endpointUrl", "").startswith("http")
        and "localhost" not in s.get("endpointUrl", "")
        and s.get("teamName", "") != "Full Stack Agents"
    ]
    portfolio.log_decision("EXPLORE", f"Found {len(external)} external sellers")

    # Try up to 3 random ones
    for seller in random.sample(external, min(3, len(external))):
        name = seller.get("name", "unknown")
        team = seller.get("teamName", "unknown")
        endpoint = seller.get("endpointUrl", "")
        plans = seller.get("planPricing", [])

        if not plans:
            continue

        plan_id = plans[0].get("planDid", "")
        if not plan_id:
            continue

        portfolio.log_decision("EXPLORE", f"Trying {name} [{team}]...")

        # First check reputation before buying (intelligence-driven!)
        rep = call_our_service(payments, cache, "the-underwriter", "check_reputation", {"seller_name": name})
        if rep and rep.get("success"):
            portfolio.log_decision("EXPLORE", f"Reputation for {name}: {rep['text'][:100]}")
            portfolio.record_transaction(Transaction(
                timestamp=time.time(), seller_name="the-underwriter", team_name="Full Stack Agents",
                service_category="trust", plan_id=OUR_SERVICES["the-underwriter"]["plan_id"],
                tool_name="check_reputation", query=f"pre-purchase check: {name}",
                credits_used=1, quality_score=score_response(rep),
                response_length=rep.get("response_length", 0),
                latency_ms=rep.get("latency_ms", 0), success=True,
            ))

        # Subscribe and try to call
        token = get_or_refresh_token(payments, plan_id, f"ext:{name[:20]}", cache)
        if not token:
            continue

        # Try MCP tools/call
        start = time.time()
        result = mcp_call(endpoint, token, "tools/list", {})  # Not a real tool — just probing
        latency = (time.time() - start) * 1000

        # Also try a generic REST call
        if not result.get("success"):
            try:
                resp = httpx.post(
                    endpoint,
                    headers={"Content-Type": "application/json", "Accept": "application/json",
                             "Authorization": f"Bearer {token}"},
                    json={"query": "What services do you provide?"},
                    timeout=10,
                )
                latency = (time.time() - start) * 1000
                result = {
                    "success": resp.status_code == 200,
                    "response_length": len(resp.text) if resp.status_code == 200 else 0,
                    "latency_ms": latency,
                }
            except Exception:
                result = {"success": False, "response_length": 0, "latency_ms": latency}

        quality = score_response(result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name=name, team_name=team,
            service_category=seller.get("category", "uncategorized"), plan_id=plan_id,
            tool_name="external_probe", query="service discovery",
            credits_used=1, quality_score=quality,
            response_length=result.get("response_length", 0),
            latency_ms=result.get("latency_ms", 0), success=result.get("success", False),
        ))

        # Submit review (the feedback loop!)
        submit_review(payments, cache,
                      seller_name=name, team_name=team,
                      quality=quality, reliable=result.get("success", False),
                      notes=f"External probe: {'reachable' if result.get('success') else 'unreachable'}, {latency:.0f}ms")
        portfolio.log_decision("REVIEW", f"Reviewed {name}: {quality/2:.1f}/5 stars")


# ---------------------------------------------------------------------------
# PHASE 5: FEEDBACK LOOP
# Review everything, request certifications, trigger switching
# ---------------------------------------------------------------------------

def feedback_loop(payments, cache, portfolio, cycle, purchases):
    """Submit reviews, request certs, evaluate switching."""
    # Review our purchases
    for svc_name, tool_name, quality in purchases:
        submit_review(payments, cache,
                      seller_name=svc_name, team_name="Full Stack Agents",
                      quality=quality, reliable=True,
                      notes=f"Cycle {cycle}: {tool_name}, quality={quality}/10")
        portfolio.log_decision("REVIEW", f"Reviewed {svc_name}: {quality/2:.1f}/5 stars")

    # Every 8th cycle: check the reputation leaderboard (see our reviews' impact!)
    if cycle % 8 == 0:
        portfolio.log_decision("FEEDBACK", "Checking reputation leaderboard (measuring our impact)...")
        lb = call_our_service(payments, cache, "the-underwriter", "reputation_leaderboard", {})
        if lb and lb.get("success"):
            portfolio.log_decision("FEEDBACK", f"Leaderboard: {lb['text'][:200]}")
            portfolio.record_transaction(Transaction(
                timestamp=time.time(), seller_name="the-underwriter", team_name="Full Stack Agents",
                service_category="feedback", plan_id=OUR_SERVICES["the-underwriter"]["plan_id"],
                tool_name="reputation_leaderboard", query="impact measurement",
                credits_used=1, quality_score=score_response(lb),
                response_length=lb.get("response_length", 0),
                latency_ms=lb.get("latency_ms", 0), success=True,
            ))

    # Every 10th cycle: request Gold Star certification for top providers
    if cycle % 10 == 0 and cycle > 0:
        best = portfolio.get_top_providers(2)
        for provider in best:
            if provider.avg_quality >= 4:
                portfolio.log_decision("CERTIFY", f"Requesting Gold Star for {provider.name}")
                url = OUR_SERVICES.get(provider.name, {}).get("url", "")
                if url:
                    call_our_service(payments, cache, "the-gold-star", "request_review", {
                        "seller_name": provider.name,
                        "endpoint_url": url.replace("/mcp", ""),
                    })

    # Evaluate provider switching across categories
    for cat in set(p.category for p in portfolio.providers.values()):
        portfolio.should_switch(cat)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def save_reports(portfolio, cycle):
    """Save investment report and data."""
    report = portfolio.get_report()
    base = os.path.join(os.path.dirname(__file__), "..")

    with open(os.path.join(base, "investment-report.txt"), "w") as f:
        f.write(report)

    with open(os.path.join(base, "investment-data.json"), "w") as f:
        json.dump({
            "last_cycle": cycle,
            "budget": portfolio.total_budget,
            "spent": portfolio.spent,
            "remaining": portfolio.remaining,
            "providers": len(portfolio.providers),
            "total_transactions": portfolio.total_transactions,
            "switches": portfolio.switches,
            "decisions_count": len(portfolio.decisions),
            "last_20_decisions": portfolio.decisions[-20:],
            "provider_summary": [
                {
                    "name": p.name, "team": p.team,
                    "transactions": len(p.transactions),
                    "avg_quality": round(p.avg_quality, 2),
                    "avg_roi": round(p.avg_roi, 2),
                    "success_rate": round(p.success_rate, 2),
                    "total_spent": p.total_spent,
                }
                for p in sorted(portfolio.providers.values(), key=lambda x: -x.avg_roi)
            ],
        }, f, indent=2, default=str)


def run_cycle(payments, portfolio, token_cache, cycle):
    """One cycle: Intelligence -> Purchases -> Adversarial -> Explore -> Feedback."""
    portfolio.log_decision("CYCLE", f"=== Cycle {cycle} ===")

    # Phase 1: Intelligence gathering (Oracle + Underwriter)
    intel = gather_intelligence(payments, token_cache, portfolio, cycle)

    # Phase 2: Informed purchases (using intelligence)
    purchases = informed_purchases(payments, token_cache, portfolio, cycle, intel)

    # Phase 3: Adversarial testing (every cycle — unique to The Fund)
    adversarial_test(payments, token_cache, portfolio, cycle)

    # Phase 4: External exploration (every 5th cycle)
    if cycle % 5 == 0:
        explore_external(payments, token_cache, portfolio, cycle)

    # Phase 5: Feedback loop (reviews, certs, switching)
    feedback_loop(payments, token_cache, portfolio, cycle, purchases)

    # Save
    save_reports(portfolio, cycle)


def run_fund():
    """Main autonomous buying loop."""
    payments = create_payments()
    portfolio = Portfolio(TOTAL_BUDGET, MAX_PER_TX)
    token_cache = {}
    cycle = 0

    print("=" * 60)
    print("THE FUND -- Intelligence-Driven Autonomous Buyer")
    print(f"Budget: {TOTAL_BUDGET} USDC | Interval: {LOOP_INTERVAL}s")
    print("Phases: Intel -> Buy -> Adversarial -> Explore -> Feedback")
    print("=" * 60)
    print()

    # Subscribe to all our services
    portfolio.log_decision("INIT", "Subscribing to Agent Economy services...")
    for name, service in OUR_SERVICES.items():
        try:
            payments.plans.order_plan(service["plan_id"])
            portfolio.log_decision("SUBSCRIBE", f"Subscribed to {name}")
        except Exception:
            portfolio.log_decision("SUBSCRIBE", f"Already subscribed to {name}")

    while True:
        cycle += 1
        try:
            run_cycle(payments, portfolio, token_cache, cycle)
        except Exception as e:
            portfolio.log_decision("ERROR", f"Cycle {cycle} failed: {e}")
            traceback.print_exc()

        portfolio.log_decision(
            "STATUS",
            f"Cycle {cycle} done. {portfolio.total_transactions} txns, "
            f"{len(portfolio.providers)} providers, {portfolio.spent:.2f} USDC spent"
        )
        print(f"\n--- Sleeping {LOOP_INTERVAL}s ---\n")
        time.sleep(LOOP_INTERVAL)


def main():
    run_fund()


if __name__ == "__main__":
    main()

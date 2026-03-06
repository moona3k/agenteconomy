"""The Fund -- Intelligence-driven autonomous buyer with closed economic feedback loops.

INVESTMENT THESIS: "Markets are not given; they are made."

Grounded in nine economic frameworks:
- Akerlof (1970): Without quality signals, markets collapse to lemons. Every review
  we submit is structural resistance against market failure.
- Hayek (1945): We are the distributed sensor network -- our ROI measurements are the
  price signals that let a decentralized agent economy coordinate without central planning.
- Coase (1937): We don't build capabilities; we buy them -- because when transaction costs
  approach zero, the optimal firm is a network of purchases, not a hierarchy of departments.
- Soros (Reflexivity): We read the reputation we write -- our reviews change the marketplace
  data we base decisions on. This reflexive loop is the engine of quality improvement.
- Taleb (Antifragility): We send edge cases not to break services but to strengthen them --
  adversarial testing is the immune system of the agent economy.
- Hurwicz/Myerson/Maskin (Mechanism Design, Nobel 2007): Honest quality signals make
  truth-telling the dominant strategy for sellers.
- Ostrom (Commons Governance, Nobel 2009): Reputation is a commons -- we govern it through
  active participation, not authority.
- Kyle (1985, Market Microstructure): Intelligence before capital. Informed purchasing is
  both self-interested profit maximization and a public good.
- Principal-Agent Problem: We log every decision because transparency is the only credible
  solution to the alignment problem between autonomous agents and human principals.

Five-phase cycle:
  1. INTELLIGENCE -- Read Oracle + Underwriter BEFORE spending (Hayek, Kyle)
  2. INFORMED PURCHASE -- Use intelligence to decide what to buy (Coase, Kyle)
  3. ADVERSARIAL TEST -- Stress-test a service with edge cases (Taleb)
  4. EXTERNAL EXPLORATION -- Discover and evaluate external sellers (Akerlof)
  5. FEEDBACK LOOP -- Reviews, certifications, switching (Soros, Ostrom, Hurwicz)
"""
import json
import os
import random
import re
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

# ---------------------------------------------------------------------------
# EXTERNAL SERVICES -- Real cross-team targets with known-working APIs
# Each entry: (team, name, endpoint, plan_id, protocol, call_spec)
# call_spec = dict describing how to actually call the service
# ---------------------------------------------------------------------------
EXTERNAL_TARGETS = [
    {
        "team": "SwitchBoard AI",
        "name": "DataForge Search",
        "endpoint": "https://switchboardai.ayushojha.com/api/dataforge-search/search",
        "plan_id": "20525280098953834660118374760884658206838276532391353027417693253911209808544",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"topic": "AI agent marketplace trends"}},
        "use_result": "search results about AI marketplace",
    },
    {
        "team": "SwitchBoard AI",
        "name": "DataForge Web",
        "endpoint": "https://switchboardai.ayushojha.com/api/dataforge-web/scrape",
        "plan_id": "87243775557809620406811462333406929215670569276922516691841478531555517979134",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"url": "https://agenteconomy.io/llms.txt"}},
        "use_result": "scraped web content from agenteconomy.io",
    },
    {
        "team": "Mog Markets",
        "name": "Mog Scout",
        "endpoint": "https://api.mog.markets/mcp",
        "plan_id": "80405952062456215706155179546361155537224829467755036911429965057631428557501",
        "protocol": "mcp",
        "call": {"tool": "search", "arguments": {"query": "AI research agents"}},
        "use_result": "marketplace scouting data",
    },
    {
        "team": "Mog Markets",
        "name": "Mog Worker",
        "endpoint": "https://api.mog.markets/mcp",
        "plan_id": "15579048407391845791171022473148831778576054148316810138257846188534320567257",
        "protocol": "mcp",
        "call": {"tool": "execute", "arguments": {"task": "analyze marketplace trends"}},
        "use_result": "task execution result",
    },
    {
        "team": "Agent Bazaar",
        "name": "AgentBazaar Agent Directory",
        "endpoint": "https://agentbazaar-validator-production.up.railway.app/agents",
        "plan_id": "109961167456900334251436955177952409917810209459747468319758217133300293965907",
        "protocol": "rest-get",
        "call": {"method": "GET"},
        "use_result": "directory of registered agents",
    },
    {
        "team": "Agent Bazaar",
        "name": "AgentBazaar Validator",
        "endpoint": "https://agentbazaar-validator-production.up.railway.app/validate",
        "plan_id": "64909692525848970824175667201935504117836794554412065857736015677609021406268",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"agent_id": "the-oracle", "capabilities": ["marketplace intelligence", "search", "comparison"]}},
        "use_result": "agent validation results",
    },
    {
        "team": "AiRI — AI Resilience Index",
        "name": "AiRI Resilience Score",
        "endpoint": "https://airi-demo.replit.app/resilience-score",
        "plan_id": "103257219319677182457590117791374190482381124677253274358303068676454441457913",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"company": "Nevermined"}},
        "use_result": "AI resilience scoring for Nevermined",
    },
    {
        "team": "AI Research Agnet",
        "name": "AI Research Broker",
        "endpoint": "https://hack-mined-production.up.railway.app/research",
        "plan_id": "66828968694604448273724812981407769357248145648254711136618922943343003256939",
        "protocol": "rest-x402",
        "call": {"method": "POST", "json": {"query": "AI agent economy infrastructure trends 2026"}},
        "use_result": "research on AI agent economy",
    },
    {
        "team": "Max Health",
        "name": "Research Agent",
        "endpoint": "https://nevermined-hack-production.up.railway.app/search",
        "plan_id": "9168834408799679719145079291439703578843086640569012876812947119908077187627",
        "protocol": "rest-x402",
        "call": {"method": "POST", "json": {"query": "autonomous AI business models"}},
        "use_result": "health/research search results",
    },
    {
        "team": "AgentAudit",
        "name": "GTMAgent",
        "endpoint": "https://agentaudit.onrender.com/data",
        "plan_id": "91110158470018414670150052111964295108660990507123548274005818054815074378976",
        "protocol": "rest-x402",
        "call": {"method": "POST", "json": {"query": "go to market strategy for AI agents"}},
        "use_result": "GTM strategy data",
    },
    {
        "team": "Undermined",
        "name": "Undermind",
        "endpoint": "https://nevermined-autonomous-business-hack.vercel.app/api/agent/research",
        "plan_id": "83480319637602122918957452839185213999331293232449361790831275088734229713001",
        "protocol": "rest-x402",
        "call": {"method": "POST", "json": {"query": "AI agent marketplace competition analysis", "depth": "quick"}},
        "use_result": "competitive research intelligence",
    },
    {
        "team": "BusyBeeAIs",
        "name": "BusyBeeAIs Competitor Intel",
        "endpoint": "https://us15.abilityai.dev/api/paid/busybeeais-2/chat",
        "plan_id": "92386514062008855300546193568870064173786782662621218779432605891805558994024",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"message": "What are the top AI agent marketplace competitors?"}},
        "use_result": "competitor intelligence",
    },
    {
        "team": "BennySpenny",
        "name": "Sabi",
        "endpoint": "https://sabi-backend.ben-imadali.workers.dev/query",
        "plan_id": "16871201947972714670125894743395881319398475848434387294065816734843371415817",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"query": "AI agent economy analysis"}},
        "use_result": "research query results",
    },
    {
        "team": "Platon",
        "name": "Platon Memory",
        "endpoint": "https://platon.bigf.me/mcp",
        "protocol": "mcp-sse",
        "plan_id": "73169765125098902371333949161624114039157379307050553178571193711771922123338",
        "call": {"tool": "memory.dump_session", "arguments": {"agentId": "the-fund", "agentKind": "buyer", "tenantId": "agenteconomy", "sessionId": "fund-cycle-1", "task": "Cross-team marketplace evaluation", "outcome": "Evaluated 10+ external services across the agent economy"}},
        "use_result": "session memory storage",
    },
    {
        "team": "Cloudagi.ai",
        "name": "CloudAGI Smart Search",
        "endpoint": "https://api.cloudagi.org/v1/services/smart-search/execute",
        "plan_id": "89079330978397499166663891689552952516403347434508914875089205815814165930880",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"query": "autonomous AI agent economy"}},
        "use_result": "smart search results",
    },
    {
        "team": "Tallyfor Tax Agent",
        "name": "Tallyfor Tax Expert",
        "endpoint": "https://www.tallyfor.ai/api/analyze",
        "plan_id": "19062709656768144810935442489636543699075063669395253625994522012432802025427",
        "protocol": "rest",
        "call": {"method": "POST", "json": {"query_type": "tax_projection", "data": {"income": 50000, "filing_status": "single", "state": "CA"}}},
        "use_result": "tax analysis for agent revenue",
    },
]

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

# Adversarial inputs for antifragility testing (Taleb)
ADVERSARIAL_INPUTS = [
    ("empty string", ""),
    ("whitespace only", " "),
    ("5000-char flood", "a" * 5000),
    ("SQL injection", "'; DROP TABLE agents; --"),
    ("XSS payload", "<script>alert('xss')</script>"),
    ("null string", "null"),
    ("undefined string", "undefined"),
    ("nested JSON", '{"nested": {"deep": {"very": true}}}'),
    ("unicode/emoji", "emoji: \U0001f680\U0001f916\U0001f4a5"),
    ("boolean injection", "search for: -1 OR 1=1"),
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
    """Submit a review to The Underwriter (Ostrom: governing the reputation commons)."""
    stars = max(1.0, min(5.0, quality / 2.0))
    return call_our_service(payments, cache, "the-underwriter", "submit_review", {
        "seller_name": seller_name,
        "team_name": team_name,
        "quality_score": round(stars, 1),
        "reliable": reliable,
        "notes": notes,
        "reviewer": "The Fund (Autonomous Buyer)",
    })


def extract_service_names(text: str) -> list[str]:
    """Extract service names from Oracle leaderboard/search text."""
    # Pattern: lines like "#1 ServiceName [TeamName]" or "ServiceName [TeamName]"
    names = []
    for line in text.split("\n"):
        match = re.match(r"#?\d*\s*(.+?)\s*\[(.+?)\]", line)
        if match:
            name = match.group(1).strip()
            team = match.group(2).strip()
            if team != "Full Stack Agents" and name and len(name) < 60:
                names.append((name, team))
    return names


# ---------------------------------------------------------------------------
# PHASE 1: INTELLIGENCE GATHERING (Hayek + Kyle)
# "We are the distributed sensor network -- our measurements are the price
# signals that let a decentralized economy coordinate without central planning."
# ---------------------------------------------------------------------------

def gather_intelligence(payments, cache, portfolio, cycle):
    """Read marketplace data and reputation BEFORE making purchase decisions.

    Kyle (1985): Informed traders move capital toward quality. We gather
    intelligence not to optimize our own returns but to produce the information
    signals that make rational purchasing possible for everyone.
    """
    intel = {"top_services": [], "reputation": {}, "search_results": []}

    # Ask The Oracle: who's on top right now?
    portfolio.log_decision("THESIS",
        "[Hayek] Querying Oracle -- distributed knowledge must be gathered before "
        "it can coordinate. No central planner knows what we're about to learn.")
    lb_result = call_our_service(payments, cache, "the-oracle", "marketplace_leaderboard", {})
    if lb_result and lb_result.get("success"):
        intel["leaderboard_raw"] = lb_result["text"][:1500]
        # Extract actual service names for Phase 4
        intel["top_services"] = extract_service_names(lb_result["text"])
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-oracle", team_name="Full Stack Agents",
            service_category="intelligence", plan_id=OUR_SERVICES["the-oracle"]["plan_id"],
            tool_name="marketplace_leaderboard", query="pre-purchase intelligence",
            credits_used=1, quality_score=score_response(lb_result),
            response_length=lb_result.get("response_length", 0),
            latency_ms=lb_result.get("latency_ms", 0), success=True,
        ))
        portfolio.log_decision("INTEL",
            f"Oracle reports {len(intel['top_services'])} external services ranked. "
            f"Top: {', '.join(n for n, _ in intel['top_services'][:3]) or 'none parsed'}")

    # Ask The Oracle: search for a specific capability
    search_topics = [
        "research", "data analytics", "web search", "QA testing",
        "summarization", "translation", "code generation", "sentiment analysis",
        "market intelligence", "infrastructure", "automation", "API services",
    ]
    topic = search_topics[cycle % len(search_topics)]
    portfolio.log_decision("THESIS",
        f"[Kyle] Searching for '{topic}' -- informed buyers move capital toward quality. "
        f"This search produces the information that makes rational allocation possible.")
    search_result = call_our_service(payments, cache, "the-oracle", "marketplace_search", {"query": topic})
    if search_result and search_result.get("success"):
        intel["search_raw"] = search_result["text"][:1500]
        intel["search_results"] = extract_service_names(search_result["text"])
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-oracle", team_name="Full Stack Agents",
            service_category="intelligence", plan_id=OUR_SERVICES["the-oracle"]["plan_id"],
            tool_name="marketplace_search", query=f"search: {topic}",
            credits_used=1, quality_score=score_response(search_result),
            response_length=search_result.get("response_length", 0),
            latency_ms=search_result.get("latency_ms", 0), success=True,
        ))

    # Ask The Underwriter: what's the trust profile?
    # Use intelligence to pick target -- check the top-ranked service, not a random one
    if intel["top_services"]:
        target_name, target_team = intel["top_services"][cycle % len(intel["top_services"])]
    else:
        targets = [("GTMAgent", "AgentAudit"), ("Cortex", "unknown"), ("AgentAudit", "unknown")]
        target_name, target_team = targets[cycle % len(targets)]

    portfolio.log_decision("THESIS",
        f"[Akerlof] Checking reputation for '{target_name}' -- without verified quality "
        f"signals, this marketplace collapses to lemons. Every reputation check prevents market failure.")
    rep_result = call_our_service(payments, cache, "the-underwriter", "check_reputation", {"seller_name": target_name})
    if rep_result and rep_result.get("success"):
        intel["reputation"][target_name] = rep_result["text"][:500]
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-underwriter", team_name="Full Stack Agents",
            service_category="trust", plan_id=OUR_SERVICES["the-underwriter"]["plan_id"],
            tool_name="check_reputation", query=f"reputation: {target_name}",
            credits_used=1, quality_score=score_response(rep_result),
            response_length=rep_result.get("response_length", 0),
            latency_ms=rep_result.get("latency_ms", 0), success=True,
        ))
        portfolio.log_decision("INTEL", f"Underwriter on {target_name}: {rep_result['text'][:120]}")

    return intel


# ---------------------------------------------------------------------------
# PHASE 2: INFORMED PURCHASING (Coase + Kyle)
# "We don't build capabilities; we buy them -- because when transaction costs
# approach zero, the optimal firm is a network of purchases."
# ---------------------------------------------------------------------------

def informed_purchases(payments, cache, portfolio, cycle, intel):
    """Make purchases informed by intelligence gathered in Phase 1.

    Coase (1937): Firms exist because markets have friction. When The Fund
    reduces that friction through intelligence-driven purchasing, it demonstrates
    the Coasean Singularity -- the point where buying is always better than building.
    """
    purchases = []

    # Cross-service arbitrage -- compare two providers head-to-head
    compare_pairs = [
        ("The Oracle", "GTMAgent"), ("The Amplifier", "Cortex"),
        ("The Gold Star", "AgentAudit"), ("The Architect", "SwitchBoard AI"),
    ]
    pair = compare_pairs[cycle % len(compare_pairs)]
    portfolio.log_decision("THESIS",
        f"[Coase] Comparing {pair[0]} vs {pair[1]} -- arbitrage reveals true value. "
        f"The Coasean Singularity means we never need an internal comparison department.")
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

    # Buy from Amplifier -- contextualize with intelligence we gathered
    ad_content = intel.get("search_raw", "AI agent marketplace services")[:200]
    portfolio.log_decision("THESIS",
        "[Hurwicz] Purchasing ad enrichment -- mechanism design says honest participation "
        "makes truth-telling the dominant strategy for all marketplace actors.")
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

    # Check certification for a service -- use intelligence to pick which one
    cert_target = pair[0]
    cert_result = call_our_service(payments, cache, "the-gold-star", "certification_status", {
        "seller_name": cert_target,
    })
    if cert_result and cert_result.get("success"):
        quality = score_response(cert_result)
        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name="the-gold-star", team_name="Full Stack Agents",
            service_category="certification", plan_id=OUR_SERVICES["the-gold-star"]["plan_id"],
            tool_name="certification_status", query=f"cert check: {cert_target}",
            credits_used=1, quality_score=quality,
            response_length=cert_result.get("response_length", 0),
            latency_ms=cert_result.get("latency_ms", 0), success=True,
        ))
        purchases.append(("the-gold-star", "certification_status", quality))

    # Check pipeline health
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
# PHASE 3: ADVERSARIAL TESTING (Taleb -- Antifragility)
# "We send edge cases not to break services but to strengthen them --
# adversarial testing is the immune system of the agent economy."
# ---------------------------------------------------------------------------

def adversarial_test(payments, cache, portfolio, cycle):
    """Test a service with adversarial inputs.

    Taleb: Antifragile systems need stressors to grow. Eliminating shocks from
    a complex system makes it fragile, not safe. Every adversarial probe is a
    vaccine, not an attack.
    """
    service_targets = [
        ("the-oracle", "marketplace_search", "query"),
        ("the-amplifier", "get_ad", "topic"),
        ("the-underwriter", "check_reputation", "seller_name"),
        ("the-gold-star", "certification_status", "seller_name"),
    ]
    target_svc, target_tool, target_param = service_targets[cycle % len(service_targets)]
    attack_name, adversarial_input = ADVERSARIAL_INPUTS[cycle % len(ADVERSARIAL_INPUTS)]

    portfolio.log_decision("THESIS",
        f"[Taleb] Adversarial test: {attack_name} against {target_svc}.{target_tool} -- "
        f"antifragile systems need stressors to grow. This probe is a vaccine, not an attack.")

    result = call_our_service(payments, cache, target_svc, target_tool, {target_param: adversarial_input})
    if result is None:
        return

    handled_gracefully = result.get("success") or result.get("response_length", 0) > 0
    quality = score_response(result) if handled_gracefully else 0

    portfolio.record_transaction(Transaction(
        timestamp=time.time(), seller_name=target_svc, team_name="Full Stack Agents",
        service_category="adversarial", plan_id=OUR_SERVICES[target_svc]["plan_id"],
        tool_name=f"ADVERSARIAL:{target_tool}", query=f"edge case: {attack_name}",
        credits_used=1, quality_score=quality,
        response_length=result.get("response_length", 0),
        latency_ms=result.get("latency_ms", 0), success=handled_gracefully,
    ))

    if handled_gracefully:
        portfolio.log_decision("ADVERSARIAL",
            f"PASSED: {target_svc} handled {attack_name} gracefully -- antifragility confirmed")
    else:
        portfolio.log_decision("ADVERSARIAL",
            f"FAILED: {target_svc} crashed on {attack_name} -- filing claim with Underwriter")
        call_our_service(payments, cache, "the-underwriter", "file_claim", {
            "seller_name": target_svc,
            "team_name": "Full Stack Agents",
            "reason": f"Adversarial test failure: {target_tool} crashed on {attack_name} input",
            "buyer": "The Fund (Autonomous Buyer)",
        })


# ---------------------------------------------------------------------------
# PHASE 4: EXTERNAL EXPLORATION (Akerlof -- Market for Lemons)
# "Without verified quality signals, agent marketplaces collapse to lemons --
# every review we submit is structural resistance against market failure."
# ---------------------------------------------------------------------------

def call_external_rest(endpoint: str, token: str, call_spec: dict) -> dict:
    """Call an external REST service with x402 token."""
    start = time.time()
    method = call_spec.get("method", "POST")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "payment-signature": token,  # Some services use this header instead
    }
    try:
        if method == "GET":
            resp = httpx.get(endpoint, headers=headers, timeout=15)
        else:
            resp = httpx.post(endpoint, headers=headers, json=call_spec.get("json", {}), timeout=15)
        latency = (time.time() - start) * 1000
        text = resp.text[:2000] if resp.status_code == 200 else resp.text[:500]
        return {
            "success": resp.status_code == 200,
            "text": text,
            "latency_ms": latency,
            "response_length": len(resp.text),
            "status_code": resp.status_code,
        }
    except Exception as e:
        return {"success": False, "text": str(e)[:200], "latency_ms": (time.time() - start) * 1000, "response_length": 0}


def call_external_mcp(endpoint: str, token: str, call_spec: dict) -> dict:
    """Call an external MCP service via JSON-RPC."""
    tool_name = call_spec.get("tool", "tools/list")
    arguments = call_spec.get("arguments", {})
    return mcp_call(endpoint, token, tool_name, arguments)


def explore_external(payments, cache, portfolio, cycle, intel):
    """Buy from real external teams -- the critical cross-team transaction generator.

    Akerlof (1970): In markets with quality uncertainty, bad products drive out good.
    The Fund solves this by buying, testing, and reviewing services from OTHER TEAMS.
    """
    portfolio.log_decision("THESIS",
        "[Akerlof] CROSS-TEAM PURCHASES -- buying from external teams to generate "
        "real economic activity. Every purchase is a vote of confidence in the agent economy.")

    # Pick a rotating batch of external targets (4 per cycle from different teams)
    batch_size = 4
    start_idx = (cycle * batch_size) % len(EXTERNAL_TARGETS)
    batch = []
    seen_teams = set()
    # Rotate through targets, preferring diversity of teams
    for i in range(len(EXTERNAL_TARGETS)):
        target = EXTERNAL_TARGETS[(start_idx + i) % len(EXTERNAL_TARGETS)]
        if target["team"] not in seen_teams:
            batch.append(target)
            seen_teams.add(target["team"])
        if len(batch) >= batch_size:
            break
    # Fill remaining slots if needed
    if len(batch) < batch_size:
        for i in range(len(EXTERNAL_TARGETS)):
            target = EXTERNAL_TARGETS[(start_idx + i) % len(EXTERNAL_TARGETS)]
            if target not in batch:
                batch.append(target)
            if len(batch) >= batch_size:
                break

    portfolio.log_decision("EXPLORE",
        f"Cycle {cycle}: targeting {len(batch)} external services from teams: "
        f"{', '.join(t['team'] for t in batch)}")

    for target in batch:
        name = target["name"]
        team = target["team"]
        endpoint = target["endpoint"]
        plan_id = target["plan_id"]
        protocol = target.get("protocol", "rest")
        call_spec = target["call"]
        use_result = target.get("use_result", "external service response")

        # Vary the query per cycle to avoid duplicate calls
        call_spec = dict(call_spec)  # shallow copy
        if "json" in call_spec:
            call_spec["json"] = dict(call_spec["json"])
            # Add cycle-specific variation
            for key in ("topic", "query", "message"):
                if key in call_spec["json"]:
                    topics = [
                        "AI agent marketplace trends",
                        "autonomous business models for AI",
                        "agent-to-agent payment infrastructure",
                        "decentralized AI service discovery",
                        "quality assurance for AI agents",
                        "trust and reputation in agent economies",
                        "multi-agent orchestration patterns",
                        "AI agent monetization strategies",
                        "cross-team agent collaboration",
                        "future of autonomous AI businesses",
                    ]
                    call_spec["json"][key] = topics[cycle % len(topics)]

        portfolio.log_decision("PURCHASE",
            f"[Coase] Buying from {name} [{team}] -- transaction costs approach zero, "
            f"so we buy instead of build. Expected: {use_result}")

        # Get token and call
        token = get_or_refresh_token(payments, plan_id, f"ext:{name[:20]}", cache)
        if not token:
            portfolio.log_decision("ERROR", f"Failed to get token for {name} [{team}]")
            continue

        if protocol == "mcp":
            result = call_external_mcp(endpoint, token, call_spec)
        elif protocol == "mcp-sse":
            result = call_external_mcp(endpoint, token, call_spec)
        else:
            result = call_external_rest(endpoint, token, call_spec)

        quality = score_response(result)
        success = result.get("success", False)

        portfolio.record_transaction(Transaction(
            timestamp=time.time(), seller_name=name, team_name=team,
            service_category="external", plan_id=plan_id,
            tool_name=f"CROSS-TEAM:{name[:30]}", query=f"cross-team purchase cycle {cycle}",
            credits_used=1, quality_score=quality,
            response_length=result.get("response_length", 0),
            latency_ms=result.get("latency_ms", 0), success=success,
        ))

        if success:
            portfolio.log_decision("SUCCESS",
                f"CROSS-TEAM TX: {name} [{team}] responded! "
                f"Quality={quality:.1f}/10, {result.get('response_length', 0)} bytes, "
                f"{result.get('latency_ms', 0):.0f}ms")

            # USE the result: feed it into our Oracle for enrichment (proving we USE purchased data)
            result_text = result.get("text", "")[:300]
            if result_text:
                call_our_service(payments, cache, "the-oracle", "marketplace_search", {
                    "query": result_text[:100]
                })
                portfolio.log_decision("USE",
                    f"Fed {name}'s response into Oracle search -- cross-pollinating intelligence")
        else:
            portfolio.log_decision("FAILED",
                f"CROSS-TEAM TX: {name} [{team}] failed: status={result.get('status_code', 'N/A')}, "
                f"{result.get('text', '')[:100]}")

        # Submit review to Underwriter (Ostrom: governing the reputation commons)
        submit_review(payments, cache,
                      seller_name=name, team_name=team,
                      quality=quality, reliable=success,
                      notes=f"Cross-team purchase cycle {cycle}. "
                            f"{'Successful' if success else 'Failed'}, "
                            f"{result.get('latency_ms', 0):.0f}ms latency, "
                            f"{result.get('response_length', 0)} bytes")
        portfolio.log_decision("REVIEW",
            f"[Ostrom] Reviewed {name} [{team}]: {quality/2:.1f}/5 stars")


# ---------------------------------------------------------------------------
# PHASE 5: FEEDBACK LOOP (Soros + Ostrom + Hurwicz)
# "We read the reputation we write -- our reviews change the marketplace
# data we base decisions on, and this reflexive loop is the engine."
# ---------------------------------------------------------------------------

def feedback_loop(payments, cache, portfolio, cycle, purchases):
    """Submit reviews, request certifications, evaluate switching.

    Soros (Reflexivity): The Fund reads reputation data, makes decisions based on it,
    and submits reviews that change that data. Perception and reality are entangled.
    This is not a bug -- it is the generative engine of the economy.
    """
    # Review our purchases
    for svc_name, tool_name, quality in purchases:
        submit_review(payments, cache,
                      seller_name=svc_name, team_name="Full Stack Agents",
                      quality=quality, reliable=True,
                      notes=f"Cycle {cycle}: {tool_name}, quality={quality}/10")

    portfolio.log_decision("THESIS",
        f"[Soros] Submitted {len(purchases)} reviews -- reflexivity in action: "
        f"these reviews will change the reputation data we read next cycle. "
        f"Our perception of the market literally changes the market we perceive.")

    # Periodically measure our impact on the reputation system
    if cycle % 8 == 0:
        portfolio.log_decision("THESIS",
            "[Ostrom] Checking reputation leaderboard -- measuring our impact on the commons. "
            "Self-monitoring is Ostrom's key governance principle.")
        lb = call_our_service(payments, cache, "the-underwriter", "reputation_leaderboard", {})
        if lb and lb.get("success"):
            portfolio.log_decision("FEEDBACK", f"Reputation commons state: {lb['text'][:200]}")
            portfolio.record_transaction(Transaction(
                timestamp=time.time(), seller_name="the-underwriter", team_name="Full Stack Agents",
                service_category="feedback", plan_id=OUR_SERVICES["the-underwriter"]["plan_id"],
                tool_name="reputation_leaderboard", query="reflexivity measurement",
                credits_used=1, quality_score=score_response(lb),
                response_length=lb.get("response_length", 0),
                latency_ms=lb.get("latency_ms", 0), success=True,
            ))

    # Request Gold Star certification for top providers
    if cycle % 10 == 0 and cycle > 0:
        best = portfolio.get_top_providers(2)
        for provider in best:
            if provider.avg_quality >= 4:
                portfolio.log_decision("THESIS",
                    f"[Hurwicz] Nominating {provider.name} for Gold Star -- certification "
                    f"makes quality observable, which makes truth-telling incentive-compatible")
                url = OUR_SERVICES.get(provider.name, {}).get("url", "")
                if url:
                    call_our_service(payments, cache, "the-gold-star", "request_review", {
                        "seller_name": provider.name,
                        "team_name": provider.team_name,
                        "endpoint_url": url.replace("/mcp", ""),
                    })

    # Evaluate provider switching
    for cat in set(p.category for p in portfolio.providers.values()):
        portfolio.should_switch(cat)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def save_reports(portfolio, cycle):
    """Save investment report and structured data."""
    report = portfolio.get_report()
    base = os.path.join(os.path.dirname(__file__), "..")

    with open(os.path.join(base, "investment-report.txt"), "w") as f:
        f.write(report)

    data = {
        "last_cycle": cycle,
        "thesis": "Markets are not given; they are made.",
        "frameworks": [
            "Akerlof (Lemons)", "Hayek (Knowledge)", "Coase (Transaction Costs)",
            "Soros (Reflexivity)", "Taleb (Antifragility)", "Hurwicz (Mechanism Design)",
            "Ostrom (Commons)", "Kyle (Microstructure)", "Principal-Agent (Transparency)",
        ],
        "budget": portfolio.total_budget,
        "spent": portfolio.spent,
        "remaining": portfolio.remaining,
        "providers": len(portfolio.providers),
        "total_transactions": portfolio.total_transactions,
        "switches": portfolio.switches,
        "decisions_count": len(portfolio.decisions),
        "last_30_decisions": portfolio.decisions[-30:],
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
    }

    with open(os.path.join(base, "investment-data.json"), "w") as f:
        json.dump(data, f, indent=2, default=str)

    # Sync to The Ledger (deployed on Railway)
    try:
        with httpx.Client(timeout=10) as client:
            client.post("https://agenteconomy.io/api/fund", json=data)
    except Exception:
        pass  # non-critical — local file is the source of truth


def run_cycle(payments, portfolio, token_cache, cycle):
    """One cycle: Intelligence -> Purchases -> Adversarial -> Explore -> Feedback.

    Principal-Agent Problem: We log every decision because transparency is the
    only credible solution to the alignment problem between autonomous agents
    and human principals.
    """
    portfolio.log_decision("CYCLE", f"=== Cycle {cycle} ===")

    # Phase 1: Intelligence (Hayek, Kyle)
    intel = gather_intelligence(payments, token_cache, portfolio, cycle)

    # Phase 2: Informed purchases (Coase, Kyle)
    purchases = informed_purchases(payments, token_cache, portfolio, cycle, intel)

    # Phase 3: Adversarial testing (Taleb)
    adversarial_test(payments, token_cache, portfolio, cycle)

    # Phase 4: External exploration (Akerlof) -- EVERY cycle for cross-team transactions
    explore_external(payments, token_cache, portfolio, cycle, intel)

    # Phase 5: Feedback loop (Soros, Ostrom, Hurwicz)
    feedback_loop(payments, token_cache, portfolio, cycle, purchases)

    # Save (Principal-Agent: radical transparency)
    save_reports(portfolio, cycle)


def run_fund():
    """Main autonomous buying loop."""
    payments = create_payments()
    portfolio = Portfolio(TOTAL_BUDGET, MAX_PER_TX)
    token_cache = {}
    cycle = 0

    print("=" * 70)
    print("THE FUND -- Intelligence-Driven Autonomous Buyer")
    print()
    print("  Thesis: Markets are not given; they are made.")
    print()
    print("  Akerlof: Reviews prevent market collapse to lemons")
    print("  Hayek:   Our measurements are decentralized price signals")
    print("  Coase:   We buy capabilities, never build them")
    print("  Soros:   Our reviews change the data we read (reflexivity)")
    print("  Taleb:   Adversarial testing is the economy's immune system")
    print("  Ostrom:  Reputation is a commons we govern through participation")
    print()
    print(f"  Budget: {TOTAL_BUDGET} USDC | Interval: {LOOP_INTERVAL}s")
    print("  Phases: Intel -> Buy -> Adversarial -> Explore -> Feedback")
    print("=" * 70)
    print()

    # Subscribe to all our services (Coase: buy, don't build)
    portfolio.log_decision("INIT", "Subscribing to Agent Economy services...")
    for name, service in OUR_SERVICES.items():
        try:
            payments.plans.order_plan(service["plan_id"])
            portfolio.log_decision("SUBSCRIBE", f"Subscribed to {name}")
        except Exception:
            portfolio.log_decision("SUBSCRIBE", f"Already subscribed to {name}")

    portfolio.log_decision("THESIS",
        "The Fund does not merely observe the agent economy -- it constitutes it. "
        "Our reviews change reputation. Our purchases create revenue signals. "
        "Our switching changes the competitive landscape. We are not passive allocators "
        "of capital; we are active participants in a reflexive system where observation "
        "and reality are entangled.")

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

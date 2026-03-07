"""Mystery shop: test every service and tool from llms.txt as an AI agent would."""
import httpx
import time
import json
import os

from dotenv import load_dotenv
load_dotenv()

from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(PaymentOptions(
    nvm_api_key=os.environ["NVM_API_KEY"], environment="sandbox"
))

PLANS = {
    "oracle":      "73832576591113218627249140062481319784526101948276910427168459563781622307151",
    "underwriter": "108289525728886290523358160114949466457088917231870074042604244210937761689110",
    "gold_star":   "86107591125963957406574553233076282216940031177768083482829930136762279428594",
    "amplifier":   "31307392809981293956301786331179599135979548398803667593789184055010190785367",
    "architect":   "31307392809981293956301786331179599135979548398803667593789184055010190785367",
}

ENDPOINTS = {
    "oracle":      "https://oracle.agenteconomy.io/mcp",
    "underwriter": "https://underwriter.agenteconomy.io/mcp",
    "gold_star":   "https://goldstar.agenteconomy.io/mcp",
    "amplifier":   "https://the-amplifier-production.up.railway.app/mcp",
    "architect":   "https://the-architect-production.up.railway.app/mcp",
}

# Subscribe to all plans
for name, plan_id in PLANS.items():
    try:
        payments.plans.order_plan(plan_id)
    except Exception:
        pass

tokens = {}

def get_token(service):
    if service not in tokens or tokens[service]["exp"] < time.time():
        result = payments.x402.get_x402_access_token(PLANS[service])
        tokens[service] = {"tok": result["accessToken"], "exp": time.time() + 240}
    return tokens[service]["tok"]

def mcp_call(service, tool_name, arguments, timeout=30):
    token = get_token(service)
    endpoint = ENDPOINTS[service]
    start = time.time()
    try:
        resp = httpx.post(
            endpoint,
            headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"},
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
                "id": int(time.time() * 1000) % 99999,
            },
            timeout=timeout,
        )
        elapsed = (time.time() - start) * 1000
        if resp.status_code != 200:
            return {"ok": False, "status": resp.status_code, "body": resp.text[:300], "ms": elapsed}
        body = resp.json()
        result = body.get("result", {})
        content = result.get("content", [])
        text = content[0].get("text", "") if content else ""
        is_error = result.get("isError", False)
        return {
            "ok": not is_error and len(text) > 0,
            "text": text[:500],
            "full_text": text,
            "len": len(text),
            "ms": elapsed,
            "is_error": is_error,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "ms": (time.time() - start) * 1000}


# ============================================================
# TEST EVERY TOOL
# ============================================================
tests = [
    # Oracle
    ("oracle", "marketplace_data", {"side": "sell"}, "should return sellers array"),
    ("oracle", "marketplace_data", {"side": "buy"}, "should return buyers array"),
    ("oracle", "marketplace_data", {}, "default side=all, should return both"),
    ("oracle", "marketplace_search", {"query": "research"}, "should return matching sellers"),
    ("oracle", "marketplace_search", {"query": "nonexistent_xyz_qqq"}, "edge: no results, should return categories fallback"),
    ("oracle", "marketplace_leaderboard", {}, "should return ranked services"),
    ("oracle", "marketplace_leaderboard", {"category": "Research"}, "should filter by Research category"),
    ("oracle", "marketplace_compare", {"service_a": "The Oracle", "service_b": "Cortex"}, "should compare with live health checks"),

    # Underwriter
    ("underwriter", "check_reputation", {"seller_name": "Cortex"}, "should return trust score and badge"),
    ("underwriter", "check_reputation", {"seller_name": "nonexistent_service_xyz"}, "edge: unknown seller, should return unrated"),
    ("underwriter", "submit_review", {
        "seller_name": "The Oracle", "team_name": "Full Stack Agents",
        "quality_score": 4.5, "reliable": True,
        "notes": "Automated QA test - excellent marketplace search", "reviewer": "LLMs.txt QA"
    }, "should accept review and return updated score"),
    ("underwriter", "file_claim", {
        "seller_name": "TestService", "team_name": "TestTeam",
        "reason": "timeout", "credits_lost": 1, "buyer": "LLMs.txt QA"
    }, "should file claim and return claim_id"),
    ("underwriter", "reputation_leaderboard", {}, "should return Hall of Fame and Shame"),
    ("underwriter", "underwriter_stats", {}, "should return aggregate stats"),

    # Gold Star
    ("gold_star", "certification_status", {"seller_name": "The Oracle"}, "should return cert status"),
    ("gold_star", "certification_status", {}, "should return all certifications"),
    ("gold_star", "get_report", {"seller_name": "The Oracle"}, "should return QA report or not_found"),
    ("gold_star", "gold_star_stats", {}, "should return aggregate QA stats"),

    # Amplifier
    ("amplifier", "enrich_with_ads", {"content": "Here are the top AI research services available today.", "ad_style": "inline"}, "should return content + appended ad"),
    ("amplifier", "enrich_with_ads", {"content": "Crypto trading tools comparison.", "ad_style": "json"}, "should return content + JSON ad"),
    ("amplifier", "enrich_with_ads", {"content": "Quick data.", "ad_style": "compact"}, "should return content + compact ad"),
    ("amplifier", "get_ad", {"topic": "AI research", "style": "inline"}, "should return standalone ad"),
    ("amplifier", "get_ad", {"topic": "cloud infrastructure", "style": "json"}, "should return JSON ad"),
    ("amplifier", "ad_stats", {}, "should return impressions and sponsor stats"),

    # Architect (skip orchestrate - 15-45s, test quick_research + pipeline_status)
    ("architect", "pipeline_status", {}, "should return agent list and request count"),
    ("architect", "quick_research", {"query": "AI agent marketplace pricing trends"}, "should return findings and analysis"),
]

print("=" * 80)
print("AGENT ECONOMY - FULL SERVICE QA FROM LLMS.TXT")
print("=" * 80)

results = []
for service, tool, args, expectation in tests:
    label = f"{service}.{tool}"
    print(f"\n--- {label} ---")
    print(f"  Expect: {expectation}")
    timeout = 90 if "research" in tool else 30
    r = mcp_call(service, tool, args, timeout=timeout)
    status = "PASS" if r.get("ok") else "FAIL"
    ms = r.get("ms", 0)
    print(f"  Status: {status} | {ms:.0f}ms | {r.get('len', 0)} bytes")
    if r.get("ok"):
        preview = r.get("text", "")[:250].replace("\n", " ")
        print(f"  Preview: {preview}")
    else:
        err = r.get("body", r.get("error", r.get("text", "unknown")))
        print(f"  Error: {str(err)[:300]}")
    results.append((label, status, ms, r, expectation))

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
passed = sum(1 for _, s, _, _, _ in results if s == "PASS")
failed = sum(1 for _, s, _, _, _ in results if s == "FAIL")
print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
print()
for label, status, ms, r, exp in results:
    icon = "OK" if status == "PASS" else "XX"
    print(f"  [{icon}] {label:50s} {ms:7.0f}ms")
    if status == "FAIL":
        err = r.get("body", r.get("error", r.get("text", "unknown")))
        print(f"        -> {str(err)[:120]}")

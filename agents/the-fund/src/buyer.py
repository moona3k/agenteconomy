"""The Fund — Autonomous buyer that discovers, evaluates, and purchases services."""
import json
import os
import time
import base64

import httpx
from dotenv import load_dotenv
from payments_py import Payments, PaymentOptions

from .portfolio import Portfolio, Transaction

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
TOTAL_BUDGET = float(os.environ.get("TOTAL_BUDGET_USDC", "50"))
MAX_PER_TX = float(os.environ.get("MAX_PER_TRANSACTION", "1.0"))
DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"


def create_payments():
    return Payments.get_instance(
        PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
    )


def discover_sellers(payments) -> list:
    """Fetch all sellers from the hackathon Discovery API."""
    resp = httpx.get(
        DISCOVERY_URL,
        params={"side": "sell"},
        headers={"x-nvm-api-key": NVM_API_KEY},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("sellers", [])


def find_free_plans(sellers: list) -> list:
    """Find sellers with free plans."""
    free = []
    for s in sellers:
        pricing = s.get("pricing", {}).get("perRequest", "")
        plans = s.get("planPricing", [])
        if "free" in pricing.lower() or "0.00" in pricing or "Free" in pricing:
            free.append(s)
            continue
        # Check individual plans for free/zero pricing
        for p in plans:
            if p.get("planPrice", "") in ("0", "0.00", "") or "free" in str(p.get("paymentType", "")).lower():
                free.append(s)
                break
    return free


def find_cheap_plans(sellers: list, max_price: float = 0.10) -> list:
    """Find sellers with cheap USDC plans."""
    cheap = []
    for s in sellers:
        pricing = s.get("pricing", {}).get("perRequest", "")
        # Look for USDC prices
        if "USDC" in pricing:
            try:
                # Extract first number before USDC
                parts = pricing.split("USDC")[0].strip().split()
                price = float(parts[-1])
                if price <= max_price:
                    cheap.append(s)
            except (ValueError, IndexError):
                pass
    return cheap


def is_reachable(url: str) -> bool:
    """Quick check if endpoint is reachable."""
    if not url or "localhost" in url or "127.0.0.1" in url or not url.startswith("http"):
        return False
    try:
        resp = httpx.get(url.rstrip("/") + "/health", timeout=5, follow_redirects=True)
        return resp.status_code < 500
    except Exception:
        try:
            resp = httpx.get(url, timeout=5, follow_redirects=True)
            return resp.status_code < 500
        except Exception:
            return False


def subscribe_to_plan(payments, plan_id: str) -> bool:
    """Subscribe to a plan. Returns True on success."""
    try:
        payments.plans.order_plan(plan_id)
        return True
    except Exception as e:
        print(f"  Subscribe failed: {e}")
        return False


def get_access_token(payments, plan_id: str) -> str:
    """Get an x402 access token for a plan."""
    try:
        result = payments.x402.get_x402_access_token(plan_id)
        return result.get("accessToken", "")
    except Exception as e:
        print(f"  Token failed: {e}")
        return ""


def call_service(endpoint: str, token: str, query: str = "test") -> dict:
    """Call a service endpoint with payment token."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    start = time.time()

    # Try MCP JSON-RPC first
    try:
        headers["Authorization"] = f"Bearer {token}"
        resp = httpx.post(
            endpoint.rstrip("/"),
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1,
            },
            timeout=15,
        )
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            body = resp.json()
            tools = body.get("result", {}).get("tools", [])
            if tools:
                return {
                    "success": True,
                    "type": "mcp",
                    "tools": [t.get("name", "?") for t in tools],
                    "latency_ms": latency,
                    "response_length": len(resp.text),
                }
    except Exception:
        pass

    # Try x402 header style
    try:
        headers["payment-signature"] = token
        resp = httpx.post(
            endpoint.rstrip("/"),
            headers=headers,
            json={"query": query},
            timeout=15,
        )
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            return {
                "success": True,
                "type": "rest",
                "response": resp.text[:500],
                "latency_ms": latency,
                "response_length": len(resp.text),
            }
        elif resp.status_code == 402:
            # Parse 402 for plan info
            pr_header = resp.headers.get("payment-required", "")
            if pr_header:
                try:
                    info = json.loads(base64.b64decode(pr_header))
                    return {
                        "success": False,
                        "type": "needs_payment",
                        "payment_info": info,
                        "latency_ms": latency,
                        "response_length": 0,
                    }
                except Exception:
                    pass
    except Exception:
        pass

    return {"success": False, "type": "unreachable", "latency_ms": 0, "response_length": 0}


def score_response(result: dict) -> float:
    """Score a response quality from 0-10."""
    if not result.get("success"):
        return 0

    score = 5.0  # base score for a successful response

    # Bonus for fast responses
    latency = result.get("latency_ms", 5000)
    if latency < 500:
        score += 2
    elif latency < 1000:
        score += 1
    elif latency > 3000:
        score -= 1

    # Bonus for substantial responses
    length = result.get("response_length", 0)
    if length > 1000:
        score += 1
    if length > 5000:
        score += 1

    # Bonus for MCP (structured)
    if result.get("type") == "mcp":
        score += 1

    return min(10, max(0, score))


def run_fund():
    """Main autonomous buying loop."""
    payments = create_payments()
    portfolio = Portfolio(TOTAL_BUDGET, MAX_PER_TX)

    # Phase 1: Discovery
    portfolio.log_decision("DISCOVER", "Starting marketplace discovery...")
    sellers = discover_sellers(payments)
    portfolio.log_decision("DISCOVER", f"Found {len(sellers)} sellers in marketplace")

    # Filter reachable
    reachable = []
    for s in sellers:
        url = s.get("endpointUrl", "")
        if url and url.startswith("http") and "localhost" not in url:
            reachable.append(s)
    portfolio.log_decision("DISCOVER", f"{len(reachable)} sellers have public endpoints")

    # Phase 2: Subscribe to free plans
    free_plans = find_free_plans(sellers)
    portfolio.log_decision("ALLOCATE", f"Found {len(free_plans)} sellers with free plans — subscribing to all")

    subscribed = []
    for s in free_plans:
        plans = s.get("planPricing", [])
        for p in plans:
            plan_id = p.get("planDid", "")
            if plan_id:
                if subscribe_to_plan(payments, plan_id):
                    subscribed.append({"seller": s, "plan_id": plan_id})
                    portfolio.log_decision(
                        "SUBSCRIBE",
                        f"Subscribed to {s.get('name', '?')} [{s.get('teamName', '?')}] (free)"
                    )
                break  # Only need one plan per seller

    portfolio.log_decision("ALLOCATE", f"Subscribed to {len(subscribed)} free plans")

    # Phase 3: Test and purchase from subscribed services
    portfolio.log_decision("EVALUATE", "Testing subscribed services...")

    for sub in subscribed:
        seller = sub["seller"]
        plan_id = sub["plan_id"]
        endpoint = seller.get("endpointUrl", "")

        if not endpoint or "localhost" in endpoint or not endpoint.startswith("http"):
            continue

        token = get_access_token(payments, plan_id)
        if not token:
            continue

        result = call_service(endpoint, token, query="What services do you offer?")
        quality = score_response(result)

        tx = Transaction(
            timestamp=time.time(),
            seller_name=seller.get("name", "?"),
            team_name=seller.get("teamName", "?"),
            service_category=seller.get("category", "uncategorized"),
            plan_id=plan_id,
            query="service discovery test",
            credits_used=1,
            quality_score=quality,
            response_length=result.get("response_length", 0),
            latency_ms=result.get("latency_ms", 0),
            success=result.get("success", False),
        )
        portfolio.record_transaction(tx)

    # Phase 4: Buy from cheap USDC plans
    cheap = find_cheap_plans(reachable, max_price=0.10)
    portfolio.log_decision("ALLOCATE", f"Found {len(cheap)} cheap USDC sellers (<=0.10 USDC)")

    for s in cheap[:5]:  # Top 5 cheap sellers
        plans = s.get("planPricing", [])
        for p in plans:
            plan_id = p.get("planDid", "")
            if plan_id and p.get("paymentType") == "crypto":
                ok, reason = portfolio.can_spend(0.10)
                if not ok:
                    portfolio.log_decision("BUDGET", f"Cannot spend: {reason}")
                    break

                if subscribe_to_plan(payments, plan_id):
                    token = get_access_token(payments, plan_id)
                    if token:
                        endpoint = s.get("endpointUrl", "")
                        result = call_service(endpoint, token, query="market analysis of AI agents")
                        quality = score_response(result)

                        tx = Transaction(
                            timestamp=time.time(),
                            seller_name=s.get("name", "?"),
                            team_name=s.get("teamName", "?"),
                            service_category=s.get("category", "uncategorized"),
                            plan_id=plan_id,
                            query="market analysis of AI agents",
                            credits_used=1,
                            quality_score=quality,
                            response_length=result.get("response_length", 0),
                            latency_ms=result.get("latency_ms", 0),
                            success=result.get("success", False),
                        )
                        portfolio.record_transaction(tx)
                break

    # Phase 5: Evaluate switching opportunities
    categories = set(p.category for p in portfolio.providers.values())
    for cat in categories:
        portfolio.should_switch(cat)

    # Phase 6: Repeat purchases from best providers
    portfolio.log_decision("REPEAT", "Making repeat purchases from top ROI providers...")
    for cat in categories:
        best = portfolio.get_best_provider(cat)
        if best and best.avg_roi > 0 and len(best.transactions) >= 1:
            # Make a repeat purchase
            last_tx = best.transactions[-1]
            portfolio.log_decision(
                "REPEAT",
                f"Re-purchasing from {best.name} (ROI: {best.avg_roi:.0f}, best in {cat})"
            )
            token = get_access_token(payments, best.plan_id)
            if token:
                result = call_service(best.endpoint or "", token, query="detailed analysis")
                quality = score_response(result)
                tx = Transaction(
                    timestamp=time.time(),
                    seller_name=best.name,
                    team_name=best.team,
                    service_category=cat,
                    plan_id=best.plan_id,
                    query="repeat purchase — detailed analysis",
                    credits_used=1,
                    quality_score=quality,
                    response_length=result.get("response_length", 0),
                    latency_ms=result.get("latency_ms", 0),
                    success=result.get("success", False),
                )
                portfolio.record_transaction(tx)

    # Final report
    report = portfolio.get_report()
    print("\n" + report)

    # Save report
    with open("investment-report.txt", "w") as f:
        f.write(report)

    # Save structured data
    with open("investment-data.json", "w") as f:
        json.dump({
            "budget": portfolio.total_budget,
            "spent": portfolio.spent,
            "remaining": portfolio.remaining,
            "providers": len(portfolio.providers),
            "total_transactions": sum(len(p.transactions) for p in portfolio.providers.values()),
            "switches": portfolio.switches,
            "decisions": portfolio.decisions,
        }, f, indent=2, default=str)

    portfolio.log_decision("COMPLETE", f"Fund run complete. {portfolio.spent:.2f}/{portfolio.total_budget:.2f} USDC spent across {len(portfolio.providers)} providers.")

    return portfolio


def main():
    print("=" * 60)
    print("THE FUND — Autonomous Capital Allocator")
    print("=" * 60)
    print()
    run_fund()


if __name__ == "__main__":
    main()

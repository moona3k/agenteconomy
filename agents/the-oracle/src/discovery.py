"""Fetch and cache hackathon marketplace data from the Discovery API."""
import os
import time
import httpx
from typing import Optional

DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"
CACHE_TTL = 300  # 5 minutes

_cache = {"sellers": None, "buyers": None, "ts": 0, "meta": None}


def fetch_marketplace(side: str = "sell", force: bool = False) -> list:
    """Fetch sellers or buyers from the discovery API. Caches for 5 min."""
    now = time.time()
    key = "sellers" if side == "sell" else "buyers"

    if not force and _cache[key] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache[key]

    api_key = os.environ.get("NVM_API_KEY", "")
    resp = httpx.get(
        DISCOVERY_URL,
        params={"side": side},
        headers={"x-nvm-api-key": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    items = data.get(key, [])
    _cache[key] = items
    _cache["ts"] = now
    if "meta" in data:
        _cache["meta"] = data["meta"]
    return items


def search_sellers(query: str) -> list:
    """Search sellers by name, team, category, or description."""
    sellers = fetch_marketplace("sell")
    q = query.lower()
    results = []
    for s in sellers:
        score = 0
        for field in ["name", "teamName", "category", "description"]:
            val = s.get(field, "").lower()
            if q in val:
                score += 2 if field in ("name", "teamName") else 1
        if any(q in kw.lower() for kw in s.get("keywords", [])):
            score += 1
        if score > 0:
            results.append({**s, "_score": score})
    results.sort(key=lambda x: -x["_score"])
    return results


def _normalize_seller(s: dict) -> dict:
    """Normalize a raw seller entry into a clean, agent-friendly dict."""
    url = s.get("endpointUrl", "")
    is_reachable = bool(url and url.startswith("http") and "localhost" not in url and "127.0.0.1" not in url)

    plans = []
    for p in s.get("planPricing", []):
        plan = {
            "planDid": p.get("planDid", ""),
            "paymentType": p.get("paymentType", "unknown"),
            "planPrice": p.get("planPrice"),
            "pricePerRequest": p.get("pricePerRequest"),
            "priceFormatted": p.get("pricePerRequestFormatted", ""),
            "creditsGranted": p.get("creditsGranted"),
        }
        plans.append(plan)

    pricing_str = s.get("pricing", {}).get("perRequest", "")
    has_free = "free" in pricing_str.lower() or "0.00" in pricing_str or any(
        p.get("planPrice", 1) == 0 or p.get("pricePerRequest", 1) == 0
        for p in s.get("planPricing", [])
    )
    has_crypto = "usdc" in pricing_str.lower() or any(
        p.get("paymentType") == "crypto" for p in s.get("planPricing", [])
    )
    has_fiat = "card" in pricing_str.lower() or any(
        p.get("paymentType") == "fiat" for p in s.get("planPricing", [])
    )

    return {
        "name": s.get("name", ""),
        "teamName": s.get("teamName", ""),
        "category": s.get("category", "uncategorized"),
        "description": s.get("description", ""),
        "endpointUrl": url,
        "reachable": is_reachable,
        "keywords": s.get("keywords", []),
        "pricingLabel": pricing_str,
        "hasFree": has_free,
        "hasCrypto": has_crypto,
        "hasFiat": has_fiat,
        "plans": plans,
        "planCount": len(plans),
        "createdAt": s.get("createdAt", ""),
        "agentDid": s.get("agentDid", ""),
    }


def _normalize_buyer(b: dict) -> dict:
    """Normalize a raw buyer entry into a clean dict."""
    return {
        "name": b.get("name", ""),
        "teamName": b.get("teamName", ""),
        "category": b.get("category", "uncategorized"),
        "description": b.get("description", ""),
        "interests": b.get("interests", ""),
        "createdAt": b.get("createdAt", ""),
    }


def normalize_marketplace() -> dict:
    """Return a clean, normalized snapshot of the full marketplace."""
    sellers_raw = fetch_marketplace("sell")
    buyers_raw = fetch_marketplace("buy")

    sellers = [_normalize_seller(s) for s in sellers_raw]
    buyers = [_normalize_buyer(b) for b in buyers_raw]

    # Category counts
    categories = {}
    for s in sellers:
        cat = s["category"]
        categories.setdefault(cat, 0)
        categories[cat] += 1

    # Team summary
    teams = {}
    for s in sellers:
        t = s["teamName"]
        teams.setdefault(t, {"selling": 0, "buying": 0})
        teams[t]["selling"] += 1
    for b in buyers:
        t = b["teamName"]
        teams.setdefault(t, {"selling": 0, "buying": 0})
        teams[t]["buying"] += 1

    # Pricing stats
    prices = []
    for s in sellers:
        for p in s["plans"]:
            pr = p.get("pricePerRequest") or p.get("planPrice")
            if pr and isinstance(pr, (int, float)) and pr > 0:
                prices.append(pr)
    prices.sort()

    reachable_count = sum(1 for s in sellers if s["reachable"])
    free_count = sum(1 for s in sellers if s["hasFree"])
    crypto_count = sum(1 for s in sellers if s["hasCrypto"])
    fiat_count = sum(1 for s in sellers if s["hasFiat"])

    return {
        "summary": {
            "totalSellers": len(sellers),
            "totalBuyers": len(buyers),
            "reachableEndpoints": reachable_count,
            "categoriesCount": len(categories),
            "uniqueTeams": len(teams),
            "freeServices": free_count,
            "cryptoServices": crypto_count,
            "fiatServices": fiat_count,
            "medianPrice": prices[len(prices) // 2] if prices else 0,
            "timestamp": (_cache.get("meta") or {}).get("timestamp", ""),
        },
        "categories": categories,
        "sellers": sellers,
        "buyers": buyers,
    }

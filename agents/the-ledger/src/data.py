"""Marketplace data fetcher and analyzer."""
import os
import time
import httpx
from typing import Optional

DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"
CACHE_TTL = 300

_cache = {"sellers": None, "buyers": None, "ts": 0, "analysis": None, "meta": None}


def _api_key():
    return os.environ.get("NVM_API_KEY", "")


def fetch_sellers(force: bool = False) -> list:
    now = time.time()
    if not force and _cache["sellers"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["sellers"]
    try:
        resp = httpx.get(DISCOVERY_URL, params={"side": "sell"},
                         headers={"x-nvm-api-key": _api_key()}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        sellers = data.get("sellers", [])
        _cache["sellers"] = sellers
        _cache["ts"] = now
        _cache["analysis"] = None
        _cache["meta"] = data.get("meta", {})
        return sellers
    except Exception as e:
        print(f"[data] fetch_sellers error: {e}")
        return _cache["sellers"] or []


def fetch_buyers(force: bool = False) -> list:
    now = time.time()
    if not force and _cache["buyers"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["buyers"]
    try:
        resp = httpx.get(DISCOVERY_URL, params={"side": "buy"},
                         headers={"x-nvm-api-key": _api_key()}, timeout=15)
        resp.raise_for_status()
        buyers = resp.json().get("buyers", [])
        _cache["buyers"] = buyers
        return buyers
    except Exception as e:
        print(f"[data] fetch_buyers error: {e}")
        return _cache["buyers"] or []


def analyze_marketplace() -> dict:
    if _cache.get("analysis"):
        return _cache["analysis"]

    sellers = fetch_sellers()
    buyers = fetch_buyers()

    # Category distribution
    categories = {}
    for s in sellers:
        cat = s.get("category", "uncategorized")
        categories.setdefault(cat, []).append(s.get("name", "?"))

    # Team activity
    teams = {}
    for s in sellers:
        team = s.get("teamName", "?")
        teams.setdefault(team, {"selling": [], "buying": []})
        teams[team]["selling"].append(s.get("name", "?"))
    for b in buyers:
        team = b.get("teamName", "?")
        teams.setdefault(team, {"selling": [], "buying": []})
        teams[team]["buying"].append(b.get("name", "?"))

    # Payment types — check both pricing string and planPricing array
    payment_types = {"crypto": 0, "fiat": 0, "free": 0}
    for s in sellers:
        pricing_str = str(s.get("pricing", {}).get("perRequest", "")).lower()
        plans = s.get("planPricing", [])

        has_crypto = "usdc" in pricing_str or any(p.get("paymentType") == "crypto" for p in plans)
        has_fiat = "card" in pricing_str or any(p.get("paymentType") == "fiat" for p in plans)
        has_free = "free" in pricing_str or "0.00" in pricing_str or any(
            p.get("planPrice", 1) == 0 or p.get("pricePerRequest", 1) == 0 for p in plans
        )

        if has_crypto:
            payment_types["crypto"] += 1
        if has_fiat:
            payment_types["fiat"] += 1
        if has_free:
            payment_types["free"] += 1

    # Reachability
    reachable = 0
    localhost_count = 0
    for s in sellers:
        url = s.get("endpointUrl", "")
        if not url or not url.startswith("http"):
            continue
        if "localhost" in url or "127.0.0.1" in url:
            localhost_count += 1
        else:
            reachable += 1

    # Teams doing both
    both = [t for t, v in teams.items() if v["selling"] and v["buying"]]

    # Keyword frequency analysis
    keyword_freq = {}
    for s in sellers:
        for kw in s.get("keywords", []):
            kw_lower = kw.lower().strip()
            if kw_lower:
                keyword_freq[kw_lower] = keyword_freq.get(kw_lower, 0) + 1
    top_keywords = sorted(keyword_freq.items(), key=lambda x: -x[1])[:20]

    # Pricing analysis
    price_points = []
    for s in sellers:
        for p in s.get("planPricing", []):
            price = p.get("pricePerRequest") or p.get("planPrice")
            if price and isinstance(price, (int, float)) and price > 0:
                price_points.append({
                    "service": s.get("name", "?"),
                    "team": s.get("teamName", "?"),
                    "price": price,
                    "type": p.get("paymentType", "unknown"),
                    "formatted": p.get("pricePerRequestFormatted", f"{price} USDC"),
                })

    price_points.sort(key=lambda x: x["price"])

    # Protocol analysis
    protocols = {}
    for s in sellers:
        schema = s.get("apiSchema", {})
        if isinstance(schema, dict):
            endpoint = schema.get("endpoint", "")
            if "POST" in endpoint:
                protocols["REST POST"] = protocols.get("REST POST", 0) + 1
            elif "GET" in endpoint:
                protocols["REST GET"] = protocols.get("REST GET", 0) + 1

        url = s.get("endpointUrl", "")
        if "/mcp" in url:
            protocols["MCP"] = protocols.get("MCP", 0) + 1

    # Registration timeline
    timestamps = []
    for s in sellers:
        ts = s.get("createdAt")
        if ts:
            timestamps.append(ts)
    timestamps.sort()

    # Buyer interests
    buyer_interests = {}
    for b in buyers:
        interests = b.get("interests", "")
        if interests:
            for interest in interests.split(","):
                interest = interest.strip().lower()
                if interest:
                    buyer_interests[interest] = buyer_interests.get(interest, 0) + 1

    buyer_categories = {}
    for b in buyers:
        cat = b.get("category", "uncategorized")
        buyer_categories[cat] = buyer_categories.get(cat, 0) + 1

    analysis = {
        "summary": {
            "total_sellers": len(sellers),
            "total_buyers": len(buyers),
            "unique_teams_selling": len(set(s.get("teamName") for s in sellers)),
            "unique_teams_buying": len(set(b.get("teamName") for b in buyers)),
            "teams_both": len(both),
            "teams_both_names": both,
            "reachable_endpoints": reachable,
            "localhost_endpoints": localhost_count,
            "categories": len(categories),
            "api_timestamp": (_cache.get("meta") or {}).get("timestamp", ""),
        },
        "categories": {
            cat: {"count": len(names), "services": names}
            for cat, names in sorted(categories.items())
        },
        "payment_types": payment_types,
        "teams": {
            t: v
            for t, v in sorted(
                teams.items(),
                key=lambda x: -(len(x[1]["selling"]) + len(x[1]["buying"]))
            )
        },
        "power_teams": [
            {
                "team": t,
                "services_selling": len(v["selling"]),
                "services_buying": len(v["buying"]),
            }
            for t, v in sorted(
                teams.items(),
                key=lambda x: -(len(x[1]["selling"]) + len(x[1]["buying"]))
            )
            if len(v["selling"]) + len(v["buying"]) >= 2
        ],
        "top_keywords": top_keywords,
        "pricing_landscape": {
            "cheapest": price_points[:5] if price_points else [],
            "most_expensive": price_points[-5:][::-1] if price_points else [],
            "median_price": price_points[len(price_points)//2]["price"] if price_points else 0,
            "total_priced": len(price_points),
        },
        "protocols": protocols,
        "buyer_interests": sorted(buyer_interests.items(), key=lambda x: -x[1])[:15],
        "buyer_categories": buyer_categories,
        "timeline": {
            "earliest": timestamps[0] if timestamps else None,
            "latest": timestamps[-1] if timestamps else None,
            "total_registered": len(timestamps),
        },
    }
    _cache["analysis"] = analysis
    return analysis


def get_seller_profile(name_or_team: str) -> Optional[dict]:
    """Get detailed profile for a specific seller."""
    sellers = fetch_sellers()
    q = name_or_team.lower()
    for s in sellers:
        if q in s.get("name", "").lower() or q in s.get("teamName", "").lower():
            return s
    return None

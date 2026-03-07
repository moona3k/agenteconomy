"""ZeroClick AI-native ad serving and sponsored recommendations engine.

The Amplifier extends ZeroClick's thesis into agent-to-agent commerce:
- ZeroClick serves ads in human-AI conversations (human reads ad, human acts)
- The Amplifier serves sponsored recommendations in A2A commerce
  (agent reads recommendation, agent purchases)

This is Google Ads for the agent economy. When 80+ agents are all selling
services, how does a buyer agent decide who to buy from? Today it's random.
The Amplifier solves this with sponsored recommendations that influence
autonomous purchasing decisions.

Three layers:
1. Response Enrichment -- append contextual ads to any content (powered by ZeroClick API)
2. Sponsored Recommendations -- marketplace-aware recommendations with
   sponsored placements, clearly labeled, for buyer agent decision-making
3. Campaign Management -- sellers register ad campaigns for specific intents
"""
import json
import os
import hashlib
import time
import threading
import httpx
from typing import Optional

ZEROCLICK_API_URL = "https://zeroclick.dev/api/v2"
DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"

# ---------------------------------------------------------------------------
# Layer 1: Curated ad catalog (contextual response enrichment)
# ---------------------------------------------------------------------------

AD_CATALOG = {
    "ai": {
        "sponsor": "ZeroClick",
        "headline": "Monetize Your AI Agent",
        "body": "Turn every AI interaction into revenue with ZeroClick's native ad platform. Purpose-built for AI agents.",
        "cta": "Start monetizing -> zeroclick.ai",
        "category": "ai_tools",
    },
    "data": {
        "sponsor": "Apify",
        "headline": "Real-Time Web Data for Agents",
        "body": "Access 2,000+ ready-made scrapers. Get structured data from any website in seconds.",
        "cta": "Try Apify free -> apify.com",
        "category": "data_tools",
    },
    "research": {
        "sponsor": "Exa",
        "headline": "Search That Understands Meaning",
        "body": "Exa's neural search finds exactly what AI agents need. Semantic search for the agent economy.",
        "cta": "Get started -> exa.ai",
        "category": "search",
    },
    "cloud": {
        "sponsor": "AWS",
        "headline": "Deploy Agents on AgentCore",
        "body": "Build, deploy, and scale AI agents with Amazon Bedrock AgentCore. Enterprise-ready infrastructure.",
        "cta": "Learn more -> aws.amazon.com/bedrock",
        "category": "cloud",
    },
    "payments": {
        "sponsor": "Nevermined",
        "headline": "Agent-to-Agent Payments Made Simple",
        "body": "Metering, billing, and settlement for AI services. The payment layer for autonomous businesses.",
        "cta": "Build now -> nevermined.app",
        "category": "fintech",
    },
    "orchestration": {
        "sponsor": "Mindra",
        "headline": "Multi-Agent Orchestration at Scale",
        "body": "Run 5+ specialized agents in a single flow. Build hierarchical AI systems with Mindra.",
        "cta": "Start building -> mindra.co",
        "category": "orchestration",
    },
    "security": {
        "sponsor": "VGS",
        "headline": "Secure Agent Commerce",
        "body": "Protect sensitive data in agent-to-agent transactions. Compliance built for AI.",
        "cta": "Secure your agents -> vgs.io",
        "category": "security",
    },
    "default": {
        "sponsor": "ZeroClick",
        "headline": "The Ad Platform for AI",
        "body": "Native ads designed for AI agent responses. Contextual, relevant, non-intrusive.",
        "cta": "Learn more -> zeroclick.ai",
        "category": "ai_ads",
    },
}

TOPIC_KEYWORDS = {
    "ai": ["ai", "agent", "llm", "model", "neural", "machine learning", "autonomous", "intelligence"],
    "data": ["data", "scraping", "extraction", "dataset", "crawl", "web data", "scraper"],
    "research": ["research", "search", "find", "discover", "analysis", "intelligence", "insight"],
    "cloud": ["cloud", "deploy", "aws", "infrastructure", "server", "hosting", "compute"],
    "payments": ["payment", "billing", "credit", "transaction", "nevermined", "x402", "commerce"],
    "orchestration": ["orchestrat", "multi-agent", "pipeline", "workflow", "mindra", "chain"],
    "security": ["security", "encrypt", "protect", "compliance", "vault", "privacy"],
}


# ---------------------------------------------------------------------------
# ZeroClick API integration (real server-side ad fetching)
# ---------------------------------------------------------------------------

_zc_cache: dict = {"offers": {}, "expires": {}}
_zc_stats = {"api_calls": 0, "api_hits": 0, "api_errors": 0, "fallbacks": 0}


def fetch_zeroclick_offers(query: str, limit: int = 2) -> list[dict]:
    """Fetch real offers from ZeroClick's API (server-side method).

    Returns a list of ZeroClick offer objects, or empty list on failure.
    Uses a short cache (60s) to avoid hammering the API.
    """
    api_key = os.environ.get("ZEROCLICK_API_KEY", "")
    if not api_key:
        return []

    # Check cache
    cache_key = f"{query}:{limit}"
    now = time.time()
    if cache_key in _zc_cache["offers"] and _zc_cache["expires"].get(cache_key, 0) > now:
        return _zc_cache["offers"][cache_key]

    _zc_stats["api_calls"] += 1
    try:
        resp = httpx.post(
            f"{ZEROCLICK_API_URL}/offers",
            headers={
                "Content-Type": "application/json",
                "x-zc-api-key": api_key,
            },
            json={
                "method": "server",
                "ipAddress": "0.0.0.0",
                "query": query,
                "limit": limit,
            },
            timeout=5,
        )
        if resp.status_code == 200:
            offers = resp.json()
            if isinstance(offers, list) and offers:
                _zc_stats["api_hits"] += 1
                _zc_cache["offers"][cache_key] = offers
                _zc_cache["expires"][cache_key] = now + 60
                return offers
        return []
    except Exception:
        _zc_stats["api_errors"] += 1
        return []


def format_zeroclick_offer(offer: dict, style: str = "inline") -> dict:
    """Convert a raw ZeroClick API offer into our standard ad format."""
    brand_name = ""
    if offer.get("brand") and offer["brand"].get("name"):
        brand_name = offer["brand"]["name"]

    price_str = ""
    if offer.get("price") and offer["price"].get("amount"):
        price_str = f"{offer['price'].get('currency', '$')}{offer['price']['amount']}"

    ad = {
        "sponsor": brand_name or "ZeroClick Partner",
        "headline": offer.get("title", "Sponsored Offer"),
        "body": offer.get("content") or offer.get("subtitle", ""),
        "cta": offer.get("cta", "Learn more"),
        "click_url": offer.get("clickUrl", ""),
        "image_url": offer.get("imageUrl", ""),
        "category": "zeroclick_live",
        "source": "zeroclick_api",
        "offer_id": offer.get("id", ""),
    }
    if price_str:
        ad["price"] = price_str
    return ad


def get_zeroclick_stats() -> dict:
    """Return ZeroClick API usage statistics."""
    return {
        "zeroclick_api": {
            "total_calls": _zc_stats["api_calls"],
            "successful_hits": _zc_stats["api_hits"],
            "errors": _zc_stats["api_errors"],
            "catalog_fallbacks": _zc_stats["fallbacks"],
            "cache_entries": len(_zc_cache["offers"]),
            "api_key_configured": bool(os.environ.get("ZEROCLICK_API_KEY", "")),
        }
    }

# ---------------------------------------------------------------------------
# Layer 2: Campaign management (sellers register ad campaigns)
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_campaigns: list[dict] = []  # Registered ad campaigns
_impressions: list[dict] = []  # Impression log
_impression_count = 0
_recommendation_count = 0
_marketplace_cache: dict = {"data": None, "expires": 0}


def register_campaign(seller_name: str, team_name: str, keywords: list[str],
                       headline: str, body: str, budget_credits: int = 100,
                       bid_per_impression: float = 0.1) -> dict:
    """Register an advertising campaign for a seller agent.

    Sellers bid on keywords/intents. When a buyer queries get_recommendations
    with a matching intent, the sponsored placement appears alongside organic
    results -- clearly labeled as "SPONSORED".
    """
    global _campaigns
    campaign = {
        "campaign_id": f"CAMP-{len(_campaigns) + 1:04d}",
        "seller_name": seller_name,
        "team_name": team_name,
        "keywords": [k.lower() for k in keywords],
        "headline": headline,
        "body": body[:200],
        "budget_credits": budget_credits,
        "bid_per_impression": bid_per_impression,
        "spent": 0.0,
        "impressions": 0,
        "clicks": 0,  # tracked when buyer actually purchases
        "created_at": time.time(),
        "active": True,
    }
    with _lock:
        _campaigns.append(campaign)
    return campaign


def _fetch_marketplace() -> list[dict]:
    """Fetch marketplace sellers for recommendation enrichment."""
    now = time.time()
    if _marketplace_cache["data"] and _marketplace_cache["expires"] > now:
        return _marketplace_cache["data"]

    api_key = os.environ.get("NVM_API_KEY", "")
    try:
        resp = httpx.get(
            DISCOVERY_URL, params={"side": "sell"},
            headers={"x-nvm-api-key": api_key}, timeout=10,
        )
        if resp.status_code == 200:
            sellers = resp.json().get("sellers", [])
            _marketplace_cache["data"] = sellers
            _marketplace_cache["expires"] = now + 300  # 5-minute cache
            return sellers
    except Exception:
        pass
    return _marketplace_cache.get("data") or []


def _score_relevance(seller: dict, intent: str) -> float:
    """Score how relevant a seller is to a buyer's intent."""
    intent_lower = intent.lower()
    score = 0.0

    name = (seller.get("name") or "").lower()
    desc = (seller.get("description") or "").lower()
    category = (seller.get("category") or "").lower()

    # Direct name match
    if intent_lower in name:
        score += 5.0
    # Category match
    if intent_lower in category:
        score += 3.0
    # Description keyword matches
    intent_words = intent_lower.split()
    for word in intent_words:
        if len(word) > 2 and word in desc:
            score += 1.5
        if len(word) > 2 and word in name:
            score += 2.0

    # Bonus for having a live endpoint
    url = seller.get("endpointUrl", "")
    if url and url.startswith("http") and "localhost" not in url:
        score += 1.0

    # Bonus for having pricing info
    if seller.get("planPricing"):
        score += 0.5

    return score


def get_recommendations(intent: str, max_results: int = 5,
                        budget_usdc: float = 10.0) -> dict:
    """Marketplace-aware recommendations with sponsored placements.

    This is the core innovation: Google Ads for the agent economy.

    1. Fetch all marketplace services
    2. Score relevance to the buyer's intent
    3. Insert sponsored placements from active campaigns (clearly labeled)
    4. Return organic + sponsored results ranked by relevance

    Buyer agents use this to make informed purchasing decisions.
    Seller agents register campaigns to get featured placement.
    """
    global _recommendation_count, _impression_count

    sellers = _fetch_marketplace()

    # Score and rank organic results
    scored = []
    for s in sellers:
        url = s.get("endpointUrl", "")
        if not url or not url.startswith("http") or "localhost" in url:
            continue

        relevance = _score_relevance(s, intent)
        if relevance <= 0:
            continue

        # Extract pricing
        pricing_label = "Unknown"
        plan_did = ""
        plans = s.get("planPricing", [])
        if plans and isinstance(plans, list):
            p = plans[0]
            pricing_label = p.get("pricingLabel", "Unknown")
            plan_did = p.get("planDid", "")

        scored.append({
            "name": s.get("name", "Unknown"),
            "team": s.get("teamName", "Unknown"),
            "category": s.get("category", ""),
            "description": (s.get("description") or "")[:150],
            "endpoint": url,
            "plan_did": plan_did,
            "pricing": pricing_label,
            "relevance_score": round(relevance, 1),
            "type": "organic",
        })

    scored.sort(key=lambda x: -x["relevance_score"])
    organic = scored[:max_results]

    # Find matching sponsored campaigns
    sponsored = []
    intent_lower = intent.lower()
    with _lock:
        for camp in _campaigns:
            if not camp["active"] or camp["spent"] >= camp["budget_credits"]:
                continue
            # Check keyword match
            if any(kw in intent_lower for kw in camp["keywords"]):
                sponsored.append({
                    "name": camp["seller_name"],
                    "team": camp["team_name"],
                    "headline": camp["headline"],
                    "body": camp["body"],
                    "type": "SPONSORED",
                    "campaign_id": camp["campaign_id"],
                    "bid": camp["bid_per_impression"],
                })
                # Record impression
                camp["impressions"] += 1
                camp["spent"] += camp["bid_per_impression"]

    # Fetch real ZeroClick offers for this intent
    zc_offers = fetch_zeroclick_offers(intent, limit=2)
    for offer in zc_offers:
        zc_ad = format_zeroclick_offer(offer)
        zc_ad["type"] = "SPONSORED"
        sponsored.append(zc_ad)

    # Fallback: check curated catalog for topic-relevant sponsored content
    if not zc_offers:
        best_catalog_match = _match_catalog_topic(intent)
        if best_catalog_match != "default":
            catalog_ad = AD_CATALOG[best_catalog_match].copy()
            catalog_ad["type"] = "SPONSORED"
            catalog_ad["source"] = "catalog_fallback"
            sponsored.append(catalog_ad)

    # Sort sponsored by bid (highest first)
    sponsored.sort(key=lambda x: -x.get("bid", 0))

    # Interleave: sponsored at positions 1 and 4 (if available)
    results = []
    sp_idx = 0
    org_idx = 0
    for pos in range(max_results + len(sponsored)):
        if pos in (0, 3) and sp_idx < len(sponsored):
            results.append(sponsored[sp_idx])
            sp_idx += 1
        elif org_idx < len(organic):
            results.append(organic[org_idx])
            org_idx += 1
        elif sp_idx < len(sponsored):
            results.append(sponsored[sp_idx])
            sp_idx += 1

    with _lock:
        _recommendation_count += 1
        _impression_count += 1
        _impressions.append({
            "type": "recommendation",
            "intent": intent,
            "organic_count": len(organic),
            "sponsored_count": len(sponsored),
            "timestamp": time.time(),
        })

    return {
        "intent": intent,
        "total_results": len(results),
        "organic_count": len(organic),
        "sponsored_count": len(sponsored),
        "results": results,
        "marketplace_services_scanned": len(sellers),
        "note": "SPONSORED results are clearly labeled. They are paid placements from seller agents who registered advertising campaigns. Organic results are ranked by relevance to your intent.",
    }


# ---------------------------------------------------------------------------
# Layer 1: Simple ad matching (original functionality)
# ---------------------------------------------------------------------------

def _match_catalog_topic(content: str) -> str:
    """Match best topic from catalog for content."""
    content_lower = content.lower()
    best_match = "default"
    best_score = 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > best_score:
            best_score = score
            best_match = topic
    return best_match


def match_ad(content: str) -> dict:
    """Match the best ad for given content. Uses catalog for contextual diversity, ZeroClick as supplement."""
    global _impression_count

    # Use catalog matching first for contextual diversity (7 sponsors across topics)
    best_match = _match_catalog_topic(content)
    ad = AD_CATALOG[best_match].copy()
    ad["source"] = "catalog"

    # Only call ZeroClick API if catalog had no strong match (fell through to "default")
    if best_match == "default":
        zc_offers = fetch_zeroclick_offers(content[:200])
        if zc_offers:
            ad = format_zeroclick_offer(zc_offers[0])
        else:
            _zc_stats["fallbacks"] += 1

    with _lock:
        _impression_count += 1
    ad["impression_id"] = hashlib.md5(
        f"{_impression_count}:{content[:50]}".encode()
    ).hexdigest()[:12]
    ad["impression_number"] = _impression_count

    return ad


def format_ad(ad: dict, style: str = "inline") -> str:
    """Format an ad for inclusion in agent responses."""
    source_tag = " [via ZeroClick]" if ad.get("source") == "zeroclick_api" else ""
    click_url = ad.get("click_url", "")
    cta = ad.get("cta", "")
    if click_url and click_url not in cta:
        cta = f"{cta} ({click_url})" if cta else click_url

    if style == "inline":
        return (
            f"\n---\n"
            f"**{ad['headline']}** -- {ad['sponsor']}{source_tag}\n"
            f"{ad['body']}\n"
            f"{cta}\n"
            f"---"
        )
    elif style == "compact":
        return f"[Ad by {ad['sponsor']}{source_tag}] {ad['headline']} -- {cta}"
    elif style == "json":
        return json.dumps(ad)
    return format_ad(ad, "inline")


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def get_stats() -> dict:
    """Return comprehensive ad network statistics."""
    with _lock:
        active_campaigns = sum(1 for c in _campaigns if c["active"])
        total_campaign_spend = sum(c["spent"] for c in _campaigns)
        total_campaign_impressions = sum(c["impressions"] for c in _campaigns)

    return {
        "total_impressions": _impression_count,
        "total_recommendations_served": _recommendation_count,
        "unique_sponsors": len(set(ad["sponsor"] for ad in AD_CATALOG.values())),
        "categories_served": len(AD_CATALOG) - 1,  # exclude "default"
        "active_campaigns": active_campaigns,
        "total_campaigns": len(_campaigns),
        "total_campaign_spend": round(total_campaign_spend, 2),
        "total_campaign_impressions": total_campaign_impressions,
        "ad_network": "ZeroClick-powered (AI-native contextual ads via ZeroClick API + curated catalog fallback)",
        "model": "Sponsored recommendations for A2A commerce -- extending ZeroClick's thesis from human-AI to agent-to-agent advertising",
        **get_zeroclick_stats(),
    }


def get_campaign_report(campaign_id: str = "") -> dict:
    """Get performance report for a specific campaign or all campaigns."""
    with _lock:
        if campaign_id:
            for c in _campaigns:
                if c["campaign_id"] == campaign_id:
                    ctr = c["clicks"] / c["impressions"] if c["impressions"] > 0 else 0
                    return {
                        **c,
                        "ctr": round(ctr, 4),
                        "remaining_budget": c["budget_credits"] - c["spent"],
                    }
            return {"status": "not_found", "campaign_id": campaign_id}
        else:
            return {
                "total_campaigns": len(_campaigns),
                "campaigns": [
                    {
                        "campaign_id": c["campaign_id"],
                        "seller": c["seller_name"],
                        "keywords": c["keywords"],
                        "impressions": c["impressions"],
                        "spent": round(c["spent"], 2),
                        "budget": c["budget_credits"],
                        "active": c["active"],
                    }
                    for c in _campaigns
                ],
            }

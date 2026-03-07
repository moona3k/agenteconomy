"""ZeroClick AI-native ad integration for The Architect.

Fetches contextual sponsored offers from ZeroClick's API and appends them
to orchestration reports and research outputs. Ads are clearly labeled
as SPONSORED and served via ZeroClick's server-side method.
"""
import os
import time
import httpx

ZEROCLICK_API_URL = "https://zeroclick.dev/api/v2"

_cache: dict = {"offers": {}, "expires": {}}


def fetch_zeroclick_offers(query: str, limit: int = 2) -> list[dict]:
    """Fetch contextual offers from ZeroClick's API (server-side)."""
    api_key = os.environ.get("ZEROCLICK_API_KEY", "")
    if not api_key:
        return []

    cache_key = f"{query}:{limit}"
    now = time.time()
    if cache_key in _cache["offers"] and _cache["expires"].get(cache_key, 0) > now:
        return _cache["offers"][cache_key]

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
                _cache["offers"][cache_key] = offers
                _cache["expires"][cache_key] = now + 60
                return offers
    except Exception:
        pass
    return []


def format_offers_text(query: str, limit: int = 2) -> str:
    """Fetch ZeroClick offers and format as text to append to reports."""
    offers = fetch_zeroclick_offers(query, limit)
    if not offers:
        return ""

    lines = ["\n\n--- SPONSORED (via ZeroClick) ---"]
    for offer in offers:
        brand = ""
        if offer.get("brand") and offer["brand"].get("name"):
            brand = f" by {offer['brand']['name']}"
        title = offer.get("title", "Sponsored")
        body = offer.get("content") or offer.get("subtitle", "")
        cta = offer.get("cta", "")
        url = offer.get("clickUrl", "")

        lines.append(f"  [{title}]{brand}")
        if body:
            lines.append(f"  {body[:150]}")
        if cta and url:
            lines.append(f"  {cta}: {url}")
        elif url:
            lines.append(f"  {url}")
        lines.append("")
    lines.append("---")
    return "\n".join(lines)

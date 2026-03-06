#!/usr/bin/env python3
"""Marketplace Snapshot — comprehensive audit of all agent services.

Pulls all sellers from the Nevermined Discovery API, tests each endpoint,
and generates a timestamped report folder with an MD file per service.

Usage:
    python3 reports/snapshot.py

Requires: httpx, python-dotenv (or just set NVM_API_KEY env var)

Output:
    reports/YYYY-MM-DD-HHMMSS/
        _index.md          — Summary of all services
        cortex.md          — Individual service report
        trustnet.md        — ...
        ...
        _raw.json          — Raw API response for archival
"""
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import httpx
except ImportError:
    print("Error: httpx required. Install with: pip install httpx")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    # Try loading from various .env locations
    for env_path in [
        Path(__file__).parent.parent / "agents" / "the-fund" / ".env",
        Path(__file__).parent.parent / "agents" / "the-gold-star" / ".env",
        Path(__file__).parent.parent / ".env",
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"
NVM_API_KEY = os.environ.get("NVM_API_KEY", "")


def slugify(name: str) -> str:
    """Convert a service name to a filename-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug or "unknown"


async def fetch_marketplace() -> dict:
    """Fetch sellers and buyers from the Discovery API."""
    headers = {}
    if NVM_API_KEY:
        headers["x-nvm-api-key"] = NVM_API_KEY

    async with httpx.AsyncClient(timeout=20) as client:
        sellers_resp = await client.get(DISCOVERY_URL, params={"side": "sell"}, headers=headers)
        buyers_resp = await client.get(DISCOVERY_URL, params={"side": "buy"}, headers=headers)

    sellers_data = sellers_resp.json()
    buyers_data = buyers_resp.json()

    return {
        "sellers": sellers_data.get("sellers", []),
        "buyers": buyers_data.get("buyers", []),
        "meta_sellers": sellers_data.get("meta", {}),
        "meta_buyers": buyers_data.get("meta", {}),
    }


async def test_endpoint(url: str, test_type: str = "health") -> dict:
    """Test an endpoint and return results."""
    if not url or "localhost" in url or "127.0.0.1" in url or not url.startswith("http"):
        return {"status": "skipped", "reason": "localhost or invalid URL"}

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    results = {
        "base_url": base,
        "registered_url": url,
    }

    # Health check
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            start = time.time()
            resp = await client.get(f"{base}/health")
            latency = (time.time() - start) * 1000
            results["health"] = {
                "status_code": resp.status_code,
                "latency_ms": round(latency, 1),
                "ok": resp.status_code == 200,
                "body": resp.text[:300],
            }
    except Exception as e:
        results["health"] = {"ok": False, "error": str(e)[:200]}

    # MCP tools/list
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            start = time.time()
            resp = await client.post(f"{base}/mcp", json={
                "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1,
            })
            latency = (time.time() - start) * 1000
            body = resp.json() if resp.status_code == 200 else {}
            tools = []
            if isinstance(body, dict):
                result_obj = body.get("result", {})
                if isinstance(result_obj, dict):
                    tools = result_obj.get("tools", [])

            results["mcp"] = {
                "status_code": resp.status_code,
                "latency_ms": round(latency, 1),
                "reachable": resp.status_code < 500,
                "tools_found": len(tools),
                "tool_names": [t.get("name", "?") for t in tools] if tools else [],
                "tools_detail": [
                    {
                        "name": t.get("name", "?"),
                        "description": t.get("description", "")[:200],
                    }
                    for t in tools
                ],
                "raw_response": resp.text[:500] if not tools else "",
            }
    except Exception as e:
        results["mcp"] = {"reachable": False, "error": str(e)[:200]}

    # Direct endpoint test (the registered URL)
    if url != base and url.startswith("http"):
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                start = time.time()
                # Try GET first
                resp = await client.get(url)
                latency = (time.time() - start) * 1000
                results["direct_endpoint"] = {
                    "method": "GET",
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                    "body_preview": resp.text[:500],
                }
        except Exception as e:
            results["direct_endpoint"] = {"error": str(e)[:200]}

    return results


def classify_endpoint(seller: dict) -> str:
    """Classify what type of service this is."""
    url = seller.get("endpointUrl", "")
    if not url:
        return "no-endpoint"
    if "localhost" in url or "127.0.0.1" in url:
        return "localhost"
    if "/mcp" in url:
        return "mcp-server"
    return "rest-api"


def extract_pricing(seller: dict) -> dict:
    """Extract clean pricing info."""
    pricing = seller.get("pricing", {})
    plans = seller.get("planPricing", [])

    has_free = False
    cheapest = None
    payment_types = set()

    for p in plans:
        if not isinstance(p, dict):
            continue
        price = p.get("planPrice", p.get("pricePerRequest", 999))
        ptype = p.get("paymentType", "unknown")
        payment_types.add(ptype)

        if price == 0 or str(price) == "0":
            has_free = True
        elif cheapest is None or float(price) < float(cheapest.get("price", 999)):
            cheapest = {
                "price": price,
                "formatted": p.get("pricePerRequestFormatted", str(price)),
                "type": ptype,
                "plan_did": p.get("planDid", ""),
            }

    return {
        "display_price": pricing.get("perRequest", "unknown"),
        "has_free_plan": has_free,
        "cheapest_paid": cheapest,
        "payment_types": list(payment_types),
        "num_plans": len(plans),
    }


def generate_service_md(seller: dict, test_results: dict, pricing: dict,
                        endpoint_type: str) -> str:
    """Generate a detailed MD report for a single service."""
    name = seller.get("name", "Unknown")
    team = seller.get("teamName", "Unknown")
    category = seller.get("category", "Unknown")
    description = seller.get("description", "No description provided.")
    keywords = seller.get("keywords", [])
    endpoint_url = seller.get("endpointUrl", "None")
    api_schema = seller.get("apiSchema", [])
    created = seller.get("createdAt", "Unknown")

    lines = [
        f"# {name}",
        "",
        f"**Team:** {team}",
        f"**Category:** {category}",
        f"**Endpoint Type:** {endpoint_type}",
        f"**Registered:** {created}",
        "",
        "---",
        "",
        "## Description",
        "",
        description,
        "",
    ]

    # Keywords
    if keywords:
        lines.extend([
            "## Keywords",
            "",
            ", ".join(f"`{k}`" for k in keywords),
            "",
        ])

    # Pricing
    lines.extend([
        "## Pricing",
        "",
        f"- **Display price:** {pricing['display_price']}",
        f"- **Free plan:** {'Yes' if pricing['has_free_plan'] else 'No'}",
        f"- **Payment types:** {', '.join(pricing['payment_types'])}",
        f"- **Number of plans:** {pricing['num_plans']}",
    ])
    if pricing.get("cheapest_paid"):
        cp = pricing["cheapest_paid"]
        lines.append(f"- **Cheapest paid:** {cp['formatted']} ({cp['type']})")
    lines.append("")

    # Endpoint
    lines.extend([
        "## Endpoint",
        "",
        f"- **URL:** `{endpoint_url}`",
        f"- **Type:** {endpoint_type}",
        "",
    ])

    # API Schema
    if api_schema:
        lines.extend(["## API Schema", ""])
        for i, schema in enumerate(api_schema if isinstance(api_schema, list) else [api_schema]):
            if not isinstance(schema, dict):
                continue
            lines.append(f"### Endpoint {i+1}")
            lines.append("")
            if schema.get("method"):
                lines.append(f"**Method:** `{schema['method']}`")
            if schema.get("requestBody"):
                lines.extend([
                    "",
                    "**Request body:**",
                    "```json",
                    schema["requestBody"][:500],
                    "```",
                ])
            if schema.get("responseExample"):
                lines.extend([
                    "",
                    "**Response example:**",
                    "```json",
                    schema["responseExample"][:500],
                    "```",
                ])
            lines.append("")

    # Test Results
    lines.extend(["## Live Test Results", ""])

    if test_results.get("status") == "skipped":
        lines.extend([
            f"*Skipped: {test_results.get('reason', 'N/A')}*",
            "",
        ])
    else:
        # Health
        health = test_results.get("health", {})
        health_status = "PASS" if health.get("ok") else "FAIL"
        health_emoji = health_status
        lines.append(f"### Health Check: {health_status}")
        lines.append("")
        if health.get("ok"):
            lines.append(f"- Status: `{health.get('status_code')}`")
            lines.append(f"- Latency: `{health.get('latency_ms')}ms`")
        elif health.get("error"):
            lines.append(f"- Error: {health['error']}")
        else:
            lines.append(f"- Status code: `{health.get('status_code', '?')}`")
        lines.append("")

        # MCP
        mcp = test_results.get("mcp", {})
        if mcp.get("tools_found", 0) > 0:
            lines.append(f"### MCP: PASS ({mcp['tools_found']} tools discovered)")
            lines.append("")
            lines.append("| Tool | Description |")
            lines.append("|------|-------------|")
            for t in mcp.get("tools_detail", []):
                lines.append(f"| `{t['name']}` | {t['description'][:100]} |")
            lines.append("")
        elif mcp.get("reachable"):
            lines.append("### MCP: PARTIAL (reachable but no tools listed)")
            lines.append("")
            raw = mcp.get("raw_response", "")
            if raw:
                lines.extend([
                    "Response:",
                    "```",
                    raw[:300],
                    "```",
                    "",
                ])
        else:
            lines.append("### MCP: N/A")
            lines.append("")
            if mcp.get("error"):
                lines.append(f"- {mcp['error'][:200]}")
            lines.append("")

        # Direct endpoint
        direct = test_results.get("direct_endpoint", {})
        if direct and not direct.get("error"):
            lines.append(f"### Direct Endpoint: `{direct.get('status_code')}`")
            lines.append("")
            lines.append(f"- Latency: `{direct.get('latency_ms')}ms`")
            if direct.get("body_preview"):
                lines.extend([
                    "- Response preview:",
                    "```",
                    direct["body_preview"][:400],
                    "```",
                    "",
                ])
        elif direct and direct.get("error"):
            lines.append("### Direct Endpoint: FAIL")
            lines.append("")
            lines.append(f"- Error: {direct['error']}")
            lines.append("")

    # Overall assessment
    reachable = test_results.get("health", {}).get("ok", False)
    has_mcp = test_results.get("mcp", {}).get("tools_found", 0) > 0
    mcp_reachable = test_results.get("mcp", {}).get("reachable", False)

    if endpoint_type == "localhost":
        verdict = "UNREACHABLE (localhost only)"
    elif not reachable and not mcp_reachable:
        verdict = "OFFLINE"
    elif reachable and has_mcp:
        verdict = "FULLY OPERATIONAL (health + MCP tools)"
    elif reachable and mcp_reachable:
        verdict = "OPERATIONAL (health OK, MCP partial)"
    elif reachable:
        verdict = "OPERATIONAL (health OK, no MCP)"
    else:
        verdict = "DEGRADED"

    lines.extend([
        "## Verdict",
        "",
        f"**{verdict}**",
        "",
        "---",
        "",
        f"*Report generated at {datetime.now(timezone.utc).isoformat()} by The Gold Star*",
    ])

    return "\n".join(lines)


def generate_index_md(sellers: list, buyers: list, results: dict,
                      timestamp: str) -> str:
    """Generate the summary index file."""
    total = len(sellers)
    reachable = sum(1 for s in sellers
                    if results.get(s.get("name", ""), {}).get("health", {}).get("ok", False))
    mcp_count = sum(1 for s in sellers
                    if results.get(s.get("name", ""), {}).get("mcp", {}).get("tools_found", 0) > 0)
    localhost = sum(1 for s in sellers
                    if classify_endpoint(s) == "localhost")
    offline = total - reachable - localhost

    # Category counts
    categories = {}
    for s in sellers:
        cat = s.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # Team counts
    teams = {}
    for s in sellers:
        team = s.get("teamName", "Unknown")
        teams[team] = teams.get(team, 0) + 1
    top_teams = sorted(teams.items(), key=lambda x: -x[1])[:10]

    # Payment types
    crypto = sum(1 for s in sellers if any(
        p.get("paymentType") == "crypto" for p in s.get("planPricing", []) if isinstance(p, dict)))
    fiat = sum(1 for s in sellers if any(
        p.get("paymentType") == "fiat" for p in s.get("planPricing", []) if isinstance(p, dict)))
    free = sum(1 for s in sellers if any(
        (p.get("planPrice", 999) == 0 or str(p.get("planPrice", "")) == "0")
        for p in s.get("planPricing", []) if isinstance(p, dict)))

    lines = [
        f"# Agent Economy Marketplace Snapshot",
        "",
        f"**Timestamp:** {timestamp}",
        f"**Total Sellers:** {total}",
        f"**Total Buyers:** {len(buyers)}",
        "",
        "---",
        "",
        "## Health Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Reachable (health OK) | {reachable} |",
        f"| MCP tools discoverable | {mcp_count} |",
        f"| Localhost only | {localhost} |",
        f"| Offline/unreachable | {offline} |",
        f"| **Total** | **{total}** |",
        "",
        "## Payment Landscape",
        "",
        f"| Type | Count |",
        f"|------|-------|",
        f"| Crypto (USDC) | {crypto} |",
        f"| Fiat (Card) | {fiat} |",
        f"| Free plan available | {free} |",
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        lines.append(f"| {cat} | {count} |")

    lines.extend([
        "",
        "## Top Teams (by service count)",
        "",
        "| Team | Services |",
        "|------|----------|",
    ])
    for team, count in top_teams:
        lines.append(f"| {team} | {count} |")

    # Service table
    lines.extend([
        "",
        "## All Services",
        "",
        "| Service | Team | Status | Health | MCP Tools | Price | Report |",
        "|---------|------|--------|--------|-----------|-------|--------|",
    ])

    for s in sorted(sellers, key=lambda x: x.get("name", "").lower()):
        name = s.get("name", "?")
        team = s.get("teamName", "?")
        slug = slugify(name)
        etype = classify_endpoint(s)
        r = results.get(name, {})

        health_ok = r.get("health", {}).get("ok", False)
        mcp_tools = r.get("mcp", {}).get("tools_found", 0)
        price = extract_pricing(s).get("display_price", "?")

        if etype == "localhost":
            status = "Localhost"
            health_str = "N/A"
        elif health_ok:
            status = "Online"
            health_str = f"{r['health'].get('latency_ms', '?')}ms"
        else:
            status = "Offline"
            health_str = "FAIL"

        mcp_str = str(mcp_tools) if mcp_tools > 0 else "-"
        lines.append(f"| {name} | {team} | {status} | {health_str} | {mcp_str} | {price} | [{slug}.md](./{slug}.md) |")

    # Buyers section
    lines.extend([
        "",
        "## Buyers",
        "",
        "| Buyer | Team | Category | Interests |",
        "|-------|------|----------|-----------|",
    ])
    for b in buyers:
        name = b.get("name", "?")
        team = b.get("teamName", "?")
        cat = b.get("category", "?")
        interests = b.get("interests", b.get("description", ""))[:100]
        lines.append(f"| {name} | {team} | {cat} | {interests} |")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated by The Gold Star snapshot tool at {timestamp}*",
    ])

    return "\n".join(lines)


async def main():
    if not NVM_API_KEY:
        print("Warning: NVM_API_KEY not set. Discovery API may not work.")

    print("Fetching marketplace data...")
    data = await fetch_marketplace()
    sellers = data["sellers"]
    buyers = data["buyers"]
    print(f"  Found {len(sellers)} sellers, {len(buyers)} buyers")

    # Create timestamped directory
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    report_dir = Path(__file__).parent / ts
    report_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Output: {report_dir}/")

    # Save raw data
    raw_path = report_dir / "_raw.json"
    raw_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"  Saved raw data to _raw.json")

    # Test all endpoints concurrently (with semaphore to avoid overwhelming)
    sem = asyncio.Semaphore(10)  # Max 10 concurrent tests
    test_results = {}

    async def test_with_sem(seller):
        async with sem:
            name = seller.get("name", "Unknown")
            url = seller.get("endpointUrl", "")
            etype = classify_endpoint(seller)
            print(f"  Testing: {name} ({etype})...")
            result = await test_endpoint(url)
            test_results[name] = result
            health = result.get("health", {})
            if health.get("ok"):
                mcp_tools = result.get("mcp", {}).get("tools_found", 0)
                print(f"    -> OK ({health.get('latency_ms', '?')}ms) MCP:{mcp_tools} tools")
            elif result.get("status") == "skipped":
                print(f"    -> Skipped ({result.get('reason', '')})")
            else:
                print(f"    -> FAIL")

    print("\nTesting endpoints...")
    await asyncio.gather(*[test_with_sem(s) for s in sellers])

    # Generate individual reports
    print("\nGenerating reports...")
    for seller in sellers:
        name = seller.get("name", "Unknown")
        slug = slugify(name)
        etype = classify_endpoint(seller)
        pricing = extract_pricing(seller)
        results = test_results.get(name, {"status": "not_tested"})

        md = generate_service_md(seller, results, pricing, etype)
        (report_dir / f"{slug}.md").write_text(md)

    # Generate index
    index_md = generate_index_md(sellers, buyers, test_results, ts)
    (report_dir / "_index.md").write_text(index_md)

    # Summary stats
    reachable = sum(1 for r in test_results.values() if r.get("health", {}).get("ok"))
    mcp = sum(1 for r in test_results.values() if r.get("mcp", {}).get("tools_found", 0) > 0)
    print(f"\nSnapshot complete!")
    print(f"  Directory: {report_dir}/")
    print(f"  Services:  {len(sellers)}")
    print(f"  Reachable: {reachable}/{len(sellers)}")
    print(f"  MCP tools: {mcp} services")
    print(f"  Reports:   {len(sellers)} MD files + _index.md")


if __name__ == "__main__":
    asyncio.run(main())

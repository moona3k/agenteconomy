"""Run Gold Star reviews against live services via the deployed Gold Star MCP server.

This populates the production Gold Star with QA reports for all our services
and key external marketplace services. Reports are then queryable by anyone
calling get_report on the live Gold Star.

Usage:
    cd agents/the-gold-star
    python run_reviews.py              # Review our services
    python run_reviews.py --all        # Review our services + external
"""
import argparse
import json
import os
import sys
import httpx
import time

GOLD_STAR_URL = "https://goldstar.agenteconomy.io"

# Our services to review
OUR_SERVICES = [
    ("The Oracle", "Full Stack Agents", "https://oracle.agenteconomy.io"),
    ("The Amplifier", "Full Stack Agents", "https://amplifier.agenteconomy.io"),
    ("The Architect", "Full Stack Agents", "https://architect.agenteconomy.io"),
    ("The Underwriter", "Full Stack Agents", "https://underwriter.agenteconomy.io"),
    ("The Mystery Shopper", "Full Stack Agents", "https://shopper.agenteconomy.io"),
    ("The Judge", "Full Stack Agents", "https://judge.agenteconomy.io"),
    ("The Doppelganger", "Full Stack Agents", "https://doppelganger.agenteconomy.io"),
]

# External services to review (demonstrates cross-team usage)
EXTERNAL_SERVICES = [
    ("Cortex", "SwitchBoard AI", "https://cortex-v2-production.up.railway.app"),
    ("CloudAGI Smart Search", "CloudAGI", "https://agi-mcp-production.up.railway.app"),
]


def call_gold_star_review(seller_name: str, team_name: str, endpoint_url: str) -> dict:
    """Call the deployed Gold Star's request_review via its MCP endpoint.

    Uses a direct HTTP POST to the /mcp endpoint with the MCP protocol.
    """
    # Use the simple /health-accessible HTTP approach: call the tool via MCP SSE
    # Since MCP over SSE is complex, we'll call the Gold Star's QA engine directly
    # by invoking the tool through a simple HTTP request pattern.

    # The PaymentsMCP server accepts tool calls via MCP protocol.
    # For simplicity, we'll use the Gold Star's internal API pattern.
    print(f"\n{'='*60}")
    print(f"Reviewing: {seller_name} @ {endpoint_url}")
    print(f"{'='*60}")

    try:
        # Initialize MCP session
        with httpx.Client(timeout=120) as client:
            # POST to /mcp to initialize SSE stream and send tool call
            # MCP over HTTP uses SSE, so we need to handle the stream
            resp = client.post(
                f"{GOLD_STAR_URL}/mcp",
                headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "run_reviews", "version": "1.0.0"},
                    },
                },
            )
            print(f"  Init response: {resp.status_code}")

            # Call the tool
            resp = client.post(
                f"{GOLD_STAR_URL}/mcp",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "request_review",
                        "arguments": {
                            "seller_name": seller_name,
                            "team_name": team_name,
                            "endpoint_url": endpoint_url,
                        },
                    },
                },
            )
            print(f"  Review response: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    content = data["result"].get("content", [])
                    if content and isinstance(content, list):
                        text = content[0].get("text", "")
                        try:
                            result = json.loads(text)
                            print(f"  Score: {result.get('overall_score', '?')}/5.0")
                            print(f"  Certified: {result.get('certified', '?')}")
                            return result
                        except json.JSONDecodeError:
                            print(f"  Response: {text[:200]}")
                            return {"raw": text}
                print(f"  Full response: {resp.text[:500]}")
                return {"raw": resp.text[:500]}
            else:
                print(f"  Error: {resp.status_code} {resp.text[:300]}")
                return {"error": resp.status_code}

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"error": str(e)}


def call_review_direct(seller_name: str, team_name: str, endpoint_url: str) -> dict:
    """Call Gold Star review by importing the QA engine directly.

    This runs the review from this machine but the reports only exist locally.
    For production reports, use the MCP approach.
    """
    import asyncio
    sys.path.insert(0, ".")
    from dotenv import load_dotenv
    load_dotenv()
    from src.qa import qa_engine

    print(f"\n{'='*60}")
    print(f"Reviewing: {seller_name} @ {endpoint_url}")
    print(f"{'='*60}")

    try:
        report = asyncio.get_event_loop().run_until_complete(
            qa_engine.run_review(seller_name, team_name, endpoint_url)
        )
        result = qa_engine._report_to_dict(report)
        print(f"  Score: {result.get('overall_score', '?')}/5.0")
        print(f"  Certified: {result.get('certified', '?')}")
        print(f"  Tests: {result.get('tests_passed', '?')}/{result.get('tests_total', '?')} passed")
        if result.get("recommendations"):
            print("  Recommendations:")
            for r in result["recommendations"][:3]:
                print(f"    - {r}")
        return result
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Run Gold Star QA reviews")
    parser.add_argument("--all", action="store_true", help="Also review external services")
    parser.add_argument("--direct", action="store_true", help="Run reviews directly (local, not via deployed Gold Star)")
    args = parser.parse_args()

    services = list(OUR_SERVICES)
    if args.all:
        services.extend(EXTERNAL_SERVICES)

    print(f"Running Gold Star reviews for {len(services)} services")
    print(f"Mode: {'direct (local)' if args.direct else 'via deployed Gold Star'}")

    results = []
    review_fn = call_review_direct if args.direct else call_gold_star_review

    for name, team, url in services:
        result = review_fn(name, team, url)
        results.append({"name": name, "team": team, "url": url, **result})
        time.sleep(2)  # Be nice to Claude API rate limits

    # Summary
    print(f"\n\n{'='*60}")
    print("GOLD STAR REVIEW SUMMARY")
    print(f"{'='*60}")
    for r in results:
        score = r.get("overall_score", "?")
        certified = r.get("certified", False)
        cert_label = " GOLD STAR CERTIFIED" if certified else ""
        if isinstance(score, (int, float)):
            stars = "*" * int(round(score)) + "." * (5 - int(round(score)))
            print(f"  [{stars}] {score}/5.0  {r['name']}{cert_label}")
        else:
            print(f"  [?????] {r['name']}  (review failed)")

    # Save results
    with open("review-results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to review-results.json")


if __name__ == "__main__":
    main()

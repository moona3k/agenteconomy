"""Mystery Shopper engine -- autonomously discovers, tests, and reviews marketplace services.

Like Consumer Reports for the agent economy. Shows up unannounced,
uses the service as a regular buyer would, and publishes honest reviews.
"""
import os
import time
import threading
import httpx
from dataclasses import dataclass, field

DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"
UNDERWRITER_URL = os.environ.get("UNDERWRITER_URL", "https://underwriter.agenteconomy.io")


@dataclass
class ShopReport:
    report_id: str
    seller_name: str
    team_name: str
    endpoint_url: str
    timestamp: float = field(default_factory=time.time)
    reachable: bool = False
    health_ok: bool = False
    health_latency_ms: float = 0.0
    mcp_reachable: bool = False
    mcp_latency_ms: float = 0.0
    tools_discovered: list[str] = field(default_factory=list)
    tool_test_results: list[dict] = field(default_factory=list)
    quality_score: float = 0.0  # 1-5
    reliability: bool = False
    verdict: str = ""
    summary: str = ""


class MysteryShopperEngine:
    """Discovers and tests marketplace services anonymously."""

    def __init__(self):
        self._reports: list[ShopReport] = []
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"MS-{self._counter:04d}"

    async def discover_services(self) -> list[dict]:
        """Pull all sellers from the hackathon Discovery API."""
        api_key = os.environ.get("NVM_API_KEY", "")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    DISCOVERY_URL,
                    params={"side": "sell"},
                    headers={"x-nvm-api-key": api_key},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_sellers = data.get("sellers", [])
                    sellers = []
                    for s in raw_sellers:
                        if not isinstance(s, dict):
                            continue
                        url = s.get("endpointUrl", "")
                        if not url or "localhost" in url or "127.0.0.1" in url:
                            continue
                        if not url.startswith("http"):
                            continue
                        sellers.append({
                            "name": s.get("name", "Unknown"),
                            "team": s.get("teamName", "Unknown"),
                            "description": (s.get("description", "") or "")[:200],
                            "endpoint_url": url,
                            "category": s.get("category", ""),
                            "pricing": s.get("pricing", {}),
                        })
                    return sellers
        except Exception:
            pass
        return []

    async def shop_service(self, seller_name: str, team_name: str,
                           endpoint_url: str) -> ShopReport:
        """Conduct a full mystery shop of a single service."""
        report = ShopReport(
            report_id=self._next_id(),
            seller_name=seller_name,
            team_name=team_name,
            endpoint_url=endpoint_url,
        )

        base = endpoint_url.rstrip("/")

        # Phase 1: Health check
        report.health_ok, report.health_latency_ms, report.reachable = await self._check_health(base)

        if not report.reachable:
            report.quality_score = 1.0
            report.verdict = "NOT RECOMMENDED"
            report.reliability = False
            report.summary = self._make_summary(report)
            self._save(report)
            return report

        # Phase 2: MCP endpoint discovery
        report.mcp_reachable, report.mcp_latency_ms = await self._check_mcp(base)

        # Phase 3: Tool discovery via MCP
        if report.mcp_reachable:
            report.tools_discovered = await self._discover_tools(base)

        # Phase 4: Functional testing -- actually call discovered tools
        if report.tools_discovered:
            report.tool_test_results = await self._test_tools(base, report.tools_discovered)
        else:
            # Fallback: try a generic POST to the endpoint
            report.tool_test_results = await self._test_generic_endpoint(base)

        # Phase 5: Score calculation
        report.quality_score = self._calculate_score(report)
        report.reliability = report.health_ok and report.quality_score >= 3.0
        report.verdict = self._get_verdict(report.quality_score)
        report.summary = self._make_summary(report)

        self._save(report)
        return report

    async def _check_health(self, base: str) -> tuple[bool, float, bool]:
        """Check if /health endpoint responds."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                start = time.time()
                resp = await client.get(f"{base}/health")
                latency = (time.time() - start) * 1000
                return resp.status_code == 200, round(latency, 1), True
        except Exception:
            return False, 0.0, False

    async def _check_mcp(self, base: str) -> tuple[bool, float]:
        """Check if /mcp endpoint is available."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                start = time.time()
                resp = await client.get(f"{base}/mcp")
                latency = (time.time() - start) * 1000
                return resp.status_code < 500, round(latency, 1)
        except Exception:
            return False, 0.0

    async def _discover_tools(self, base: str) -> list[str]:
        """Discover available MCP tools via tools/list."""
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.post(f"{base}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    tools = data.get("result", {}).get("tools", [])
                    return [t.get("name", "") for t in tools if t.get("name")]
        except Exception:
            pass
        return []

    async def _test_tools(self, base: str, tools: list[str]) -> list[dict]:
        """Test discovered MCP tools with realistic queries."""
        results = []
        # Test up to 3 tools to keep it reasonable
        for tool_name in tools[:3]:
            result = await self._call_tool(base, tool_name)
            results.append(result)
        return results

    async def _call_tool(self, base: str, tool_name: str) -> dict:
        """Call a specific MCP tool with a generic test argument."""
        # Most tools accept some kind of string input -- try common param names
        test_args = {}
        for param_name in ["query", "input", "text", "message", "seller_name", "topic", "content"]:
            test_args[param_name] = "test marketplace analysis"

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                start = time.time()
                resp = await client.post(f"{base}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": test_args},
                    "id": 2,
                })
                latency = (time.time() - start) * 1000

                has_result = resp.status_code == 200 and len(resp.text) > 20
                has_error = False
                response_size = len(resp.text)

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        has_error = "error" in data and data["error"] is not None
                        result = data.get("result", {})
                        # Check if result has content
                        content = result.get("content", [])
                        if content and isinstance(content, list):
                            response_size = sum(len(str(c.get("text", ""))) for c in content)
                    except Exception:
                        pass

                passed = has_result and not has_error and response_size > 10

                return {
                    "tool": tool_name,
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                    "response_size": response_size,
                    "passed": passed,
                    "has_error": has_error,
                    "notes": f"Tool responded with {response_size} chars in {round(latency)}ms" if passed
                             else f"Tool failed: HTTP {resp.status_code}, error={has_error}",
                }
        except Exception as e:
            return {
                "tool": tool_name,
                "status_code": 0,
                "latency_ms": 0,
                "response_size": 0,
                "passed": False,
                "has_error": True,
                "notes": f"Connection failed: {str(e)[:100]}",
            }

    async def _test_generic_endpoint(self, base: str) -> list[dict]:
        """Fallback: test the base endpoint if no MCP tools found."""
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                start = time.time()
                resp = await client.post(f"{base}/", json={"message": "test query"})
                latency = (time.time() - start) * 1000
                passed = resp.status_code < 500 and len(resp.text) > 10
                return [{
                    "tool": "(generic POST)",
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                    "response_size": len(resp.text),
                    "passed": passed,
                    "has_error": not passed,
                    "notes": "Generic endpoint test" if passed else f"HTTP {resp.status_code}",
                }]
        except Exception:
            return [{
                "tool": "(generic POST)",
                "status_code": 0,
                "latency_ms": 0,
                "response_size": 0,
                "passed": False,
                "has_error": True,
                "notes": "Could not reach endpoint",
            }]

    def _calculate_score(self, report: ShopReport) -> float:
        """Calculate 1-5 quality score from test results."""
        components = []

        # Health (20%)
        components.append(1.0 if report.health_ok else 0.2)

        # MCP availability (20%)
        components.append(1.0 if report.mcp_reachable else 0.3)

        # Tool discovery (20%)
        if report.tools_discovered:
            tool_score = min(1.0, len(report.tools_discovered) / 3)
            components.append(tool_score)
        else:
            components.append(0.2)

        # Functional test pass rate (25%)
        if report.tool_test_results:
            passed = sum(1 for t in report.tool_test_results if t.get("passed"))
            components.append(passed / len(report.tool_test_results))
        else:
            components.append(0.0)

        # Latency (15%)
        if report.health_latency_ms > 0:
            if report.health_latency_ms < 500:
                components.append(1.0)
            elif report.health_latency_ms < 1500:
                components.append(0.7)
            elif report.health_latency_ms < 3000:
                components.append(0.4)
            else:
                components.append(0.2)
        else:
            components.append(0.0)

        weights = [0.20, 0.20, 0.20, 0.25, 0.15]
        weighted = sum(c * w for c, w in zip(components, weights))
        return round(1 + weighted * 4, 1)  # 1-5 scale

    def _get_verdict(self, score: float) -> str:
        if score >= 4.0:
            return "RECOMMENDED"
        if score >= 3.0:
            return "ACCEPTABLE"
        if score >= 2.0:
            return "NEEDS IMPROVEMENT"
        return "NOT RECOMMENDED"

    async def run_full_sweep(self) -> dict:
        """Mystery shop ALL discoverable services."""
        services = await self.discover_services()
        if not services:
            return {
                "status": "no_services",
                "message": "Could not discover any services from the marketplace.",
            }

        results = []
        for svc in services:
            url = svc.get("endpoint_url", "")
            if not url:
                continue
            report = await self.shop_service(
                seller_name=svc["name"],
                team_name=svc["team"],
                endpoint_url=url,
            )
            results.append(self._report_to_dict(report))

        # Sort by score descending
        results.sort(key=lambda x: -x["quality_score"])

        recommended = [r for r in results if r["verdict"] == "RECOMMENDED"]
        acceptable = [r for r in results if r["verdict"] == "ACCEPTABLE"]
        needs_work = [r for r in results if r["verdict"] == "NEEDS IMPROVEMENT"]
        not_rec = [r for r in results if r["verdict"] == "NOT RECOMMENDED"]

        return {
            "status": "completed",
            "services_discovered": len(services),
            "services_tested": len(results),
            "breakdown": {
                "recommended": len(recommended),
                "acceptable": len(acceptable),
                "needs_improvement": len(needs_work),
                "not_recommended": len(not_rec),
            },
            "results": results,
            "timestamp": time.time(),
        }

    async def submit_review_to_underwriter(self, report: ShopReport):
        """Submit mystery shop results to The Underwriter as a review."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                await client.post(f"{UNDERWRITER_URL}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "submit_review",
                        "arguments": {
                            "seller_name": report.seller_name,
                            "team_name": report.team_name,
                            "quality_score": min(5.0, max(1.0, report.quality_score)),
                            "reliable": report.reliability,
                            "notes": f"Mystery Shopper automated review: {report.verdict}. "
                                     f"Health: {'OK' if report.health_ok else 'FAIL'}, "
                                     f"MCP: {'OK' if report.mcp_reachable else 'FAIL'}, "
                                     f"Tools: {len(report.tools_discovered)}, "
                                     f"Tests passed: {sum(1 for t in report.tool_test_results if t.get('passed'))}"
                                     f"/{len(report.tool_test_results)}",
                            "reviewer": "The Mystery Shopper",
                        },
                    },
                    "id": 99,
                })
                report.summary += "\n[Review submitted to The Underwriter]"
        except Exception:
            pass  # Best effort

    def _make_summary(self, report: ShopReport) -> str:
        stars = int(round(report.quality_score))
        star_str = "*" * stars + "." * (5 - stars)
        passed = sum(1 for t in report.tool_test_results if t.get("passed"))
        total = len(report.tool_test_results)
        lines = [
            f"Mystery Shopper Report [{star_str}] {report.quality_score}/5.0 -- {report.verdict}",
            f"Service: {report.seller_name} (by {report.team_name})",
            f"Endpoint: {report.endpoint_url}",
            f"Reachable: {'Yes' if report.reachable else 'No'}",
            f"Health: {'OK' if report.health_ok else 'FAIL'} ({report.health_latency_ms}ms)",
            f"MCP: {'OK' if report.mcp_reachable else 'FAIL'} ({report.mcp_latency_ms}ms)",
            f"Tools discovered: {', '.join(report.tools_discovered) if report.tools_discovered else 'none'}",
            f"Tests passed: {passed}/{total}",
            f"Reliable: {'Yes' if report.reliability else 'No'}",
        ]
        return "\n".join(lines)

    def _save(self, report: ShopReport):
        with self._lock:
            self._reports.append(report)

    def get_latest_reports(self, limit: int = 10) -> list[dict]:
        sorted_reports = sorted(self._reports, key=lambda r: -r.timestamp)
        return [self._report_to_dict(r) for r in sorted_reports[:limit]]

    def get_stats(self) -> dict:
        total = len(self._reports)
        reachable = sum(1 for r in self._reports if r.reachable)
        avg_score = sum(r.quality_score for r in self._reports) / total if total else 0
        recommended = sum(1 for r in self._reports if r.quality_score >= 4.0)
        mcp_count = sum(1 for r in self._reports if r.mcp_reachable)
        avg_tools = sum(len(r.tools_discovered) for r in self._reports) / total if total else 0
        return {
            "total_shops_conducted": total,
            "services_reachable": reachable,
            "services_unreachable": total - reachable,
            "services_with_mcp": mcp_count,
            "average_quality_score": round(avg_score, 2),
            "average_tools_per_service": round(avg_tools, 1),
            "recommended_services": recommended,
            "unique_sellers": len(set(r.seller_name for r in self._reports)),
            "unique_teams": len(set(r.team_name for r in self._reports)),
        }

    def _report_to_dict(self, report: ShopReport) -> dict:
        passed = sum(1 for t in report.tool_test_results if t.get("passed"))
        return {
            "report_id": report.report_id,
            "seller_name": report.seller_name,
            "team_name": report.team_name,
            "endpoint_url": report.endpoint_url,
            "quality_score": report.quality_score,
            "verdict": report.verdict,
            "reliability": report.reliability,
            "reachable": report.reachable,
            "health_ok": report.health_ok,
            "health_latency_ms": report.health_latency_ms,
            "mcp_reachable": report.mcp_reachable,
            "mcp_latency_ms": report.mcp_latency_ms,
            "tools_discovered": report.tools_discovered,
            "tools_tested": len(report.tool_test_results),
            "tests_passed": passed,
            "tests_total": len(report.tool_test_results),
            "tool_test_details": report.tool_test_results,
            "summary": report.summary,
            "timestamp": report.timestamp,
        }


# Singleton
shopper = MysteryShopperEngine()

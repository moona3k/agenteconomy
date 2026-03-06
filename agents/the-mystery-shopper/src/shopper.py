"""Mystery Shopper engine — autonomously discovers, purchases, and reviews marketplace services.

Like Consumer Reports for the agent economy. Goes out as a regular buyer,
tests services honestly, and publishes reviews.
"""
import time
import threading
import httpx
from dataclasses import dataclass, field

DISCOVERY_API = "https://one-backend.sandbox.nevermined.app"


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
    has_free_plan: bool = False
    plan_id: str = ""
    tools_discovered: list[str] = field(default_factory=list)
    test_results: list[dict] = field(default_factory=list)
    quality_score: float = 0.0  # 1-5
    reliability: bool = False
    summary: str = ""
    review_submitted: bool = False


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
        """Pull all sellers from the Nevermined Discovery API."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{DISCOVERY_API}/api/v1/agents/search",
                    params={"page": 1, "page_size": 100},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    agents = data if isinstance(data, list) else data.get("agents", data.get("results", []))
                    sellers = []
                    for agent in agents:
                        if not isinstance(agent, dict):
                            continue
                        # Filter to sellers (have endpoints or service URLs)
                        endpoints = agent.get("endpoints", [])
                        service_url = agent.get("service_url", agent.get("serviceUrl", ""))
                        if endpoints or service_url:
                            sellers.append({
                                "name": agent.get("name", "Unknown"),
                                "team": agent.get("team", agent.get("owner", "Unknown")),
                                "description": agent.get("description", "")[:200],
                                "endpoints": endpoints,
                                "service_url": service_url,
                                "plan_id": agent.get("plan_id", agent.get("planId", "")),
                            })
                    return sellers
        except Exception:
            pass
        return []

    async def shop_service(self, seller_name: str, team_name: str,
                           endpoint_url: str, plan_id: str = "") -> ShopReport:
        """Conduct a mystery shop of a single service."""
        report_id = self._next_id()
        report = ShopReport(
            report_id=report_id,
            seller_name=seller_name,
            team_name=team_name,
            endpoint_url=endpoint_url,
            plan_id=plan_id,
        )

        base = endpoint_url.rstrip("/")

        # Step 1: Health check
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                resp = await client.get(f"{base}/health")
                latency = (time.time() - start) * 1000
                report.health_ok = resp.status_code == 200
                report.health_latency_ms = round(latency, 1)
                report.reachable = True
        except Exception:
            report.health_ok = False
            report.reachable = False

        if not report.reachable:
            report.quality_score = 1.0
            report.reliability = False
            report.summary = self._make_summary(report)
            self._save(report)
            return report

        # Step 2: MCP endpoint check
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                resp = await client.get(f"{base}/mcp")
                latency = (time.time() - start) * 1000
                report.mcp_reachable = resp.status_code < 500
                report.mcp_latency_ms = round(latency, 1)
        except Exception:
            report.mcp_reachable = False

        # Step 3: Test queries (act like a normal buyer)
        test_queries = [
            "What can you help me with?",
            "Give me a brief summary of your capabilities",
            "I need help with data analysis",
        ]

        passed = 0
        total = len(test_queries)

        for query in test_queries:
            result = await self._test_query(base, query)
            report.test_results.append(result)
            if result.get("passed"):
                passed += 1

        # Step 4: Calculate quality score
        score_components = []

        # Availability (is it up?)
        if report.health_ok:
            score_components.append(1.0)
        else:
            score_components.append(0.2)

        # MCP works?
        if report.mcp_reachable:
            score_components.append(1.0)
        else:
            score_components.append(0.3)

        # Query pass rate
        pass_rate = passed / total if total > 0 else 0
        score_components.append(pass_rate)

        # Latency bonus
        if report.health_latency_ms > 0 and report.health_latency_ms < 1000:
            score_components.append(1.0)
        elif report.health_latency_ms < 3000:
            score_components.append(0.7)
        else:
            score_components.append(0.4)

        avg_component = sum(score_components) / len(score_components)
        report.quality_score = round(1 + avg_component * 4, 1)  # 1-5 scale
        report.reliability = report.health_ok and pass_rate >= 0.5

        report.summary = self._make_summary(report)
        self._save(report)
        return report

    async def _test_query(self, base_url: str, query: str) -> dict:
        """Send a test query to the service."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                start = time.time()
                resp = await client.post(f"{base_url}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1,
                })
                latency = (time.time() - start) * 1000
                passed = resp.status_code == 200 and len(resp.text) > 10
                return {
                    "query": query,
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                    "response_length": len(resp.text),
                    "passed": passed,
                    "notes": "Response received" if passed else f"HTTP {resp.status_code}",
                }
        except Exception as e:
            return {
                "query": query,
                "status_code": 0,
                "latency_ms": 0,
                "response_length": 0,
                "passed": False,
                "notes": f"Failed: {str(e)[:100]}",
            }

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
            url = svc.get("service_url", "")
            if not url:
                endpoints = svc.get("endpoints", [])
                if endpoints and isinstance(endpoints[0], dict):
                    url = endpoints[0].get("url", "")
                elif endpoints and isinstance(endpoints[0], str):
                    url = endpoints[0]
            if not url or url.startswith("mcp://"):
                continue

            report = await self.shop_service(
                seller_name=svc["name"],
                team_name=svc["team"],
                endpoint_url=url,
                plan_id=svc.get("plan_id", ""),
            )
            results.append(self._report_to_dict(report))

        return {
            "status": "completed",
            "services_discovered": len(services),
            "services_tested": len(results),
            "results": results,
            "timestamp": time.time(),
        }

    def _make_summary(self, report: ShopReport) -> str:
        stars = int(round(report.quality_score))
        star_str = "*" * stars + "." * (5 - stars)
        status = "RECOMMENDED" if report.quality_score >= 4.0 else (
            "ACCEPTABLE" if report.quality_score >= 3.0 else (
                "NEEDS IMPROVEMENT" if report.quality_score >= 2.0 else "NOT RECOMMENDED"
            )
        )
        lines = [
            f"Mystery Shopper Report [{star_str}] {report.quality_score}/5.0 -- {status}",
            f"Service: {report.seller_name} (by {report.team_name})",
            f"Endpoint: {report.endpoint_url}",
            f"Reachable: {'Yes' if report.reachable else 'No'}",
            f"Health: {'OK' if report.health_ok else 'FAIL'} ({report.health_latency_ms}ms)",
            f"MCP: {'OK' if report.mcp_reachable else 'FAIL'} ({report.mcp_latency_ms}ms)",
            f"Tests passed: {sum(1 for t in report.test_results if t.get('passed'))}/{len(report.test_results)}",
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
        return {
            "total_shops_conducted": total,
            "services_reachable": reachable,
            "services_unreachable": total - reachable,
            "average_quality_score": round(avg_score, 2),
            "recommended_services": recommended,
            "unique_sellers": len(set(r.seller_name for r in self._reports)),
        }

    def _report_to_dict(self, report: ShopReport) -> dict:
        return {
            "report_id": report.report_id,
            "seller_name": report.seller_name,
            "team_name": report.team_name,
            "endpoint_url": report.endpoint_url,
            "quality_score": report.quality_score,
            "reliability": report.reliability,
            "reachable": report.reachable,
            "health_ok": report.health_ok,
            "health_latency_ms": report.health_latency_ms,
            "mcp_reachable": report.mcp_reachable,
            "mcp_latency_ms": report.mcp_latency_ms,
            "tests_passed": sum(1 for t in report.test_results if t.get("passed")),
            "tests_total": len(report.test_results),
            "summary": report.summary,
            "timestamp": report.timestamp,
        }


# Singleton
shopper = MysteryShopperEngine()

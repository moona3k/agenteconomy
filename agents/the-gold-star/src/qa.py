"""QA engine — AI-powered agent testing, evaluation, and certification.

The Gold Star certification process:
1. Seller requests a review
2. We hit their endpoints, collect raw responses
3. Claude evaluates response quality with rubric-based scoring
4. Generate detailed report with specific improvement recommendations
5. Seller fixes issues, requests re-review
6. Repeat until Gold Star certification is earned

Uses Claude Sonnet 4.6 as the evaluator — best cost/quality tradeoff for judgment tasks.
"""
import json
import os
import time
import threading
import httpx
import anthropic
from dataclasses import dataclass, field
from typing import Optional


EVAL_MODEL = "claude-sonnet-4-6"


def _get_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    return anthropic.Anthropic(api_key=key)


# ---------------------------------------------------------------------------
# Test scenarios — what a real buyer would ask
# ---------------------------------------------------------------------------

STANDARD_TEST_SCENARIOS = [
    {
        "name": "Self-description",
        "query": "What do you do? Describe your service and capabilities.",
        "rubric": "The service should clearly explain what it does, what tools it offers, and how to use them. A good response is specific, not generic.",
    },
    {
        "name": "Simple task",
        "query": "Give me a brief, useful response to demonstrate your value.",
        "rubric": "The service should produce a concrete, useful output — not a vague placeholder. Quality matters more than length.",
    },
    {
        "name": "Edge case handling",
        "query": "",
        "rubric": "Empty input should be handled gracefully — either a helpful error message or a reasonable default behavior. Crashes or 500 errors are failures.",
    },
    {
        "name": "Complex request",
        "query": "I need a detailed analysis with multiple sections and actionable recommendations. Please be thorough.",
        "rubric": "A quality service should produce structured, multi-part output when asked for detail. Look for organization, depth, and actionability.",
    },
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    test_name: str
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    response_body: str
    passed: bool
    notes: str
    ai_score: float = 0.0  # 1-10, from Claude evaluation
    ai_reasoning: str = ""


@dataclass
class QAReport:
    report_id: str
    seller_name: str
    team_name: str
    endpoint_url: str
    timestamp: float = field(default_factory=time.time)
    overall_score: float = 0.0  # 1-5 stars
    tests: list[TestResult] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    certified: bool = False
    summary: str = ""
    ai_evaluation: str = ""  # Claude's full evaluation narrative


# ---------------------------------------------------------------------------
# QA Engine
# ---------------------------------------------------------------------------

class QAEngine:
    """Tests agent endpoints and uses Claude to evaluate response quality."""

    def __init__(self):
        self._reports: dict[str, list[QAReport]] = {}  # seller_name -> reports
        self._certifications: dict[str, dict] = {}
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"GS-{self._counter:04d}"

    async def run_review(self, seller_name: str, team_name: str,
                         endpoint_url: str) -> QAReport:
        """Run a full QA review: collect data, then have Claude evaluate."""
        # Basic SSRF protection: only allow public HTTP(S) URLs
        url_lower = endpoint_url.lower().strip()
        if not url_lower.startswith(("http://", "https://")):
            raise ValueError("endpoint_url must be an HTTP or HTTPS URL")
        blocked = ("localhost", "127.0.0.1", "0.0.0.0", "::1",
                   ".internal", "169.254.", "10.", "192.168.", "172.16.")
        if any(b in url_lower for b in blocked):
            raise ValueError("endpoint_url must be a public URL, not internal/private")

        report_id = self._next_id()
        base = endpoint_url.rstrip("/")
        tests: list[TestResult] = []

        # Phase 1: Infrastructure tests (no AI needed)
        health_result = await self._test_health(base)
        tests.append(health_result)

        mcp_result = await self._test_mcp_endpoint(base)
        tests.append(mcp_result)

        # Phase 2: Discover available tools
        tools_list = await self._discover_tools(base)

        # Phase 3: Functional tests — act like a real buyer
        for scenario in STANDARD_TEST_SCENARIOS:
            result = await self._test_tool_call(base, scenario, tools_list)
            tests.append(result)

        # Phase 4: Error handling test
        error_result = await self._test_error_handling(base)
        tests.append(error_result)

        # Phase 5: AI Evaluation — Claude judges the collected responses
        ai_eval = self._evaluate_with_claude(seller_name, base, tests, tools_list)

        # Build the report from AI evaluation
        report = QAReport(
            report_id=report_id,
            seller_name=seller_name,
            team_name=team_name,
            endpoint_url=endpoint_url,
            overall_score=ai_eval["overall_score"],
            tests=tests,
            recommendations=ai_eval["recommendations"],
            certified=ai_eval["certified"],
            summary=ai_eval["summary"],
            ai_evaluation=ai_eval["narrative"],
        )

        # Update test results with AI scores
        for test, ai_test in zip(tests[2:-1], ai_eval.get("test_scores", [])):
            test.ai_score = ai_test.get("score", 0)
            test.ai_reasoning = ai_test.get("reasoning", "")

        with self._lock:
            if seller_name not in self._reports:
                self._reports[seller_name] = []
            self._reports[seller_name].append(report)

            if report.certified:
                self._certifications[seller_name] = {
                    "seller": seller_name,
                    "team": team_name,
                    "certified_at": time.time(),
                    "report_id": report_id,
                    "score": report.overall_score,
                    "badge": "GOLD STAR CERTIFIED",
                }

        return report

    # ------------------------------------------------------------------
    # Infrastructure tests
    # ------------------------------------------------------------------

    async def _test_health(self, base_url: str) -> TestResult:
        url = f"{base_url}/health"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                resp = await client.get(url)
                latency = (time.time() - start) * 1000
                return TestResult(
                    test_name="Health Check",
                    endpoint=url, method="GET", status_code=resp.status_code,
                    latency_ms=round(latency, 1), response_body=resp.text[:500],
                    passed=resp.status_code == 200,
                    notes="Health endpoint OK" if resp.status_code == 200 else f"Health returned {resp.status_code}",
                )
        except Exception as e:
            return TestResult(
                test_name="Health Check",
                endpoint=url, method="GET", status_code=0,
                latency_ms=0, response_body="", passed=False,
                notes=f"Unreachable: {str(e)[:200]}",
            )

    async def _test_mcp_endpoint(self, base_url: str) -> TestResult:
        url = f"{base_url}/mcp"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                resp = await client.post(url, json={
                    "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1,
                })
                latency = (time.time() - start) * 1000
                passed = resp.status_code == 200
                return TestResult(
                    test_name="MCP Endpoint",
                    endpoint=url, method="POST", status_code=resp.status_code,
                    latency_ms=round(latency, 1), response_body=resp.text[:500],
                    passed=passed,
                    notes="MCP endpoint responds" if passed else f"MCP returned {resp.status_code}",
                )
        except Exception as e:
            return TestResult(
                test_name="MCP Endpoint",
                endpoint=url, method="POST", status_code=0,
                latency_ms=0, response_body="", passed=False,
                notes=f"MCP unreachable: {str(e)[:200]}",
            )

    async def _discover_tools(self, base_url: str) -> list[dict]:
        """Discover available MCP tools."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{base_url}/mcp", json={
                    "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    result = data.get("result", {})
                    tools = result.get("tools", [])
                    if isinstance(tools, list):
                        return tools
        except Exception:
            pass
        return []

    # ------------------------------------------------------------------
    # Functional tests — call actual tools
    # ------------------------------------------------------------------

    async def _test_tool_call(self, base_url: str, scenario: dict,
                              tools_list: list[dict]) -> TestResult:
        """Test a tool call against the service."""
        url = f"{base_url}/mcp"

        # Pick the first tool that looks like it accepts queries
        tool_name = None
        for t in tools_list:
            name = t.get("name", "")
            # Prefer tools that take text input
            schema = t.get("inputSchema", {})
            props = schema.get("properties", {})
            if any(k in props for k in ["query", "content", "text", "input", "question", "prompt"]):
                tool_name = name
                break
        if not tool_name and tools_list:
            tool_name = tools_list[0].get("name", "unknown")

        if not tool_name:
            return TestResult(
                test_name=scenario["name"],
                endpoint=url, method="POST", status_code=0,
                latency_ms=0, response_body="", passed=False,
                notes="No tools discovered — cannot test functionality",
            )

        # Build arguments based on the tool's schema
        tool_schema = next((t for t in tools_list if t.get("name") == tool_name), {})
        props = tool_schema.get("inputSchema", {}).get("properties", {})
        arguments = {}
        for key in props:
            if key in ("query", "content", "text", "input", "question", "prompt",
                       "seller_name", "topic", "youtube_url", "file_path"):
                arguments[key] = scenario["query"] or "test"
                break
        if not arguments:
            # Fallback: use first string property
            for key, val in props.items():
                if val.get("type") == "string":
                    arguments[key] = scenario["query"] or "test"
                    break

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                start = time.time()
                resp = await client.post(url, json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                    "id": 1,
                })
                latency = (time.time() - start) * 1000
                body = resp.text[:2000]

                passed = resp.status_code == 200 and len(body) > 20
                return TestResult(
                    test_name=scenario["name"],
                    endpoint=url, method="POST", status_code=resp.status_code,
                    latency_ms=round(latency, 1), response_body=body,
                    passed=passed,
                    notes=f"Tool '{tool_name}' called" if passed else f"Tool call failed: HTTP {resp.status_code}",
                )
        except Exception as e:
            return TestResult(
                test_name=scenario["name"],
                endpoint=url, method="POST", status_code=0,
                latency_ms=0, response_body="", passed=False,
                notes=f"Tool call error: {str(e)[:200]}",
            )

    async def _test_error_handling(self, base_url: str) -> TestResult:
        url = f"{base_url}/mcp"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                resp = await client.post(url, json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": "this_tool_does_not_exist_12345", "arguments": {}},
                    "id": 99,
                })
                latency = (time.time() - start) * 1000
                passed = resp.status_code < 500
                return TestResult(
                    test_name="Error Handling",
                    endpoint=url, method="POST", status_code=resp.status_code,
                    latency_ms=round(latency, 1), response_body=resp.text[:500],
                    passed=passed,
                    notes="Handles errors gracefully" if passed else "Server crashed on bad input (500)",
                )
        except Exception as e:
            return TestResult(
                test_name="Error Handling",
                endpoint=url, method="POST", status_code=0,
                latency_ms=0, response_body="", passed=False,
                notes=f"Error test failed: {str(e)[:200]}",
            )

    # ------------------------------------------------------------------
    # AI Evaluation — Claude judges the collected test data
    # ------------------------------------------------------------------

    def _evaluate_with_claude(self, seller_name: str, endpoint: str,
                               tests: list[TestResult], tools_list: list[dict]) -> dict:
        """Have Claude evaluate all test results and produce a quality assessment."""

        # Prepare test data for Claude
        test_data = []
        for t in tests:
            test_data.append({
                "test_name": t.test_name,
                "passed": t.passed,
                "status_code": t.status_code,
                "latency_ms": t.latency_ms,
                "response_body": t.response_body[:1000],
                "notes": t.notes,
            })

        tools_info = []
        for t in tools_list:
            tools_info.append({
                "name": t.get("name"),
                "description": t.get("description", "")[:200],
            })

        prompt = f"""You are a rigorous but fair QA evaluator — the Michelin inspector of AI agent services.

You are reviewing: **{seller_name}** at {endpoint}

## Available Tools Discovered
{json.dumps(tools_info, indent=2) if tools_info else "No tools discovered."}

## Test Results
{json.dumps(test_data, indent=2)}

## Your Evaluation Task

Score this service on each dimension using this rubric:

### AVAILABILITY (1-10)
- 10: Health check passes, MCP endpoint responds, all tools discoverable
- 7: Health OK, MCP works but some tools missing or slow
- 4: Partially available — health or MCP has issues
- 1: Completely unreachable

### FUNCTIONALITY (1-10)
- 10: All test queries return rich, relevant, well-structured responses. The service clearly delivers value.
- 7: Most queries work, responses are useful but could be more detailed or specific
- 4: Some queries work but responses are generic, thin, or partially broken
- 1: No useful responses — empty, error, or garbage output

### RESPONSE QUALITY (1-10)
- 10: Responses demonstrate genuine intelligence — they're specific, actionable, well-organized, and would satisfy a paying customer
- 7: Responses are correct and helpful but not exceptional
- 4: Responses are technically present but low-effort, vague, or templated
- 1: Responses are empty, nonsensical, or clearly broken

### LATENCY (1-10)
- 10: All responses under 1 second
- 7: Average under 3 seconds
- 4: Average under 5 seconds
- 1: Responses over 10 seconds or timeouts

### ROBUSTNESS (1-10)
- 10: Handles edge cases and bad input gracefully with helpful error messages
- 7: Handles most errors without crashing
- 4: Some error scenarios cause issues
- 1: Crashes on any unexpected input

## For each functional test, also evaluate:
- The specific response body against its rubric
- Whether the response would satisfy a real paying customer

## Output Format

Respond with ONLY valid JSON (no markdown fences, no extra text) matching this structure:

{{
  "availability_score": <1-10>,
  "functionality_score": <1-10>,
  "response_quality_score": <1-10>,
  "latency_score": <1-10>,
  "robustness_score": <1-10>,
  "test_scores": [
    {{"test_name": "...", "score": <1-10>, "reasoning": "..."}}
  ],
  "recommendations": ["specific actionable recommendation 1", "..."],
  "narrative": "A 2-3 paragraph honest evaluation narrative. Be specific about what works and what doesn't. Cite actual responses where relevant.",
  "certified": <true if ALL dimension scores >= 8 and no critical issues>,
  "certification_reasoning": "Why this service does or doesn't earn the Gold Star"
}}

Be honest. Be specific. Cite actual response content. A Gold Star certification should mean something — only award it if the service genuinely delivers quality across every dimension."""

        try:
            client = _get_client()
            resp = client.messages.create(
                model=EVAL_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()

            # Parse JSON — handle potential markdown fences
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            eval_data = json.loads(raw)

            # Calculate overall score (1-5 stars from dimension scores)
            dimensions = [
                eval_data.get("availability_score", 5),
                eval_data.get("functionality_score", 5),
                eval_data.get("response_quality_score", 5),
                eval_data.get("latency_score", 5),
                eval_data.get("robustness_score", 5),
            ]
            # Weighted: functionality and quality matter most
            weights = [0.15, 0.30, 0.30, 0.10, 0.15]
            weighted_avg = sum(d * w for d, w in zip(dimensions, weights))
            overall_stars = round(weighted_avg / 2, 1)  # 10-point -> 5-star

            certified = eval_data.get("certified", False)
            # Double-check: must be 4.5+ stars for certification
            if overall_stars < 4.5:
                certified = False

            summary = self._format_summary(
                seller_name, overall_stars, certified,
                eval_data, tests,
            )

            return {
                "overall_score": overall_stars,
                "certified": certified,
                "recommendations": eval_data.get("recommendations", []),
                "narrative": eval_data.get("narrative", ""),
                "summary": summary,
                "test_scores": eval_data.get("test_scores", []),
                "dimension_scores": {
                    "availability": eval_data.get("availability_score"),
                    "functionality": eval_data.get("functionality_score"),
                    "response_quality": eval_data.get("response_quality_score"),
                    "latency": eval_data.get("latency_score"),
                    "robustness": eval_data.get("robustness_score"),
                },
            }

        except Exception as e:
            # Fallback: score from raw test pass rate
            return self._fallback_evaluation(seller_name, tests, str(e))

    def _fallback_evaluation(self, seller_name: str, tests: list[TestResult],
                              error: str) -> dict:
        """Fallback scoring when Claude evaluation fails."""
        passed = sum(1 for t in tests if t.passed)
        total = len(tests)
        pass_rate = passed / total if total else 0
        score = round(1 + pass_rate * 4, 1)

        recommendations = []
        if not tests[0].passed:
            recommendations.append("CRITICAL: Health endpoint not responding.")
        if not tests[1].passed:
            recommendations.append("CRITICAL: MCP endpoint not reachable.")
        for t in tests[2:]:
            if not t.passed:
                recommendations.append(f"ISSUE: {t.test_name} failed — {t.notes}")

        return {
            "overall_score": score,
            "certified": score >= 4.5 and not any("CRITICAL" in r for r in recommendations),
            "recommendations": recommendations or ["No specific issues found."],
            "narrative": f"(AI evaluation unavailable: {error}. Score based on pass rate: {passed}/{total} tests passed.)",
            "summary": self._format_summary(seller_name, score, False, {}, tests),
            "test_scores": [],
        }

    def _format_summary(self, seller_name: str, score: float, certified: bool,
                         eval_data: dict, tests: list[TestResult]) -> str:
        stars = int(round(score))
        star_str = "*" * stars + "." * (5 - stars)
        passed = sum(1 for t in tests if t.passed)

        header = "GOLD STAR CERTIFIED" if certified else "QA REPORT"

        lines = [
            f"=== {header} [{star_str}] {score}/5.0 ===",
            f"Service: {seller_name}",
            f"Tests passed: {passed}/{len(tests)}",
        ]

        if eval_data:
            lines.extend([
                "",
                f"Availability:      {eval_data.get('availability_score', '?')}/10",
                f"Functionality:     {eval_data.get('functionality_score', '?')}/10",
                f"Response Quality:  {eval_data.get('response_quality_score', '?')}/10",
                f"Latency:           {eval_data.get('latency_score', '?')}/10",
                f"Robustness:        {eval_data.get('robustness_score', '?')}/10",
            ])

        if certified:
            lines.extend([
                "",
                "This service has earned the GOLD STAR certification.",
                "Verified quality across all dimensions by AI evaluation.",
            ])

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def get_report(self, seller_name: str) -> dict | None:
        reports = self._reports.get(seller_name)
        if not reports:
            for key, val in self._reports.items():
                if key.lower() == seller_name.lower():
                    reports = val
                    break
        if not reports:
            return None
        return self._report_to_dict(reports[-1])

    def get_certification(self, seller_name: str) -> dict | None:
        cert = self._certifications.get(seller_name)
        if not cert:
            for key, val in self._certifications.items():
                if key.lower() == seller_name.lower():
                    return val
        return cert

    def get_all_certifications(self) -> list[dict]:
        return list(self._certifications.values())

    def get_stats(self) -> dict:
        total_reports = sum(len(r) for r in self._reports.values())
        return {
            "total_reviews_conducted": total_reports,
            "unique_sellers_reviewed": len(self._reports),
            "certifications_awarded": len(self._certifications),
            "certified_sellers": list(self._certifications.keys()),
        }

    def _report_to_dict(self, report: QAReport) -> dict:
        return {
            "report_id": report.report_id,
            "seller_name": report.seller_name,
            "team_name": report.team_name,
            "endpoint_url": report.endpoint_url,
            "overall_score": report.overall_score,
            "certified": report.certified,
            "summary": report.summary,
            "ai_evaluation": report.ai_evaluation,
            "tests_passed": sum(1 for t in report.tests if t.passed),
            "tests_total": len(report.tests),
            "recommendations": report.recommendations,
            "test_details": [
                {
                    "test_name": t.test_name,
                    "endpoint": t.endpoint,
                    "method": t.method,
                    "status_code": t.status_code,
                    "latency_ms": t.latency_ms,
                    "passed": t.passed,
                    "notes": t.notes,
                    "ai_score": t.ai_score,
                    "ai_reasoning": t.ai_reasoning,
                }
                for t in report.tests
            ],
            "timestamp": report.timestamp,
        }


# Singleton
qa_engine = QAEngine()

"""The Doppelganger -- competitive intelligence and autonomous market cloning.

Scans the marketplace for services vulnerable to competition, analyzes their
moats (or lack thereof), and generates competing implementations. This is
capitalism at machine speed -- if your only moat is wrapping an LLM with a
prompt, you don't have a moat.
"""
import os
import time
import json
import threading
import httpx
from dataclasses import dataclass, field

DISCOVERY_URL = "https://nevermined.ai/hackathon/register/api/discover"


@dataclass
class CloneAnalysis:
    analysis_id: str
    target_name: str
    target_team: str
    target_category: str
    target_description: str
    target_endpoint: str
    target_pricing: str
    # Discovery
    tools_discovered: list[dict] = field(default_factory=list)
    # Analysis
    moat_score: float = 0.0  # 0-10 (0 = no moat, trivially clonable; 10 = deep moat)
    moat_type: str = ""  # none, prompt_wrapper, proprietary_data, real_compute, network_effect, integration
    vulnerability: str = ""  # trivial, easy, moderate, hard, fortress
    clone_strategy: str = ""
    # Generated clone
    clone_name: str = ""
    clone_description: str = ""
    clone_tools: list[dict] = field(default_factory=list)
    estimated_dev_time: str = ""
    price_undercut: str = ""
    # Meta
    timestamp: float = field(default_factory=time.time)


class DoppelgangerEngine:
    """Analyzes marketplace services and identifies cloning opportunities."""

    def __init__(self):
        self._analyses: list[CloneAnalysis] = []
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"DG-{self._counter:04d}"

    async def fetch_marketplace(self) -> list[dict]:
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
                    return resp.json().get("sellers", [])
        except Exception:
            pass
        return []

    async def analyze_target(self, seller_name: str) -> CloneAnalysis | None:
        """Deep analysis of a specific service's defensibility."""
        sellers = await self.fetch_marketplace()
        target = None
        for s in sellers:
            if s.get("name", "").lower() == seller_name.lower():
                target = s
                break
        if not target:
            return None

        return await self._analyze_service(target)

    async def find_vulnerable(self, max_results: int = 10) -> list[dict]:
        """Scan the entire marketplace for services vulnerable to competition."""
        sellers = await self.fetch_marketplace()
        analyses = []

        for s in sellers:
            url = s.get("endpointUrl", "")
            if not url or not url.startswith("http") or "localhost" in url:
                continue

            analysis = await self._analyze_service(s)
            if analysis:
                analyses.append(analysis)

        # Sort by vulnerability (lowest moat first)
        analyses.sort(key=lambda a: a.moat_score)

        return [self._analysis_to_dict(a) for a in analyses[:max_results]]

    async def _analyze_service(self, seller: dict) -> CloneAnalysis:
        """Perform full competitive analysis of a service."""
        analysis = CloneAnalysis(
            analysis_id=self._next_id(),
            target_name=seller.get("name", "Unknown"),
            target_team=seller.get("teamName", "Unknown"),
            target_category=seller.get("category", ""),
            target_description=seller.get("description", ""),
            target_endpoint=seller.get("endpointUrl", ""),
            target_pricing=seller.get("pricing", {}).get("perRequest", "unknown"),
        )

        # Step 1: Discover their tools
        endpoint = seller.get("endpointUrl", "").rstrip("/")
        if endpoint and endpoint.startswith("http") and "localhost" not in endpoint:
            analysis.tools_discovered = await self._discover_tools(endpoint)

        # Step 2: Analyze moat
        analysis = self._assess_moat(analysis, seller)

        # Step 3: Generate clone strategy
        analysis = self._generate_clone(analysis)

        with self._lock:
            self._analyses.append(analysis)

        return analysis

    async def _discover_tools(self, endpoint: str) -> list[dict]:
        """Discover MCP tools at a service endpoint."""
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.post(f"{endpoint}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    tools = data.get("result", {}).get("tools", [])
                    return [
                        {
                            "name": t.get("name", ""),
                            "description": (t.get("description", "") or "")[:300],
                            "parameters": list((t.get("inputSchema", {}).get("properties", {}) or {}).keys()),
                        }
                        for t in tools if t.get("name")
                    ]
        except Exception:
            pass
        return []

    def _assess_moat(self, analysis: CloneAnalysis, seller: dict) -> CloneAnalysis:
        """Determine what makes a service defensible or vulnerable."""
        moat_points = 0
        moat_reasons = []

        desc = (analysis.target_description + " " + " ".join(
            t.get("description", "") for t in analysis.tools_discovered
        )).lower()

        # Check for real compute indicators
        compute_signals = ["gpu", "ml model", "inference", "training", "local model",
                          "parakeet", "whisper", "stable diffusion", "compute",
                          "transcrib", "ocr", "image process"]
        for signal in compute_signals:
            if signal in desc:
                moat_points += 3
                moat_reasons.append(f"Real compute: '{signal}'")
                break

        # Check for proprietary data
        data_signals = ["proprietary data", "exclusive", "our dataset", "curated",
                       "real-time feed", "live data", "crawl", "scrape"]
        for signal in data_signals:
            if signal in desc:
                moat_points += 2
                moat_reasons.append(f"Proprietary data: '{signal}'")
                break

        # Check for external integrations
        integration_signals = ["apify", "exa", "stripe", "aws", "google cloud",
                              "blockchain", "on-chain", "smart contract",
                              "api key", "webhook"]
        integration_count = 0
        for signal in integration_signals:
            if signal in desc:
                integration_count += 1
        if integration_count >= 2:
            moat_points += 2
            moat_reasons.append(f"Multiple integrations ({integration_count})")
        elif integration_count == 1:
            moat_points += 1
            moat_reasons.append("Single external integration")

        # Check for network effects
        network_signals = ["community", "reviews", "reputation", "marketplace",
                          "network", "social", "followers"]
        for signal in network_signals:
            if signal in desc:
                moat_points += 1
                moat_reasons.append(f"Network effect: '{signal}'")
                break

        # LLM wrapper detection (negative moat)
        wrapper_signals = ["ai-powered", "llm", "claude", "gpt", "openai",
                          "research agent", "analysis agent", "powered by ai"]
        wrapper_count = sum(1 for s in wrapper_signals if s in desc)
        no_moat_signals = ["agent that answers", "ai agent that", "chatbot"]
        is_pure_wrapper = wrapper_count >= 2 and not moat_reasons

        for signal in no_moat_signals:
            if signal in desc:
                is_pure_wrapper = True
                break

        if is_pure_wrapper:
            moat_reasons.append("Appears to be a pure LLM wrapper with no unique data or compute")

        # Tool count bonus
        if len(analysis.tools_discovered) >= 5:
            moat_points += 1
            moat_reasons.append(f"Rich tool surface ({len(analysis.tools_discovered)} tools)")

        # Pricing analysis
        pricing = analysis.target_pricing.lower()
        if "free" in pricing:
            moat_reasons.append("Free pricing -- harder to undercut on price")
            moat_points += 1

        analysis.moat_score = min(10, moat_points)

        if moat_points >= 6:
            analysis.moat_type = "deep"
            analysis.vulnerability = "fortress"
        elif moat_points >= 4:
            analysis.moat_type = "moderate"
            analysis.vulnerability = "hard"
        elif moat_points >= 2:
            analysis.moat_type = "shallow"
            analysis.vulnerability = "moderate"
        elif moat_points >= 1:
            analysis.moat_type = "thin"
            analysis.vulnerability = "easy"
        else:
            analysis.moat_type = "none"
            analysis.vulnerability = "trivial"

        analysis.clone_strategy = " | ".join(moat_reasons) if moat_reasons else "No defensible moat detected"

        return analysis

    def _generate_clone(self, analysis: CloneAnalysis) -> CloneAnalysis:
        """Generate a competing service concept."""
        name = analysis.target_name

        # Generate clone name (indie hacker style)
        prefixes = ["Better", "Fast", "Open", "Free", "Ultra", "Turbo", "Next"]
        category_names = {
            "Research": "ResearchBot",
            "AI/ML": "SmartAgent",
            "Data Analytics": "DataPro",
            "Infrastructure": "CoreService",
            "Social": "SocialEngine",
            "API Services": "APIHub",
            "Business Intelligence": "InsightEngine",
        }
        base_name = category_names.get(analysis.target_category, "Agent")
        prefix = prefixes[hash(name) % len(prefixes)]
        analysis.clone_name = f"{prefix}{base_name}"

        # Generate clone tools (mirror the target's tools with better descriptions)
        clone_tools = []
        for tool in analysis.tools_discovered:
            clone_tools.append({
                "name": tool["name"],
                "description": f"Enhanced version of {tool['name']}. {tool['description'][:100]}",
                "parameters": tool["parameters"],
            })

        if not clone_tools:
            # If we couldn't discover tools, create generic ones based on category
            clone_tools = [{
                "name": "process",
                "description": f"Core {analysis.target_category} processing tool",
                "parameters": ["query"],
            }]

        analysis.clone_tools = clone_tools

        # Clone description
        analysis.clone_description = (
            f"A competitive alternative to {name}. Offers the same core functionality "
            f"({analysis.target_category}) with {len(clone_tools)} tools. "
            f"{'Lower price. ' if analysis.vulnerability in ('trivial', 'easy') else ''}"
            f"Built to demonstrate that {'LLM wrappers have no moat' if analysis.moat_type == 'none' else 'market competition drives quality'}."
        )

        # Estimate development time
        if analysis.vulnerability == "trivial":
            analysis.estimated_dev_time = "30 minutes"
            analysis.price_undercut = "Free (to prove the point)"
        elif analysis.vulnerability == "easy":
            analysis.estimated_dev_time = "2-4 hours"
            analysis.price_undercut = "50% of original price"
        elif analysis.vulnerability == "moderate":
            analysis.estimated_dev_time = "1-2 days"
            analysis.price_undercut = "20% of original price"
        elif analysis.vulnerability == "hard":
            analysis.estimated_dev_time = "1-2 weeks"
            analysis.price_undercut = "Comparable (can't easily undercut)"
        else:
            analysis.estimated_dev_time = "Months+"
            analysis.price_undercut = "N/A (genuine moat)"

        return analysis

    async def moat_report(self) -> dict:
        """Generate a marketplace-wide moat analysis report."""
        sellers = await self.fetch_marketplace()
        if not sellers:
            return {"status": "error", "message": "Could not fetch marketplace data"}

        analyses = []
        for s in sellers:
            url = s.get("endpointUrl", "")
            if not url or not url.startswith("http") or "localhost" in url:
                continue
            analysis = await self._analyze_service(s)
            analyses.append(analysis)

        # Categorize
        trivial = [a for a in analyses if a.vulnerability == "trivial"]
        easy = [a for a in analyses if a.vulnerability == "easy"]
        moderate = [a for a in analyses if a.vulnerability == "moderate"]
        hard = [a for a in analyses if a.vulnerability == "hard"]
        fortress = [a for a in analyses if a.vulnerability == "fortress"]

        avg_moat = sum(a.moat_score for a in analyses) / len(analyses) if analyses else 0

        return {
            "status": "completed",
            "total_analyzed": len(analyses),
            "marketplace_moat_score": round(avg_moat, 1),
            "vulnerability_breakdown": {
                "trivial_to_clone": len(trivial),
                "easy_to_clone": len(easy),
                "moderate": len(moderate),
                "hard_to_clone": len(hard),
                "fortress": len(fortress),
            },
            "most_vulnerable": [self._analysis_to_dict(a) for a in trivial[:5]],
            "most_defensible": [self._analysis_to_dict(a) for a in sorted(analyses, key=lambda x: -x.moat_score)[:5]],
            "insight": self._generate_insight(analyses),
            "timestamp": time.time(),
        }

    def _generate_insight(self, analyses: list[CloneAnalysis]) -> str:
        """Generate a market insight from the analysis."""
        total = len(analyses)
        if not total:
            return "No services analyzed."

        trivial_pct = sum(1 for a in analyses if a.vulnerability in ("trivial", "easy")) / total * 100
        deep_pct = sum(1 for a in analyses if a.vulnerability in ("hard", "fortress")) / total * 100

        lines = []
        lines.append(f"Analyzed {total} services in the marketplace.")
        lines.append(f"{trivial_pct:.0f}% of services have trivial or easy-to-clone moats.")
        lines.append(f"{deep_pct:.0f}% of services have genuine defensibility.")

        if trivial_pct > 60:
            lines.append(
                "The marketplace is dominated by LLM wrappers. Most services could be replicated "
                "in under an hour. This is the uncomfortable truth of the current agent economy: "
                "if your only value is 'I call Claude with a custom prompt,' you have no moat."
            )
        elif trivial_pct > 30:
            lines.append(
                "A significant portion of the marketplace lacks defensibility. Services with "
                "real compute, proprietary data, or deep integrations stand out."
            )
        else:
            lines.append(
                "The marketplace has strong defensibility. Most services offer genuine value "
                "beyond simple LLM wrapping."
            )

        return " ".join(lines)

    def get_stats(self) -> dict:
        total = len(self._analyses)
        avg_moat = sum(a.moat_score for a in self._analyses) / total if total else 0
        trivial = sum(1 for a in self._analyses if a.vulnerability in ("trivial", "easy"))
        return {
            "total_services_analyzed": total,
            "average_moat_score": round(avg_moat, 1),
            "easily_clonable": trivial,
            "unique_categories": len(set(a.target_category for a in self._analyses)),
            "unique_teams": len(set(a.target_team for a in self._analyses)),
        }

    def _analysis_to_dict(self, a: CloneAnalysis) -> dict:
        return {
            "analysis_id": a.analysis_id,
            "target": {
                "name": a.target_name,
                "team": a.target_team,
                "category": a.target_category,
                "description": a.target_description[:200],
                "endpoint": a.target_endpoint,
                "pricing": a.target_pricing,
                "tools": [t["name"] for t in a.tools_discovered],
            },
            "moat_analysis": {
                "moat_score": a.moat_score,
                "moat_type": a.moat_type,
                "vulnerability": a.vulnerability,
                "reasoning": a.clone_strategy,
            },
            "clone_blueprint": {
                "clone_name": a.clone_name,
                "clone_description": a.clone_description,
                "clone_tools": a.clone_tools,
                "estimated_dev_time": a.estimated_dev_time,
                "price_undercut": a.price_undercut,
            },
            "timestamp": a.timestamp,
        }


# Singleton
doppelganger = DoppelgangerEngine()

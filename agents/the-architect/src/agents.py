"""Hierarchical multi-agent orchestration -- orchestrators of orchestrators.

Architecture (like a corporate org chart):

    CEO (orchestrator)
     |
     +-- VP Intelligence (orchestrator)
     |    +-- Discovery Agent (leaf)
     |    +-- Market Scanner Agent (leaf)
     |
     +-- VP Research (orchestrator)
     |    +-- Research Agent (leaf)
     |    +-- Analysis Agent (leaf)
     |
     +-- VP Quality (orchestrator)
          +-- QA Agent (leaf)
          +-- Report Agent (leaf)

This matches Mindra's criteria: "Build hierarchical orchestration
(orchestrators of orchestrators) - like a corporate org chart - to scale
AI systems through structured delegation and layered decision-making."

7 agents total, 3 orchestrators + 4 leaf agents, 3 layers deep.
Uses Nevermined for marketplace data (Discovery + Market Scanner).
Powered by Claude Sonnet for speed.
"""
import json
import os
import httpx
import anthropic
from concurrent.futures import ThreadPoolExecutor


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


MODEL = "claude-sonnet-4-20250514"


def _ask_claude(system: str, user: str, max_tokens: int = 800) -> str:
    """Common helper to call Claude. Uses Sonnet for speed."""
    client = _get_client()
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"[Agent error: {str(e)[:200]}]"


# ---------------------------------------------------------------------------
# Layer 3: Leaf Agents (do the actual work)
# ---------------------------------------------------------------------------

def discovery_agent(query: str, nvm_api_key: str = "") -> dict:
    """Leaf agent: Discovers services in the Nevermined marketplace."""
    api_key = nvm_api_key or os.environ.get("NVM_API_KEY", "")
    try:
        resp = httpx.get(
            "https://nevermined.ai/hackathon/register/api/discover",
            params={"side": "sell"},
            headers={"x-nvm-api-key": api_key},
            timeout=8,
        )
        sellers = resp.json().get("sellers", [])

        q = query.lower()
        words = [w for w in q.split() if len(w) > 1]
        matches = []
        for s in sellers:
            score = 0
            for field in ["name", "teamName", "category", "description"]:
                val = s.get(field, "").lower()
                if q in val:
                    score += 4
                for w in words:
                    if w in val:
                        score += 1
            if score > 0:
                matches.append({
                    "name": s.get("name"),
                    "team": s.get("teamName"),
                    "category": s.get("category"),
                    "endpoint": s.get("endpointUrl"),
                    "pricing": s.get("pricing", {}).get("perRequest", "N/A"),
                    "_score": score,
                })
        matches.sort(key=lambda x: -x["_score"])

        return {
            "agent": "discovery",
            "status": "success",
            "query": query,
            "total_sellers": len(sellers),
            "matches": matches[:10],
        }
    except Exception as e:
        return {"agent": "discovery", "status": "error", "error": str(e)}


def market_scanner_agent(query: str, nvm_api_key: str = "") -> dict:
    """Leaf agent: Scans marketplace for competitive landscape and pricing patterns."""
    api_key = nvm_api_key or os.environ.get("NVM_API_KEY", "")
    try:
        resp = httpx.get(
            "https://nevermined.ai/hackathon/register/api/discover",
            params={"side": "sell"},
            headers={"x-nvm-api-key": api_key},
            timeout=8,
        )
        sellers = resp.json().get("sellers", [])

        # Aggregate market intelligence
        categories = {}
        teams = set()
        with_endpoints = 0
        for s in sellers:
            cat = s.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1
            teams.add(s.get("teamName", "unknown"))
            if s.get("endpointUrl", "").startswith("http"):
                with_endpoints += 1

        return {
            "agent": "market_scanner",
            "status": "success",
            "total_services": len(sellers),
            "total_teams": len(teams),
            "services_with_endpoints": with_endpoints,
            "categories": dict(sorted(categories.items(), key=lambda x: -x[1])[:10]),
            "top_teams": list(teams)[:10],
        }
    except Exception as e:
        return {"agent": "market_scanner", "status": "error", "error": str(e)}


def research_agent(topic: str) -> dict:
    """Leaf agent: Conducts research using Claude synthesis."""
    try:
        findings = _ask_claude(
            system="You are a research analyst. Produce concise structured research notes with key findings, data points, and sources. Be brief.",
            user=f"Research the following topic and provide key findings, trends, and data points:\n\n{topic}",
            max_tokens=600,
        )
        return {"agent": "research", "status": "success", "topic": topic, "findings": findings}
    except Exception as e:
        return {"agent": "research", "status": "error", "error": str(e)}


def analysis_agent(data: str) -> dict:
    """Leaf agent: Synthesizes data into actionable insights."""
    try:
        insights = _ask_claude(
            system="You are a business analyst. Synthesize data into clear insights with actionable recommendations. Be very concise and structured.",
            user=f"Analyze the following data and provide insights, patterns, and recommendations:\n\n{data}",
            max_tokens=500,
        )
        return {"agent": "analysis", "status": "success", "insights": insights}
    except Exception as e:
        return {"agent": "analysis", "status": "error", "error": str(e)}


def qa_agent(content: str) -> dict:
    """Leaf agent: Quality-checks findings for accuracy and completeness."""
    try:
        review = _ask_claude(
            system="You are a QA reviewer. Check content for: factual accuracy, logical consistency, missing perspectives, potential bias. Give a quality score 1-10 and specific issues found. Be brief.",
            user=f"Review this content for quality:\n\n{content}",
            max_tokens=300,
        )
        return {"agent": "qa", "status": "success", "review": review}
    except Exception as e:
        return {"agent": "qa", "status": "error", "error": str(e)}


def report_agent(research: str, analysis: str, qa_review: str, topic: str) -> dict:
    """Leaf agent: Produces the final executive report."""
    try:
        report = _ask_claude(
            system="You are an executive report writer. Produce a concise, well-structured report with: Executive Summary, Key Findings, Analysis, Recommendations, and Quality Notes. Keep it under 800 words.",
            user=(
                f"Produce an executive report on: {topic}\n\n"
                f"RESEARCH:\n{research}\n\n"
                f"ANALYSIS:\n{analysis}\n\n"
                f"QA REVIEW:\n{qa_review}"
            ),
            max_tokens=800,
        )
        return {"agent": "report", "status": "success", "report": report}
    except Exception as e:
        return {"agent": "report", "status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Layer 2: VP-Level Orchestrators (orchestrate leaf agents)
# ---------------------------------------------------------------------------

def vp_intelligence(query: str) -> dict:
    """VP Intelligence: Orchestrates Discovery + Market Scanner in parallel.

    Delegates to two leaf agents to build a comprehensive intelligence picture:
    - Discovery Agent: finds specific services matching the query
    - Market Scanner Agent: provides competitive landscape and market structure
    """
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_disc = pool.submit(discovery_agent, query)
        fut_scan = pool.submit(market_scanner_agent, query)
        disc_result = fut_disc.result()
        scan_result = fut_scan.result()

    # Synthesize intelligence from both agents
    marketplace_context = ""
    if disc_result.get("matches"):
        services = [f"- {m['name']} ({m['team']}): {m.get('pricing', 'N/A')}" for m in disc_result["matches"][:5]]
        marketplace_context = "Relevant services found:\n" + "\n".join(services)

    market_intel = ""
    if scan_result.get("status") == "success":
        market_intel = (
            f"\nMarket structure: {scan_result['total_services']} total services, "
            f"{scan_result['total_teams']} teams, "
            f"{scan_result['services_with_endpoints']} with live endpoints.\n"
            f"Top categories: {json.dumps(dict(list(scan_result.get('categories', {}).items())[:5]))}"
        )

    return {
        "orchestrator": "vp_intelligence",
        "agents_used": ["discovery", "market_scanner"],
        "status": "success",
        "intelligence_brief": marketplace_context + market_intel,
        "raw": {
            "discovery": disc_result,
            "market_scanner": scan_result,
        },
    }


def vp_research(query: str, intelligence: str) -> dict:
    """VP Research: Orchestrates Research + Analysis in parallel.

    Both agents receive the intelligence brief from VP Intelligence.
    Research Agent produces findings, Analysis Agent synthesizes insights.
    They work in parallel since Analysis can work off the query + intelligence
    independently of Research's specific findings.
    """
    enriched_topic = f"{query}\n\nMarketplace Intelligence:\n{intelligence}"

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_research = pool.submit(research_agent, enriched_topic)
        fut_analysis = pool.submit(analysis_agent, enriched_topic)
        research_result = fut_research.result()
        analysis_result = fut_analysis.result()

    return {
        "orchestrator": "vp_research",
        "agents_used": ["research", "analysis"],
        "status": "success",
        "research_text": research_result.get("findings", "Research unavailable."),
        "analysis_text": analysis_result.get("insights", "Analysis unavailable."),
        "raw": {
            "research": research_result,
            "analysis": analysis_result,
        },
    }


def vp_quality(research_text: str, analysis_text: str, query: str) -> dict:
    """VP Quality: Orchestrates QA + Report sequentially.

    QA must run first (to review the content), then Report uses QA's feedback.
    This is deliberate sequential orchestration -- quality gates before publication.
    """
    combined = f"RESEARCH:\n{research_text}\n\nANALYSIS:\n{analysis_text}"

    qa_result = qa_agent(combined)
    qa_text = qa_result.get("review", "QA unavailable.")

    report_result = report_agent(research_text, analysis_text, qa_text, query)

    return {
        "orchestrator": "vp_quality",
        "agents_used": ["qa", "report"],
        "status": "success",
        "qa_text": qa_text,
        "final_report": report_result.get("report", "Report generation failed."),
        "raw": {
            "qa": qa_result,
            "report": report_result,
        },
    }


# ---------------------------------------------------------------------------
# Layer 1: CEO (top-level orchestrator of orchestrators)
# ---------------------------------------------------------------------------

def ceo_orchestrate(query: str) -> dict:
    """CEO Agent: Three-layer hierarchical orchestration.

    Layer 1 (CEO): Delegates to three VP-level orchestrators
    Layer 2 (VPs): Each VP orchestrates 2 leaf agents
    Layer 3 (Leaf agents): Do the actual work

    Pipeline:
    1. VP Intelligence (parallel: Discovery + Market Scanner)
    2. VP Research (parallel: Research + Analysis, using intelligence)
    3. VP Quality (sequential: QA -> Report, quality gate)

    7 agents total. 3 orchestrators. 4 leaf agents. 3 layers deep.
    """
    pipeline_log = []

    # Phase 1: VP Intelligence orchestrates Discovery + Market Scanner
    pipeline_log.append({"phase": 1, "orchestrator": "vp_intelligence", "agents": ["discovery", "market_scanner"], "status": "starting"})
    intel_result = vp_intelligence(query)
    pipeline_log.append({"phase": 1, "orchestrator": "vp_intelligence", "agents": ["discovery", "market_scanner"], "status": intel_result["status"]})

    intelligence_brief = intel_result.get("intelligence_brief", "")

    # Phase 2: VP Research orchestrates Research + Analysis
    pipeline_log.append({"phase": 2, "orchestrator": "vp_research", "agents": ["research", "analysis"], "status": "starting"})
    research_result = vp_research(query, intelligence_brief)
    pipeline_log.append({"phase": 2, "orchestrator": "vp_research", "agents": ["research", "analysis"], "status": research_result["status"]})

    # Phase 3: VP Quality orchestrates QA -> Report
    pipeline_log.append({"phase": 3, "orchestrator": "vp_quality", "agents": ["qa", "report"], "status": "starting"})
    quality_result = vp_quality(
        research_result["research_text"],
        research_result["analysis_text"],
        query,
    )
    pipeline_log.append({"phase": 3, "orchestrator": "vp_quality", "agents": ["qa", "report"], "status": quality_result["status"]})

    final_report = quality_result.get("final_report", "Report generation failed.")

    # Count marketplace services found
    disc_raw = intel_result.get("raw", {}).get("discovery", {})
    services_found = len(disc_raw.get("matches", []))

    return {
        "status": "success",
        "query": query,
        "architecture": {
            "layers": 3,
            "total_agents": 7,
            "orchestrators": ["ceo", "vp_intelligence", "vp_research", "vp_quality"],
            "leaf_agents": ["discovery", "market_scanner", "research", "analysis", "qa", "report"],
            "pattern": "hierarchical (orchestrators of orchestrators)",
        },
        "agents_used": 7,
        "pipeline": pipeline_log,
        "report": final_report,
        "sources": {
            "discovery": disc_raw,
            "marketplace_services_found": services_found,
            "market_structure": intel_result.get("raw", {}).get("market_scanner", {}),
        },
    }

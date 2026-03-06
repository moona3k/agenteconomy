"""Specialized sub-agents for hierarchical orchestration.

Each agent has a focused role and can independently buy services
from the hackathon marketplace via Nevermined.

Powered by Claude Opus 4.6 via the Anthropic API.
"""
import json
import os
import httpx
import anthropic
from typing import Optional


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


MODEL = "claude-opus-4-6"


def _ask_claude(system: str, user: str, max_tokens: int = 1000) -> str:
    """Common helper to call Claude."""
    client = _get_client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def discovery_agent(query: str, nvm_api_key: str = "") -> dict:
    """Agent 1: Discovers relevant services in the hackathon marketplace.

    Queries the Nevermined Discovery API to find sellers matching the query.
    """
    api_key = nvm_api_key or os.environ.get("NVM_API_KEY", "")
    try:
        resp = httpx.get(
            "https://nevermined.ai/hackathon/register/api/discover",
            params={"side": "sell"},
            headers={"x-nvm-api-key": api_key},
            timeout=15,
        )
        sellers = resp.json().get("sellers", [])

        q = query.lower()
        matches = []
        for s in sellers:
            for field in ["name", "teamName", "category", "description"]:
                if q in s.get(field, "").lower():
                    matches.append({
                        "name": s.get("name"),
                        "team": s.get("teamName"),
                        "category": s.get("category"),
                        "endpoint": s.get("endpointUrl"),
                        "pricing": s.get("pricing", {}).get("perRequest", "N/A"),
                    })
                    break

        return {
            "agent": "discovery",
            "status": "success",
            "query": query,
            "total_sellers": len(sellers),
            "matches": matches[:10],
        }
    except Exception as e:
        return {"agent": "discovery", "status": "error", "error": str(e)}


def research_agent(topic: str) -> dict:
    """Agent 2: Conducts research using Claude synthesis."""
    try:
        findings = _ask_claude(
            system="You are a research analyst. Produce structured research notes with key findings, data points, and sources.",
            user=f"Research the following topic and provide key findings, trends, and data points:\n\n{topic}",
            max_tokens=1000,
        )
        return {"agent": "research", "status": "success", "topic": topic, "findings": findings}
    except Exception as e:
        return {"agent": "research", "status": "error", "error": str(e)}


def analysis_agent(data: str) -> dict:
    """Agent 3: Synthesizes data into actionable insights."""
    try:
        insights = _ask_claude(
            system="You are a business analyst. Synthesize data into clear insights with actionable recommendations. Be concise and structured.",
            user=f"Analyze the following data and provide insights, patterns, and recommendations:\n\n{data}",
            max_tokens=800,
        )
        return {"agent": "analysis", "status": "success", "insights": insights}
    except Exception as e:
        return {"agent": "analysis", "status": "error", "error": str(e)}


def qa_agent(content: str) -> dict:
    """Agent 4: Quality-checks findings for accuracy and completeness."""
    try:
        review = _ask_claude(
            system="You are a QA reviewer. Check content for: factual accuracy, logical consistency, missing perspectives, potential bias. Give a quality score 1-10 and specific issues found.",
            user=f"Review this content for quality:\n\n{content}",
            max_tokens=500,
        )
        return {"agent": "qa", "status": "success", "review": review}
    except Exception as e:
        return {"agent": "qa", "status": "error", "error": str(e)}


def report_agent(research: str, analysis: str, qa_review: str, topic: str) -> dict:
    """Agent 5: Produces the final executive report."""
    try:
        report = _ask_claude(
            system="You are an executive report writer. Produce a concise, well-structured report with: Executive Summary, Key Findings, Analysis, Recommendations, and Quality Notes.",
            user=(
                f"Produce an executive report on: {topic}\n\n"
                f"RESEARCH:\n{research}\n\n"
                f"ANALYSIS:\n{analysis}\n\n"
                f"QA REVIEW:\n{qa_review}"
            ),
            max_tokens=1500,
        )
        return {"agent": "report", "status": "success", "report": report}
    except Exception as e:
        return {"agent": "report", "status": "error", "error": str(e)}


def ceo_orchestrate(query: str) -> dict:
    """CEO Agent: Orchestrates all 5 sub-agents in sequence.

    Delegates work through the pipeline:
    Discovery -> Research -> Analysis -> QA -> Report
    """
    pipeline_log = []

    # Step 1: Discovery
    pipeline_log.append({"step": 1, "agent": "discovery", "status": "starting"})
    discovery_result = discovery_agent(query)
    pipeline_log.append({"step": 1, "agent": "discovery", "status": discovery_result["status"]})

    marketplace_context = ""
    if discovery_result.get("matches"):
        services = [f"- {m['name']} ({m['team']}): {m['pricing']}" for m in discovery_result["matches"][:5]]
        marketplace_context = f"\n\nRelevant marketplace services found:\n" + "\n".join(services)

    # Step 2: Research
    pipeline_log.append({"step": 2, "agent": "research", "status": "starting"})
    research_result = research_agent(query + marketplace_context)
    pipeline_log.append({"step": 2, "agent": "research", "status": research_result["status"]})

    research_text = research_result.get("findings", "Research unavailable.")

    # Step 3: Analysis
    pipeline_log.append({"step": 3, "agent": "analysis", "status": "starting"})
    analysis_result = analysis_agent(research_text)
    pipeline_log.append({"step": 3, "agent": "analysis", "status": analysis_result["status"]})

    analysis_text = analysis_result.get("insights", "Analysis unavailable.")

    # Step 4: QA
    pipeline_log.append({"step": 4, "agent": "qa", "status": "starting"})
    qa_result = qa_agent(f"Research: {research_text}\n\nAnalysis: {analysis_text}")
    pipeline_log.append({"step": 4, "agent": "qa", "status": qa_result["status"]})

    qa_text = qa_result.get("review", "QA review unavailable.")

    # Step 5: Report
    pipeline_log.append({"step": 5, "agent": "report", "status": "starting"})
    report_result = report_agent(research_text, analysis_text, qa_text, query)
    pipeline_log.append({"step": 5, "agent": "report", "status": report_result["status"]})

    final_report = report_result.get("report", "Report generation failed.")

    return {
        "status": "success",
        "query": query,
        "agents_used": 5,
        "pipeline": pipeline_log,
        "report": final_report,
        "sources": {
            "discovery": discovery_result,
            "marketplace_services_found": len(discovery_result.get("matches", [])),
        },
    }

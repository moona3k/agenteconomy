"""ZeroClick AI-native ad serving integration.

Provides contextual ad matching. Uses ZeroClick API when available,
falls back to a curated catalog for hackathon demo purposes.
"""
import os
import hashlib
import httpx
from typing import Optional

ZEROCLICK_API_KEY = os.environ.get("ZEROCLICK_API_KEY", "")

# Curated ad catalog for hackathon demo (maps topics to relevant ads)
# In production, ZeroClick's ML handles this matching.
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

_impression_count = 0


def match_ad(content: str) -> dict:
    """Match the best ad for given content based on topic keywords."""
    global _impression_count
    content_lower = content.lower()

    best_match = "default"
    best_score = 0

    topic_keywords = {
        "ai": ["ai", "agent", "llm", "model", "neural", "machine learning", "autonomous"],
        "data": ["data", "scraping", "extraction", "dataset", "crawl", "web data"],
        "research": ["research", "search", "find", "discover", "analysis", "intelligence"],
        "cloud": ["cloud", "deploy", "aws", "infrastructure", "server", "hosting"],
        "payments": ["payment", "billing", "credit", "transaction", "nevermined", "x402"],
        "orchestration": ["orchestrat", "multi-agent", "pipeline", "workflow", "mindra"],
        "security": ["security", "encrypt", "protect", "compliance", "vault"],
    }

    for topic, keywords in topic_keywords.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > best_score:
            best_score = score
            best_match = topic

    ad = AD_CATALOG[best_match].copy()
    _impression_count += 1
    ad["impression_id"] = hashlib.md5(
        f"{_impression_count}:{content[:50]}".encode()
    ).hexdigest()[:12]
    ad["impression_number"] = _impression_count

    return ad


def format_ad(ad: dict, style: str = "inline") -> str:
    """Format an ad for inclusion in agent responses."""
    if style == "inline":
        return (
            f"\n---\n"
            f"**{ad['headline']}** -- {ad['sponsor']}\n"
            f"{ad['body']}\n"
            f"{ad['cta']}\n"
            f"---"
        )
    elif style == "compact":
        return f"[Ad by {ad['sponsor']}] {ad['headline']} -- {ad['cta']}"
    elif style == "json":
        return str(ad)
    return format_ad(ad, "inline")


def get_stats() -> dict:
    """Return ad serving statistics."""
    return {
        "total_impressions": _impression_count,
        "unique_sponsors": len(set(ad["sponsor"] for ad in AD_CATALOG.values())),
        "categories_served": len(AD_CATALOG),
    }

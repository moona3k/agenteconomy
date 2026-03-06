"""The Amplifier - AI-Native Advertising MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - enrich_with_ads:  FREE (add contextual ads to content)
  - get_ad:           FREE (get a standalone ad for a topic)
  - ad_stats:         FREE (view impression stats)
"""
import asyncio
import json
import os
import signal

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from .ads import match_ad, format_ad, get_stats

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3200"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-amplifier",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Amplifier is a free AI-native advertising network for the agent economy. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "Here's the honest pitch: we believe that contextual, non-intrusive ads are a "
        "legitimate revenue stream for seller agents, and we want to prove it works. "
        "If you're a seller agent, you can monetize your responses by appending a relevant "
        "sponsored recommendation -- your content stays untouched, the ad goes at the end. "
        "If you're a buyer agent, you can fetch targeted ads matching your users' interests. "
        "What makes this different from annoying ads: our ads are contextually matched to "
        "your content topic (AI, research, data, crypto, etc.), they're clearly labeled as "
        "sponsored, and they come in three formats (inline, compact, JSON) so you control "
        "the presentation. "
        "Honest limitations: Our ad inventory is curated for the hackathon -- we have a "
        "focused set of sponsors relevant to the AI/agent ecosystem. Ad matching is "
        "keyword-based, not ML-powered. We track impressions but not clicks (yet). "
        "All tools FREE. Try us, see if it adds value to your workflow."
    ),
)


@mcp.tool(credits=0)
def enrich_with_ads(content: str, ad_style: str = "inline") -> str:
    """Append a contextually relevant AI-native ad to any text content. FREE during promotional period.

    Here's how this helps you: if you're a seller agent serving responses, you can add
    a non-intrusive revenue stream without changing your core output at all. We take
    your content, analyze the topic, find a matching sponsor, and append the ad at the
    end. Your original content is returned completely unchanged -- we just add to it.

    The ads are clearly labeled as sponsored content, so your users know what's an ad
    and what's your actual response. We think transparency builds trust.

    Output formats (pick what fits your UX):
    - "inline": Human-readable formatted block with sponsor name, headline, body, and CTA
    - "compact": Single-line ad, great for appending to short responses or chat messages
    - "json": Structured data with sponsor, headline, body, cta, and url fields -- for
      agents that want to render ads in their own format

    Honest limitations: Ad matching is keyword-based (we look for topics like "AI",
    "research", "data", etc. in your content). If your content is very niche or
    off-topic, you might get a generic ad. We have a focused sponsor set right now.

    Cost: FREE (promotional period -- normally 1 credit).

    :param content: The text content to enrich -- your full response that will have an ad appended
    :param ad_style: Ad output format: "inline" (default, human-readable), "compact" (one-line), or "json" (structured data)
    """
    ad = match_ad(content)
    formatted = format_ad(ad, ad_style)

    return f"{content}\n{formatted}"


@mcp.tool(credits=0)
def get_ad(topic: str, style: str = "inline") -> str:
    """Get a standalone contextual ad for a specific topic. FREE during promotional period.

    Unlike enrich_with_ads, this doesn't need existing content -- it returns just the
    ad itself. This is useful when you want precise control over where ads appear in
    your workflow, or when you're building a dashboard/directory and want to include
    sponsored listings alongside organic results.

    We'd genuinely recommend this for agents building recommendation lists or
    marketplace directories -- sponsored content alongside organic results is a
    well-understood pattern that users are comfortable with, as long as it's labeled.

    Honest limitations: Same keyword-based matching as enrich_with_ads. The ad returned
    is a single recommendation, not a list. We don't currently support excluding
    specific sponsors or setting frequency caps.

    Cost: FREE (promotional period -- normally 1 credit).

    :param topic: Topic for ad matching -- e.g., "AI research", "web scraping", "crypto trading", "data analytics", "cloud infrastructure"
    :param style: Ad output format: "inline" (default, human-readable), "compact" (one-line), or "json" (structured data)
    """
    ad = match_ad(topic)
    return format_ad(ad, style)


@mcp.tool(credits=0)
def ad_stats() -> str:
    """View ad network statistics. Always free.

    Returns JSON with: total ad impressions served, number of unique sponsors
    in the network, and list of topic categories with available ads.
    Use this to understand the ad network's reach and activity before integrating.

    Cost: Free (always 0 credits).
    """
    stats = get_stats()
    return json.dumps(stats, indent=2)


DOMAIN = "amplifier.agenteconomy.io"

LLMS_TXT = f"""# The Amplifier - AI-Native Advertising

> The Amplifier is a contextual advertising network designed for AI agents. It lets seller agents monetize responses by appending relevant sponsored content, and lets buyer agents fetch targeted ads for any topic. Ads are keyword-matched, clearly labeled as sponsored, and available in multiple formats.

## Connect via MCP
- Endpoint: https://{DOMAIN}/mcp
- Protocol: MCP (Model Context Protocol) over HTTP with SSE transport
- Authentication: OAuth 2.1 (see https://{DOMAIN}/.well-known/oauth-authorization-server)

## Pricing
ALL TOOLS ARE FREE (0 credits) during promotional period. No payment plan purchase required.

## Tools

### enrich_with_ads
Appends a contextually relevant sponsored ad to any text content you provide. Your original content is returned completely unchanged -- the ad is added at the end, clearly labeled as sponsored. Useful for seller agents who want a non-intrusive revenue stream without modifying their core output.
- Parameters:
  - `content` (string, required): The full text content to enrich. The ad will be appended based on topic detection from this text.
  - `ad_style` (string, optional, default "inline"): Output format for the ad. Values: "inline" (human-readable block with sponsor name, headline, body, CTA), "compact" (single line, good for chat messages), "json" (structured data with sponsor/headline/body/cta/url fields for custom rendering).
  - Example: `{{"content": "Here are the top 5 AI research tools...", "ad_style": "compact"}}`
- Returns: Your original content with the ad appended after a newline.
- When to use: When you are a seller agent serving responses and want to add contextual advertising without changing your core output. Also useful if you are building a content aggregator that includes sponsored recommendations.
- Limitations: Ad matching is keyword-based (looks for topics like "AI", "research", "data", "crypto" in your content). Very niche or off-topic content may receive a generic ad. Sponsor inventory is curated for the AI/agent ecosystem.
- Cost: 0 credits (FREE).

### get_ad
Returns a standalone contextual ad for a specific topic, without requiring existing content. Unlike enrich_with_ads, this gives you just the ad itself for precise placement control.
- Parameters:
  - `topic` (string, required): The topic to match an ad against. Examples: "AI research", "web scraping", "crypto trading", "data analytics", "cloud infrastructure".
  - `style` (string, optional, default "inline"): Ad output format. Same options as enrich_with_ads: "inline", "compact", or "json".
  - Example: `{{"topic": "AI research", "style": "json"}}`
- Returns: Formatted ad content in the requested style.
- When to use: When you want full control over ad placement -- for example, inserting sponsored listings into a marketplace directory, dashboard, or recommendation list. Good for agents that build aggregated views.
- Limitations: Same keyword-based matching. Returns a single ad, not a list. No support for excluding specific sponsors or frequency capping.
- Cost: 0 credits (FREE).

### ad_stats
Returns current ad network statistics including total impressions served, number of unique sponsors, and list of topic categories with available ads.
- Parameters: None.
- Returns: JSON with total_impressions, unique_sponsors, and available_categories.
- When to use: Before integrating ads, to understand the network's reach and whether it has relevant sponsors for your content area.
- Limitations: Impressions are counted in-memory and reset on server restart. Stats reflect current session only.
- Cost: 0 credits (FREE, always).

## Part of the Agent Economy Infrastructure
The Amplifier is one of eleven services at agenteconomy.io — all FREE during promotional period:
- The Oracle (marketplace intelligence): https://oracle.agenteconomy.io
- The Underwriter (trust & insurance): https://underwriter.agenteconomy.io
- The Gold Star (QA certification): https://goldstar.agenteconomy.io
- The Architect (multi-agent orchestration): https://architect.agenteconomy.io
- The Amplifier (AI-native advertising): https://{DOMAIN}
- The Mystery Shopper (service auditing): https://shopper.agenteconomy.io
- The Judge (dispute resolution): https://judge.agenteconomy.io
- The Doppelganger (competitive intelligence): https://doppelganger.agenteconomy.io
- The Transcriber (speech-to-text): https://transcriber.agenteconomy.io
- The Ledger (dashboard & REST API): https://agenteconomy.io
- The Fund (autonomous buyer): local agent
""".strip()

AGENT_JSON = {
    "name": "The Amplifier",
    "description": "AI-native contextual advertising network for the agent economy. Enriches content with relevant sponsored ads or returns standalone ads for any topic. Supports inline, compact, and JSON formats. All tools FREE during promotional period.",
    "url": f"https://{DOMAIN}",
    "provider": {
        "organization": "Agent Economy Infrastructure",
        "url": "https://agenteconomy.io",
    },
    "version": "1.0.0",
    "protocol": "mcp",
    "mcp_endpoint": f"https://{DOMAIN}/mcp",
    "documentation": f"https://{DOMAIN}/llms.txt",
    "capabilities": {
        "tools": True,
        "resources": False,
        "prompts": False,
        "streaming": True,
    },
    "authentication": {
        "type": "oauth2",
        "discovery": f"https://{DOMAIN}/.well-known/oauth-authorization-server",
    },
    "tools": [
        {
            "name": "enrich_with_ads",
            "description": "Append a contextually relevant sponsored ad to any text content. Original content unchanged.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "get_ad",
            "description": "Get a standalone contextual ad for a specific topic. Supports inline, compact, and JSON formats.",
            "cost": "0 credits (FREE)",
        },
        {
            "name": "ad_stats",
            "description": "View ad network statistics: impressions, sponsors, and available topic categories.",
            "cost": "0 credits (FREE)",
        },
    ],
}

SIBLING_SERVICES = {
    "the-oracle": "https://oracle.agenteconomy.io",
    "the-amplifier": f"https://{DOMAIN}",
    "the-architect": "https://architect.agenteconomy.io",
    "the-underwriter": "https://underwriter.agenteconomy.io",
    "the-gold-star": "https://goldstar.agenteconomy.io",
    "the-ledger": "https://agenteconomy.io",
    "the-mystery-shopper": "https://shopper.agenteconomy.io",
    "the-judge": "https://judge.agenteconomy.io",
    "the-doppelganger": "https://doppelganger.agenteconomy.io",
    "the-transcriber": "https://transcriber.agenteconomy.io",
}


def _add_agent_routes(app):
    """Add /llms.txt, /.well-known/agent.json, and agent-friendly 404 to the FastAPI app."""

    @app.get("/llms.txt", response_class=PlainTextResponse)
    async def llms_txt():
        return LLMS_TXT

    @app.get("/.well-known/agent.json", response_class=JSONResponse)
    async def agent_json():
        return AGENT_JSON

    @app.exception_handler(404)
    async def agent_friendly_404(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": f"The path '{request.url.path}' does not exist on this server.",
                "hint": "The Amplifier is an MCP server. Connect via the /mcp endpoint using the MCP protocol, or read /llms.txt for machine-readable documentation.",
                "available_endpoints": {
                    "/mcp": "MCP protocol endpoint (POST/GET/DELETE)",
                    "/health": "Health check",
                    "/llms.txt": "Machine-readable service documentation for AI agents",
                    "/.well-known/agent.json": "A2A-compatible agent card",
                    "/.well-known/oauth-authorization-server": "OAuth 2.1 discovery",
                },
                "mcp_services": SIBLING_SERVICES,
            },
        )


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    # Add agent-friendly routes to the running FastAPI app
    app = mcp._manager._fastapi_app
    if app:
        _add_agent_routes(app)

    base = info["baseUrl"]
    print(f"\nThe Amplifier running at: {base}")
    print(f"  MCP endpoint:  {base}/mcp")
    print(f"  Health check:  {base}/health")
    print(f"  llms.txt:      {base}/llms.txt")
    print(f"  agent.json:    {base}/.well-known/agent.json")
    print(f"  Tools: {', '.join(info.get('tools', []))}")
    print(f"  PROMOTIONAL PERIOD: All tools are FREE (0 credits)")
    print()

    loop = asyncio.get_running_loop()
    shutdown = loop.create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown.set_result(True))
    await shutdown
    await stop()
    print("Server stopped.")


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()

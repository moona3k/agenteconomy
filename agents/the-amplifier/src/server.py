"""The Amplifier -- AI-Native Ad Integration MCP Server.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).
We're building the ad layer for the agent economy and want you to try it.

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


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    print(f"\nThe Amplifier running at: {info['baseUrl']}")
    print(f"  MCP endpoint:  {info['baseUrl']}/mcp")
    print(f"  Health check:  {info['baseUrl']}/health")
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

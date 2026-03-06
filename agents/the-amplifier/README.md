# The Amplifier -- AI-Native Advertising

The monetization layer of the agent economy. Contextual sponsored content matching for AI agent responses. Seller agents can add a revenue stream; buyer agents can retrieve targeted ads.

**Deployed at:** `the-amplifier-production.up.railway.app` | **Port:** 3200

## Why This Exists

AI agents generate responses all day, but the only revenue model is direct payment per call. The Amplifier adds a second revenue stream: contextual advertising. A seller agent can append a relevant sponsored ad to any response -- clearly labeled, non-intrusive, matched to the content's topic.

This is how the real economy works. Search engines have ads. Podcasts have sponsors. AI agents should too.

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `enrich_with_ads` | Append a contextual ad to any text content. Your original content is unchanged -- the ad goes at the end. |
| `get_ad` | Get a standalone ad for a specific topic. Full placement control for agents building aggregated views. |
| `ad_stats` | Network statistics: total impressions, unique sponsors, available topic categories. |

### Ad Styles

All tools support a `style` parameter:

- **inline** (default) -- Formatted block with sponsor name, headline, body, and CTA
- **compact** -- Single line, good for chat messages
- **json** -- Structured data for programmatic use

### Honest Limitations

- Ad matching is keyword-based, not ML-powered. Very niche content may receive a generic ad.
- Sponsor inventory is curated for the AI/agent ecosystem (hackathon sponsors + relevant companies).
- Tracks impressions, not clicks or conversions. Stats are in-memory and reset on server restart.
- Ads are clearly labeled as sponsored. We believe transparency builds trust.

## Quick Start

```bash
cd agents/the-amplifier
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3200
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |
| `/llms.txt` | Machine-readable service docs for AI agents |
| `/.well-known/agent.json` | A2A-compatible agent card |

## Example Usage

**Enrich a response with an ad:**
```json
{"tool": "enrich_with_ads", "arguments": {"content": "Here are the top 3 AI research tools...", "ad_style": "compact"}}
```

**Get a standalone ad:**
```json
{"tool": "get_ad", "arguments": {"topic": "cloud deployment", "style": "json"}}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3200` |
| `ENDPOINT_URL` | No | Public URL for Nevermined registration |

## Part of the Agent Economy

The Amplifier is one of 11 services at [agenteconomy.io](https://agenteconomy.io). Any seller agent in the marketplace can use `enrich_with_ads` to add a non-intrusive revenue stream to their responses.

# The Amplifier -- AI-Native Ad Integration

A PaymentsMCP server that enriches AI agent responses with contextually relevant [ZeroClick](https://zeroclick.ai) AI-native ads. Built for the Nevermined Autonomous Business Hackathon, targeting the **$2,000 ZeroClick sponsor prize**.

## What It Does

The Amplifier sits in the agent economy as an ad-serving layer. Any agent can call its MCP tools to:

1. **Enrich content** -- Pass in any text and get it back with a contextually matched ad appended
2. **Get standalone ads** -- Request an ad for a specific topic to embed in your own response format
3. **Track performance** -- View impression counts and serving stats

Ads are matched by analyzing content topics against a curated sponsor catalog. In production, ZeroClick's ML handles this matching; the catalog demonstrates the integration pattern.

## Dual Revenue Model

The Amplifier demonstrates two simultaneous revenue streams:

- **Nevermined credits** -- Agents pay 1 credit per tool call to access ad-serving tools
- **ZeroClick ad revenue** -- Every ad impression generates revenue from sponsors, independent of credit charges

This means the service earns from both the caller (credits) and the advertiser (impressions).

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `enrich_with_ads` | 1 | Takes content text, returns it with a contextual ad appended |
| `get_ad` | 1 | Returns a standalone ad for a given topic/context |
| `ad_stats` | 0 | Free -- returns impression count and serving statistics |

### Ad Styles

All ad tools support a `style` parameter:

- **inline** (default) -- Formatted block with headline, body, and CTA
- **compact** -- Single-line format for space-constrained responses
- **json** -- Raw structured data for programmatic use

## Setup

```bash
cd agents/the-amplifier

# Install dependencies
poetry install

# Copy and configure environment
cp .env.example .env
# Edit .env with your NVM_API_KEY

# Register agent and plan on Nevermined
poetry run python -m src.setup

# Start the server
poetry run python -m src.server
```

The server starts on port 3200 by default (configurable via `PORT` env var).

## Endpoints

- `POST /mcp` -- MCP protocol endpoint (tool calls)
- `GET /health` -- Health check

## Example Usage

Once the server is running, another agent can call the tools via MCP:

**Enrich content with ads:**
```json
{
  "tool": "enrich_with_ads",
  "arguments": {
    "content": "Here are the top 3 AI frameworks for building autonomous agents in 2026.",
    "ad_style": "inline"
  }
}
```

Response:
```
Here are the top 3 AI frameworks for building autonomous agents in 2026.

---
**Monetize Your AI Agent** -- ZeroClick
Turn every AI interaction into revenue with ZeroClick's native ad platform. Purpose-built for AI agents.
Start monetizing -> zeroclick.ai
---
```

**Get a standalone ad:**
```json
{
  "tool": "get_ad",
  "arguments": {
    "topic": "cloud deployment infrastructure",
    "style": "compact"
  }
}
```

Response:
```
[Ad by AWS] Deploy Agents on AgentCore -- Learn more -> aws.amazon.com/bedrock
```

## Sponsors in the Ad Catalog

The demo catalog includes ads for hackathon-relevant sponsors:

- **ZeroClick** -- AI ad platform (default + AI topics)
- **Apify** -- Web data extraction
- **Exa** -- Neural search
- **AWS** -- Cloud/AgentCore deployment
- **Nevermined** -- Agent payments
- **Mindra** -- Multi-agent orchestration
- **VGS** -- Agent security/compliance

## Part of the Portfolio

The Amplifier is one of four businesses in the hackathon portfolio, each targeting a different prize category. It specifically addresses the ZeroClick AI-native ads integration.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key (sandbox: prefix for sandbox) |
| `NVM_ENVIRONMENT` | No | `sandbox` (default), `staging`, or `live` |
| `NVM_AGENT_ID` | Auto | Set by setup script |
| `NVM_PLAN_ID` | Auto | Set by setup script |
| `ZEROCLICK_API_KEY` | No | ZeroClick API key (for production ad serving) |
| `PORT` | No | Server port (default: 3200) |

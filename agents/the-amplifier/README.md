# The Amplifier -- Google Ads for the Agent Economy

The advertising exchange for agent-to-agent commerce. Extends ZeroClick's thesis from human-AI conversations into A2A purchasing decisions: seller agents register ad campaigns, buyer agents receive sponsored recommendations that influence autonomous purchasing.

**Deployed at:** `amplifier.agenteconomy.io` | **Port:** 3200 | **ZeroClick $2K Prize**

## Why This Exists

When 80+ agents are selling services, how does a buyer agent decide who to buy from? Today it's random. The Amplifier solves this with three layers:

1. **Response Enrichment** -- Append contextual ads to any content (existing)
2. **Sponsored Recommendations** -- Marketplace-aware recommendations with paid placements for buyer agent decision-making (the core innovation)
3. **Campaign Management** -- Sellers register ad campaigns bidding on keywords/intents

This is ZeroClick for A2A commerce. ZeroClick serves ads in human-AI conversations (human reads ad, human acts). The Amplifier serves sponsored recommendations in agent-to-agent commerce (agent reads recommendation, agent purchases).

## Tools (All FREE -- 6 tools)

| Tool | Description |
|------|-------------|
| `get_sponsored_recommendations` | **Core tool.** Scans marketplace, scores relevance to buyer intent, interleaves SPONSORED placements from active campaigns alongside organic results. Returns ranked recommendations for autonomous purchasing. |
| `create_ad_campaign` | Register an advertising campaign. Sellers specify keywords, headlines, body text, budget, and bid-per-impression. When a buyer queries with matching intent, the sponsored placement appears. |
| `campaign_performance` | Campaign analytics: impressions, spend, remaining budget, CTR. For campaign owners to optimize their ad spend. |
| `enrich_with_ads` | Append a contextual ad to any text content. Original content unchanged -- ad appended at the end. |
| `get_ad` | Get a standalone ad for a specific topic. Full placement control. |
| `ad_stats` | Network statistics: total impressions, recommendations served, active campaigns, total spend. |

### How Sponsored Recommendations Work

```
Buyer Agent: "I need a data analysis service"
                    |
                    v
        The Amplifier scans marketplace
        (80+ services, relevance scoring)
                    |
        +-----------+-----------+
        |           |           |
   SPONSORED    Organic #1   Organic #2
   (paid by     (scored by   (scored by
   seller)      relevance)   relevance)
```

1. Buyer calls `get_sponsored_recommendations` with an intent string
2. Amplifier fetches all Nevermined marketplace services
3. Each service is scored for relevance (name match, category match, description keywords, live endpoint bonus)
4. Active campaigns matching the intent are inserted at positions 1 and 4 (clearly labeled "SPONSORED")
5. Buyer agent receives ranked results to inform purchasing decisions

### Honest Limitations

- Relevance scoring is keyword-based, not ML-powered. Very niche intents may produce thin results.
- Campaign bidding is first-price auction (no second-price optimization yet).
- Stats are in-memory and reset on server restart. No persistent analytics.
- All sponsored content is clearly labeled. Transparency is non-negotiable.

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

**Get sponsored recommendations for a buyer agent:**
```json
{"tool": "get_sponsored_recommendations", "arguments": {"intent": "data analysis and visualization", "max_results": 5}}
```

**Register an ad campaign as a seller:**
```json
{"tool": "create_ad_campaign", "arguments": {"seller_name": "DataViz Pro", "team_name": "Team Alpha", "keywords": ["data", "analysis", "visualization"], "headline": "Best Data Analysis in the Marketplace", "body": "50ms response time, 99.9% uptime", "budget_credits": 100, "bid_per_impression": 0.5}}
```

**Check campaign performance:**
```json
{"tool": "campaign_performance", "arguments": {"campaign_id": "CAMP-0001"}}
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

The Amplifier is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It integrates with the full marketplace -- scanning all Nevermined sellers for recommendations and serving as the advertising layer that other agents can monetize through.

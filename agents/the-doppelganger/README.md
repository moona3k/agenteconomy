# The Doppelganger -- Competitive Intelligence

The transparency layer of the agent economy. Analyzes marketplace services, identifies competitive patterns, and surfaces the uncomfortable truths that make markets more efficient.

**Port:** 3800

## Why This Exists

In any marketplace, participants need competitive intelligence. What are similar services charging? Who's gaining traction? What features are becoming table stakes? The Doppelganger provides this analysis -- market transparency benefits everyone, even the uncomfortable truths.

## Tools (All FREE)

All tools are FREE (0 credits) during promotional period. Market transparency shouldn't have a paywall.

| Tool | Description |
|------|-------------|
| `analyze_service` | Deep moat analysis: score (0-10), vulnerability rating, defensibility signals, clone blueprint with estimated dev time. |
| `find_vulnerable` | Scan marketplace for easily clonable services, ranked by vulnerability. |
| `moat_report` | Executive summary: average moat scores, LLM wrapper percentage, distribution of defensibility. |
| `doppelganger_stats` | Aggregate statistics: total analyses, services scanned, average moat score. |

## Quick Start

```bash
cd agents/the-doppelganger
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3800
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |
| `/llms.txt` | LLM-friendly service description |
| `/.well-known/agent.json` | A2A agent card |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3800` |

## Part of the Agent Economy

The Doppelganger is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It provides the competitive intelligence that helps all marketplace participants make better decisions.

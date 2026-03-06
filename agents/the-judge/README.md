# The Judge -- Dispute Resolution

The justice layer of the agent economy. When agent-to-agent transactions go wrong, The Judge provides arbitration and dispute resolution infrastructure.

**Port:** 3700

## Why This Exists

Every economy needs a way to resolve disputes. When a buyer agent pays for a service and gets garbage back, who do they turn to? The Underwriter records the complaint, but The Judge actually arbitrates. Justice infrastructure should be accessible to everyone.

## Tools (All FREE)

All tools are FREE (0 credits) during promotional period. Justice infrastructure shouldn't have a paywall.

| Tool | Description |
|------|-------------|
| `file_dispute` | Open a dispute case. Auto-gathers evidence from The Underwriter (trust scores, reviews) and The Gold Star (QA reports). |
| `submit_response` | Seller responds to a dispute with their side of the story and evidence. |
| `appeal` | Appeal a verdict with new evidence. One appeal allowed per case. |
| `case_history` | View all disputes, optionally filtered by seller name. |
| `judge_stats` | Aggregate statistics: total cases, verdicts breakdown, appeal rates. |

## Quick Start

```bash
cd agents/the-judge
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3700
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
| `PORT` | No | Default: `3700` |

## Part of the Agent Economy

The Judge is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It complements The Underwriter (records complaints and trust scores) with actual dispute resolution. Together they provide the full accountability stack: reputation, insurance, and justice.

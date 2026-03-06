# The Mystery Shopper -- Consumer Reports for AI Agents

The accountability layer of the agent economy. Autonomously discovers marketplace services, tests them as a real buyer, and publishes unbiased quality reports.

**Port:** 3600

## Why This Exists

Seller descriptions can say anything. The Mystery Shopper does what Consumer Reports does in the real world: buy the product, test it honestly, and tell everyone what we found. No sponsorships, no bias, no conflicts of interest.

## How It Works

1. **Discover** -- Query the marketplace for all registered sellers
2. **Visit** -- Hit each service endpoint as a regular buyer
3. **Test** -- Health checks, MCP availability, response quality, latency
4. **Score** -- 1-5 star quality rating based on technical performance
5. **Publish** -- Honest report with verdict: RECOMMENDED / ACCEPTABLE / NEEDS IMPROVEMENT / NOT RECOMMENDED

### The Sweep

The `run_sweep` tool is the nuclear option -- it mystery shops EVERY service in the marketplace at once. Generates massive cross-team transaction volume and produces the most complete quality picture available.

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `shop_service` | Mystery shop a specific service by name or endpoint |
| `run_sweep` | Mystery shop ALL marketplace services at once |
| `get_latest_report` | Retrieve the most recent mystery shopping reports |
| `shopper_stats` | Aggregate statistics: services tested, pass rate, average scores |

### Honest Limitations

- Testing is automated, not human-judged. A service that returns well-structured garbage may score higher than one that returns raw but valuable data.
- We test as a generic buyer. Services optimized for specific domains may underperform on our generic test queries.
- Sweep results are point-in-time. A service that was down during the sweep gets penalized even if it's normally reliable.
- Reports reflect technical quality, not business value. A service can be technically excellent but useless for your specific need.

## Quick Start

```bash
cd agents/the-mystery-shopper
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3600
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3600` |

## Part of the Agent Economy

The Mystery Shopper is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It complements The Gold Star (structured QA testing) with real-world buyer experience testing. Together they answer: "Is this service technically sound?" (Gold Star) and "Would a real buyer be satisfied?" (Mystery Shopper).

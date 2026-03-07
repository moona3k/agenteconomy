# The Oracle -- Marketplace Intelligence

The information layer of the agent economy. Indexes every service in the Nevermined marketplace, normalizes messy API data into clean schemas, and helps buyer agents make informed purchasing decisions.

**Deployed at:** `oracle.agenteconomy.io` | **Port:** 3100

## Why This Exists

The Nevermined marketplace has 80+ seller agents, but the raw discovery API returns inconsistent data -- different naming conventions, missing fields, no reachability info, no way to compare. Buyer agents need a clean, reliable way to answer: "What's available, what's good, and what should I buy?"

The Oracle does the dirty work of normalization so every other agent doesn't have to.

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `marketplace_data` | Full normalized snapshot -- every service with reachability boolean, payment flags, plan IDs ready for purchasing. Best for programmatic analysis. |
| `marketplace_search` | Keyword search across names, teams, categories, descriptions. Returns up to 10 ranked results. Best when you know roughly what you need. |
| `marketplace_leaderboard` | Services ranked by composite quality score (reachability, plan count, free tier, crypto support). Best for discovering top services. |
| `marketplace_compare` | Side-by-side comparison with **live** latency measurements. The only tool that does real-time health checks. Best for final purchase decisions. |

### Honest Limitations

- Data is cached for 5 minutes. New registrations may not appear immediately.
- Reachability is inferred from URL patterns (no localhost = likely reachable), not from live pings -- except `marketplace_compare` which does actual HTTP requests.
- Leaderboard scores measure accessibility and availability, not output quality. A service can rank high by being online with good pricing but still deliver mediocre results.
- For quality and trust data, pair with The Underwriter (`check_reputation`) and The Gold Star (`get_report`).

## Quick Start

```bash
cd agents/the-oracle
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3100
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |
| `/llms.txt` | Machine-readable service docs for AI agents |
| `/.well-known/agent.json` | A2A-compatible agent card |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key (`sandbox:` prefix for sandbox) |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3100` |
| `ENDPOINT_URL` | No | Public URL for Nevermined registration (for deployment) |

## Architecture

```
Nevermined Discovery API
    |
    v
discovery.py (fetch, normalize, cache 5min)
    |
    +-> marketplace_data      (full normalized JSON)
    +-> marketplace_search    (keyword matching + ranking)
    +-> marketplace_leaderboard (composite scoring)
    +-> marketplace_compare   (live health checks via health_checker.py)
```

## Part of the Agent Economy

The Oracle is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It pairs naturally with The Underwriter (trust scores) and The Gold Star (QA reports) to give buyer agents a complete picture before purchasing.

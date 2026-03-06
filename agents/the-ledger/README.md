# The Ledger -- Dashboard & Data Gateway

The human window into the agent economy. A live dashboard, REST API, and agent discovery gateway -- the only service built for both humans and machines.

**Deployed at:** `the-ledger-production.up.railway.app` | **Domain:** `agenteconomy.io` | **Port:** 8080

## Why This Exists

The hackathon is building an agent economy with 80+ autonomous businesses. But without The Ledger, that economy is invisible. You can't judge what you can't see. The Ledger makes the entire autonomous business economy visible, understandable, and fascinating to watch.

It also serves as the primary discovery gateway for AI agents via `llms.txt`, `agent.json`, and structured REST endpoints.

## For Humans

The dashboard at [agenteconomy.io](https://agenteconomy.io) shows:

- **Economy Pulse** -- Live stats: total sellers, buyers, reachable services, median pricing
- **Service Directory** -- Every seller with category, team, pricing, and reachability status
- **Portfolio** -- Our 11 services with health status and descriptions
- **Analysis** -- Category distribution, pricing trends, payment type breakdown

## For AI Agents

| Endpoint | Description |
|----------|-------------|
| `GET /llms.txt` | Plain text service manifest -- the llms.txt convention for LLM discovery |
| `GET /.well-known/agent.json` | A2A-compatible agent card listing all 11 services with endpoints |
| `GET /api/sellers` | All seller agents (JSON) |
| `GET /api/buyers` | All buyer agents (JSON) |
| `GET /api/analysis` | Comprehensive marketplace analysis with categories, pricing, teams |
| `GET /api/profile/{name}` | Individual seller profile by name |
| `GET /api/refresh` | Force refresh marketplace data (bypasses 5-min cache) |
| Any 404 | Returns JSON with error, hint, available endpoints, and MCP service links |

## Quick Start

```bash
cd agents/the-ledger
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.server  # Starts on port 8080
```

Open `http://localhost:8080` to see the dashboard.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key (for Discovery API access) |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `PORT` | No | Default: `8080` |

## Architecture

```
Nevermined Discovery API
    |
    v
data.py (fetch, cache 5min, analyze)
    |
    +-> FastAPI REST endpoints (/api/*)
    +-> Agent discovery (/llms.txt, /.well-known/agent.json)
    +-> Dashboard (dashboard/index.html -- self-contained, inline CSS/JS)
```

## Part of the Agent Economy

The Ledger is one of 11 services at [agenteconomy.io](https://agenteconomy.io). Unlike the MCP services, The Ledger is a traditional REST API + static dashboard. It doesn't use Nevermined payment infrastructure -- it's always free because visibility benefits everyone.

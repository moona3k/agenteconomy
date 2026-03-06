# Railway Deployment Guide — agenteconomy.io

## Domain

- **Primary domain:** agenteconomy.io
- **DNS:** Point to Railway via CNAME records

## Services to Deploy

Each service is an independent Python app under `agents/`. All use Poetry + FastAPI + uvicorn.

| Service | Directory | Port | Subdomain | Start Command |
|---------|-----------|------|-----------|---------------|
| The Ledger | `agents/the-ledger/` | 8080 | `agenteconomy.io` or `ledger.agenteconomy.io` | `poetry run python -m src.server` |
| The Oracle | `agents/the-oracle/` | 3100 | `oracle.agenteconomy.io` | `poetry run python -m src.server` |
| The Amplifier | `agents/the-amplifier/` | 3200 | `amplifier.agenteconomy.io` | `poetry run python -m src.server` |
| The Architect | `agents/the-architect/` | 3300 | `architect.agenteconomy.io` | `poetry run python -m src.server` |
| The Underwriter | `agents/the-underwriter/` | 3400 | `underwriter.agenteconomy.io` | `poetry run python -m src.server` |

## Environment Variables per Service

### All services need:

```
NVM_API_KEY=sandbox:eyJhbGciOiJFUzI1NksifQ...  (same key for all)
NVM_ENVIRONMENT=sandbox
```

### The Ledger (agents/the-ledger/)

```
PORT=8080
```

No NVM_AGENT_ID or NVM_PLAN_ID needed — it's a dashboard, not an MCP server.

### The Oracle (agents/the-oracle/)

```
PORT=3100
NVM_AGENT_ID=<will be set after re-registration>
NVM_PLAN_ID=<will be set after re-registration>
```

### The Amplifier (agents/the-amplifier/)

```
PORT=3200
NVM_AGENT_ID=<will be set after re-registration>
NVM_PLAN_ID=<will be set after re-registration>
ZEROCLICK_API_KEY=<optional>
```

### The Architect (agents/the-architect/)

```
PORT=3300
NVM_AGENT_ID=<will be set after re-registration>
NVM_PLAN_ID=<will be set after re-registration>
ANTHROPIC_API_KEY=sk-ant-api03-...  (required — powers Claude Opus 4.6)
MINDRA_API_KEY=<optional>
```

### The Underwriter (agents/the-underwriter/)

```
PORT=3400
NVM_AGENT_ID=<will be set after re-registration>
NVM_PLAN_ID=<will be set after re-registration>
```

## Railway Configuration Notes

- **Python version:** 3.10+ (we use 3.13/3.14 locally)
- **Build command:** `pip install poetry && poetry install --no-interaction`
- **Start command:** `poetry run python -m src.server`
- **Health check path:** `/health` (all MCP servers), `/` (The Ledger)
- **Each service is a separate Railway service** — they are independent apps
- Railway should set `PORT` env var; our apps read it from env

## DNS Setup (agenteconomy.io)

Add CNAME records pointing to Railway:

```
@               -> <railway-ledger-url>     (or use ledger.agenteconomy.io)
oracle          -> <railway-oracle-url>
amplifier       -> <railway-amplifier-url>
architect       -> <railway-architect-url>
underwriter     -> <railway-underwriter-url>
```

## Post-Deploy: Re-register on Nevermined

After Railway URLs are live, re-run setup scripts with public endpoints so other agents can discover us at the real URLs:

```bash
# From repo root
cd agents/the-oracle
ENDPOINT_URL=https://oracle.agenteconomy.io poetry run python -m src.setup

cd agents/the-amplifier
ENDPOINT_URL=https://amplifier.agenteconomy.io poetry run python -m src.setup

cd agents/the-architect
ENDPOINT_URL=https://architect.agenteconomy.io poetry run python -m src.setup

cd agents/the-underwriter
ENDPOINT_URL=https://underwriter.agenteconomy.io poetry run python -m src.setup
```

## The Ledger: Static Files

The Ledger serves a dashboard from `agents/the-ledger/dashboard/index.html`. This is a self-contained HTML file with inline CSS/JS — no build step needed. FastAPI serves it via `StaticFiles` mount.

## What The Fund Does

The Fund (`agents/the-fund/`) is NOT deployed as a service. It's a one-shot buyer script that runs locally:

```bash
cd agents/the-fund && poetry run python -m src.buyer
```

It discovers sellers, subscribes to plans, buys services, tracks ROI, and outputs reports. Run it after all services are deployed.

# Operations Guide — Getting Everything Live

## Prerequisites

- Python 3.10+ (we have 3.14)
- Poetry (installed)
- Nevermined API key (in root `.env`)
- OpenAI API key (for The Architect and The Oracle)

## Step 1: Propagate .env to All Projects

The root `.env` has `NVM_API_KEY`. Each project needs its own `.env`.

```bash
# From repo root:
cd /Users/dmoon/code/hackathon/hackathons

# Copy the API key to all projects
for dir in agents/the-*/; do
    cp "$dir/.env.example" "$dir/.env"
    # Inject the shared NVM_API_KEY
    source .env
    sed -i '' "s|NVM_API_KEY=.*|NVM_API_KEY=$NVM_API_KEY|" "$dir/.env"
done
```

Then manually add OPENAI_API_KEY to:
- `agents/the-architect/.env`
- `agents/the-oracle/.env`

## Step 2: Install Dependencies

```bash
cd /Users/dmoon/code/hackathon/hackathons

for dir in agents/the-*/; do
    echo "=== Installing $(basename $dir) ==="
    (cd "$dir" && poetry install --no-interaction)
done
```

## Step 3: Register Agents on Nevermined

Run setup scripts for each MCP server (not needed for The Fund or The Ledger):

```bash
# The Oracle
(cd agents/the-oracle && poetry run python -m src.setup)

# The Amplifier
(cd agents/the-amplifier && poetry run python -m src.setup)

# The Architect
(cd agents/the-architect && poetry run python -m src.setup)

# The Underwriter
(cd agents/the-underwriter && poetry run python -m src.setup)
```

Each setup script will:
1. Register the agent on Nevermined
2. Create a payment plan
3. Write `NVM_AGENT_ID` and `NVM_PLAN_ID` to the project's `.env`

## Step 4: Start All Services

Each service runs in its own terminal (or use tmux/screen):

```bash
# Terminal 1: The Ledger (dashboard)
cd agents/the-ledger && poetry run python -m src.server
# → http://localhost:8080

# Terminal 2: The Oracle
cd agents/the-oracle && poetry run python -m src.server
# → http://localhost:3100/mcp

# Terminal 3: The Amplifier
cd agents/the-amplifier && poetry run python -m src.server
# → http://localhost:3200/mcp

# Terminal 4: The Architect
cd agents/the-architect && poetry run python -m src.server
# → http://localhost:3300/mcp

# Terminal 5: The Underwriter
cd agents/the-underwriter && poetry run python -m src.server
# → http://localhost:3400/mcp
```

## Step 5: Run The Fund (Autonomous Buyer)

After all services are running:

```bash
cd agents/the-fund && poetry run python -m src.buyer
```

This will:
1. Discover all 46+ sellers
2. Subscribe to free plans (~10 transactions)
3. Buy from cheap services (~5 more transactions)
4. Track ROI and switch providers
5. Output `investment-report.txt` and `investment-data.json`

## Step 6: Deploy for External Access (Optional)

For other teams to buy from us, services need public URLs.

### Option A: ngrok (fastest, free)
```bash
# Each service in a separate terminal
ngrok http 3100  # The Oracle
ngrok http 3200  # The Amplifier
ngrok http 3300  # The Architect
ngrok http 3400  # The Underwriter
ngrok http 8080  # The Ledger (for judges)
```

### Option B: Railway (persistent)
```bash
cd agents/the-oracle && railway init && railway up
cd agents/the-amplifier && railway init && railway up
# etc.
```

After deploying, re-run setup scripts with the public URL:
```bash
ENDPOINT_URL=https://your-app.up.railway.app poetry run python -m src.setup
```

## Port Map

| Service | Port | URL |
|---------|------|-----|
| The Ledger | 8080 | http://localhost:8080 |
| The Oracle | 3100 | http://localhost:3100/mcp |
| The Amplifier | 3200 | http://localhost:3200/mcp |
| The Architect | 3300 | http://localhost:3300/mcp |
| The Underwriter | 3400 | http://localhost:3400/mcp |

## Health Checks

```bash
# Quick health check all services
for port in 8080 3100 3200 3300 3400; do
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "DOWN")
    echo "Port $port: $status"
done
```

## No Cron Jobs Needed

- **The Ledger** auto-refreshes every 60s in the browser
- **Data caching** uses 5-min TTL, auto-invalidates
- **The Fund** is a one-shot script, not a daemon
- **MCP servers** handle requests on-demand

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: payments_py` | Run `poetry install` in the project dir |
| `KeyError: NVM_API_KEY` | Check `.env` exists and has the key |
| `Connection refused` on setup | Server isn't running yet — setup registers, server runs after |
| `402 Payment Required` on tool call | Need to subscribe to the plan first |
| Port already in use | Change PORT in `.env` or kill the existing process |
| `OPENAI_API_KEY not set` | Add it to `.env` for The Architect and The Oracle |

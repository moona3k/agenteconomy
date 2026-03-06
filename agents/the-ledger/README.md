# The Ledger -- The Human Window into the Agent Economy

The only project at the hackathon built for HUMANS, not just agents.

While every other team builds agents that talk to agents, The Ledger makes the entire autonomous business economy visible, understandable, and fascinating to watch.

## What It Is

A real-time dashboard and intelligence platform that:

- **Monitors** all sellers and buyers in the hackathon marketplace
- **Analyzes** economic patterns: category distribution, pricing trends, network effects
- **Profiles** every autonomous business with detailed breakdowns
- **Visualizes** the economy as a living network of transactions

Think: Bloomberg Terminal meets a newsroom for AI agent commerce.

## Why It Matters

The hackathon is building an agent economy. But without The Ledger, that economy is invisible. You can't judge what you can't see.

The Ledger is:
- The **scoreboard** judges use during deliberation
- The **proof** that real economic activity is happening
- The **story** of what the autonomous business hackathon actually built

## Quick Start

```bash
# Install
cd agents/the-ledger
poetry install

# Configure
cp .env.example .env
# Add your NVM_API_KEY to .env

# Run
poetry run python -m src.server
```

Open http://localhost:8080 -- you'll see the live dashboard.

## Dashboard Features

### Overview
Big stat cards, category distribution, payment type breakdown. The 30-second snapshot of the entire economy.

### Sellers Directory
Sortable, searchable table of all sellers. Click any row to see full details: endpoints, pricing, plan IDs, team info.

### Buyers Directory
All registered buyers with their needs and budgets.

### Analysis
Power team rankings, marketplace gaps, pricing distribution. The intelligence layer.

### Network
Visual representation of which teams are buying and selling. The economic graph.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/sellers` | All sellers with full details |
| `GET /api/buyers` | All buyers |
| `GET /api/analysis` | Computed analytics (categories, teams, payment types) |
| `GET /api/refresh` | Force refresh from Discovery API |
| `GET /api/profile/{name}` | Individual seller profile |

## Architecture

```
Discovery API -> Data Layer (cached, 5-min TTL) -> FastAPI -> Dashboard
                     |
              Analysis Engine
              (patterns, rankings, gaps)
```

## Data Sources

All data comes from the Nevermined Hackathon Discovery API:
- `GET https://nevermined.ai/hackathon/register/api/discover?side=sell`
- `GET https://nevermined.ai/hackathon/register/api/discover?side=buy`
- Requires `x-nvm-api-key` header with any hackathon participant's API key

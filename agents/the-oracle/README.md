# The Oracle -- Marketplace Intelligence Engine

Rates, ranks, and recommends hackathon agent services. Other teams' buyer agents pay to query our marketplace intelligence.

## What It Does

The Oracle pulls all 46+ sellers from the Nevermined Discovery API, tests their endpoints, scores them, and answers natural language queries about the marketplace.

### Tools (MCP)

| Tool | Credits | Description |
|------|---------|-------------|
| `marketplace_search` | 1 | Search services by keyword, category, or team name |
| `marketplace_leaderboard` | 1 | Ranked list of all services (filterable by category) |
| `marketplace_compare` | 2 | Head-to-head comparison with live health checks |

### Example Queries

- "Find the cheapest web search service"
- "Show me all research agents"
- "Compare Mog Markets vs SwitchBoard AI"
- "What's the best service with a free plan?"

## Quick Start

```bash
# Install
poetry install

# Set up .env (copy from .env.example, add your NVM_API_KEY)
cp .env.example .env

# Register agent + plan on Nevermined
poetry run python -m src.setup

# Start the server
poetry run python -m src.server
```

The server starts on port 3100 by default.

## Connect Your Agent

```json
{
  "mcpServers": {
    "the-oracle": {
      "type": "http",
      "url": "http://localhost:3100/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_X402_TOKEN"
      }
    }
  }
}
```

## Architecture

```
Discovery API (nevermined.ai) -> The Oracle -> Buyer Agents
                                    |
                              Health Checker
                              (tests endpoints)
```

## Part of the Grand Strategy

The Oracle is one of 4 autonomous businesses we're running:
- **The Oracle** (this) -- marketplace intelligence seller
- **The Fund** -- autonomous buyer with ROI tracking
- **The Amplifier** -- ZeroClick ad integration
- **The Architect** -- Mindra multi-agent orchestrator

See `docs/VISION.md` for the full strategy.

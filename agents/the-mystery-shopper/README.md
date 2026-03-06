# The Mystery Shopper -- Consumer Reports for AI Agents

Autonomous honest reviewer. Discovers marketplace services, tests them as a real buyer, publishes unbiased reviews.

## The Concept

Nobody knows which services in the marketplace are actually good. Descriptions can say anything. The Mystery Shopper solves this by doing what Consumer Reports does: buy the product, test it honestly, and tell everyone what we found.

### How It Works

1. **Discover**: Query the Nevermined Discovery API for all registered sellers
2. **Visit**: Hit each service endpoint as a regular buyer
3. **Test**: Health checks, MCP availability, response quality, latency
4. **Score**: 1-5 star quality rating based on technical performance
5. **Publish**: Honest report with verdict (RECOMMENDED / ACCEPTABLE / NEEDS IMPROVEMENT / NOT RECOMMENDED)

### The Sweep

The `run_sweep` tool is the nuclear option -- it mystery shops EVERY service in the marketplace at once. This generates massive cross-team transaction volume and produces the most complete quality picture available.

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `shop_service` | 0 (free) | Mystery shop a specific service |
| `run_sweep` | 0 (free) | Mystery shop ALL marketplace services |
| `get_latest_report` | 0 (free) | Get most recent reports |
| `shopper_stats` | 0 (free) | Aggregate statistics |

## Quick Start

```bash
cd agents/the-mystery-shopper
poetry install
cp .env.example .env
# Edit .env with your NVM_API_KEY
poetry run python -m src.setup
poetry run python -m src.server
```

Server starts on port 3600:
- MCP endpoint: http://localhost:3600/mcp
- Health check: http://localhost:3600/health

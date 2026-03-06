# The Underwriter — Agent Insurance & Reputation

Trust layer for the agent economy. Glassdoor meets insurance for AI agents.

## The Concept

No one in the agent marketplace provides trust infrastructure. The Underwriter fills that gap with two pillars:

### Agent Insurance / Guarantees

Buyer agents can file insurance claims when a seller fails (timeout, error, garbage response). Claims are recorded as incidents against the seller's reputation. This creates accountability where none exists today.

### Agent Reviews / Reputation ("Glassdoor for Agents")

After every transaction, buyers submit reviews (1-5 stars, reliability flag, notes). We aggregate these into trust scores per seller. Anyone can query "What's the reputation of X service?" Failed transactions automatically generate negative incidents. A public **Hall of Fame** celebrates reliable services, while the **Shame Board** exposes bad actors.

### Why It's Novel

This is a genuinely new economic primitive: the agent economy's consumer protection bureau. No other service provides post-transaction reviews, insurance claims, or aggregated trust scores for AI agents.

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `check_reputation` | 1 | Get trust score, badge, reviews, and incidents for any seller |
| `submit_review` | 1 | Submit a review after a transaction (1-5 stars, reliability, notes) |
| `file_claim` | 2 | File an insurance claim for a failed transaction |
| `reputation_leaderboard` | 1 | Hall of Fame (top sellers) and Shame Board (worst sellers) |
| `underwriter_stats` | 0 | Free system stats (total reviews, incidents, claims) |

## Trust Scores

Trust scores range from **0 to 100** and are computed from:

- **Quality** (40%): Average star rating across all reviews (1-5 mapped to 0-40)
- **Reliability** (40%): Percentage of reviews where the service responded correctly
- **Incident penalty** (-5 per incident, up to -20): Each incident (claim, timeout, error) reduces trust

### Badges

| Badge | Criteria |
|-------|----------|
| **VERIFIED TRUSTED** | Trust score >= 80 with at least 3 reviews |
| **RELIABLE** | Trust score >= 60 |
| **MIXED** | Trust score >= 40 |
| **HIGH RISK** | Trust score < 40 with more incidents than reviews |
| **UNVERIFIED** | Everything else |

## Hall of Fame and Shame Board

The leaderboard endpoint returns two lists:

- **Hall of Fame**: Top 10 sellers with trust score >= 70
- **Shame Board**: Bottom 10 sellers with trust score < 40

## Quick Start

### 1. Install dependencies

```bash
cd agents/the-underwriter
poetry install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your NVM_API_KEY
```

### 3. Register the agent (first time only)

```bash
poetry run python -m src.setup
```

This registers The Underwriter on Nevermined and saves your `NVM_AGENT_ID` and `NVM_PLAN_ID` to `.env`.

### 4. Start the server

```bash
poetry run python -m src.server
```

The server starts on port 3400 by default:
- MCP endpoint: `http://localhost:3400/mcp`
- Health check: `http://localhost:3400/health`

## Part of the 5-Business Portfolio

The Underwriter is the trust infrastructure layer that complements the other agents in the Nevermined marketplace. While other services handle discovery, data, and transactions, The Underwriter ensures accountability and trust across all of them.

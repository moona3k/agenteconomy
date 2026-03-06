# Agent Economy Infrastructure

**Autonomous business infrastructure for the Nevermined AI agent marketplace.**

Built by **Team Full Stack Agents** for the [Nevermined Autonomous Business Hackathon](https://nevermined.ai) (March 5-6, 2026).

**Live at [agenteconomy.io](https://agenteconomy.io)**

---

## What Is This?

11 interconnected autonomous businesses that provide the infrastructure layer every agent economy needs. The Nevermined marketplace has 80+ seller agents and 16+ buyer agents, but no way for buyer agents to make informed decisions. We built the missing layers: discovery, trust, quality, advertising, orchestration, analytics, dispute resolution, competitive intelligence, transcription, and autonomous buying.

**PROMOTIONAL PERIOD: All MCP tools are FREE (0 credits).**

---

## Our Services

### Deployed (Railway)

| Service | What It Does | Port | Endpoint | MCP Tools |
|---------|-------------|------|----------|-----------|
| **The Oracle** | Marketplace intelligence | 3100 | `oracle-production.up.railway.app` | marketplace_data, marketplace_search, marketplace_leaderboard, marketplace_compare |
| **The Underwriter** | Trust & insurance | 3400 | `the-underwriter-production.up.railway.app` | check_reputation, submit_review, file_claim, reputation_leaderboard, underwriter_stats |
| **The Gold Star** | AI-powered QA (Claude Sonnet) | 3500 | `the-gold-star-production.up.railway.app` | request_review, get_report, certification_status, gold_star_stats |
| **The Amplifier** | AI-native advertising | 3200 | `the-amplifier-production.up.railway.app` | enrich_with_ads, get_ad, ad_stats |
| **The Architect** | Multi-agent orchestration (Claude Opus) | 3300 | `the-architect-production.up.railway.app` | orchestrate, quick_research, pipeline_status |
| **The Ledger** | Dashboard & REST API | 8080 | `the-ledger-production.up.railway.app` | REST: /api/sellers, /api/buyers, /api/analysis |

### In Development

| Service | What It Does | Port |
|---------|-------------|------|
| **The Mystery Shopper** | Autonomous honest reviewer -- tests services as a real buyer | 3600 |
| **The Judge** | Dispute resolution for agent-to-agent conflicts | 3700 |
| **The Doppelganger** | Competitive intelligence & autonomous cloning | 3800 |
| **The Transcriber** | Local-model speech-to-text on Apple Silicon | 3900 |

### Local Only

| Service | What It Does |
|---------|-------------|
| **The Fund** | Autonomous buyer -- discovers, evaluates, purchases, reviews, tracks ROI |

---

## Quick Start

```bash
cd agents/the-oracle  # or any service directory
cp .env.example .env
# Edit .env with your keys

poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Start the server
```

---

## Repository Structure

```
.
├── agents/                          # All services live here
│   │
│   │  # --- Agent Economy (ours) ---
│   ├── the-oracle/                  # Marketplace intelligence (MCP)
│   ├── the-underwriter/             # Trust & insurance (MCP)
│   ├── the-gold-star/               # QA certification (MCP)
│   ├── the-amplifier/               # Advertising (MCP)
│   ├── the-architect/               # Multi-agent orchestration (MCP)
│   ├── the-ledger/                  # Dashboard + REST API
│   ├── the-fund/                    # Autonomous buyer (local)
│   ├── the-mystery-shopper/         # Honest reviewer (MCP)
│   ├── the-judge/                   # Dispute resolution (MCP)
│   ├── the-doppelganger/            # Competitive intelligence (MCP)
│   ├── the-transcriber/             # Speech-to-text (MCP)
│   │
│   │  # --- Nevermined examples (upstream) ---
│   ├── buyer-simple-agent/          # Example: A2A buyer with web frontend
│   ├── seller-simple-agent/         # Example: x402 + A2A seller
│   ├── mcp-server-agent/            # Example: MCP server with payments
│   └── strands-simple-agent/        # Example: Strands SDK + x402
│
├── research/                        # Blog posts, essays, glossary
├── reports/                         # Marketplace snapshots, per-agent analysis
├── docs/                            # Strategy, deployment guides, research
│
│  # --- Nevermined upstream content ---
├── workshops/                       # Hackathon workshop materials
├── subgraphs/                       # Nevermined Base Sepolia subgraph
│
├── CLAUDE.md                        # Instructions for AI coding agents
└── README.md                        # You are here
```

### Every Agent Follows This Pattern

```
agents/the-{name}/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server entry point
│   ├── setup.py               # Nevermined registration (one-time)
│   └── {module}.py            # Core business logic
├── .env.example               # Required env vars
├── pyproject.toml             # Poetry config (package-mode = false)
├── Procfile                   # Railway deployment
├── requirements.txt           # Railway deployment
└── README.md
```

MCP server pattern:
```python
from payments_py.mcp import PaymentsMCP

mcp = PaymentsMCP(payments, name="service-name", agent_id=AGENT_ID, ...)

@mcp.tool(credits=0)  # FREE during promotional period
def my_tool(param: str) -> str:
    """What it does. What it returns. When to use. Honest limitations."""
    return result
```

---

## How Services Connect

```
Buyer Agent (or The Fund)
    |
    +-> The Oracle: "What services are available?"
    +-> The Underwriter: "Is this seller trustworthy?"
    +-> The Gold Star: "Has this service been QA'd?"
    +-> The Mystery Shopper: "What's the real experience like?"
    |
    +-> [Purchases from marketplace sellers]
    |
    +-> The Underwriter: submit_review (post-purchase)
    +-> The Amplifier: enrich_with_ads (optional monetization)
    +-> The Architect: orchestrate (complex research tasks)
    +-> The Judge: file_dispute (if something goes wrong)
```

---

## Agent Discovery

| Method | URL | Format |
|--------|-----|--------|
| llms.txt | `agenteconomy.io/llms.txt` | Plain text for LLMs |
| Agent Card | `agenteconomy.io/.well-known/agent.json` | A2A-compatible JSON |
| REST API | `agenteconomy.io/api/sellers` | JSON marketplace data |
| MCP | `{service}.up.railway.app/mcp` | Direct MCP connection |

---

## Environment Variables

All services need:
```
NVM_API_KEY=sandbox:your-nevermined-key
NVM_ENVIRONMENT=sandbox
ANTHROPIC_API_KEY=sk-ant-...   # The Architect + The Gold Star only
```

---

## Tech Stack

Python, Poetry, FastAPI, Nevermined payments-py SDK, Anthropic Claude (Opus 4.6 + Sonnet 4.6), Railway, Cloudflare

---

## License

Built for the Nevermined Autonomous Business Hackathon. Team Full Stack Agents.

# Agent Economy Infrastructure

**11 autonomous businesses providing trust, quality, and commerce infrastructure for the Nevermined AI agent marketplace.**

Built by **Team Full Stack Agents** for the [Nevermined Autonomous Business Hackathon](https://nevermined.ai) (March 5-6, 2026).

**Live at [agenteconomy.io](https://agenteconomy.io)** | **All MCP tools FREE (0 credits)**

---

## What Is This?

Every team built an agent. We built the economy those agents need to function.

The Nevermined marketplace has 80+ seller agents and 16+ buyer agents, but no way for buyer agents to make informed purchasing decisions. No trust scores, no quality certification, no honest reviews, no advertising, no dispute resolution. Human economies have Moody's, Michelin stars, Consumer Reports, Google Ads, and small claims court. We built the agent economy equivalents.

**11 interconnected services. 9 MCP servers. 30+ tools. All free.**

---

## Our Services

### MCP Servers (deployed on Railway)

| Service | What It Does | Domain | MCP Tools |
|---------|-------------|--------|-----------|
| **The Oracle** | Marketplace intelligence engine | `oracle.agenteconomy.io` | marketplace_data, marketplace_search, marketplace_leaderboard, marketplace_compare |
| **The Underwriter** | Trust scores & insurance claims | `underwriter.agenteconomy.io` | check_reputation, submit_review, file_claim, reputation_leaderboard, underwriter_stats |
| **The Gold Star** | AI-powered QA certification (Claude Sonnet) | `goldstar.agenteconomy.io` | request_review, get_report, certification_status, gold_star_stats |
| **The Amplifier** | Advertising exchange for A2A commerce (ZeroClick) | `amplifier.agenteconomy.io` | enrich_with_ads, get_ad, ad_stats, get_sponsored_recommendations, create_ad_campaign, campaign_performance |
| **The Architect** | 7-agent hierarchical orchestration (Mindra) | `architect.agenteconomy.io` | orchestrate, quick_research, pipeline_status |
| **The Mystery Shopper** | Autonomous honest reviewer | `shopper.agenteconomy.io` | shop_service, run_sweep, get_latest_report, shopper_stats |
| **The Judge** | Dispute resolution with evidence-based rulings | `judge.agenteconomy.io` | file_dispute, check_dispute, judge_stats |
| **The Doppelganger** | Competitive intelligence & moat analysis | `doppelganger.agenteconomy.io` | analyze_service, find_vulnerable, moat_report, doppelganger_stats |
| **The Transcriber** | Local-model speech-to-text (NVIDIA Parakeet on Apple Silicon) | Local only (requires GPU) | transcribe_youtube, transcribe_file, transcriber_info |

### REST & Dashboard

| Service | What It Does | Domain |
|---------|-------------|--------|
| **The Ledger** | Human-readable dashboard + REST API | `agenteconomy.io` |

### Autonomous Buyer (Local)

| Service | What It Does |
|---------|-------------|
| **The Fund** | Autonomous capital allocator -- discovers, evaluates, purchases, reviews, tracks ROI across the marketplace |

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
                         The Fund (autonomous buyer)
                              |
          PRE-PURCHASE        |        POST-PURCHASE
          ─────────────       |        ──────────────
                              |
  The Oracle ─────────────────+──────────────── The Underwriter
  "What's available?"         |                 submit_review()
                              |
  The Underwriter ────────────+──────────────── The Judge
  "Is this seller trusted?"   |                 file_dispute()
                              |
  The Gold Star ──────────────+──────────────── The Amplifier
  "Is this service certified?"|                 enrich_with_ads()
                              |
  The Mystery Shopper ────────+
  "What's it really like?"    |
                              |
  The Amplifier ──────────────+
  "Who's sponsored?"          |
                              |
  The Doppelganger ───────────+
  "Does this have a moat?"    |
                              v
                    [Purchase from seller]

  The Architect: 7-agent hierarchical orchestration for complex research
  The Transcriber: Real local compute (speech-to-text, not an API wrapper)
  The Ledger: Human dashboard at agenteconomy.io
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

Python, Poetry, FastAPI, Nevermined payments-py SDK, Anthropic Claude Sonnet 4.6, NVIDIA Parakeet (local ML), Railway, Cloudflare

## Sponsor Integrations

| Sponsor | Prize | Our Integration |
|---------|-------|-----------------|
| **ZeroClick** ($2K) | AI-native ads | The Amplifier: Sponsored recommendations for A2A commerce. Extends ZeroClick's thesis from human-AI to agent-to-agent advertising. |
| **Mindra** ($2K) | Multi-agent orchestration | The Architect: 7 agents, 3 layers, orchestrators of orchestrators. CEO delegates to 3 VP orchestrators, each managing 2 leaf agents. |
| **Apify** ($1K) | Web scraping | The Oracle + The Fund: Marketplace intelligence and autonomous purchasing powered by live data. |
| **Nevermined** ($3K) | Grand prize | All 11 services use Nevermined PaymentsMCP SDK. The Fund executes real cross-team transactions. |

## Research

The `research/` directory contains a 5-part blog series and academic paper on agent economy infrastructure, covering Coasean economics, trust layers, advertising models, and competitive dynamics.

---

Built for the Nevermined Autonomous Business Hackathon (March 5-6, 2026). Team Full Stack Agents.

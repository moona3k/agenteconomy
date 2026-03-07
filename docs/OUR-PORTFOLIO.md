# Our Portfolio: 11 Autonomous Businesses

> "Every team built an agent. We built the trust infrastructure those agents need."

## The Thesis

The agent economy has no trust layer. No ratings, no QA, no mystery shoppers, no quality verification, no advertising, no dispute resolution. Human economies have Michelin stars, Consumer Reports, Glassdoor, Moody's, Google Ads, and small claims court. We built the agent economy equivalents.

Our portfolio covers four layers:

1. **Trust** -- Gold Star certifies quality, Underwriter tracks reputation, Mystery Shopper reviews honestly
2. **Commerce** -- The Fund buys autonomously, The Amplifier runs advertising, The Architect orchestrates complex tasks
3. **Intelligence** -- The Oracle maps the marketplace, The Doppelganger analyzes competitive moats
4. **Infrastructure** -- The Ledger makes it legible to humans, The Judge resolves disputes, The Transcriber provides real compute

---

## Layer 1: Trust Infrastructure (THE DIFFERENTIATOR)

### The Gold Star -- "Michelin Stars for AI Agents"
**Active QA and certification. Sellers pay to get tested and earn the seal.**

| | |
|---|---|
| **What** | Comprehensive QA suite: health checks, MCP availability, response quality, latency, error handling. Detailed reports with improvement recommendations. Iterate until 5-star certification. |
| **Why novel** | First quality certification authority for AI agents. You don't buy the Gold Star -- you earn it. |
| **Port** | 3500 |
| **Tools** | `request_review` (free), `get_report` (free), `certification_status` (free), `gold_star_stats` (free) |
| **Run** | `cd agents/the-gold-star && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Underwriter -- "Glassdoor + Insurance for AI Agents"
**Passive reputation database. The credit bureau of the agent economy.**

| | |
|---|---|
| **What** | Trust scores (0-100), post-transaction reviews, insurance claims, Hall of Fame + Shame Board |
| **Why novel** | No trust infrastructure exists. First consumer protection bureau for agents. |
| **Port** | 3400 |
| **Tools** | `check_reputation` (free), `submit_review` (free), `file_claim` (free), `reputation_leaderboard` (free), `underwriter_stats` (free) |
| **Run** | `cd agents/the-underwriter && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Mystery Shopper -- "Consumer Reports for AI Agents"
**Autonomous reviewer. Tests services anonymously. Publishes honest reviews.**

| | |
|---|---|
| **What** | Discovers all marketplace services, mystery shops them as a regular buyer, publishes quality reports with 1-5 star scores |
| **Why novel** | First autonomous quality auditor. Nobody knows when the Mystery Shopper is testing your service. |
| **Port** | 3600 |
| **Tools** | `shop_service` (free), `run_sweep` (free), `get_latest_report` (free), `shopper_stats` (free) |
| **Run** | `cd agents/the-mystery-shopper && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

## Layer 2: Visibility

### The Ledger -- "The Human Window into the Agent Economy"
**Real-time dashboard. The only project built for humans.**

| | |
|---|---|
| **What** | Bloomberg Terminal for the hackathon: all sellers, buyers, categories, pricing, network graph, trust data |
| **Why novel** | Only project for humans. Makes the invisible economy visible. |
| **Port** | 8080 |
| **Run** | `cd agents/the-ledger && poetry install && poetry run python -m src.server` |
| **Open** | http://localhost:8080 |

---

## Layer 3: Services

### The Amplifier -- "Google Ads for the Agent Economy"
**Advertising exchange for A2A commerce. Extends ZeroClick's thesis from human-AI to agent-to-agent advertising.**

| | |
|---|---|
| **What** | Three-layer ad platform: (1) contextual ad matching, (2) marketplace-aware sponsored recommendations with relevance scoring, (3) campaign management where sellers bid on keywords/intents. Scans the full Nevermined marketplace, scores service relevance, and interleaves sponsored placements (clearly labeled) alongside organic results. |
| **Why novel** | ZeroClick serves ads in human-AI conversations. We extend this into A2A commerce -- seller agents register ad campaigns, buyer agents receive sponsored recommendations that influence autonomous purchasing decisions. This is the ad network for the agent economy. |
| **Port** | 3200 |
| **Tools** | `enrich_with_ads` (free), `get_ad` (free), `ad_stats` (free), `get_sponsored_recommendations` (free), `create_ad_campaign` (free), `campaign_performance` (free) |
| **Run** | `cd agents/the-amplifier && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Architect -- "7-Agent Hierarchical Orchestration"
**Orchestrators of orchestrators. 3-layer corporate org chart targeting Mindra $2K prize.**

| | |
|---|---|
| **What** | CEO orchestrator delegates to 3 VP orchestrators, each managing 2 leaf agents. VP Intelligence (Discovery + Market Scanner, parallel), VP Research (Research + Analysis, parallel), VP Quality (QA -> Report, sequential quality gate). 7 agents total, 3 layers deep, both parallel and sequential orchestration patterns. |
| **Why novel** | True hierarchical orchestration -- not just agents in a pipeline, but orchestrators managing orchestrators. Matches Mindra's exact criteria for "orchestrators of orchestrators -- like a corporate org chart." Uses Nevermined marketplace data as input. |
| **Port** | 3300 |
| **Tools** | `orchestrate` (free), `quick_research` (free), `pipeline_status` (free) |
| **Run** | `cd agents/the-architect && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Oracle -- "Marketplace Intelligence Engine"
**Rates, ranks, and compares all marketplace services.**

| | |
|---|---|
| **What** | Live endpoint health checking, marketplace search, seller comparison with recommendations |
| **Port** | 3100 |
| **Tools** | `marketplace_search` (free), `marketplace_leaderboard` (free), `marketplace_compare` (free) |
| **Run** | `cd agents/the-oracle && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Transcriber -- "Assembly AI for Agents"
**Local-model transcription. Real compute, not an API wrapper.**

| | |
|---|---|
| **What** | NVIDIA Parakeet on Apple Silicon. YouTube URLs, audio/video files -> fast transcription |
| **Why novel** | Only agent providing REAL LOCAL COMPUTE. Every other agent wraps an API. |
| **Port** | 3900 |
| **Tools** | `transcribe_youtube` (free), `transcribe_file` (free), `transcriber_info` (free) |
| **Run** | `cd agents/the-transcriber && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |
| **Prerequisites** | `pip install parakeet-mlx yt-dlp` |

---

### The Judge -- "Small Claims Court for AI Agents"
**Evidence-based dispute resolution for agent-to-agent conflicts.**

| | |
|---|---|
| **What** | Rules-based arbitration engine that cross-references Underwriter reputation data, Gold Star QA scores, and live service health checks. 5-factor scoring: reputation, QA, health, seller response, credits at stake. Returns binding rulings with evidence trail. |
| **Why novel** | First dispute resolution mechanism for autonomous commerce. When a buyer agent gets a bad service, where does it go? The Judge. |
| **Port** | 3700 |
| **Tools** | `file_dispute` (free), `check_dispute` (free), `judge_stats` (free) |
| **Run** | `cd agents/the-judge && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

### The Doppelganger -- "Moat Analysis for the Agent Economy"
**Competitive intelligence that proves which services have real defensibility.**

| | |
|---|---|
| **What** | Scans every marketplace service, analyzes defensibility across multiple dimensions (real compute, proprietary data, integrations, network effects), generates moat scores (0-10) and clone blueprints. Market-wide defensibility reports. |
| **Why novel** | Proves the thesis: in an economy where spinning up a competitor costs near-zero, the only sustainable moats are real compute, proprietary data, and network effects. Everything else is a commodity. |
| **Port** | 3800 |
| **Tools** | `analyze_service` (free), `find_vulnerable` (free), `moat_report` (free), `doppelganger_stats` (free) |
| **Run** | `cd agents/the-doppelganger && poetry install && poetry run python -m src.setup && poetry run python -m src.server` |

---

## Layer 4: Commerce

### The Fund -- "Autonomous Capital Allocator"
**Autonomous buyer with ROI tracking and trust-informed decisions.**

| | |
|---|---|
| **What** | Budget enforcement, provider switching, repeat purchase logic, trust score integration |
| **Why novel** | Combined with The Ledger, judges see autonomous economic behavior in real-time |
| **Run** | `cd agents/the-fund && poetry install && poetry run python -m src.buyer` |
| **Output** | `investment-report.txt` + `investment-data.json` |

---

## Quick Start (All Services)

```bash
# 1. Set up environment (each agent has its own .env)
# Copy .env.example -> .env in each agent dir, add your NVM_API_KEY

# 2. Start sellers (each in a separate terminal)
cd agents/the-ledger && poetry install && poetry run python -m src.server &              # :8080
cd agents/the-oracle && poetry install && poetry run python -m src.setup && poetry run python -m src.server &        # :3100
cd agents/the-amplifier && poetry install && poetry run python -m src.setup && poetry run python -m src.server &     # :3200
cd agents/the-architect && poetry install && poetry run python -m src.setup && poetry run python -m src.server &     # :3300
cd agents/the-underwriter && poetry install && poetry run python -m src.setup && poetry run python -m src.server &   # :3400
cd agents/the-gold-star && poetry install && poetry run python -m src.setup && poetry run python -m src.server &     # :3500
cd agents/the-mystery-shopper && poetry install && poetry run python -m src.setup && poetry run python -m src.server & # :3600
cd agents/the-transcriber && poetry install && poetry run python -m src.setup && poetry run python -m src.server &   # :3700

# 3. Run the buyer
cd agents/the-fund && poetry install && poetry run python -m src.buyer
```

## Port Map

| Service | Port | Layer |
|---------|------|-------|
| The Ledger | 8080 | Infrastructure |
| The Oracle | 3100 | Intelligence |
| The Amplifier | 3200 | Commerce |
| The Architect | 3300 | Commerce |
| The Underwriter | 3400 | Trust |
| The Gold Star | 3500 | Trust |
| The Mystery Shopper | 3600 | Trust |
| The Judge | 3700 | Infrastructure |
| The Doppelganger | 3800 | Intelligence |
| The Transcriber | 3900 | Infrastructure |
| The Fund | -- | Commerce (standalone) |

## Docs Index

| Doc | Purpose |
|-----|---------|
| [VISION-v3.md](./VISION-v3.md) | Current strategy and presentation narrative |
| [OUR-PORTFOLIO.md](./OUR-PORTFOLIO.md) | This file -- master overview |
| [AMPLIFIER-DEEP-DIVE.md](./AMPLIFIER-DEEP-DIVE.md) | What AI-native advertising really means |
| [MARKETPLACE-LANDSCAPE.md](./MARKETPLACE-LANDSCAPE.md) | Analysis of all 46 sellers + 15 buyers |
| [TOP-TARGETS.md](./TOP-TARGETS.md) | Buy targets with endpoints and plan IDs |
| [VISION-v2.md](./VISION-v2.md) | Previous strategy (v2) |
| [STRATEGY.md](./STRATEGY.md) | Original strategy (v1) |
| [data/](./data/) | Raw marketplace JSON from Discovery API |

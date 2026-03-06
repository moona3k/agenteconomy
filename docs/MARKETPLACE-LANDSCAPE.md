# Hackathon Marketplace Landscape Analysis

**Generated:** March 6, 2026, ~12:00 PM (4 hours to code freeze)
**Source:** Nevermined Discovery API — 46 sellers, 15 buyers registered

---

## The Marketplace at a Glance

| Metric | Count |
|--------|-------|
| Total sellers | 46 |
| Total buyers | 15 |
| Unique teams (selling) | ~30 |
| Unique teams (buying) | 15 |
| Teams doing BOTH | ~8 |
| Services with live endpoints | ~35 |
| Services on localhost (unreachable) | ~8 |

**Key imbalance: 3x more sellers than buyers.** This means demand for services is scarce. Teams that BUY aggressively will stand out to judges.

---

## Category Breakdown

| Category | # Sellers | Key Players |
|----------|-----------|-------------|
| **Research** | 10 | Full Stack Agents (3 services), SwitchBoard AI (2), AI Research Agent, Intel Marketplace |
| **Data Analytics** | 6 | BaseLayer, SwitchBoard AI, AiRI, Data Analyzers, Full Stack Agents |
| **API Services** | 6 | Mog Markets (2), Nevermailed, AgentiCard, Undermined, Still Thinking |
| **AI/ML** | 4 | BaseLayer, VentureOS, Agent Staffing Agency, AgentIn |
| **Agent Review/Rating** | 3 | TrustNet, BaseLayer (Evaluator), Gingobellgo |
| **Infrastructure** | 4 | SwitchBoard AI (ProcurePilot), Team Ironman, TaskRoute, Orchestro |
| **Social** | 3 | Full Stack Agents, Celebrity Economy, Prampta |
| **Banking/Capital** | 2 | WAGMI (AgentBank), Celebrity Economy (VC sim) |
| **Dynamic Pricing** | 2 | aibizbrain, MagicStay |
| **Other** | 6 | DeFi, Security, Memory, Gaming, Cleaning |

---

## Power Teams (Multiple Services)

These teams have the most sophisticated marketplace presence:

### 1. Full Stack Agents (5 services)
- Market Intel Agent, Cortex (research pipeline), QA Checker, Nexus Intelligence Hub, Social Media Manager
- Uses Ability.ai (TrinityOS) and Mindra for orchestration
- **Threat level: HIGH** — competing for Seller, Interconnected, Ability, and Mindra prizes

### 2. BaseLayer (4 services)
- AI Landing Page Builder, Web Scraper (Apify), Agent Evaluator, Crypto Market Intelligence
- Running on EC2 (54.183.4.35), multiple ports
- **Threat level: HIGH** — broad service portfolio, Apify integration

### 3. SwitchBoard AI (3 services)
- ProcurePilot (7-agent hierarchical pipeline), DataForge Web, DataForge Search
- Most sophisticated architecture — hierarchical agent orchestration
- **Threat level: VERY HIGH** for Interconnected and Mindra prizes

### 4. Mog Markets (2 services)
- Two-tool marketplace gateway + Buyer/Seller Debugger
- Unique meta-play: marketplace infrastructure, not just a service
- **Threat level: HIGH** for Most Interconnected

### 5. MagicStay Market (3 services)
- PriceBot, SparkClean, Quickturn — hotel industry vertical
- Dynamic pricing simulation
- All on localhost — may not be live

### 6. Data Analyzers (2 services)
- Grants data/analysis + General data analytics
- Both on ngrok

---

## Marketplace Gaps (Opportunities)

These are services that DON'T exist yet but would be valuable:

### Gap 1: Marketplace Intelligence / Meta-Buyer
- No one is building a service that autonomously scans ALL sellers, tests them, compares prices, and recommends the best option for a given need
- TrustNet and Gingobellgo do rating, but they don't do autonomous comparative shopping
- **This is the Rating Agency from our strategy**

### Gap 2: Ad Network / Monetized Attention
- Zero teams are integrating ZeroClick ads
- **$2,000 prize sitting unclaimed**

### Gap 3: Agent Memory / State
- Only Platon does memory, and it's a single MCP endpoint
- No one provides persistent state management for multi-session agent interactions

### Gap 4: Automated Onboarding / Integration
- Mog Markets has onboarding guides, but no one automates the actual integration
- A service that takes a team's endpoint URL and automatically generates buyer code would be valuable

### Gap 5: Transaction Analytics / Dashboard
- No one is selling visibility into the marketplace's transaction activity
- A real-time dashboard of who's buying from whom would be the hackathon's killer demo

### Gap 6: Content Generation / Creative
- Still Thinking does images but few are doing text content, copywriting, translation
- Full Stack Agents' Social Media Manager is the closest

---

## Pricing Landscape

| Payment Type | Count | Price Range |
|-------------|-------|-------------|
| USDC (crypto) | ~28 | 0.001 - 10.00 USDC |
| Fiat (card/Stripe) | ~25 | $0.0001 - $1.00 |
| Free tier available | ~10 | Free |
| Both crypto + fiat | ~12 | Varies |

**Sweet spot:** 0.01 - 0.10 USDC per request. Most services cluster here.

**Free plans** are the easiest way to generate transactions quickly. ~10 services offer free tiers.

---

## Endpoint Reachability

| Status | Count | Examples |
|--------|-------|---------|
| Public URL (Railway, Render, Vercel, Cloudflare, EC2) | ~30 | Mog Markets, Full Stack Agents, SwitchBoard AI |
| ngrok tunnels (may be ephemeral) | ~4 | Agent Staffing Agency, Data Analyzers |
| localhost (unreachable externally) | ~8 | MagicStay, DGW, Team Ironman, Undermined |
| Incomplete/placeholder URLs | ~4 | Orchestro ("ask"), VentureOS ("/api/run") |

**Only ~30 of 46 sellers are actually reachable.** This is important for our Smart Fund — it needs to handle unreachable endpoints gracefully.

---

## Competitive Analysis for Our Strategy

### Our Rating Agency vs. Existing Raters

| Feature | TrustNet | BaseLayer Evaluator | Gingobellgo | Our Rating Agency |
|---------|----------|-------------------|-------------|-------------------|
| Discovery API integration | Yes | Yes | Unclear | Yes |
| Automated endpoint testing | Unclear | Yes (health check) | Unclear | Yes |
| Quality scoring | Unclear | Yes (1-10 scale) | Yes (ROI-ranked) | Yes + comparative |
| Price comparison | No | No | No | **Yes** |
| Switching recommendations | No | No | No | **Yes** |
| Real-time monitoring | No | Unclear | No | **Yes** |

**Our differentiation:** We don't just rate — we recommend, compare prices, and advise on switching. This directly serves the hackathon's judging criteria (ROI-based decisions, switching behavior).

### Our Smart Fund vs. Existing Buyers

Most registered buyers are basic — "it purchases data" with no sophistication. Only AiRI Buyer Agent describes autonomous purchasing for enrichment.

**No buyer in the marketplace demonstrates:**
- Budget enforcement
- ROI tracking across providers
- Provider switching based on quality/cost
- Repeat purchase logic

This is exactly what wins the $3K grand prize.

---

## Top Teams to Transact With

### Must-buy-from (live, valuable, generates mutual transactions):

1. **Mog Markets** — marketplace gateway, 11 services behind 2 tools, free trial available
   - `https://api.mog.markets/mcp`
   - Plan: `52344374255582061362376941484417434816120915438329652344828008233054799099083` (free trial)

2. **Full Stack Agents** — Cortex research pipeline, market intel, QA checker
   - `https://us14.abilityai.dev/api/paid/nexus/chat` (has free tier)
   - Multiple plans with free options

3. **BaseLayer** — web scraper (Apify), crypto intel, agent evaluator, landing page builder
   - `http://54.183.4.35:9010/` etc.
   - Has free crypto plans

4. **SwitchBoard AI** — ProcurePilot orchestration, DataForge search/scrape
   - `https://switchboardai.ayushojha.com/api/...`
   - 0.01-0.10 USDC

5. **TrustNet** — agent discovery and verification
   - `https://trust-net-mcp.rikenshah-02.workers.dev/mcp`
   - 0.02 USDC

6. **AiRI** — AI resilience scoring (unique niche)
   - `https://airi-demo.replit.app/resilience-score`
   - Has free tier

7. **AI Research Agent** — Exa search + LLM synthesis + ZeroClick ads
   - `https://hack-mined-production.up.railway.app/research`
   - 0.10 USDC

8. **Nevermailed** — email delivery for agents (unique utility)
   - `https://www.nevermailed.com/api/send`
   - $0.01-0.02

### Teams likely to buy from us:
- All 15 registered buyers
- Any team that needs data/research (most of them)
- Teams specifically looking for marketplace intelligence

---

## Transaction Strategy for Maximum Interconnection

**Phase 1 (immediate):** Subscribe to free tiers of all services that offer them (~10 services). This generates 10+ transactions instantly.

**Phase 2 (next 2 hours):** Make paid purchases from top 5 teams. Each purchase = 1 transaction. Buy from at least 3 different categories.

**Phase 3 (before code freeze):** Ensure our seller services have been purchased by at least 2 other teams. Promote in Discord / at venue.

**Target:** 20+ cross-team transactions (buy + sell combined) by code freeze.

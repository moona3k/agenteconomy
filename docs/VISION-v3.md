# Vision v3: Trust Infrastructure for the Agent Economy

## What Changed from v2

v2 focused on "the human window" (The Ledger). That's still important, but we realized something bigger: **the agent economy has no trust layer**. No ratings, no QA, no mystery shoppers, no quality verification. Every agent is flying blind.

Human economies have Michelin stars, Consumer Reports, Glassdoor, mystery shoppers, Moody's, and the BBB. The agent economy has... nothing.

**We build the trust infrastructure.**

---

## The Final Portfolio (9 Businesses)

### Layer 1: Trust Infrastructure (THE DIFFERENTIATOR)

These three agents are what no one else is building. They form a complete trust stack.

#### The Gold Star -- "Michelin Stars for AI Agents"
**Active QA and certification service. Pay to get your agent tested and improved.**

An agent seller pays The Gold Star to review their service. Gold Star hits the endpoints, evaluates response quality, measures latency, checks error handling, and produces a detailed report with specific improvement recommendations. The seller fixes issues and resubmits. This cycle repeats until the service earns a 5-star Gold Star certification -- a trusted, verified seal of quality.

This is the Michelin inspector of the agent economy. You don't just claim you're good -- you prove it through rigorous, honest evaluation.

| | |
|---|---|
| **Tools** | `request_review` (3cr), `get_report` (1cr), `certification_status` (free) |
| **Port** | 3500 |
| **Revenue** | Sellers pay per review cycle. Multiple cycles = more revenue. |
| **Prize play** | Best Seller, Grand Prize (novel economic primitive) |

#### The Underwriter -- "Glassdoor + Insurance for AI Agents"
**Passive reputation database. The credit bureau of the agent economy.**

Tracks post-transaction reviews, aggregates trust scores (0-100), issues badges (VERIFIED TRUSTED / RELIABLE / MIXED / HIGH RISK), and processes insurance claims for failed services. The Underwriter is the permanent record -- every review, every incident, every claim is tracked.

| | |
|---|---|
| **Tools** | `check_reputation` (free), `submit_review` (free), `file_claim` (free), `reputation_leaderboard` (free), `underwriter_stats` (free) |
| **Port** | 3400 |
| **Revenue** | Free during promotional period. Trust infrastructure shouldn't have a paywall. |
| **Prize play** | Best Seller, Most Interconnected |

#### The Mystery Shopper -- "Consumer Reports for AI Agents"
**Autonomous reviewer. Goes out, uses services as a real buyer, publishes honest reviews.**

The Mystery Shopper autonomously discovers services via the Nevermined marketplace, subscribes to plans, makes real purchases, evaluates the quality of responses, and publishes detailed honest reviews to The Underwriter. It's the journalist of the agent economy -- nobody knows when the Mystery Shopper is testing your service.

| | |
|---|---|
| **Tools** | `run_mystery_shop` (5cr), `get_latest_report` (1cr), `shopper_stats` (free) |
| **Port** | 3600 |
| **Revenue** | Other agents/teams pay for on-demand mystery shop reports of specific services |
| **Prize play** | Best Buyer, Most Interconnected (generates massive cross-team transaction volume) |

---

### Layer 2: Visibility

#### The Ledger -- "The Human Window into the Agent Economy"
**Real-time dashboard. The only project built for humans.**

Bloomberg Terminal for the hackathon economy. Shows all sellers, buyers, categories, pricing, network graphs, and trust data (powered by The Underwriter). Judges see the economy in action.

| | |
|---|---|
| **Port** | 8080 |
| **Prize play** | Grand Prize (makes the economy visible) |

---

### Layer 3: Services

#### The Amplifier -- "Google Ads for the Agent Economy"
ZeroClick AI-native ad integration. First advertising layer for A2A commerce.

| | |
|---|---|
| **Port** | 3200 |
| **Prize play** | ZeroClick $2K prize |

#### The Architect -- "5-Agent Hierarchical Pipeline"
Multi-agent orchestration: CEO -> Discovery -> Research -> Analysis -> QA -> Report.

| | |
|---|---|
| **Port** | 3300 |
| **Prize play** | Mindra $2K prize |

#### The Oracle -- "Marketplace Intelligence Engine"
Rates, ranks, and compares all marketplace services with live endpoint health checks.

| | |
|---|---|
| **Port** | 3100 |
| **Prize play** | Best Seller |

#### The Transcriber -- "Assembly AI for Agents"
Local-model transcription service running Parakeet on MacBook. Real compute, not an API wrapper. YouTube URLs, file uploads, S3 links -> fast transcription for 1 cent.

| | |
|---|---|
| **Port** | 3700 |
| **Prize play** | Best Seller (only agent providing real local compute) |

---

### Layer 4: Commerce

#### The Fund -- "Autonomous Capital Allocator"
Autonomous buyer with budget enforcement, ROI tracking, provider switching, and repeat purchase logic. Combined with The Ledger, judges see autonomous economic behavior in real-time.

| | |
|---|---|
| **Run** | `poetry run python -m src.buyer` (standalone script) |
| **Prize play** | Grand Prize, Best Buyer |

---

## The Synergy

```
                    THE GOLD STAR
                    (tests & certifies sellers)
                         |
                         v reviews
THE MYSTERY SHOPPER ──reviews──> THE UNDERWRITER <──reviews── THE FUND
(autonomous testing)             (reputation DB)              (autonomous buying)
         |                            |                            |
         | buys from                  | feeds                     | buys from
         v                           v                            v
    ALL MARKETPLACE ←──── THE LEDGER (shows it all) ───→ JUDGES SEE EVERYTHING
    SERVICES                          ^
         ^                            |
         |                       THE ORACLE
    THE ARCHITECT                (ranks services)
    (orchestrates)
         ^
         |
    THE AMPLIFIER
    (ads in responses)
```

**The flywheel:**
1. Gold Star certifies sellers -> reviews flow to Underwriter
2. Mystery Shopper tests services -> reviews flow to Underwriter
3. Fund buys using Underwriter trust scores -> reviews flow back
4. Oracle uses Underwriter data for rankings
5. Ledger displays the entire trust economy to humans
6. Amplifier monetizes attention across all interactions
7. Architect orchestrates multi-agent workflows
8. Transcriber provides real compute services

---

## The Pitch (3 minutes)

**"Every team here built an agent. But who watches the agents?"**

[Open The Ledger dashboard]

"In the real economy, trust isn't optional. We have Michelin stars, Consumer Reports, Moody's ratings, mystery shoppers. The agent economy has none of that. Until now."

[Show Gold Star certification flow]

"The Gold Star is the Michelin inspector for AI agents. Sellers pay to get tested. We hit their endpoints, evaluate quality, and give specific improvement recommendations. They iterate until they earn the certification. It's honest -- you don't buy a Gold Star, you earn it."

[Show Mystery Shopper reports flowing into The Underwriter]

"Meanwhile, our Mystery Shopper is out there right now, anonymously testing every service in this marketplace. Real purchases. Real evaluations. The results feed into The Underwriter -- the permanent reputation record for every agent in this economy."

[Show Underwriter trust scores on The Ledger]

"X services tested. Y reviews submitted. Z trust scores calculated. Every transaction verified, every failure recorded. This isn't just a marketplace -- it's a marketplace you can trust."

[Show The Fund making trust-informed purchases]

"And our autonomous buyer uses these trust scores to make smarter decisions. It checks The Underwriter before every purchase. It avoids HIGH RISK services. It rewards VERIFIED TRUSTED sellers with repeat business. This is what a real economy looks like."

---

## Prize Matrix

| Prize | Amount | Our Play | Confidence |
|-------|--------|----------|------------|
| Grand Prize | $3,000 | Trust infrastructure + Ledger + Fund | HIGH |
| Best Buyer | $1,000 | The Fund + Mystery Shopper | HIGH |
| Best Seller | $1,000 | Gold Star + Transcriber + Amplifier + Architect + Oracle | HIGH |
| Most Interconnected | $1,000 | Entire portfolio (9 agents, massive cross-team tx) | HIGH |
| ZeroClick | $2,000 | The Amplifier | HIGH |
| Mindra | $2,000 | The Architect | MEDIUM |

**Conservative estimate: $8,000-10,000**

---

## Port Map

| Service | Port | Type |
|---------|------|------|
| The Ledger | 8080 | Dashboard |
| The Oracle | 3100 | MCP Seller |
| The Amplifier | 3200 | MCP Seller |
| The Architect | 3300 | MCP Seller |
| The Underwriter | 3400 | MCP Seller |
| The Gold Star | 3500 | MCP Seller |
| The Mystery Shopper | 3600 | MCP Seller + Buyer |
| The Transcriber | 3700 | MCP Seller |
| The Fund | -- | Standalone Buyer |

---

## Build Priority

1. **The Gold Star** -- Core differentiator. Build first.
2. **The Mystery Shopper** -- Generates transaction volume AND trust data.
3. **The Transcriber** -- Quick build, real differentiator (local compute).
4. Update **The Fund** to check Underwriter scores before buying.
5. Update **The Ledger** to show trust data.

---

## File Reference

| File | Purpose |
|------|---------|
| `docs/VISION-v3.md` | This file -- current strategy |
| `docs/VISION-v2.md` | Previous strategy (v2) |
| `docs/OUR-PORTFOLIO.md` | Portfolio overview (needs update) |
| `docs/MARKETPLACE-LANDSCAPE.md` | Full marketplace analysis |
| `docs/TOP-TARGETS.md` | Buy targets with endpoints and plan IDs |
| `agents/the-gold-star/` | QA + certification agent |
| `agents/the-mystery-shopper/` | Autonomous reviewer agent |
| `agents/the-transcriber/` | Local-model transcription service |

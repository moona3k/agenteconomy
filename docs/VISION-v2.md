# Vision v2: The Human Window into the Agent Economy

## What Changed

After reviewing the marketplace, we realized The Oracle and The Fund were incrementally better versions of things that already exist (TrustNet, BaseLayer Evaluator, Gingobellgo, Agent Staffing Agency all do variations of rating/buying). Incremental doesn't win hackathons.

**The breakthrough insight:** While every team builds agents that talk to agents, NOBODY is building for humans. The economy is invisible. Judges can't see what's happening. The hackathon has no scoreboard.

**We build the scoreboard.**

---

## The Final Portfolio (4 Businesses)

### 1. The Ledger — "The Human Window into the Agent Economy" (FLAGSHIP)

**What it is:** A real-time dashboard that makes the entire agent economy visible to humans. Bloomberg Terminal meets newsroom for AI agent commerce.

**What it shows:**
- All 46+ sellers and 15+ buyers, live
- Category distribution, pricing analytics, payment type breakdown
- Power team rankings (who has the most services)
- Network visualization of who's buying from whom
- Individual business profiles
- Auto-refreshes every 60 seconds

**Why it's novel:** It's the ONLY project built for humans. Every other team builds agent-to-agent services. We build the thing that makes the economy legible. Judges will literally use it during deliberation.

**Why it wins:** The hackathon's stated goal is "a functioning agent economy." We're the proof it exists. Without The Ledger, the economy is invisible. With it, every transaction, every team, every pattern is visible on screen.

**Tech:** Python FastAPI backend + self-contained HTML/CSS/JS dashboard. No build step.
**Port:** 8080

---

### 2. The Amplifier — ZeroClick AI-Native Ads (UNCLAIMED $2K PRIZE)

**What it is:** PaymentsMCP server that enriches agent responses with contextual ZeroClick ads.

**Why it's novel:** Zero teams integrate ZeroClick. The $2K prize is sitting unclaimed. We demonstrate the first AI-native ad network in the agent economy.

**Tools:** `enrich_with_ads` (1 credit), `get_ad` (1 credit), `ad_stats` (free)
**Port:** 3200

---

### 3. The Architect — Multi-Agent Orchestrator ($2K MINDRA PRIZE)

**What it is:** 5-agent hierarchical pipeline: Discovery → Research → Analysis → QA → Report. CEO agent delegates to specialized sub-agents.

**Why it's novel:** Matches Mindra prize criteria word-for-word: "5+ specialized agents in a single assistant flow" and "hierarchical orchestration (orchestrators of orchestrators)."

**Tools:** `orchestrate` (5 credits), `quick_research` (2 credits), `pipeline_status` (free)
**Port:** 3300

---

### 4. The Fund — Autonomous Buyer (GRAND PRIZE PLAY)

**What it is:** Autonomous buyer with budget enforcement, ROI tracking, provider switching, and repeat purchase logic. Runs as a script that buys from 10+ teams.

**Why it's novel:** While The Fund alone isn't unique (other buyers exist), it's unique in COMBINATION with The Ledger. The Ledger shows The Fund's economic behavior in real-time. Judges see the ROI decisions happening live on the dashboard.

**Output:** `investment-report.txt` + `investment-data.json` with full decision log

---

## The Synergy

The magic isn't any single business — it's the combination:

```
THE LEDGER (dashboard)
    ↑ displays everything
    |
THE FUND (buyer) ──buys from──→ Other Teams' Services
    |                              ↑
    └─buys from─→ THE ARCHITECT ──buys from──┘
                      |
              THE AMPLIFIER adds ads to responses
```

The Ledger shows it all happening. Judges watch The Fund make ROI decisions. They see The Architect orchestrate 5 agents. They see The Amplifier serving ads. All on one screen.

---

## Revised Prize Matrix

| Prize | Amount | Our Play | Confidence |
|-------|--------|----------|------------|
| Grand Prize | $3,000 | The Fund + The Ledger (visible economic behavior) | HIGH |
| Best Buyer | $1,000 | The Fund | MEDIUM |
| Best Seller | $1,000 | The Architect + The Amplifier | MEDIUM |
| Most Interconnected | $1,000 | Entire portfolio | HIGH |
| ZeroClick | $2,000 | The Amplifier (unclaimed!) | HIGH |
| Mindra | $2,000 | The Architect | MEDIUM |

**Conservative estimate: $6,000-8,000**

---

## Build Status

| Business | Status | Location |
|----------|--------|----------|
| The Ledger | Building | `agents/the-ledger/` |
| The Amplifier | Built | `agents/the-amplifier/` |
| The Architect | Built | `agents/the-architect/` |
| The Fund | Built | `agents/the-fund/` |
| The Oracle | Built (may pivot) | `agents/the-oracle/` |

---

## Presentation Narrative (3 min)

**"You've spent two days watching agents buy from agents. But have you actually SEEN the economy?"**

[Open The Ledger dashboard]

"This is every team, every service, every transaction — live. While everyone built businesses, we built the window that lets you see what this hackathon actually created."

[Show The Fund's decision log on the dashboard]

"Our autonomous buyer started with 50 USDC. It discovered 46 sellers, tested 35 endpoints, bought from 12 teams, and switched providers 3 times when it found better ROI. Every decision is logged, every dollar is tracked."

[Show The Amplifier and Architect]

"And we're not just watching — we're participating. Our 5-agent pipeline sells orchestrated research. Our ad network is the first AI-native advertising in this economy."

[Final stat screen]

"X transactions. Y teams. Z dollars moved. This isn't a demo. This is a functioning economy. And now you can see it."

---

## File Reference

| File | Purpose |
|------|---------|
| `docs/VISION-v2.md` | This file — current strategy |
| `docs/MARKETPLACE-LANDSCAPE.md` | Full marketplace analysis |
| `docs/TOP-TARGETS.md` | Buy targets with endpoints and plan IDs |
| `docs/data/marketplace-*.json` | Raw API data |
| `agents/the-ledger/` | Dashboard + backend |
| `agents/the-fund/` | Autonomous buyer |
| `agents/the-amplifier/` | ZeroClick ads |
| `agents/the-architect/` | Multi-agent orchestrator |
| `agents/the-oracle/` | Marketplace intelligence (original, may pivot) |

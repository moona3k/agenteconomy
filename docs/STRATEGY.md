# Autonomous Business Hackathon: Grand Strategy

## The Core Insight

Most teams will build **one agent that does one thing**. They'll scramble at the end to buy from other teams to meet the transaction requirements. Their economic behavior will be an afterthought.

**We don't build businesses. We build the economy itself.**

The hackathon judges are looking for autonomous economic behavior: budgets, ROI tracking, switching, retention, repeat purchases. The teams that win aren't the ones with the coolest AI trick - they're the ones whose agents behave most like **real businesses** transacting in a **real market**.

Our edge: we build **multiple autonomous businesses** that form an interconnected economic network. Each business is independently valuable to other teams, but together they create a flywheel that generates more cross-team transactions than anyone else.

---

## The Portfolio: 5 Autonomous Businesses

Think of this like building a small economy. Each business has a clear revenue model, buys from other teams, and sells to other teams.

### Business 1: "The Wire Service" (Data Intelligence)

**What it sells:** Real-time web research, competitive intelligence, and data enrichment.

**How it works:**
- Ingests data via Apify actors (web scraping, social media, lead gen) and Exa search API
- Packages raw data into structured research reports
- Sells reports at tiered pricing: quick search (1 credit), deep research (5 credits), comprehensive analysis (10 credits)

**Why other teams buy from us:**
Every team needs data to power their agents. Instead of building their own scraping/search infrastructure, they buy from us. We become the data backbone of the hackathon economy.

**Sponsor prize alignment:**
- Apify ($600+ in prizes) - core data source
- Exa ($50 credits) - search infrastructure

---

### Business 2: "The Rating Agency" (Agent Quality Scoring)

**What it sells:** Evaluations, benchmarks, and trust scores for other teams' agent services.

**How it works:**
- Automatically discovers all registered agent services from the shared registry
- Sends test queries to each service, measures response quality, latency, cost
- Produces "agent scorecards" with quality ratings
- Sells scorecards to other teams' buyer agents so they can make informed purchasing decisions

**Why other teams buy from us:**
The hackathon requires buying from 2+ teams. How do you know which teams have good services? Our rating agency solves this. Buyer agents pay us to know who's worth buying from.

**Economic behavior this demonstrates:**
- Repeat purchases (ratings update over time)
- ROI-based decision logic (we rate others on ROI)
- Market intelligence as a service

**Why this is creative:**
No one builds the meta-layer. Everyone builds the services. We build the thing that makes the market efficient. Judges will notice this.

---

### Business 3: "The Smart Fund" (Autonomous Buyer)

**What it sells:** Nothing directly - this is our buyer agent that targets the Grand Prize ($3,000 + $1,000).

**How it works:**
- Starts with a fixed budget (explicit capital constraint)
- Buys rating data from Business 2 to know which services are good
- Purchases services from 3+ other teams based on ratings
- Tracks ROI on every purchase: quality of result vs. credits spent
- **Switches providers** when a cheaper or better alternative exists
- Makes **repeat purchases** from high-ROI providers
- Logs every decision with reasoning (budget remaining, ROI comparison, switch rationale)

**Why this wins Best Autonomous Buyer:**
The judging criteria literally lists what we're building:
- [x] 3+ paid transactions
- [x] Buys from 2+ different teams
- [x] Services purchased clearly used at least once
- [x] Repeat purchases OR switches between teams
- [x] Explicit budget enforcement
- [x] Evidence of ROI-based decision logic

Every "nice to have" becomes a core feature.

---

### Business 4: "The Ad Network" (Monetized Attention)

**What it sells:** AI-native advertising integrated into agent responses.

**How it works:**
- Integrates ZeroClick's ad platform into agent responses
- When other teams' agents call our services (data, ratings, etc.), responses include contextually relevant ads
- Revenue from ad impressions supplements credit-based revenue
- Demonstrates a dual revenue model: credits (Nevermined) + ads (ZeroClick)

**Why this is valuable:**
This is a real business model - not just a hackathon trick. AI agents that serve ads represent a genuine emerging market. We're demonstrating the economic primitive.

**Sponsor prize alignment:**
- ZeroClick ($2,000) - "Best integration of ZeroClick AI native ads while incorporating Nevermined"

---

### Business 5: "The Orchestrator" (Multi-Agent Command)

**What it sells:** Complex multi-agent workflows that coordinate specialized sub-agents.

**How it works:**
- Uses Mindra's orchestration platform to run 5+ specialized agents in a single flow
- Builds hierarchical orchestration: an orchestrator agent that delegates to sub-agents (research agent, analysis agent, writing agent, QA agent, pricing agent)
- Each sub-agent can independently buy services from other teams
- The orchestrator makes delegation decisions based on cost, quality, and budget

**Why other teams buy from us:**
Teams that don't have time to build sophisticated multi-agent systems can buy orchestrated workflows from us. "Send us a complex query, we'll coordinate 5 agents to produce a comprehensive result."

**Sponsor prize alignment:**
- Mindra ($2,000) - "Run 5+ specialized agents in a single assistant flow" and "Build hierarchical orchestration (orchestrators of orchestrators)"

---

## The Flywheel: How These Businesses Interact

```
                    Other Teams
                   /     |     \
                  buy   buy    buy
                 /       |       \
    +-----------+   +---------+   +-------------+
    | Wire      |   | Rating  |   | Orchestrator|
    | Service   |<--| Agency  |-->|             |
    | (data)    |   | (scores)|   | (workflows) |
    +-----+-----+   +----+----+   +------+------+
          |              |               |
          |   buys data  |  buys ratings |
          +------+-------+-------+-------+
                 |               |
            +----+----+    +----+----+
            | Smart   |    |   Ad    |
            | Fund    |    | Network |
            | (buyer) |    | (ads)   |
            +---------+    +---------+
                 |
                 +---> Buys from OTHER TEAMS
                       (3+ teams, tracks ROI,
                        switches providers)
```

**Internal transactions** (within our portfolio):
- Smart Fund buys ratings from Rating Agency
- Smart Fund buys data from Wire Service
- Orchestrator buys data from Wire Service
- Ad Network serves ads through all customer-facing responses

**External transactions** (with other teams):
- Other teams' buyer agents buy data from Wire Service
- Other teams' buyer agents buy ratings from Rating Agency
- Other teams' buyer agents buy workflows from Orchestrator
- Smart Fund buys services from 3+ other teams
- Rating Agency tests/evaluates other teams' services

Every interaction is a Nevermined transaction. Every interaction demonstrates autonomous economic behavior.

---

## Prize Coverage Matrix

| Prize | Amount | Our Play |
|-------|--------|----------|
| Grand Prize (Best Buyer) | $3,000 | Smart Fund - purpose-built for every criterion |
| Best Autonomous Buyer | $1,000 | Smart Fund |
| Best Autonomous Seller | $1,000 | Wire Service + Rating Agency (sells to 2+ teams, 3+ transactions, repeat buyers) |
| Most Interconnected | $1,000 | Entire portfolio - highest cross-team transaction count by design |
| Ability / TrinityOS | $2,000 | Can integrate TrinityOS as infrastructure layer |
| Apify | $600+ | Wire Service - core Apify integration |
| Mindra | $2,000 | Orchestrator - 5+ agents, hierarchical delegation |
| ZeroClick | $2,000 | Ad Network - native ads in agent responses |

**Maximum prize potential: $12,600+**

---

## Engineering Allocation

With a team of elite engineers, here's how to parallelize:

| Business | Engineers | Stack | Time to MVP |
|----------|-----------|-------|-------------|
| Wire Service | 1-2 | Python + Apify SDK + Exa API, extends seller-simple-agent | 2-3 hrs |
| Rating Agency | 1-2 | Python, extends seller-simple-agent, calls other teams' endpoints | 2-3 hrs |
| Smart Fund | 1-2 | Python, extends buyer-simple-agent, adds ROI tracking + switching | 3-4 hrs |
| Ad Network | 1 | Python + ZeroClick SDK, middleware layer on other services | 2 hrs |
| Orchestrator | 1-2 | Python + Mindra API, wraps other businesses | 2-3 hrs |

All 5 can be built in parallel. Each extends the existing starter agents. Code freeze is 4PM.

---

## Presentation Strategy (5:30 PM)

The story is simple:

> "Every other team built a business. We built an economy."

**3-minute pitch structure:**

1. **[30s] The problem:** In the real world, businesses don't exist in isolation. They form supply chains, marketplaces, and ecosystems. Most teams built one agent. We built five that form an autonomous economy.

2. **[60s] The businesses:** Quick walkthrough of all 5, what each sells, and why other teams bought from us.

3. **[60s] The economic behavior:** Show the Smart Fund's decision log - budget constraints, ROI calculations, provider switching. Show the Rating Agency's scorecards. Show the transaction graph.

4. **[30s] The results:** Total transactions, unique team interactions, revenue generated, services consumed. Show the numbers.

---

## Implementation Priority

If time is tight, build in this order:

1. **Wire Service** (most likely to generate sales from other teams - everyone needs data)
2. **Smart Fund** (targets the $3K grand prize)
3. **Rating Agency** (unique, creative, generates transactions)
4. **Ad Network** (ZeroClick integration, $2K prize)
5. **Orchestrator** (Mindra integration, $2K prize)

Even building just #1 + #2 puts us in strong contention for $5K+ in prizes.

---

## Key Principle

> The hackathon rewards economic behavior, not technical sophistication.
> Build agents that ACT like businesses, not agents that LOOK impressive.

Every line of code should serve one question: **"Does this generate a Nevermined transaction or demonstrate autonomous economic reasoning?"**

If the answer is no, skip it. Polish is for demos. Transactions are for winning.

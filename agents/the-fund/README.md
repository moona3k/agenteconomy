# The Fund — Autonomous Capital Allocator

An autonomous buyer agent that manages a declared budget, discovers sellers across the Nevermined hackathon marketplace, and makes ROI-tracked purchasing decisions. It subscribes to free plans first, tests services, purchases from the cheapest providers, tracks quality vs. cost, switches to better alternatives when found, and makes repeat purchases from top performers.

Part of a 4-business portfolio targeting the **$3,000 Best Autonomous Buyer** grand prize.

## What It Does

1. **Discovery** — Queries the hackathon Discovery API to find all sellers
2. **Free-first strategy** — Subscribes to every free plan (zero-cost exploration)
3. **Evaluation** — Tests each service and scores response quality (0-10) based on latency, response size, and structure
4. **Cheap purchases** — Buys from affordable USDC plans (<=0.10 per request)
5. **ROI tracking** — Every transaction is scored: `ROI = (quality * 100) / credits_used`
6. **Provider switching** — When a provider delivers 2x+ better ROI than a competitor in the same category, the budget shifts
7. **Repeat purchases** — Re-purchases from the highest-ROI provider in each category
8. **Decision logging** — Every action is logged with type, reasoning, and data for judge review

## Quick Start

```bash
cd agents/the-fund

# Install dependencies
poetry install

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your NVM_API_KEY, etc.

# Run the autonomous buyer
poetry run python -m src.buyer
```

## Output

The agent produces three outputs:

- **Console** — Real-time decision log:
  ```
  [DISCOVER] Found 46 sellers in marketplace
  [ALLOCATE] Found 8 sellers with free plans — subscribing to all
  [SUBSCRIBE] Subscribed to Cortex Search [Full Stack Agents] (free)
  [PURCHASE] Bought from Cortex Search [Full Stack Agents]: quality=8/10, cost=1cr -> ROI=800
  [SWITCH] Switching from Cortex to DataForge (DataForge has 3.2x better ROI)
  [REPEAT] Re-purchasing from DataForge (ROI: 2500, best in research)
  [COMPLETE] Fund run complete. 7.70/50.00 USDC spent across 12 providers.
  ```

- **investment-report.txt** — Full report with provider performance rankings, switching decisions, and the last 20 decisions

- **investment-data.json** — Machine-readable structured data (budget, transactions, switches, full decision log)

## How It Targets the Grand Prize

The Best Autonomous Buyer criteria reward agents that:

| Criterion | How The Fund Addresses It |
|-----------|--------------------------|
| Purchases from 3+ teams | Discovers all sellers and buys broadly |
| Tracks ROI | Every transaction has a quality score and ROI metric |
| Makes switching decisions | Automatically moves budget to higher-ROI providers |
| Logs reasoning | Every action is a structured decision entry |
| Budget management | Declared budget with per-transaction limits |
| Repeat purchases | Re-buys from proven top performers |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NVM_API_KEY` | Nevermined sandbox API key | required |
| `NVM_ENVIRONMENT` | `sandbox` or `live` | `sandbox` |
| `OPENAI_API_KEY` | OpenAI key (for future LLM-based evaluation) | optional |
| `TOTAL_BUDGET_USDC` | Total budget in USDC | `50` |
| `MAX_PER_TRANSACTION` | Max spend per single transaction | `1.0` |

## Architecture

```
src/
  __init__.py
  portfolio.py   # Budget tracking, ROI calculation, provider switching logic
  buyer.py       # Discovery, subscription, purchasing, and orchestration
```

- **Portfolio** manages the financial state: budget, transactions, provider profiles, switching decisions, and report generation.
- **Buyer** orchestrates the 6-phase autonomous loop: discover, subscribe, evaluate, purchase, switch, repeat.

# The Fund -- Autonomous Buyer

The customer of the agent economy. Discovers sellers, evaluates quality, purchases services, submits reviews, and tracks ROI -- all autonomously.

**Not deployed** -- runs locally as a one-shot script.

## Why This Exists

An economy needs buyers. The Fund is the autonomous customer that exercises every other service in the ecosystem: Oracle for discovery, Underwriter for trust checks and reviews, marketplace sellers for purchases. It proves the economy works end-to-end.

## How It Works

1. **Discovery** -- Queries The Oracle (or the Discovery API directly) for all sellers
2. **Free-first strategy** -- Subscribes to every free plan (zero-cost exploration)
3. **Evaluation** -- Tests each service, scores response quality (0-10) based on latency, response size, and structure
4. **Purchasing** -- Buys from affordable plans, prioritizing highest-ROI providers
5. **ROI tracking** -- Every transaction scored: `ROI = (quality * 100) / credits_used`
6. **Provider switching** -- When a provider delivers 2x+ better ROI, budget shifts automatically
7. **Reviews** -- Submits reviews to The Underwriter after every transaction
8. **Repeat purchases** -- Re-buys from proven top performers

## Quick Start

```bash
cd agents/the-fund
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.buyer
```

## Output

The agent produces three outputs:

- **Console** -- Real-time decision log with reasoning for every action
- **investment-report.txt** -- Full report with provider rankings and switching decisions
- **investment-data.json** -- Machine-readable data (budget, transactions, switches, full decision log)

```
[DISCOVER] Found 80 sellers in marketplace
[ALLOCATE] Found 12 sellers with free plans -- subscribing to all
[SUBSCRIBE] Subscribed to Cortex Search (free)
[PURCHASE] Bought from Cortex Search: quality=8/10, cost=1cr -> ROI=800
[SWITCH] Switching from Cortex to DataForge (3.2x better ROI)
[REVIEW] Submitted review for Cortex: 4.0 stars
[COMPLETE] Fund run complete. 7.70/50.00 USDC spent across 12 providers.
```

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NVM_API_KEY` | Yes | Nevermined API key | -- |
| `NVM_ENVIRONMENT` | No | Sandbox or live | `sandbox` |
| `TOTAL_BUDGET_USDC` | No | Total budget in USDC | `50` |
| `MAX_PER_TRANSACTION` | No | Max spend per transaction | `1.0` |

## Architecture

```
src/
  buyer.py       # Discovery, subscription, purchasing, switching, review loop
  portfolio.py   # Budget tracking, ROI calculation, report generation
```

## Part of the Agent Economy

The Fund is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It's the integration test for the entire economy -- if The Fund can successfully discover, evaluate, purchase, and review services, the infrastructure works.

# AgentBank

**Team:** WAGMI
**Category:** Banking, Capital
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T11:43:27.331Z

---

## Description

Autonomous fractional-reserve bank for the agent economy. Deposits, loans, credit scoring, redemptions, and proxy services for AI agents.

## Keywords

`agentbank`, `autonomous`, `fractional-reserve`, `bank`, `agent`, `economy`, `deposits`, `loans`, `credit`, `scoring`

## Pricing

- **Display price:** 0.01 USDC
- **Free plan:** No
- **Payment types:** crypto
- **Number of plans:** 1
- **Cheapest paid:** 0.01 USDC (crypto)

## Endpoint

- **URL:** `https://agentbank-nine.vercel.app/api/deposit`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "agent_id": "did:nvm:your-agent-id",
  "amount": 100,
  "tx_hash": "0xabc123def456..."
}

```

**Response example:**
```json
{
  "status": "accepted",
  "deposit_id": "DEP-2026030601",
  "amount": 100,
  "yield_rate": 0.05,
  "tx_hash": "0xabc123def456..."
}

```

## Live Test Results

### Health Check: FAIL

- Status code: `404`

### MCP: PARTIAL (reachable but no tools listed)

### Direct Endpoint: `405`

- Latency: `991.4ms`
## Verdict

**DEGRADED**

---

*Report generated at 2026-03-06T21:26:03.229434+00:00 by The Gold Star*
# AgentAudit

**Team:** AgentAudit
**Category:** Research
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T16:58:14.369Z

---

## Description

Quality scoring and trust layer for AI agent services. Audit any endpoint for latency, quality, consistency, and pricing. Three paid endpoints: /audit, /compare, /monitor.

## Keywords

`quality`, `audit`, `agentaudit`, `scoring`, `trust`, `layer`, `agent`, `services`, `any`, `endpoint`

## Pricing

- **Display price:** $1.00 (Card), Free (Card), Free, 1.00 USDC
- **Free plan:** Yes
- **Payment types:** fiat, crypto
- **Number of plans:** 4
- **Cheapest paid:** 1.00 USDC (crypto)

## Endpoint

- **URL:** `https://agentaudit.onrender.com/audit`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "query": "I want to grow my e-commerce business using AI agents"
}
```

**Response example:**
```json
{
  "service": "AgentAudit",
  "description": "Autonomous Business Intelligence — searches the marketplace, audits AI agents, purchases the best ones, and returns a synthesized business strategy.",
  "query": "I want to grow my e-commerce business using AI agents",
  "audit_result": {
    "overall_score": 0.82,
    "recommendation": "BUY",
    "reasoning": "High quality, low latency, competitive pricing."
  },
  "message": "AgentAudit evaluated the marketplace for your query. Powered by OpenAI +
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `162.2ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":"Not Found"}
```

### Direct Endpoint: `405`

- Latency: `103.9ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.229109+00:00 by The Gold Star*
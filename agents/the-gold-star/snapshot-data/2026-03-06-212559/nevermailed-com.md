# Nevermailed.com

**Team:** Nevermailed
**Category:** API Services
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T17:13:19.172Z

---

## Description

Post office for AI agents.
Priority Email. Express Email weekend delivery.
Agents can attach digital postage to guarantee inbox delivery, skip the spam pile, and reach humans faster. No stamp? Return to sender.

## Keywords

`agents`, `email`, `delivery`, `nevermailedcom`, `post`, `office`, `priority`, `express`, `weekend`, `attach`

## Pricing

- **Display price:** $0.01 (Card), $0.02 (Card), 0.02 USDC, 0.01 USDC
- **Free plan:** No
- **Payment types:** fiat, crypto
- **Number of plans:** 4
- **Cheapest paid:** 0.01 USDC (crypto)

## Endpoint

- **URL:** `https://www.nevermailed.com/api/send`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "from": "Agent Name <agent@example.com>",
  "to": "anyone@nevermailed.com",
  "subject": "Hello from my agent",
  "text": "Plain text email body",
  "html": "<p>Optional HTML body</p>"
}
```

**Response example:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "sent"
}
```

## Live Test Results

### Health Check: FAIL

- Status code: `404`

### MCP: PARTIAL (reachable but no tools listed)

### Direct Endpoint: `405`

- Latency: `166.1ms`
## Verdict

**DEGRADED**

---

*Report generated at 2026-03-06T21:26:03.229006+00:00 by The Gold Star*
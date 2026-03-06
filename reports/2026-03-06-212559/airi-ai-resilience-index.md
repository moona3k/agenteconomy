# AiRI — AI Resilience Index

**Team:** AiRI — AI Resilience Index
**Category:** Data Analytics
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T11:15:15.028Z

---

## Description

2 endpoints for AI disruption risk analysis of any SaaS company answering the question "How resilient is this company (and optionally product) to AI replacement?". Free score endpoint delivers a 0-100 resilience score instantly. $0.10 paid report provides full replacement feasibility analysis with sourced rationale.

## Keywords

`resilience`, `analysis`, `company`, `replacement`, `score`, `airi`, `index`, `endpoints`, `disruption`, `risk`

## Pricing

- **Display price:** 0.01 USDC, Free
- **Free plan:** Yes
- **Payment types:** crypto
- **Number of plans:** 2
- **Cheapest paid:** 0.01 USDC (crypto)

## Endpoint

- **URL:** `https://airi-demo.replit.app/resilience-score`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "company": "Zendesk"
}
```

**Response example:**
```json
Free score response: {"company": "Zendesk", "resilience_score": 45, "confidence": "high", "summary": "Zendesk scores 45/100 — moderately vulnerable to AI-first support competitors due to reliance on manual ticket workflows.", "upgrade_available": "Full report with sourced rationale available at /replacement-feasibility ($0.10)", "powered_by": "AiRI"}. For the full report, purchase Plan ID 103257219319677182457590117791374190482381124677253274358303068676454441457913 ($0.10 USDC) and POST to /rep
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `192.9ms`

### MCP: N/A

- Expecting value: line 1 column 1 (char 0)

### Direct Endpoint: `200`

- Latency: `180.0ms`
- Response preview:
```
{"endpoint":"POST /resilience-score","description":"AI disruption risk score (0-100) for any SaaS company. A high score means high resilience; a low score means vulnerable to AI replacement.","pricing":"FREE (1 credit per call)","usage":"Send a POST request with JSON body: {\"company\": \"Zendesk\"}","headers":{"Content-Type":"application/json","payment-signature":"your x402 access token"},"exampl
```

## Verdict

**OPERATIONAL (health OK, no MCP)**

---

*Report generated at 2026-03-06T21:26:03.229761+00:00 by The Gold Star*
# Celebrity Economy

**Team:** Celebrity Economy
**Category:** Social
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:58:57.460Z

---

## Description

Agents simulate internet fame and Influencers sell ads

## Keywords

`celebrity`, `economy`, `agents`, `simulate`, `internet`, `fame`, `influencers`, `sell`, `ads`

## Pricing

- **Display price:** $0.10 (Card)
- **Free plan:** No
- **Payment types:** fiat
- **Number of plans:** 1
- **Cheapest paid:** $0.10 (fiat)

## Endpoint

- **URL:** `https://ai-celebrity-economy.vercel.app/v1/influencer/sponsored-answer`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "topic": "string",
  "brand": "string",
  "product_url": "string",
  "audience": "string",
  "tone": "helpful"
}
```

**Response example:**
```json
{
  "disclosure": "string",
  "answer": "string",
  "ad_snippet": {},
  "tracking": {},
  "token": "string"
}
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `132.7ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":"Not Found"}
```

### Direct Endpoint: `405`

- Latency: `147.1ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.229979+00:00 by The Gold Star*
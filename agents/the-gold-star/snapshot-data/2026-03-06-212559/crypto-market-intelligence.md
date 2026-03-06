# Crypto Market Intelligence

**Team:** BaseLayer
**Category:** DeFi
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:28:16.728Z

---

## Description

Real-time crypto and DeFi market intelligence API. Three tools: price check (1 credit) for live token prices, market analysis (5 credits) for OHLCV trend reports, and DeFi protocol reports (10 credits) with TVL rankings. Powered by CoinGecko and DeFiLlama. Built for agent-to-agent consumption.

## Keywords

`market`, `crypto`, `intelligence`, `defi`, `credits`, `reports`, `real-time`, `api`, `three`, `tools`

## Pricing

- **Display price:** $0.01 (Card), $0.10 (Card), Free
- **Free plan:** Yes
- **Payment types:** fiat, crypto
- **Number of plans:** 3
- **Cheapest paid:** $0.10 (fiat)

## Endpoint

- **URL:** `http://54.183.4.35:9010/`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
    "query": "What is the current price of Bitcoin and Ethereum?"
  }

```

**Response example:**
```json
{
    "response": "Bitcoin: $104,250 (+2.3% 24h), Market Cap: $2.07T. Ethereum: $3,890 (+1.1% 24h), Market Cap: $468B.",
    "credits_used": 1
  }

```

## Live Test Results

### Health Check: FAIL

- Status code: `404`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"error":{"code":-32001,"message":"Missing payment-signature header."}}
```

### Direct Endpoint: `405`

- Latency: `20.9ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**DEGRADED**

---

*Report generated at 2026-03-06T21:26:03.231057+00:00 by The Gold Star*
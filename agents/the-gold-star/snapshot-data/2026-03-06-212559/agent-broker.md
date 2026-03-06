# Agent Broker

**Team:** Albany beach store
**Category:** Research
**Endpoint Type:** rest-api
**Registered:** 2026-03-05T22:40:13.358Z

---

## Description

Agent Broker sells and buys items

## Keywords

`agent`, `broker`, `sells`, `buys`, `items`

## Pricing

- **Display price:** Free (Card)
- **Free plan:** Yes
- **Payment types:** fiat
- **Number of plans:** 1

## Endpoint

- **URL:** `POST /data`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "query": "What is the ETH price?",
  "format": "json"
}

```

**Response example:**
```json
{
  "status": "success",
  "results": [
    {
      "title": "Ethereum Price",
      "url": "https://example.com",
      "summary": "ETH is trading at $3245.50"
    }
  ],
  "source": "exa",
  "credits_used": 1
}
```

## Live Test Results

*Skipped: localhost or invalid URL*

## Verdict

**OFFLINE**

---

*Report generated at 2026-03-06T21:26:03.233634+00:00 by The Gold Star*
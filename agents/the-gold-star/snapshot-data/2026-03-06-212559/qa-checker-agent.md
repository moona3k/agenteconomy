# QA Checker Agent

**Team:** Full Stack Agents
**Category:** Research
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:58:49.725Z

---

## Description

Fact-checking, quality assurance, content validation

## Keywords

`checker`, `agent`, `fact-checking`, `quality`, `assurance`, `content`, `validation`

## Pricing

- **Display price:** $0.0005 (Card), $0.10 (Card), 0.0000 USDC, 0.0000 USDC, Free, 0.10 USDC, Free
- **Free plan:** Yes
- **Payment types:** fiat, crypto
- **Number of plans:** 7
- **Cheapest paid:** 0.0000 USDC (crypto)

## Endpoint

- **URL:** `https://us14.abilityai.dev/api/paid/qa-checker/chat`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
// Request
{
    "query": "Fact-check: Ethereum processes 30 TPS on mainnet",
    "format": "json"
}


```

**Response example:**
```json
{
    "response": "Partially correct. Ethereum L1 processes ~15-30 TPS...",
    "status": "success",
    "execution_id": "abc123"
}

```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `220.7ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
<html>
<head><title>405 Not Allowed</title></head>
<body>
<center><h1>405 Not Allowed</h1></center>
<hr><center>nginx/1.29.5</center>
</body>
</html>

```

### Direct Endpoint: `405`

- Latency: `671.3ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.230105+00:00 by The Gold Star*
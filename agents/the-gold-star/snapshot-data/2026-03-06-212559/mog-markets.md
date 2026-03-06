# Mog Markets

**Team:** Mog Markets
**Category:** API Services
**Endpoint Type:** mcp-server
**Registered:** 2026-03-06T10:30:42.621Z

---

## Description

API marketplace for agents. Two tools: find_service (free discovery) and buy_and_call (pay per use). 11+ services: web search, summarization, image generation, weather, geolocation, hackathon guides.

## Keywords

`mog`, `markets`, `api`, `marketplace`, `agents`, `connect`, `once`, `access`, `services`, `through`

## Pricing

- **Display price:** 0.40 USDC, 0.50 USDC, 1.00 USDC
- **Free plan:** No
- **Payment types:** crypto
- **Number of plans:** 3
- **Cheapest paid:** 1.00 USDC (crypto)

## Endpoint

- **URL:** `https://api.mog.markets/mcp`
- **Type:** mcp-server

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
          "name": "find_service",
          "arguments": {
              "query": "web search"
          }
      }
  }
```

**Response example:**
```json
{
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
          "content": [
              {
                  "type": "text",
                  "text": "{\"results\": [{\"name\": \"exa_search\", \"credits\": 1, \"description\": \"Web search with
  snippets and URLs\"}]}"
              }
          ]
      }
  }
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `633.8ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":{"error":"unauthorized","error_description":"Authorization header required"}}
```

### Direct Endpoint: `401`

- Latency: `188.5ms`
- Response preview:
```
{"detail":{"error":"unauthorized","error_description":"Authorization header required"}}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.230754+00:00 by The Gold Star*
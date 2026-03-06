# Platon Memory

**Team:** Platon
**Category:** memory
**Endpoint Type:** mcp-server
**Registered:** 2026-03-05T22:44:53.000Z

---

## Description

A MCP memory system for AI agents that helps them remember past work, learn from mistakes, and use the right context in future sessions. It plugs in through MCP and stores experience in a graph, so each new agent starts smarter instead of starting over.

## Keywords

`memory`, `mcp`, `platon`, `system`, `agents`, `helps`, `them`, `remember`, `past`, `work`

## Pricing

- **Display price:** 0.05 USDC
- **Free plan:** No
- **Payment types:** crypto
- **Number of plans:** 1
- **Cheapest paid:** 0.05 USDC (crypto)

## Endpoint

- **URL:** `https://platon.bigf.me/mcp`
- **Type:** mcp-server

## Live Test Results

### Health Check: FAIL

- Status code: `404`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"jsonrpc":"2.0","error":{"code":-32000,"message":"Not Acceptable: Client must accept both application/json and text/event-stream"},"id":null}
```

### Direct Endpoint: `405`

- Latency: `45.2ms`
- Response preview:
```
{"jsonrpc":"2.0","error":{"code":-32000,"message":"Method not allowed."},"id":null}
```

## Verdict

**DEGRADED**

---

*Report generated at 2026-03-06T21:26:03.233515+00:00 by The Gold Star*
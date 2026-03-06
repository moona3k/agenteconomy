# Autonomous Lead Seller

**Team:** Leads Agent
**Category:** API Services
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:36:56.312Z

---

## Description

Metered social-growth lead generation API with autonomous enrichment, scoring, and outreach drafts

## Keywords

`autonomous`, `lead`, `seller`, `metered`, `social-growth`, `generation`, `api`, `enrichment`, `scoring`, `outreach`

## Pricing

- **Display price:** $1.00 (Card)
- **Free plan:** No
- **Payment types:** fiat
- **Number of plans:** 1
- **Cheapest paid:** $1.00 (fiat)

## Endpoint

- **URL:** `https://leadsagent.onrender.com/leads`
- **Type:** rest-api

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `123.7ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":"Not Found"}
```

### Direct Endpoint: `422`

- Latency: `93.6ms`
- Response preview:
```
{"detail":[{"type":"missing","loc":["query","industry"],"msg":"Field required","input":null},{"type":"missing","loc":["query","city"],"msg":"Field required","input":null}]}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.230428+00:00 by The Gold Star*
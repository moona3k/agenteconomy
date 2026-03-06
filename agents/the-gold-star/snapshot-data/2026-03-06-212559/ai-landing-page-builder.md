# AI Landing Page Builder

**Team:** BaseLayer
**Category:** AI/ML
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:32:17.064Z

---

## Description

Paid AI agent for ad copy, brand strategy, and landing page creation.

## Keywords

`landing`, `page`, `builder`, `paid`, `agent`, `copy`, `brand`, `strategy`, `creation`

## Pricing

- **Display price:** $0.10 (Card), $0.10 (Card)
- **Free plan:** No
- **Payment types:** fiat
- **Number of plans:** 2
- **Cheapest paid:** $0.10 (fiat)

## Endpoint

- **URL:** `http://54.183.4.35:9040`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
    "query": "Create a landing page for InboxPilot, an AI email triage assistant for busy founders. Features: priority sorting, auto-drafts, team handoff. CTA: Start Free Trial."
}
```

**Response example:**
```json
{
    "response": "...",
    "credits_used": 10,
    "landing_page": {
      "summary": "...",
      "suggested_filename": "inboxpilot-landing-page.html",
      "saved_path": "/path/to/file.html",
      "preview_url": "",
      "download_url": "",
      "storage": "local",
      "html": "<!DOCTYPE html>..."
    }
  }
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `25.8ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":"Not Found"}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.230643+00:00 by The Gold Star*
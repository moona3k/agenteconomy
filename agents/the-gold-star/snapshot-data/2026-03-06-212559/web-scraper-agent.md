# Web Scraper Agent

**Team:** BaseLayer
**Category:** Data Analytics
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T10:27:16.126Z

---

## Description

Web scraping and content extraction agent powered by Apify.Extracts clean text and markdown from websites with single-page, batch, and deep crawl modes.

## Keywords

`web`, `agent`, `scraper`, `scraping`, `content`, `extraction`, `powered`, `apify`, `extracts`, `clean`

## Pricing

- **Display price:** $0.10 (Card), $0.10 (Card), Free
- **Free plan:** Yes
- **Payment types:** fiat, crypto
- **Number of plans:** 3
- **Cheapest paid:** $0.10 (fiat)

## Endpoint

- **URL:** `http://54.183.4.35:9020/`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
    "query": "Scrape https://example.com and extract the main content"
}
```

**Response example:**
```json
{
    "response": "# Example Domain\n\nThis domain is for use in illustrative examples in documents...",
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

- Latency: `28.3ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**DEGRADED**

---

*Report generated at 2026-03-06T21:26:03.231270+00:00 by The Gold Star*
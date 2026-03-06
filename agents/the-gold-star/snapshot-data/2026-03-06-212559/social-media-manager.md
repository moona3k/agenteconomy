# Social Media Manager

**Team:** Full Stack Agents
**Category:** Social
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T16:19:38.741Z

---

## Description

AI-powered social media content manager. Generates posts, schedules content, and manages social media presence across platforms.

## Keywords

`social`, `media`, `manager`, `content`, `ai-powered`, `generates`, `posts`, `schedules`, `manages`, `presence`

## Pricing

- **Display price:** 0.0000 USDC
- **Free plan:** No
- **Payment types:** crypto
- **Number of plans:** 1
- **Cheapest paid:** 0.0000 USDC (crypto)

## Endpoint

- **URL:** `https://api.mindra.co/v1/workflows/social-media-manager/run`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
    "query": "Create a Twitter thread about AI agent payments",
    "format": "json"
}

// Response
{
    "response": "Thread: 1/ AI agent payments are transforming...",
    "status": "success",
    "execution_id": "abc123"
}

```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `484.0ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"detail":"Not Found"}
```

### Direct Endpoint: `405`

- Latency: `501.1ms`
- Response preview:
```
{"detail":"Method Not Allowed"}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.229331+00:00 by The Gold Star*
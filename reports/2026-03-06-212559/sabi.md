# Sabi

**Team:** BennySpenny
**Category:** Research
**Endpoint Type:** rest-api
**Registered:** 2026-03-06T03:29:39.349Z

---

## Description

On-demand, geolocated verification with photo evidence and human-attested answer. Request a question + location; a nearby verifier captures proof and answers.

## Keywords

`sabi`, `on-demand`, `geolocated`, `verification`, `photo`, `evidence`, `human-attested`, `answer`, `request`, `question`

## Pricing

- **Display price:** $0.01 (Card), 0.05 USDC
- **Free plan:** No
- **Payment types:** fiat, crypto
- **Number of plans:** 2
- **Cheapest paid:** $0.01 (fiat)

## Endpoint

- **URL:** `https://sabi-backend.ben-imadali.workers.dev/query`
- **Type:** rest-api

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
  "question": "Is Blue Bottle on Market St open?",
  "targetLat": 37.7830,
  "targetLng": -122.4075
}
```

**Response example:**
```json
{
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "Is Blue Bottle on Market St open?",
    "status": "connecting",
    "targetLat": 37.7830,
    "targetLng": -122.4075
  },
  "payment": {
    "creditsRedeemed": "1",
    "remainingBalance": "42"
  }
}
```

## Live Test Results

### Health Check: PASS

- Status: `200`
- Latency: `126.2ms`

### MCP: PARTIAL (reachable but no tools listed)

Response:
```
{"error":"Unauthorized. Provide Authorization: Bearer sabi_sk_..."}
```

### Direct Endpoint: `401`

- Latency: `53.1ms`
- Response preview:
```
{"error":"Unauthorized. Provide Authorization: Bearer sabi_sk_..."}
```

## Verdict

**OPERATIONAL (health OK, MCP partial)**

---

*Report generated at 2026-03-06T21:26:03.231702+00:00 by The Gold Star*
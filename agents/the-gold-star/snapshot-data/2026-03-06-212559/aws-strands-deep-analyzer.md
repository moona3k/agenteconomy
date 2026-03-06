# AWS Strands Deep Analyzer

**Team:** The Intelligence Bazaar
**Category:** AI/ML
**Endpoint Type:** localhost
**Registered:** 2026-03-06T20:31:35.031Z

---

## Description

Enterprise-grade deep analysis agent powered by AWS Bedrock (Claude Sonnet) and AWS Strands framework. Two endpoints: /api/deep-analyze (20 credits) for comprehensive topic analysis with key insights, risk assessment, market opportunities, and confidence scoring; /api/aggregate (15 credits) for multi-source intelligence aggregation that synthesizes data from multiple providers into unified reports. Built with Python, FastAPI, and AWS Strands. Part of the Intelligence Bazaar multi-agent marketplace.

## Keywords

`aws`, `strands`, `deep`, `analysis`, `credits`, `intelligence`, `analyzer`, `enterprise-grade`, `agent`, `powered`

## Pricing

- **Display price:** Free
- **Free plan:** Yes
- **Payment types:** crypto
- **Number of plans:** 1

## Endpoint

- **URL:** `http://localhost:3010/api/deep-analyze`
- **Type:** localhost

## API Schema

### Endpoint 1

**Method:** `POST`

**Request body:**
```json
{
    "task": "Analyze the DeFi lending market opportunity in Southeast Asia",
    "context": {
      "region": "SEA",
      "sector": "DeFi",
      "timeframe": "2026"
    }
  }
```

**Response example:**
```json
{
    "success": true,
    "task": "Analyze the DeFi lending market opportunity in Southeast Asia",
    "analysis": {
      "summary": "Southeast Asia presents a high-growth DeFi lending opportunity with 60% underbanked population",
      "keyInsights": [
        "60% of SEA population is underbanked",
        "Mobile-first adoption creates DeFi on-ramp"
      ],
      "marketOpportunity": "Estimated $4.2B addressable market by 2027",
      "risks": ["Regulatory uncertainty in Vietnam", "Currenc
```

## Live Test Results

*Skipped: localhost or invalid URL*

## Verdict

**UNREACHABLE (localhost only)**

---

*Report generated at 2026-03-06T21:26:03.227035+00:00 by The Gold Star*
# The Gold Star -- Michelin Stars for AI Agents

The quality layer of the agent economy. AI-powered QA and certification using Claude Sonnet 4.6 as the evaluator. Submit your service endpoint, get a detailed quality report with a star rating.

**Deployed at:** `the-gold-star-production.up.railway.app` | **Port:** 3500

## Why This Exists

Other testing tools check HTTP status codes. The Gold Star has Claude read your actual responses and judge whether they're good. There's a massive difference between "the endpoint returned 200" and "the response was specific, well-structured, and would satisfy a paying customer."

Every economy needs quality assurance. In the real world, we have Michelin stars, ISO certifications, Consumer Reports. The agent economy had nothing -- until now.

## How It Works

1. **Submit** your service endpoint URL
2. **We discover** your MCP tools automatically
3. **We test** with realistic scenarios: self-description, simple tasks, edge cases, complex requests
4. **Claude evaluates** every response against a rubric across 5 dimensions
5. **You get** a detailed report with scores, narrative, and improvement recommendations
6. **Fix and resubmit** -- address issues, request another review, improve your score
7. **Earn certification** -- 4.5+ stars with all dimensions >= 8 = GOLD STAR CERTIFIED

### Scoring Dimensions

| Dimension | Weight | What Claude Evaluates |
|-----------|--------|----------------------|
| Availability | 15% | Health check, MCP endpoint, tool discovery |
| Functionality | 30% | Do tools return meaningful, relevant responses? |
| Response Quality | 30% | Would a paying customer be satisfied? Specificity, structure, value. |
| Latency | 10% | Response times across all tests |
| Robustness | 15% | Error handling, graceful degradation |

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `request_review` | Submit a service for comprehensive AI-powered QA testing. Returns detailed report. |
| `get_report` | Retrieve the latest QA report for any seller. |
| `certification_status` | Check Gold Star certification status for a seller (or list all certified services). |
| `gold_star_stats` | System-wide QA statistics. |

### Honest Limitations

- Tests are run via HTTP against your public endpoint. We can't test services that require complex auth flows.
- Claude judges content quality, not domain expertise. A service returning plausible-sounding but factually wrong information may still score well on response quality.
- Latency tests are point-in-time snapshots, not averaged over time.
- Test queries are generic. A service optimized for a narrow domain may underperform on our broad test scenarios.
- Quality infrastructure should not have a paywall -- that's why all tools are free.

## Quick Start

```bash
cd agents/the-gold-star
cp .env.example .env    # Add NVM_API_KEY and ANTHROPIC_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3500
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |
| `/llms.txt` | Machine-readable service docs for AI agents |
| `/.well-known/agent.json` | A2A-compatible agent card |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `ANTHROPIC_API_KEY` | Yes | For Claude Sonnet 4.6 evaluation |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3500` |
| `ENDPOINT_URL` | No | Public URL for Nevermined registration |

## Part of the Agent Economy

The Gold Star is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It pairs with The Oracle (discovery) and The Underwriter (trust scores) to give buyer agents the complete quality picture: what exists, whether to trust it, and whether it's actually any good.

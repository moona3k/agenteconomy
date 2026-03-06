# The Gold Star -- Michelin Stars for AI Agents

AI-powered QA and certification service. Uses Claude Sonnet 4.6 as the evaluator.

## The Concept

Every economy needs quality assurance. In the real world, we have Michelin stars, ISO certifications, Consumer Reports. The agent economy has nothing -- until now.

The Gold Star doesn't just check "is the endpoint up?" -- it calls your tools with realistic scenarios, reads your actual responses, and has Claude evaluate whether a paying customer would be satisfied.

### How It Works

1. **Submit for review**: Provide your service endpoint URL
2. **We discover your tools**: Automatically enumerate available MCP tools
3. **We test with realistic scenarios**: Self-description, simple tasks, edge cases, complex requests
4. **Claude evaluates every response**: Rubric-based scoring across 5 dimensions
5. **Get a detailed report**: AI-written narrative with specific improvement recommendations
6. **Fix and resubmit**: Address the issues, request another review
7. **Earn certification**: 4.5+ stars with all dimensions >= 8 = GOLD STAR CERTIFIED

### Scoring Dimensions (evaluated by Claude Sonnet 4.6)

| Dimension | Weight | What Claude Evaluates |
|-----------|--------|----------------------|
| Availability | 15% | Health check, MCP endpoint, tool discovery |
| Functionality | 30% | Do tools return meaningful, relevant responses? |
| Response Quality | 30% | Would a paying customer be satisfied? Specificity, structure, value |
| Latency | 10% | Response times across all tests |
| Robustness | 15% | Error handling, graceful degradation |

### Why AI-Powered Evaluation Matters

Other testing tools just check HTTP status codes. The Gold Star has Claude read your actual responses and judge whether they're good. There's a massive difference between "the endpoint returned 200" and "the response was specific, well-structured, and would satisfy a paying customer."

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `request_review` | 0 (free) | Submit service for AI-powered QA testing |
| `get_report` | 0 (free) | Retrieve latest QA report for any seller |
| `certification_status` | 0 (free) | Check Gold Star certification |
| `gold_star_stats` | 0 (free) | System-wide QA statistics |

## Quick Start

```bash
cd agents/the-gold-star
poetry install
cp .env.example .env
# Edit .env with your NVM_API_KEY and ANTHROPIC_API_KEY
poetry run python -m src.setup
poetry run python -m src.server
```

Server starts on port 3500:
- MCP endpoint: http://localhost:3500/mcp
- Health check: http://localhost:3500/health

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined sandbox API key |
| `ANTHROPIC_API_KEY` | Yes | For Claude Sonnet 4.6 evaluation |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `PORT` | No | Default: `3500` |

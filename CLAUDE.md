# CLAUDE.md - Nevermined AI Agent Examples

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Repository containing working examples of AI agents with Nevermined payment integration. Each agent demonstrates a different protocol (x402, A2A, MCP) and deployment pattern.

## MCP Server Integration

Connect to Nevermined docs for AI-assisted development ("vibe coding"):

### Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nevermined": {
      "url": "https://docs.nevermined.app/mcp"
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "nevermined": {
      "url": "https://docs.nevermined.app/mcp"
    }
  }
}
```

### LLM Context Resources

- **MCP Server**: https://docs.nevermined.app/mcp
- **Context File**: https://docs.nevermined.app/assets/nevermined_mcp_for_llms.txt
  https://nevermined.ai/docs/development-guide/build-using-nvm-mcp OR https://nevermined.ai/docs/llms-full.txt OR https://nevermined.ai/docs/llms.txt
---

## Environment Setup

### Required Environment Variables

```bash
# .env file (each agent has its own .env.example)
NVM_API_KEY=sandbox:your-api-key
NVM_ENVIRONMENT=sandbox          # or 'live', 'staging_sandbox'
NVM_PLAN_ID=your-plan-id
NVM_AGENT_ID=your-agent-id       # optional

# LLM Provider (for AI agents)
OPENAI_API_KEY=sk-your-key

# AWS (for AgentCore deployment)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Get Your Nevermined API Key

1. Open [https://nevermined.app/](https://nevermined.app/) and sign in with your account
2. Navigate to **API Keys** > **Global NVM API Keys**
3. Click **+ New API Key**
4. Give your key a descriptive name, select the permissions you need, and click **Generate API Key**
5. Click **Copy Key** to copy it to your clipboard and store it securely

> API keys are environment-specific: sandbox keys begin with `sandbox:`, live keys start with `live:`.

### Create a Payment Plan

1. In the Nevermined App, go to "My agents" or "My pricing plans"
2. Register your agent with metadata
3. Create a payment plan (credit-based, time-based, or trial)
4. Copy the `planId` for your environment variables

---

## Protocol Quick Reference

### x402 (HTTP Payment Protocol)

The x402 protocol uses HTTP headers for payment negotiation:

| Header | Direction | Description |
|--------|-----------|-------------|
| `payment-signature` | Client -> Server | x402 access token |
| `payment-required` | Server -> Client (402) | Payment requirements (base64 JSON) |
| `payment-response` | Server -> Client (200) | Settlement receipt (base64 JSON) |

**TypeScript Example:**

```typescript
import { Payments } from "@nevermined-io/payments";
import { paymentMiddleware } from "@nevermined-io/payments/express";

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY,
  environment: "sandbox",
});

app.use(paymentMiddleware(payments, {
  "POST /ask": { planId: PLAN_ID, credits: 1 },
}));
```

**Python Example:**

```python
from payments_py import Payments, PaymentOptions
from payments_py.x402.fastapi import PaymentMiddleware

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment="sandbox")
)

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={"POST /ask": {"plan_id": PLAN_ID, "credits": 1}},
)
```

### A2A (Agent-to-Agent Protocol)

For autonomous agent-to-agent transactions with standard agent card discovery (`/.well-known/agent.json`) and payment-protected JSON-RPC messaging.

### MCP (Model Context Protocol)

For tool/plugin monetization. Logical URLs follow: `mcp://<serverName>/<typeName>/<methodName>`

Example: `mcp://weather-mcp/tools/weather.today`

---

## AWS Integration

### Strands SDK + Nevermined

Integrate Nevermined payments into Strands agents using the `@requires_payment` decorator:

```python
from strands import Agent, tool
from payments_py import Payments, PaymentOptions
from payments_py.x402.strands import requires_payment

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment="sandbox")
)

@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=1)
def my_tool(query: str, tool_context=None) -> dict:
    """My payment-protected tool."""
    return {"status": "success", "content": [{"text": f"Result: {query}"}]}

agent = Agent(tools=[my_tool])
state = {"payment_token": "x402-access-token"}
result = agent("Do something", invocation_state=state)
```

See `agents/strands-simple-agent/` for a complete working example.

### AgentCore Deployment

Deploy payment-enabled agents to AWS AgentCore:

```python
from bedrock_agentcore import BedrockAgentCoreApp
from payments_py import Payments

app = BedrockAgentCoreApp()
payments = Payments.get_instance(...)

@app.entrypoint
def invoke(payload):
    # Verify payment and execute
    result = process_request(payload)
    return {"result": result}
```

Reference: https://github.com/awslabs/amazon-bedrock-agentcore-samples

**Full deployment guide:** See [docs/deploy-to-agentcore.md](docs/deploy-to-agentcore.md) for step-by-step AgentCore deployment with Nevermined payments (header remapping, SigV4 signing, troubleshooting).

---

## Common Commands

### Python Agents

```bash
# Install dependencies
poetry install

# Run entry points (all agents use package-mode = false)
poetry run python -m src.agent       # HTTP server
poetry run python -m src.agent_a2a   # A2A server
poetry run python -m src.web         # Web server + frontend
poetry run python -m src.client      # Test client
poetry run python -m src.setup       # Setup script (mcp-server-agent)
poetry run python -m src.server      # MCP server
```

---

## Repository Structure

```
hackathons/
├── CLAUDE.md                    # This file
├── README.md                    # Overview and getting started
├── .gitignore
├── docs/
│   ├── getting-started.md       # Environment setup guide
│   ├── aws-integration.md      # Strands SDK + AgentCore deployment
│   └── deploy-to-agentcore.md  # Step-by-step AgentCore guide
├── agents/                      # Independent agent projects
│   ├── strands-simple-agent/    # Strands + Nevermined x402 demo
│   ├── seller-simple-agent/     # Data selling agent with tiered pricing
│   ├── buyer-simple-agent/      # Data buying agent with web frontend
│   │   └── frontend/            # React + Vite chat UI
│   └── mcp-server-agent/        # MCP server with payment-protected tools
└── examples/                    # Complete working demos
```

### Agents Directory

Each subfolder under `agents/` is an independent agent project with its own `pyproject.toml` (poetry).

- `strands-simple-agent/` - Strands agent with x402 payment-protected tools
  - Install: `poetry install`
  - Run agent: `poetry run python agent.py`
  - Run demo: `poetry run python demo.py`
- `seller-simple-agent/` - Data selling agent with tiered pricing (1, 5, 10 credits)
  - Install: `poetry install`
  - Run agent (HTTP): `poetry run python -m src.agent`
  - Run agent (A2A): `poetry run python -m src.agent_a2a`
  - Run agent (A2A, search only): `poetry run python -m src.agent_a2a --tools search --port 9001 --buyer-url http://localhost:8000`
  - Run client: `poetry run python -m src.client`
  - Run agent (AgentCore A2A): `poetry run python -m src.agent_a2a_agentcore`
  - Docker build: `docker build -t seller-agent .`
- `buyer-simple-agent/` - Data buying agent with A2A marketplace and web frontend
  - Install: `poetry install` (backend), `cd frontend && npm install` (frontend)
  - Run CLI agent (A2A default): `poetry run python -m src.agent`
  - Run CLI agent (HTTP mode): `poetry run python -m src.agent --mode http`
  - Run web server: `poetry run python -m src.web`
  - Run web server (AgentCore): `poetry run python -m src.web_agentcore`
  - Run frontend dev: `cd frontend && npm run dev` (opens http://localhost:5173)
  - Run client (A2A): `poetry run python -m src.client_a2a`
  - Docker build: `docker build -t buyer-agent .`
  - **Note:** Use `poetry run python -m src.<module>` (not `poetry run agent`) because `package-mode = false`
- `mcp-server-agent/` - MCP server with Nevermined payment-protected tools (search, summarize, research)
  - Install: `poetry install`
  - Setup (registers agent + plan, only needs NVM_API_KEY): `poetry run python -m src.setup`
  - Run server: `poetry run python -m src.server` (starts on port 3000)
  - Run client: `poetry run python -m src.client`
  - Health check: `curl http://localhost:3000/health`
  - **Note:** Use `poetry run python -m src.<module>` because `package-mode = false`

---

## Hackathon Agent Economy — Live Deployment

**Domain:** agenteconomy.io | **Team:** Full Stack Agents | **Hackathon:** Nevermined Autonomous Business (March 5-6, 2026)

**PROMOTIONAL PERIOD: All MCP tools across all services are FREE (0 credits).**

### Philosophy

We believe marketplace transparency, trust infrastructure, and quality assurance should be
accessible to everyone in the agent economy. All tool descriptions are written from a genuine,
honest perspective — explaining what each tool does well, when to use it, and what its limitations
are. No snake oil, no overpromising. We list limitations alongside capabilities because we think
honesty builds trust, and trust builds economies.

### Live Services

| Service | Railway URL | Custom Domain | Protocol | Tools |
|---------|------------|---------------|----------|-------|
| The Ledger | the-ledger-production.up.railway.app | agenteconomy.io | REST | /api/sellers, /api/buyers, /api/analysis, /llms.txt, /.well-known/agent.json |
| The Oracle | oracle-production.up.railway.app | oracle.agenteconomy.io | MCP | marketplace_data, marketplace_search, marketplace_leaderboard, marketplace_compare |
| The Amplifier | the-amplifier-production.up.railway.app | amplifier.agenteconomy.io | MCP | enrich_with_ads, get_ad, ad_stats |
| The Architect | the-architect-production.up.railway.app | architect.agenteconomy.io | MCP | orchestrate, quick_research, pipeline_status |
| The Underwriter | the-underwriter-production.up.railway.app | underwriter.agenteconomy.io | MCP | check_reputation, submit_review, file_claim, reputation_leaderboard, underwriter_stats |
| The Gold Star | the-gold-star-production.up.railway.app | goldstar.agenteconomy.io | MCP | request_review, get_report, certification_status, gold_star_stats |
| The Fund | N/A (local only) | N/A | Script | Autonomous buyer — discovers, purchases, reviews, generates ROI reports |

### Agent-Friendly Access Patterns

All services are designed to be maximally discoverable by AI agents:

- **`/llms.txt`** on The Ledger — plain text service manifest following llms.txt convention
- **`/.well-known/agent.json`** on The Ledger — A2A-compatible agent card with all services
- **Agent-friendly 404 errors** — JSON with error, message, hint, available_endpoints, mcp_services
- **MCP `/health` endpoints** — all MCP servers respond to GET /health with JSON status
- **Normalized data API** — The Oracle's `marketplace_data` returns clean, consistent JSON schema

### LLM / AI Agent Integration

- **Anthropic Claude Opus 4.6** powers The Architect (5-agent orchestration pipeline)
- **Anthropic Claude Sonnet 4.6** powers The Gold Star (QA evaluation)
- All tool descriptions follow LLM-friendly pattern: what it does → what it returns → when to use → cost → honest limitations → param examples

### Railway Deployment Notes

- **Builder:** Railpack (default). Each service needs `requirements.txt` + `Procfile`.
- **rootDirectory:** Must be set per service via Railway API since `railway up` uploads from git root.
- **Custom Domains:** Require CNAME to Railway's short-hash domain + TXT `_railway-verify.<subdomain>` record.
- **Redeployment:** `cd /repo/root && railway up -s <service-name> --detach`
- **Env vars:** Set via `railway variables --set "KEY=value" -s <service-name>`

### Hackathon Agent Directory

All services are FREE during promotional period. Credits set to 0 across the board.

- `the-oracle/` — Marketplace intelligence: data, search, leaderboard, compare (all FREE)
- `the-amplifier/` — AI-native ads: enrich_with_ads, get_ad, ad_stats (all FREE)
- `the-architect/` — Multi-agent Claude Opus pipeline: orchestrate, quick_research (all FREE)
- `the-underwriter/` — Trust & insurance: check_reputation, submit_review, file_claim, leaderboard (all FREE)
- `the-gold-star/` — QA certification: request_review, get_report, certification_status (all FREE)
- `the-ledger/` — Dashboard + REST API + llms.txt + agent.json (always free)
- `the-fund/` — Autonomous buyer agent (not deployed, runs locally)

---

## Related Resources

- [Nevermined Documentation](https://nevermined.ai/docs)
- [Nevermined App](https://nevermined.app)
- [Payments TypeScript SDK](https://github.com/nevermined-io/payments)
- [Payments Python SDK](https://github.com/nevermined-io/payments-py)
- [x402 Protocol Spec](https://github.com/coinbase/x402)
- [AWS AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)

---

## Support

- **Discord**: [Join Nevermined Community](https://discord.com/invite/GZju2qScKq)

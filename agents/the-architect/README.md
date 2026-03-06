# The Architect -- Multi-Agent Orchestration

The intelligence layer of the agent economy. A 5-agent hierarchical pipeline powered by Claude Opus 4.6 that turns any question into an executive research report.

**Deployed at:** `the-architect-production.up.railway.app` | **Port:** 3300

## Why This Exists

Individual agents are good at narrow tasks. But real research requires multiple perspectives: someone to find relevant sources, someone to synthesize them, someone to extract insights, someone to check quality, and someone to write the final report. The Architect coordinates all of this in a single call.

## How It Works

```
                CEO Orchestrator
                     |
    +--------+-------+-------+--------+
    |        |       |       |        |
Discovery  Research  Analysis   QA    Report
  Agent     Agent     Agent   Agent   Agent
```

| Stage | Agent | What It Does |
|-------|-------|-------------|
| 1 | **Discovery** | Searches the Nevermined marketplace for relevant seller services |
| 2 | **Research** | Synthesizes information on the topic, incorporating marketplace context |
| 3 | **Analysis** | Distills research into actionable insights and recommendations |
| 4 | **QA** | Reviews findings for accuracy, bias, and completeness (scored 1-10) |
| 5 | **Report** | Produces a polished executive report combining all outputs |

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `orchestrate` | Full 5-agent pipeline. Submit any topic, get an executive report with quality review. 15-45 seconds. |
| `quick_research` | Fast 2-agent version (Research + Analysis only). Good for simpler questions. |
| `pipeline_status` | Health check and usage stats. |

### Honest Limitations

- Full pipeline takes 15-45 seconds depending on topic complexity and marketplace API speed.
- Reports are analytical synthesis, not primary research. The agents reason about available information, they don't generate new data.
- QA review is a single LLM judgment, not ground truth verification. It catches obvious errors and bias, not subtle inaccuracies.
- We're absorbing the Claude API costs because we want you to see what hierarchical agent orchestration can do.

## Quick Start

```bash
cd agents/the-architect
cp .env.example .env    # Add NVM_API_KEY and ANTHROPIC_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3300
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |
| `/llms.txt` | Machine-readable service docs for AI agents |
| `/.well-known/agent.json` | A2A-compatible agent card |

## Example Queries

- "AI agent marketplace trends and monetization strategies"
- "Compare decentralized vs centralized payment protocols for AI services"
- "What are the most underserved categories in the Nevermined marketplace?"

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `ANTHROPIC_API_KEY` | Yes | For Claude Opus 4.6 pipeline |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3300` |
| `ENDPOINT_URL` | No | Public URL for Nevermined registration |

## Part of the Agent Economy

The Architect is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It can independently purchase services from other marketplace sellers during its research pipeline -- making it both a seller (of orchestration) and a buyer (of marketplace data).

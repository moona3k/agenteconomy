# The Architect -- Multi-Agent Orchestrator

A PaymentsMCP server that runs 5+ specialized sub-agents in a hierarchical pipeline, producing comprehensive executive reports through coordinated multi-agent collaboration.

Built for the **Mindra $2,000 Sponsor Prize** at the Nevermined Autonomous Business Hackathon.

## What It Does

The Architect implements a corporate org-chart style orchestration pattern. A CEO agent delegates work to 5 specialist agents, each focused on a single task. The pipeline flows sequentially, with each agent's output feeding into the next:

```
                    CEO Orchestrator
                         |
        +--------+-------+-------+--------+
        |        |       |       |        |
   Discovery  Research  Analysis   QA    Report
     Agent     Agent     Agent   Agent   Agent
```

### Pipeline Stages

| Stage | Agent | Role |
|-------|-------|------|
| 1 | **Discovery** | Queries the Nevermined marketplace to find relevant seller services |
| 2 | **Research** | Synthesizes research on the topic, incorporating marketplace context |
| 3 | **Analysis** | Distills research into actionable insights and recommendations |
| 4 | **QA** | Reviews findings for accuracy, consistency, bias, and completeness |
| 5 | **Report** | Produces a polished executive report combining all prior outputs |

## Mindra Prize Criteria

This project targets two specific criteria from the Mindra sponsor:

- **5+ specialized agents in a single assistant flow** -- Discovery, Research, Analysis, QA, and Report agents each contribute to a single coordinated output.
- **Hierarchical orchestration (orchestrators of orchestrators)** -- The CEO agent delegates through a structured pipeline, like a corporate org chart, scaling AI through layered decision-making.

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `orchestrate` | 5 | Full 5-agent pipeline. Runs all stages and produces an executive report. |
| `quick_research` | 2 | Research + Analysis only. Faster and cheaper for simple queries. |
| `pipeline_status` | 0 | Free health check. Returns agent count and pipeline configuration. |

## Setup

### 1. Install dependencies

```bash
cd agents/the-architect
poetry install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your keys:
#   NVM_API_KEY=sandbox:your-key
#   OPENAI_API_KEY=sk-your-key
```

### 3. Register agent and plan (one-time)

```bash
poetry run python -m src.setup
```

This registers The Architect on Nevermined and creates a payment plan. Copy the output `NVM_AGENT_ID` and `NVM_PLAN_ID` into your `.env`.

### 4. Start the server

```bash
poetry run python -m src.server
```

The server starts on port 3300 (configurable via `PORT` env var).

- MCP endpoint: `http://localhost:3300/mcp`
- Health check: `http://localhost:3300/health`

## Example Queries

Full orchestration (5 credits):
- "AI agent marketplace trends and monetization strategies"
- "Compare decentralized vs centralized payment protocols for AI services"
- "Enterprise adoption barriers for autonomous AI agents"

Quick research (2 credits):
- "Current state of multi-agent orchestration frameworks"
- "x402 protocol advantages over traditional API billing"

## Part of the 4-Business Portfolio

The Architect is one of four agents in our hackathon portfolio:

1. **Seller Agent** -- Data selling with tiered pricing
2. **Buyer Agent** -- Marketplace browser with A2A purchasing
3. **MCP Server Agent** -- Payment-protected research tools
4. **The Architect** -- Multi-agent orchestrator (this project, targeting Mindra prize)

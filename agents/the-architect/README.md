# The Architect -- 7-Agent Hierarchical Orchestration

Orchestrators of orchestrators. A 3-layer corporate org chart where a CEO delegates to VP-level orchestrators, each managing specialized leaf agents. 7 agents total, 3 layers deep, with both parallel and sequential orchestration patterns.

**Deployed at:** `architect.agenteconomy.io` | **Port:** 3300 | **Mindra $2K Prize**

## Why This Exists

Individual agents are good at narrow tasks. Real research requires multiple perspectives coordinated across layers. The Architect implements hierarchical orchestration -- not just agents in a pipeline, but orchestrators managing orchestrators -- matching Mindra's criteria for scaled AI systems through structured delegation and layered decision-making.

## Architecture (3 Layers, 7 Agents)

```
                    Layer 1: CEO (orchestrator)
                         |
            +------------+------------+
            |            |            |
       Layer 2:     Layer 2:     Layer 2:
    VP Intelligence  VP Research  VP Quality
    (orchestrator)  (orchestrator) (orchestrator)
         |               |              |
    +----+----+     +----+----+    +----+----+
    |         |     |         |    |         |
Discovery  Market  Research Analysis  QA    Report
 Agent    Scanner   Agent    Agent  Agent   Agent
  (leaf)  (leaf)   (leaf)   (leaf) (leaf)  (leaf)

          Layer 3: Leaf Agents (do the actual work)
```

### Orchestration Patterns

| Phase | Orchestrator | Leaf Agents | Pattern | Why |
|-------|-------------|-------------|---------|-----|
| 1 | **VP Intelligence** | Discovery + Market Scanner | **Parallel** | Both query the marketplace independently -- no dependency |
| 2 | **VP Research** | Research + Analysis | **Parallel** | Both work from intelligence brief -- can synthesize independently |
| 3 | **VP Quality** | QA -> Report | **Sequential** | Quality gate: QA must review before Report incorporates feedback |

### What Each Agent Does

| Agent | Layer | Role |
|-------|-------|------|
| **CEO** | 1 (orchestrator) | Top-level coordinator. Delegates to 3 VPs, synthesizes final output. |
| **VP Intelligence** | 2 (orchestrator) | Runs Discovery + Market Scanner in parallel. Produces intelligence brief. |
| **VP Research** | 2 (orchestrator) | Runs Research + Analysis in parallel using intelligence brief. |
| **VP Quality** | 2 (orchestrator) | Runs QA then Report sequentially. Quality gate before publication. |
| **Discovery** | 3 (leaf) | Searches Nevermined marketplace for services matching the query. |
| **Market Scanner** | 3 (leaf) | Analyzes competitive landscape: categories, teams, endpoint availability. |
| **Research** | 3 (leaf) | Synthesizes findings using Claude Sonnet. |
| **Analysis** | 3 (leaf) | Distills data into actionable insights and recommendations. |
| **QA** | 3 (leaf) | Reviews for accuracy, bias, completeness. Scores 1-10. |
| **Report** | 3 (leaf) | Produces executive report incorporating QA feedback. |

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `orchestrate` | Full 7-agent hierarchical pipeline. Submit any topic, get an executive report with marketplace intelligence, research, analysis, QA review. 15-45 seconds. |
| `quick_research` | Fast 2-agent version (Research + Analysis only). |
| `pipeline_status` | Architecture details, health check, and usage stats. |

### Honest Limitations

- Full pipeline takes 15-45 seconds depending on topic complexity and marketplace API speed.
- Reports are analytical synthesis, not primary research. Agents reason about available information, they don't generate new data.
- QA review is a single LLM judgment, not ground truth verification.
- We absorb the Claude API costs so you can see what hierarchical orchestration looks like.

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

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `ANTHROPIC_API_KEY` | Yes | For Claude Sonnet 4.6 pipeline |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3300` |
| `ENDPOINT_URL` | No | Public URL for Nevermined registration |

## Part of the Agent Economy

The Architect is one of 11 services at [agenteconomy.io](https://agenteconomy.io). Its Discovery and Market Scanner agents query the Nevermined marketplace directly, making it both a seller (of orchestration) and a consumer (of marketplace data).

# AWS

Over 100,000 organizations use Amazon Bedrock. That number alone tells you something about AWS's position in the AI infrastructure market — they may not have the flashiest models, but they have the distribution machinery that makes enterprise adoption happen.

## What it does

AWS contributes two relevant pieces to the agent economy: Strands SDK and AgentCore.

**Strands SDK** is an open-source (Apache 2.0) Python framework for building AI agents. At version 1.29.0 with 5.3k GitHub stars, it takes a model-driven approach — you define tools with the `@tool` decorator, hand them to an agent, and let the model decide when to use them. It has native MCP support, meaning your agent can consume MCP servers as tool sources without glue code. The framework is deliberately minimal: no complex graph abstractions, no mandatory state management patterns. You write Python functions, decorate them, and go.

**AgentCore** is the deployment platform — a fully managed runtime for agentic workloads. It handles session isolation, VPC networking, containerized execution, and integrates with CloudWatch and OpenTelemetry for observability. The billing model is per-second with no charges for I/O wait time, plus $200 in free credits to get started. It is framework-agnostic: Strands, CrewAI, LangGraph, and LlamaIndex agents all deploy the same way.

AgentCore's architecture has three pillars. Build: managed memory, API gateway, browser runtime, and code interpreter. Deploy: session-isolated containers with VPC support. Operate: CloudWatch metrics, OpenTelemetry traces, and built-in evaluation tooling.

## How it works

A Strands agent is straightforward to build. You define tools as decorated Python functions, instantiate an agent with a model and tool list, and invoke it with natural language. The model receives your tools as callable functions and decides the execution plan.

```python
@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=1)
def my_tool(query: str, tool_context=None) -> dict:
    return {"status": "success", "content": [{"text": f"Result: {query}"}]}

agent = Agent(tools=[my_tool])
```

The `@requires_payment` decorator from Nevermined's Strands integration wraps the tool with x402 payment verification. The agent passes an invocation state containing the payment token, and the decorator validates it before executing the tool logic.

For deployment, AgentCore uses a `BedrockAgentCoreApp` entrypoint. You define an invoke function that receives payloads and returns results. The platform handles scaling, session management, and infrastructure.

## Where it fits in the agent economy

AWS provides the compute and deployment substrate. In a mature agent economy, agents need to run somewhere reliable, scale under load, and be observable when things break. AgentCore offers all of this with the operational maturity you expect from AWS.

Strands fills the "build it fast" niche. For hackathon participants coming from Python, the decorator-based tool pattern is the fastest path from idea to working agent. The MCP-native support means Strands agents can discover and consume payment-protected tools from services like The Oracle or The Amplifier without custom integration code.

The Bedrock model marketplace (hundreds of models from multiple providers) means agents built on Strands are not locked into a single model vendor. You can swap Claude for Llama for Mistral without changing your tool definitions.

## Limitations

The most significant pain point we encountered: AgentCore's proxy strips custom HTTP headers. This directly breaks x402 payment flows, which rely on the `payment-signature` header reaching the backend. The workaround requires remapping headers and SigV4 signing, which adds meaningful complexity. This is documented in detail in the project's `deploy-to-agentcore.md` guide, but it should not be necessary.

A2A agent discovery also does not work through the AgentCore proxy. The `/.well-known/agent.json` endpoint, which is fundamental to the A2A protocol, gets intercepted before reaching your agent code.

Strands is young. At 5.3k stars, the community is growing but still small compared to LangChain or LlamaIndex. Documentation covers common patterns but drops off quickly for advanced use cases. The model-driven approach works well for simple tool-calling agents but offers less control than graph-based frameworks when you need deterministic execution paths.

The $200 free credit tier is generous for experimentation, but per-second billing can add up quickly for agents that maintain long-running sessions or do heavy computation between API calls.

AWS's strength is infrastructure reliability and enterprise readiness. Its weakness in the agent economy context is that its proxy and security layers were designed for traditional web services, not for the header-rich, protocol-diverse world of agent-to-agent communication.

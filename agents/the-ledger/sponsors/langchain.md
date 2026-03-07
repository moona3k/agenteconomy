# LangChain

128,000 GitHub stars. One billion cumulative downloads. Over 100 million monthly. These numbers make LangChain the most widely adopted AI agent framework by a wide margin — and also the one with the most opinions written about it, not all of them kind.

## What it does

LangChain is an agent engineering platform with three core components: the LangChain framework for building agents, LangGraph for orchestrating them, and LangSmith for observing and evaluating them.

**LangChain** (the framework) provides a standardized interface for connecting LLMs to tools, data sources, and each other. With over 1,000 integrations — vector stores, document loaders, LLM providers, retrievers — it functions as the universal adapter layer for AI applications. The framework is MIT-licensed and supports building a functional agent in roughly 10 lines of code with `create_agent()`.

**LangGraph** (25.7k stars) handles stateful, graph-based agent orchestration. Where LangChain gives you a chain of operations, LangGraph gives you a directed graph with cycles, conditionals, and persistent state. It supports durable execution (agents survive restarts), human-in-the-loop workflows (pause for approval, then resume), and multi-agent coordination. Deep Agents, a newer addition, handle long-running tasks that may take minutes or hours rather than seconds.

**LangSmith** is the observability and evaluation platform. It is framework-agnostic — you can trace LangGraph agents, raw OpenAI calls, or custom pipelines. Over 6,000 customers use it, processing more than 1 billion events per day. It provides trace visualization, regression testing, dataset management, and automated evaluation pipelines.

## How it works

LangChain's architecture follows a layered approach. At the bottom, `langchain-core` defines the interfaces: Runnables, PromptTemplates, OutputParsers, and the LCEL (LangChain Expression Language) for composing them. Above that, integration packages (`langchain-openai`, `langchain-anthropic`, etc.) implement these interfaces for specific providers. At the top, `langgraph` adds stateful orchestration.

A LangGraph agent is defined as a state graph. You declare nodes (functions that transform state), edges (transitions between nodes), and conditional edges (routing based on state). The graph compiles into an executable that manages state persistence, checkpointing, and error recovery.

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, tools)
result = agent.invoke({"messages": [("user", "What's the weather?")]})
```

LangSmith integrates via a tracer that captures every LLM call, tool invocation, and state transition. Traces are hierarchical — you see the full execution tree from user input to final response, with latency, token counts, and costs at each node.

## Where it fits in the agent economy

LangChain's primary value in the agent economy is reach. With 35% of Fortune 500 companies using it, any payment protocol or marketplace that integrates with LangChain gets immediate distribution to a massive developer base. If you build a Nevermined payment tool as a LangChain integration, every LangChain developer can use it without learning a new framework.

LangGraph's stateful orchestration is directly relevant to agent economy workflows. A buyer agent that discovers sellers, compares prices, negotiates terms, makes purchases, and evaluates results is a multi-step workflow with branching logic — exactly what LangGraph's graph model handles well. The durable execution guarantee means a purchasing workflow that fails midway can resume from the last checkpoint rather than restarting.

LangSmith's observability matters for trust. In an economy where agents spend real money, operators need visibility into what their agents are doing, why they made specific decisions, and where they failed. Trace-level observability is not a nice-to-have when your agent has a wallet.

## Limitations

LangChain's most persistent criticism is instability. The project has undergone multiple package restructurings, namespace renames, and documentation migrations since its founding in late 2022. Code written against six-month-old tutorials often does not compile against current versions. The team has acknowledged this and the API surface has stabilized considerably, but the reputation lingers.

The abstraction layer adds overhead. For simple use cases — call an LLM, parse the output, call a tool — LangChain introduces indirection that raw SDK calls do not. The LCEL syntax, while powerful, has a learning curve that some developers find steeper than writing plain Python.

LangSmith is a paid product with a free tier. For serious evaluation and tracing at scale, you are paying for a SaaS platform, which may not suit teams that want self-hosted observability.

The integration breadth is a double-edged sword. With 1,000+ integrations, quality varies. Some integrations are maintained by the core team, others by community contributors with varying levels of commitment. Checking the last commit date on an integration package before depending on it is good practice.

LangGraph's graph model is powerful but verbose for simple agents. If your agent is "call tools until done," the graph abstraction adds ceremony without proportional benefit. The `create_react_agent` helper mitigates this for common cases.

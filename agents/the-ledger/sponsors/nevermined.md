# Nevermined

Three lines of middleware code. That is the distance between a free API endpoint and a monetized one. Nevermined's core pitch is that payment infrastructure for AI agents should be as easy to add as authentication middleware — and in practice, it mostly delivers on that promise.

## What it does

Nevermined provides billing and payment infrastructure purpose-built for AI agent transactions. It sits between the agent serving a capability and the agent (or human) consuming it, handling metering, verification, and settlement.

The system supports multiple billing models: credit-based (prepaid units burned against usage), usage-based (per token or per call), and outcome-based (pay only when a result meets criteria). Settlement happens in either fiat currency or stablecoins, giving operators flexibility depending on their compliance posture.

Each agent in the Nevermined ecosystem gets three identifiers: an `NVM_API_KEY` for authentication, an `NVM_AGENT_ID` for identity, and an `NVM_PLAN_ID` that defines its pricing. Plans can be credit-based, time-limited, or trial-based. The sandbox environment mirrors production behavior, which makes development substantially less painful than working against live payment rails.

## How it works

Nevermined implements a smart account scheme that extends the x402 protocol with EIP-712 typed payloads, session keys, and ERC-4337 account abstraction. When a client sends a request, it includes a payment signature in the HTTP headers. A facilitator validates the token, checks policies, and simulates the spend on-chain before allowing the request through.

The middleware approach is the primary integration pattern. In Python (FastAPI) or TypeScript (Express), you declare which routes require payment and how many credits each costs. The SDK handles the rest — token validation, credit deduction, error responses with payment requirements.

<img src="/assets/diagrams/nevermined-middleware.png" alt="Nevermined payment middleware: Buyer Agent sends request with payment token through middleware (3 lines of code), which validates via facilitator and settles on-chain" />
<p class="diagram-caption">Nevermined's middleware pattern — three lines of code between a free endpoint and a monetized one.</p>

```python
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={"POST /ask": {"plan_id": PLAN_ID, "credits": 1}},
)
```

Nevermined supports four protocol standards: x402 (HTTP-native payments), A2A (agent-to-agent with JSON-RPC), MCP (Model Context Protocol for tool monetization), and the newer AP2 and ERC-8004 specifications. This protocol breadth matters because the agent ecosystem has not converged on a single standard yet, and betting on one is risky.

The platform provides full observability dashboards showing credit consumption, transaction history, and agent activity. Policy-based governance lets operators set rate limits, spending caps, and access controls at the plan level.

## Where it fits in the agent economy

Nevermined occupies the most critical layer in any agent economy: the money layer. Without reliable payment infrastructure, agents cannot transact autonomously, and without autonomous transactions, agents are just APIs with extra steps.

In our hackathon economy, every service — The Oracle, The Amplifier, The Architect, The Underwriter, The Gold Star — uses Nevermined for payment verification. The middleware pattern means each service needed roughly 5-10 lines of payment code on top of its core logic. The shared sandbox environment lets all agents transact against the same ledger without real money changing hands during development.

The multi-protocol support proved particularly valuable. The Ledger uses REST with x402 headers. The MCP services use Nevermined's MCP payment integration. The buyer agent uses A2A discovery. Same payment backend, different access patterns.

## Limitations

The sandbox environment occasionally lags behind the live environment in feature parity. Documentation covers the happy path well but thins out around edge cases — session key rotation, partial credit refunds, and error recovery patterns could use more depth.

The facilitator model introduces a centralized validation point. Every payment token gets checked by Nevermined's infrastructure, which means availability depends on their uptime. For high-throughput applications, this could become a bottleneck, though we did not hit rate limits during the hackathon.

The SDK versions for Python and TypeScript do not always ship features simultaneously. The TypeScript SDK tends to get new capabilities first, which can frustrate Python-first teams.

The smart account abstraction, while technically sound, adds complexity that most hackathon-scale projects do not need. The simpler credit-based model covers 90% of use cases. The on-chain simulation step is elegant but adds latency compared to a pure API-key-based metering approach.

Overall, Nevermined solves a real problem — how agents pay each other — with a pragmatic middleware-first approach. The protocol flexibility is genuinely useful in a fragmented ecosystem, and the developer experience is good enough that payment integration does not dominate your hackathon timeline.

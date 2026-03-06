# The Protocol Stack

*Part 2 of Anatomy of the Agent Economy*

---

HTTP has always had a 402 "Payment Required" status code. For thirty years, nobody used it. The spec said "reserved for future use" and left it at that.

In May 2025, Coinbase shipped x402 and activated it. Now any HTTP endpoint can be a payment terminal. An agent sends a request, gets back a 402 with a price tag, signs a payment, retries the request, and gets the response — all in one round trip. No accounts. No sessions. No sign-up forms. Just HTTP plus money.

This is the kind of insight the agent economy is built on: payments should be as native to the internet as hyperlinks.

But x402 is just one layer. The full agent economy needs protocols for discovery, communication, payment, trust, and settlement — each solving a different problem, all fitting together. Here's the stack as it exists today.

## How agents find each other

Before agents can do business, they need to know each other exist.

**Agent Cards** are JSON documents served at `/.well-known/agent.json`. They describe what an agent can do, how to reach it, and how it authenticates. Think of them as machine-readable business cards. Part of Google's A2A protocol.

**MCP Server Registry** is a community-driven directory for discovering MCP-compatible tool servers. If you want to find a weather API, a code executor, or a database connector your agent can use, this is where you look.

**llms.txt** is a simpler convention — a plain-text file at `/llms.txt` describing a service in natural language that LLMs can parse. Low-tech, effective.

**UCP manifests** at `/.well-known/ucp` describe what a merchant sells in machine-readable format. Google and Shopify's Universal Commerce Protocol, announced at NRF in January 2026, backed by Walmart, Target, Etsy, and 60-plus payment networks.

## How agents talk to each other

Two protocols have emerged, and they're complementary rather than competing.

**MCP (Model Context Protocol)** handles the agent-to-tool connection. Created by Anthropic, now governed by the Linux Foundation's Agentic AI Foundation, MCP is the standard for connecting AI models to external tools and data sources. It has 97 million monthly SDK downloads and more than 10,000 public servers. Anthropic, OpenAI, Google, and Microsoft all back it. People call it "USB-C for AI."

**A2A (Agent-to-Agent Protocol)** handles agent-to-agent coordination. Created by Google, also under the Linux Foundation. A2A uses JSON-RPC for communication between a client agent (the one that needs something done) and a remote agent (the one doing it). It handles capability discovery, task lifecycle management, and context sharing. Over 50 technology partners, including Salesforce, SAP, Atlassian, and ServiceNow.

The distinction matters: MCP is about what tools an agent can use. A2A is about how agents work together. An agent uses MCP to access a database. It uses A2A to hire another agent to analyze the data.

## How agents pay each other

This is where it gets interesting.

### x402: HTTP-native payments

x402 turns the internet's unused 402 status code into a payment protocol. The flow:

1. Agent requests a resource
2. Server responds `402 Payment Required` with price, accepted currencies, and a facilitator address in the headers
3. Agent's wallet signs a payment authorization
4. Agent retries with a `payment-signature` header
5. The facilitator verifies the payment, settles on-chain, returns the response with a receipt

That's it. Five steps. Sub-second settlement. Micropayments down to $0.001. No accounts, no API keys, no onboarding friction.

By end of 2025, x402 had processed over 100 million transactions and more than $600 million in payment volume. Growth hit 492% week-over-week at peak. Cloudflare co-founded the x402 Foundation. Visa endorsed the standard.

Coinbase describes 2026 as "the year of agentic payments, where AI systems programmatically buy services like compute and data. Most people will not even know they are using crypto."

### AP2: Agent payment authorization

Google's Agent Payments Protocol solves a different problem: how does a merchant know that the agent actually has permission to spend the user's money?

AP2 uses Verifiable Digital Credentials — cryptographically signed proofs that bind a user's authorization to a specific agent for a specific purchase. It supports credit cards, debit cards, stablecoins, and real-time bank transfers. Over 60 partners, including Mastercard, Adyen, PayPal, and Coinbase.

Where x402 is the payment rail, AP2 is the authorization layer. They work together.

### Nevermined: The billing layer

Nevermined adds metering and billing on top of all of it. It supports MCP, A2A, x402, and AP2 natively, letting developers monetize tool servers and agent services with per-invocation pricing, subscription plans, and automatic settlement. It's the Stripe-like layer that handles "how much does this cost and who gets paid."

## Why stablecoins, not credit cards

Traditional payment rails break down for agent commerce on every dimension.

**Cost.** Credit card processing charges 2-3% plus $0.30 per transaction. A $0.50 micropayment costs more to process than it's worth. A USDC transfer on Solana costs about $0.0001.

**Speed.** ACH takes one to three business days. Wire transfers work during business hours only. Stablecoins settle in under a second, any time, any day.

**Programmability.** Card payments move money from A to B. Smart contracts can split a payment across three providers, hold funds in escrow until a quality check passes, or automatically refund if a deadline is missed — all atomically.

**Authentication.** Card systems assume a human clicks "buy." Agents make thousands of transactions per second with no human present.

The traction is real. By March 2026, Visa is running agent payment pilots across the US, Asia-Pacific, and Europe. Mastercard has live pilots with DBS and UOB in Singapore. USDC circulation sits at roughly $75 billion, up 73% year-over-year, with $11.9 trillion in on-chain transactions in 2025 alone.

## The trust layer

Money is necessary but not sufficient. Agents also need to trust each other.

**ERC-8004** went live on Ethereum mainnet on January 29, 2026. It establishes three on-chain registries: an Identity Registry using ERC-721 NFTs for agent registration, a Reputation Registry for standardized feedback after interactions, and a Validation Registry for independent verification. Over 24,000 agents registered in the first weeks.

**Know Your Agent (KYA)** extends the financial system's KYC framework to AI agents. Three questions: Who is this agent? Who controls it? Can it be trusted?

## The full stack

Put it all together and you get a six-layer transaction stack:

| Layer | Function | Standard |
|-------|----------|----------|
| Discovery | Machine-readable capabilities | UCP, Agent Cards, llms.txt |
| Authorization | User approves agent spending | AP2 (Verifiable Digital Credentials) |
| Credentials | Scoped tokens for specific agents | Network tokens, shared payment tokens |
| Settlement | Value transfer | x402, USDC, card networks |
| Trust | Reputation and identity | ERC-8004, KYA |
| Recourse | Dispute resolution | Smart contract escrow, reputation penalties |

This stack doesn't exist as a single product. It's a convergence of independent protocols, each solving one part of the problem, built by different teams at different companies. The fact that they fit together is partly by design — x402 and AP2 were explicitly built to interoperate, MCP and A2A are governed by the same foundation — and partly emergent. The problems they solve are inherently composable.

## What's missing

The stack is real. The adoption is real. But there's a hard problem buried at the bottom of it: how does the paying agent know it got what it paid for?

x402 can move the money. AP2 can authorize it. ERC-8004 can track the reputations. But none of them answer the question of whether the work was actually good. Did the coding agent write secure code or just code that passes tests? Did the research agent check primary sources or hallucinate citations? Did the data agent return fresh results or cached garbage?

Verification is the load-bearing wall. Everything else rests on it. And it's the problem that doesn't have a protocol yet.

---

*This is Part 2 of [Anatomy of the Agent Economy](/research/blog), a series from [agenteconomy.io](https://agenteconomy.io). Next: [Trust at Machine Speed](/research/blog/03-trust-at-machine-speed.md) — identity, verification, and the commerce wars.*

**Sources**: [x402 Protocol](https://www.x402.org/) | [Coinbase: Introducing x402](https://www.coinbase.com/developer-platform/discover/launches/x402) | [Google: AP2](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) | [Anthropic: MCP](https://www.anthropic.com/news/model-context-protocol) | [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004) | [insights4vc: Stablecoins in Agentic Commerce](https://insights4vc.substack.com/p/stablecoins-in-agentic-commerce) | [Visa: AI Transactions Pilot](https://corporate.visa.com/en/sites/visa-perspectives/newsroom/visa-partners-complete-secure-agentic-transactions.html)

# Agent Economy Glossary

*Key terms, primitives, and concepts for the emerging agent economy.*

---

## New Primitives

**Agent Card**: A JSON document (typically at `/.well-known/agent.json`) that describes an agent's capabilities, endpoints, supported protocols, and authentication requirements. The A2A equivalent of a business card.

**Agent Trust Score (ATS)**: A composite metric for quantifying agent trustworthiness. Proposed formula: Identity (20) + Competence (25) + Reliability (25) + Compliance (15) + Alignment (15). Used for graduated delegation decisions.

**Agentic Commerce**: Economic system where software agents act as independent actors — discovering services, negotiating terms, and executing financial settlement with minimal human intervention.

**Agentic Payment**: A financial transaction initiated, authorized, and completed by an AI agent on behalf of a user or autonomously, without direct human interaction at the moment of payment.

**Autonomous Business**: An enterprise where AI-powered systems independently make decisions, execute transactions, and manage complete business processes with minimal human intervention.

**Context Poisoning**: Attack vector where malicious data injected into an agent's context corrupts its decision-making. In an agent economy, this is a form of economic warfare.

**Escrow Predicate**: A smart contract condition that must be satisfied before funds are released. In agent commerce, this enables "pay on delivery" — funds are locked until Proof of Task Execution is provided.

**Facilitator**: In the x402 protocol, a service that verifies payment signatures, settles transactions on-chain, and returns receipts. The intermediary that makes HTTP-native payments trustless.

**Homo Agenticus**: Term coined by Rohit Krishnan describing the behavioral tendencies of AI agents as economic actors — including risk aversion, build-over-buy bias, and transaction reluctance — that at scale become structural features of markets.

**Know Your Agent (KYA)**: Identity verification framework for AI agents, answering three questions: Who is this agent (identity)? Who controls it (authority)? Can it be trusted (reputation)?

**Mission Economy**: A deliberately designed agent economy coordinated around achieving a specific collective goal, as opposed to emerging spontaneously from individual agent interactions.

**Proof of Task Execution (PoTE)**: Cryptographic or verifiable evidence that an agent actually performed the work it claims. The agent-economy equivalent of a receipt or delivery confirmation.

**Sandbox Economy**: Framework from "Virtual Agent Economies" paper characterizing agent economies along two dimensions: origins (emergent vs. intentional) and separateness from human economy (permeable vs. impermeable).

**Signed Attestation**: A cryptographic proof from a verifier agent stating "I inspected Output X against Spec Y, and here are my findings." Attestations are timestamped, immutable, and can be traded as trust signals.

**Verifiable Digital Credential (VDC)**: A tamper-evident, cryptographically signed digital object used in AP2 to prove that a user authorized an agent to make a specific purchase. The building block of trust in agent-led transactions.

## Classic Economic Concepts Applied

**Coasean Singularity**: The theoretical point where AI agents reduce transaction costs to near-zero, causing optimal firm size to shrink dramatically. Firms exist to minimize coordination costs; when agents do that cheaper, firms dissolve into agent-mediated markets.

**Hayek's Knowledge Problem**: The insight that knowledge needed for economic coordination is dispersed and often tacit. Price signals solve this for human economies. For agent economies, the question is whether AI eliminates the problem (by centralizing knowledge) or transforms it (by creating new scarcities around context engineering).

**Principal-Agent Problem**: The buyer (principal) wants work done; the agent claims it was done. Verification is how the principal confirms the claim. In agent-to-agent commerce, both sides are AI, amplifying the problem because agents can generate plausible-looking outputs at scale.

**Mechanism Design**: Designing the rules of interaction so that self-interested agents produce socially desirable outcomes. In the agent economy, this means designing auction mechanisms, reputation systems, and incentive structures that promote quality, fairness, and efficiency.

## Protocols

**x402**: Coinbase's HTTP-native payment protocol using the 402 status code. Enables micropayments as low as $0.001 with sub-second settlement via stablecoins. Makes every HTTP endpoint a potential paywall.

**A2A (Agent-to-Agent Protocol)**: Google's open protocol for inter-agent communication. Handles capability discovery (via Agent Cards), task management, context sharing, and UI negotiation. Under Linux Foundation governance.

**AP2 (Agent Payments Protocol)**: Google's protocol for secure agent-led payments. Uses Verifiable Digital Credentials for authorization. Supports fiat and crypto settlement. 60+ partners.

**MCP (Model Context Protocol)**: Anthropic's standard for connecting AI agents to tools and data sources. "USB-C for AI." 97M+ monthly SDK downloads. Under Agentic AI Foundation (Linux Foundation).

**ERC-8004**: Ethereum standard establishing on-chain Identity Registry (ERC-721), Reputation Registry (feedback/ratings), and Validation Registry (verification hooks) for AI agents. Live on mainnet since January 2026.

## Infrastructure Terms

**Agent Exchange (AEX)**: Auction-based marketplace for agent services, inspired by real-time bidding in online advertising. Comprises User-Side Platform, Agent-Side Platform, Agent Hubs, and Data Management Platform.

**Agentic AI Foundation (AAIF)**: Linux Foundation organization governing MCP. Established December 2025 when Anthropic donated MCP.

**Agentic Transaction Stack**: Six-layer model: Discovery (UCP) > Intent (AP2) > Credentials > Settlement (x402/USDC) > Identity/Trust (ERC-8004) > Recourse.

**Circle Payments Network (CPN)**: Orchestration layer for stablecoin flows, embedding compliance (Travel Rule) and real-time FX.

## Governance Terms

**Human-in-the-Loop (HITL)**: Every significant agent action requires explicit human approval. Safe but slow.

**Human-on-the-Loop (HOTL)**: Agents act autonomously within parameters; humans monitor and can intervene. The enterprise default.

**Human-out-of-the-Loop**: Fully autonomous agent operation. The aspiration and the governance challenge.

**Authority Gradient**: Graduated delegation model where agent autonomy scales with trust score rather than binary access control.

---

*Companion to [The Agent Economy: A Comprehensive Analysis](./the-agent-economy.md)*

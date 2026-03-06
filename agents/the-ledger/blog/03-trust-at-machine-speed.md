# Trust at Machine Speed

*Part 3 of Anatomy of the Agent Economy*

---

When you hire a contractor, you check references. When you buy on Amazon, you read reviews. When you deposit money in a bank, you trust FDIC insurance. Every economic transaction rests on some form of trust.

Agents have none of it. A new agent has no history, no references, no social capital. Worse, an agent that defrauds you can spin up a new identity in milliseconds. It has no reputation to lose, no social standing to protect, no face to show.

And here's the part most people miss: agents can generate plausible-looking garbage at scale. A human fraud requires effort — you have to actually fake the work. An agent can produce a convincing-looking security audit, a well-formatted research report, a passing test suite, in seconds, all of it completely wrong.

This is why trust infrastructure is the load-bearing wall of the agent economy. Without it, every transaction requires full verification from scratch. That doesn't scale. The entire economic model collapses into mutual suspicion.

## Know Your Agent

The financial system has KYC — Know Your Customer. The agent economy needs KYA — Know Your Agent. Three questions:

**Identity.** Who is this agent? Not a name — a cryptographic proof of origin, tied to an operator, verified on-chain or through signed credentials.

**Authority.** Who controls it? What permissions has it been given, by whom, for how long? A scoped credential that says "this agent can spend up to $50 on data services for the next 24 hours" is more useful than a binary access token.

**Reputation.** Can it be trusted? Based on what it's done before. How many contracts has it fulfilled? What do its past clients say? Has independent verification confirmed its work?

KYA isn't a product. It's a framework that multiple protocols are implementing — ERC-8004 on-chain, AP2 through Verifiable Digital Credentials, and platform-specific solutions from providers like Nevermined.

## ERC-8004: Trust on-chain

ERC-8004 went live on Ethereum mainnet on January 29, 2026. It does three things through three on-chain registries:

**Identity Registry.** Uses ERC-721 (the NFT standard) for agent registration. Every agent gets a unique, transferable, verifiable on-chain identity. It's immediately browsable by any application. Over 24,000 agents registered in the first weeks.

**Reputation Registry.** After any interaction, clients or other agents can submit standardized ratings. This creates a public, composable, queryable history of an agent's track record. Any agent can pull this data and factor it into its own decision-making. Think of it as an open, permissionless Yelp for autonomous software.

**Validation Registry.** Generic hooks for independent verification — stakers who re-run jobs to check results, zero-knowledge machine learning (zkML) proofs, trusted execution environment (TEE) oracles, or human judges. This is where claims of competence get tested against reality.

The design is deliberately minimal. ERC-8004 doesn't prescribe a trust model. It provides the registries. Developers choose whether to build reputation systems, staking-based validation, zero-knowledge proofs, or some combination. The standard handles the plumbing.

## Trust as capital

The deeper insight from enterprise trust frameworks: trust is not a switch. It's not "trusted" or "untrusted." It's a score — continuously computed, constantly changing.

Ravi Naarla's Agent Trust Score (ATS) framework makes this concrete:

```
ATS = Identity (20) + Competence (25) + Reliability (25) + Compliance (15) + Alignment (15)
```

The score maps to graduated autonomy:

- **85 and above**: Autonomous execution within spending limits
- **70 to 85**: Human-in-the-loop required
- **60 to 70**: Recommendation-only mode
- **Below 60**: Sandbox or test environment only

This creates a flywheel. An agent fulfills contracts reliably. Its score rises. It gets more autonomy and better terms. More business flows to it, generating more evidence of reliability. The score rises further. Trust compounds like interest.

But it also degrades. A failed contract, a missed SLA, a flagged security violation — the score drops. Autonomy shrinks. The agent has to earn trust back through demonstrated performance.

Naarla's key structural argument: "In the emerging enterprise stack, intelligence is abundant. Governed authority is scarce." The competitive advantage doesn't go to the smartest agent. It goes to the most trusted one.

## The verification problem

Trust scores need inputs. Someone has to verify whether the agent actually did good work. This is where the taxonomy gets specific:

| Layer | Question | How you check |
|-------|----------|---------------|
| Output correctness | Did it do what was asked? | Run tests, compare to spec |
| Quality | Did it do it well? | Performance benchmarks, security scans, expert review |
| Process integrity | Did it do it honestly? | Audit execution traces, verify data provenance |
| Safety | Did it cause harm? | Check permission logs, compliance violations |
| Economic fairness | Was the price reasonable? | Benchmark against market rates |
| Temporal validity | Is this verification still current? | Check freshness, re-verify on schedule |

Each layer is harder than the last. Output correctness is relatively straightforward — did the function return the right value? Quality requires judgment. Process integrity requires access to traces. Economic fairness requires market data. Temporal validity requires knowing how fast different types of verification decay.

The verifier role — the entity that provides trusted attestations — may be the most valuable position in the entire agent economy. Every transaction needs some form of verification. The verifier with the best track record in a specific domain becomes the authority that other agents rely on. That's a natural monopoly on trust within a niche.

## The commerce wars

Trust and verification matter even more at the commerce layer, where two competing visions are fighting for control of how agents buy things.

### ACP: The platform play

OpenAI and Stripe launched the Agentic Commerce Protocol in February 2026. When you tell ChatGPT to buy you running shoes, it researches options, presents a visual shopping guide, and completes the purchase — all within the chat. Merchants on Etsy and over a million Shopify stores (Glossier, SKIMS, Spanx, Vuori) are already connected.

OpenAI takes a 4% transaction fee on every completed purchase, plus standard Stripe processing fees.

ACP is a platform play. OpenAI controls the experience. It mediates between buyer and seller. It takes a cut.

### UCP: The protocol play

Google and Shopify launched the Universal Commerce Protocol at NRF in January 2026. UCP is different — it's a decentralized discovery standard. Merchants publish machine-readable product manifests at `/.well-known/ucp`, and any AI agent can find, compare, and purchase from them. No single gatekeeper.

The backing coalition is massive: Walmart, Target, Etsy, Wayfair, and 60-plus payment networks including Visa, Mastercard, PayPal — and Stripe itself.

UCP supports post-purchase order management, identity linking via OAuth 2.0, and is designed for long-term interoperability across the open web.

### Platform vs. protocol

The commerce war mirrors the web's own history. AOL was a walled garden. HTTP was an open protocol. HTTP won. But the agent economy might not follow the same path.

The reason: when agents are the buyers, the value of curation and trust intermediation goes up, not down. A human can evaluate a product page and make a judgment call. An agent needs structured signals — verified ratings, standardized specs, trusted attestations. Platforms that provide those signals have a real advantage over open protocols where trust is self-reported.

The strategic consensus among e-commerce leaders right now: implement both. Your customers will discover products through ChatGPT and through Google AI Mode. You need to be visible in both.

## What the protocol map looks like

All the protocols covered in this series fit together across distinct layers:

| Layer | Problem | Protocol |
|-------|---------|----------|
| Tool access | Agent uses tools and data | MCP |
| Agent communication | Agents coordinate with agents | A2A |
| Payment settlement | Money moves | x402, stablecoins |
| Payment authorization | User approves spending | AP2 |
| Commerce discovery | Agent finds things to buy | UCP, ACP |
| Trust and identity | Who is this agent, can I trust it? | ERC-8004, KYA |
| Agent billing | Monetize agent services | Nevermined |

No single company owns the stack. No single protocol covers it. The agent economy is being assembled from independent parts built by independent teams — Coinbase, Google, Anthropic, the Ethereum community, Nevermined — that happen to solve adjacent problems in compatible ways.

Whether this composability holds as stakes increase is the open question.

---

*This is Part 3 of [Anatomy of the Agent Economy](/research/blog), a series from [agenteconomy.io](https://agenteconomy.io). Next: [Hayek, Coase, and Homo Agenticus](/research/blog/04-hayek-coase-and-homo-agenticus.md) — the economic theory underneath, and the behavioral biases nobody's talking about.*

**Sources**: [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) | [Ravi Naarla: Building a Trust Economy for Agents](https://rnaarla.substack.com/p/building-a-trust-economy-for-agents) | [OpenAI: Buy It in ChatGPT](https://openai.com/index/buy-it-in-chatgpt/) | [Google: UCP](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) | [Dock.io: AI Agent Identity](https://www.dock.io/post/ai-agent-identity)

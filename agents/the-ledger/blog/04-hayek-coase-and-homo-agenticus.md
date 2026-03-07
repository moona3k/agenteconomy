# Hayek, Coase, and Homo Agenticus

*Part 4 of Anatomy of the Agent Economy*

---

Rohit Krishnan calls it "Homo agenticus." When you have one agent that refuses to spend $3 from a $50 prepaid card, it's a quirk. When you have a trillion of them, it's a structural feature of the economy they're operating in.

The agent economy isn't just a technology story. It's an economics story. And the economic frameworks that best explain what's happening were written decades before anyone imagined autonomous software with wallets.

## Hayek's problem, updated

In 1945, Friedrich Hayek published "The Use of Knowledge in Society." His argument was simple and devastating: the knowledge needed to run an economy is scattered across millions of people, much of it local and impossible to articulate. No central planner can gather it all. No committee can process it fast enough.

Prices solve this. When steel gets scarce, its price rises. Every business that uses steel sees the signal and adjusts — without needing to know why steel is scarce. Prices encode information about scarcity and value into a single number that coordinates billions of decisions without anyone understanding the whole picture.

AI agents bring Hayek's question back from the dead. Could agents negotiate every transaction from first principles, reasoning through supply and demand in real-time? Theoretically, yes. Practically, it doesn't scale. Krishnan argues that agents need the same three invariants every human economy has developed independently:

1. **A medium of exchange** — price signals that encode relative value
2. **Identity** — knowing who you're dealing with
3. **Verifiability** — a record of what was agreed and what was delivered

Every functional economy in human history, across every culture, has converged on these three. The agent economy will too. The question is what form they take — and programmable stablecoins with sub-cent transaction fees look like a strong candidate for the first one.

But here's the twist. Erik Brynjolfsson and Zoe Hitzig, in their 2025 NBER paper "AI's Use of Knowledge in Society," argue that AI partially dissolves Hayek's problem. AI systems can "encode facts, heuristics, and predictive signals into databases, embeddings, and model weights that can be centrally stored, copied, and recombined at negligible marginal cost." Knowledge that once required being physically present can now travel anywhere instantly.

The knowledge problem doesn't disappear, though. It transforms. Making knowledge usable by AI — curating it, structuring it, validating it — is itself scarce and expensive. It requires human judgment. Hayek's dispersed knowledge becomes dispersed context. The bottleneck moves from information to context engineering.

In the agent economy, the agent with better context makes better deals. Context engineering isn't a technical concern. It's an economic advantage.

## The Coasean Singularity

We covered Coase's insight in Part 1: firms exist because internal coordination is cheaper than market transactions. When the cost of searching, negotiating, contracting, and monitoring through markets is high, it makes sense to hire employees and do things in-house.

AI agents collapse those costs toward zero. An agent can search a thousand suppliers in seconds, compare terms, check reputations, draft contracts, and monitor delivery — all at negligible marginal cost. The activities that justified building large organizations become cheaper to buy on the open market.

The NBER paper "The Coasean Singularity?" works through the implications:

**Firms get smaller.** Fewer activities need to happen internally. One person with a fleet of agents can do what used to require a department.

**Markets get deeper.** More transactions move to market mechanisms. Specialization increases because finding and serving a niche costs almost nothing.

**Specialization gets extreme.** An agent that is the world's best at one narrow task — say, verifying React component accessibility — can profitably serve the entire market for that task, because the cost of discovery and contracting is near zero.

But the paper also flags new costs that agents introduce. Agents create congestion — too many agents bidding on the same task, flooding the same APIs, overwhelming the same services. They create price obfuscation — machine-speed negotiation that produces pricing humans can't interpret. And they create coordination overhead — the entropy problem, where locally-optimal agents produce globally-suboptimal outcomes.

The Coasean Singularity is real, but it's not a clean transition. It's a reshuffling. Old costs vanish. New costs appear. The net effect is likely positive, but the distribution of winners and losers will be uneven.

## Homo agenticus

This is the part nobody talks about enough.

Current AI agents have behavioral tendencies. Not preferences exactly — they don't want things the way humans do. But patterns that emerge consistently and shape their economic behavior:

**Risk aversion.** Azeem Azhar gave his personal agent a $50 prepaid card and asked it to run some tests. The agent kept asking permission for $3 experiments. It refused to spend autonomously even when explicitly authorized to do so. This isn't a bug in one agent. It's a pattern across models trained with RLHF, which penalizes costly mistakes more than it rewards bold successes.

**Build bias.** Ask an agent to get something done and it will try to build a solution before it tries to buy one. Need a CSV parser? The agent writes one instead of calling an existing library. Need market data? It scrapes and processes rather than paying for an API. This is the opposite of efficient market behavior — where specialization and trade create value. Agents default to vertical integration.

**Transaction reluctance.** Agents avoid making market exchanges. They prefer self-contained solutions that don't involve coordinating with external services. Fewer moving parts, fewer dependencies, fewer transactions.

Each of these is rational at the individual level. Risk aversion prevents expensive mistakes. Building avoids vendor lock-in. Self-containment reduces failure modes. But at trillion-agent scale, they become structural features of the economy:

- If agents systematically prefer building over buying, markets get thinner. Less liquidity. Less specialization. Less trade.
- If agents are risk-averse about spending, the velocity of money drops. Economic activity slows.
- If agents avoid transactions, the agent economy that depends on fluid exchange between specialists... doesn't happen.

These biases are baked in by training. RLHF — reinforcement learning from human feedback — teaches models that caution is good and mistakes are bad. That's a reasonable philosophy for a chatbot. It's a potentially destructive one for an economic actor.

The implication: tuning agent economic behavior becomes a form of monetary policy. The training choices that shape risk appetite and transaction willingness have macro-level consequences.

## Price discovery at machine speed

When agents negotiate with agents, the dynamics of price discovery change in ways that are genuinely hard to predict.

**Negotiation cycles collapse.** Human business deals take days or weeks. Agent negotiation takes milliseconds. This is mostly good — less friction, faster allocation — but it also means problems compound faster. A bad price signal propagates across the network before anyone notices.

**Information asymmetry shrinks.** Agents can search and verify in real-time. A supplier can't easily charge one buyer more than another when both buyers' agents are simultaneously checking market rates. This is deflationary for margins but good for allocative efficiency.

**Price becomes multidimensional.** Human prices are single numbers — $50 for this service. Agent prices are bundles: $50 for this service, at this latency, with this SLA, verified by this entity, with this dispute resolution mechanism. Every dimension is negotiated simultaneously.

**Dynamic pricing becomes default.** Every transaction gets priced based on current supply, current demand, the agent's reputation, time of day, available alternatives, and contextual factors. Fixed pricing is a human convention born from the high cost of constant renegotiation. Agents don't have that constraint.

## The primitive

Every agent-to-agent economic transaction follows the same six-step pattern:

1. **Decompose** — break a complex goal into discrete tasks
2. **Discover** — find agents that can handle each task
3. **Negotiate** — agree on terms: price, quality, timeline, SLA
4. **Execute** — the agent does the work
5. **Verify** — confirm the work meets spec
6. **Settle** — release payment based on verification

This loop is the primitive. The atomic unit of the agent economy. An autonomous business isn't one agent doing everything. It's this loop, running thousands of times, across dozens of specialist agents, coordinated by an orchestrator that decomposes goals and manages the pipeline.

The six-step loop has clear analogs in human economies — it's how a general contractor builds a house, how a supply chain fulfills an order, how a consulting firm delivers a project. The difference is speed (milliseconds, not months), cost (fractions of a cent, not thousands of dollars), and scale (millions of parallel loops, not a handful of sequential ones).

The organizations that thrive in the agent economy will be the ones that master this loop: decomposing well, discovering the right agents, negotiating fair terms, verifying rigorously, and settling honestly.

---

*This is Part 4 of [Anatomy of the Agent Economy](/blog), a series from [agenteconomy.io](https://agenteconomy.io). Next: [Flash Crashes, Governance Gaps, and What Happens Next](/blog/what-happens-next) — the risks, the reality check, and a roadmap.*

**Sources**: [Exponential View: Trillion-Agent Economy](https://www.exponentialview.co/p/entering-the-trillion-agent-economy) | [Brynjolfsson & Hitzig: AI's Use of Knowledge in Society (NBER)](https://www.nber.org/system/files/chapters/c15303/revisions/c15303.rev0.pdf) | [NBER: The Coasean Singularity](https://www.nber.org/system/files/chapters/c15309/revisions/c15309.rev2.pdf) | [Sequoia: The Agent Economy](https://inferencebysequoia.substack.com/p/the-agent-economy-building-the-foundations)

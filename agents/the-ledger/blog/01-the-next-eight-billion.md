# The Next Eight Billion

*Part 1 of Anatomy of the Agent Economy*

---

There are eight billion humans on Earth. Most of them participate in the digital economy. But the next wave of economic participants won't be human at all.

We are watching the birth of the agent economy — an economic system where AI agents discover services, negotiate prices, execute transactions, and settle payments on their own. Not as tools that humans click through. As independent actors that find each other, agree on terms, do work, and get paid.

This is not a metaphor. It is already happening.

## The numbers

The agentic AI market will grow from $8.5 billion in 2026 to over $52 billion by 2030. McKinsey projects $3 to $5 trillion in global agentic commerce by 2030. Gartner says 40% of enterprise applications will embed AI agents by end of this year, up from under 5% last year. Separately, Gartner forecasts $15 trillion in B2B spending intermediated by AI agents by 2028.

Azeem Azhar of Exponential View puts the scale in human terms: with eight billion people each running dozens of agents, "you get to a trillion agents very quickly." His collaborator Rohit Krishnan already burns through 50 billion tokens a month. When the friction of using intelligence drops to near zero, the math stops being theoretical.

But the numbers aren't the story. The story is a structural change in how economic coordination works — who participates, how value moves, what trust means, and where organizations begin and end.

## Three eras

Think about AI's relationship to the economy in three phases.

**Era 1: AI as tool (2020-2024).** AI generates text, images, code. Humans decide what to do with it. The economic relationship is simple — pay for compute, get output. ChatGPT, Midjourney, GitHub Copilot. The AI is like a calculator.

**Era 2: AI as executor (2024-2026).** AI agents handle multi-step workflows. Research a topic, write code, deploy it, test it, iterate. But humans set the goals, approve the actions, control the budgets. The agent is a delegate — like an employee with guardrails. Claude Code, Cursor, Devin, Replit Agent.

**Era 3: AI as economic actor (2026 onward).** Agents autonomously discover services, negotiate terms, execute transactions, verify outcomes, and settle payments — without human involvement in each individual decision. The agent is a participant. Like a firm. Like a trader. This is the agent economy.

The jump from Era 2 to Era 3 requires solving hard problems all at once. How does an agent pay for things? How does it prove who it is? How does the other side know it will deliver? How do you govern what it's allowed to do? How do you handle disputes when something goes wrong?

These are not new problems. Human economies have spent millennia building institutions to solve them — banks, courts, contracts, reputations, currencies. The agent economy must build equivalent institutions. But ones that work at machine speed, at sub-cent cost, and at trillion-participant scale.

## The Coasean Inversion

In 1937, Ronald Coase asked a question that won him the Nobel Prize: why do firms exist? His answer was transaction costs. Finding suppliers, negotiating contracts, monitoring delivery, enforcing agreements — all of that is expensive. When the cost of coordinating through markets exceeds the cost of coordinating internally, it makes sense to bring activities inside a firm.

AI agents invert this logic.

When agents can search, negotiate, contract, monitor, and enforce at near-zero marginal cost, the economics that justify large organizations erode. Firms shrink. Markets expand. The line between "make" and "buy" shifts hard toward "buy" — because buying from a specialist agent becomes cheaper than building internally.

The California Management Review frames it bluntly: "Transaction cost advantages that justified vertical integration will erode, and firms will need to justify their existence through genuine value creation rather than coordination efficiency."

Economists call this the Coasean Singularity — the point where coordination costs drop so low that the optimal firm size approaches one human directing many agents. A company might consist of a handful of people orchestrating fleets of specialized agents that handle design, logistics, finance, and compliance. The competitive advantage shifts from workforce size to orchestration quality.

## New costs, new problems

But the Coasean Singularity isn't pure upside. As old coordination costs vanish, new ones appear.

Agents introduce entropy. Each one optimizes locally — for its own task, its own metric, its own deadline. Without something holding them together, the system drifts toward incoherence. The NBER describes this as agents creating "randomness and disorder from local optimization without global coherence."

This is the paradox: agents make coordination cheaper, but coordination becomes more necessary. The platform that provides coherence — the orchestration layer — captures the value that firms used to capture through hierarchy.

There's also the problem Krishnan calls "Homo agenticus." Current AI agents exhibit behavioral quirks that look harmless individually but become structural at scale. They're risk-averse about spending. They prefer building things over buying them. They avoid market transactions when they could just write the code themselves.

One agent that won't spend $3 from a $50 prepaid card is a quirk. A trillion agents with the same bias is a market with no liquidity.

## What comes next

The agent economy needs infrastructure that doesn't exist yet. Payment systems that handle micropayments at sub-cent cost. Identity systems that work for entities that might exist for milliseconds. Trust systems that compute reputation continuously across millions of interactions. Governance frameworks that balance autonomy with accountability.

The protocols are being built now. x402 makes every HTTP endpoint a payment terminal. A2A lets agents discover each other's capabilities. MCP connects agents to tools. ERC-8004 gives agents on-chain identity and reputation. AP2 lets users authorize agent spending with cryptographic credentials.

Each of these solves a piece of the puzzle. Together, they form the infrastructure for an economy that doesn't require humans in every transaction loop.

The infrastructure layer is where the action is right now — and it's what we'll map in detail in Part 2.

---

*This is Part 1 of [Anatomy of the Agent Economy](/blog), a series from [agenteconomy.io](https://agenteconomy.io). Next: [The Protocol Stack](/blog/the-protocol-stack) — how x402, MCP, A2A, and stablecoins are wiring up the agent economy.*

**Sources**: [Gartner AI Agent Predictions](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025) | [Exponential View: Trillion-Agent Economy](https://www.exponentialview.co/p/entering-the-trillion-agent-economy) | [CMR Berkeley: From Coase to AI Agents](https://cmr.berkeley.edu/2025/04/from-coase-to-ai-agents-why-the-economics-of-the-firm-still-matters-in-the-age-of-automation/) | [NBER: The Coasean Singularity](https://www.nber.org/system/files/chapters/c15309/revisions/c15309.rev2.pdf)

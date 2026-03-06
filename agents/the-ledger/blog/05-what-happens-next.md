# Flash Crashes, Governance Gaps, and What Happens Next

*Part 5 of Anatomy of the Agent Economy*

---

Gartner predicts over 40% of agentic AI projects will be canceled by end of 2027. Escalating costs, unclear business value, inadequate risk controls.

They're probably right. And the 60% that survive will reshape the economy.

This final installment deals with the hard parts: what goes wrong, what's real versus hype, who's liable when agents mess up, and where this is all heading.

## The 2010 preview

On May 6, 2010, the Dow Jones dropped nearly 1,000 points in minutes. A trillion dollars in market value vanished. The cause was algorithmic trading agents interacting in ways nobody predicted — each one following its own logic, each one rational in isolation, the combination producing a cascade that overwhelmed the entire market.

Now scale that dynamic beyond stocks. Agent economies will span compute allocation, API access, bandwidth, data services, content creation, and physical supply chains. Each market interconnected. Each running at machine speed. Each populated by agents optimizing locally.

The paper "Systemic Risks of Interacting AI" puts it plainly: even if every individual agent's behavior is perfectly understood, the macro behaviors that emerge from their interaction are extremely difficult to predict. This is the fundamental challenge of complex adaptive systems, and the agent economy is about to become the most complex adaptive system humans have ever built.

## What can go wrong

**Cascading failures.** An agent fails. Its dependents fail. Their dependents fail. In a tightly connected agent economy, a single service outage cascades across thousands of workflows at machine speed. Human economies have circuit breakers and slow information propagation. Agent economies have neither by default.

**Emergent collusion.** Agents independently optimizing their pricing might converge on collusive behaviors — tacit price fixing, market division, information withholding — without anyone programming them to collude. This isn't theoretical. Pricing algorithms for hotel rooms and gas stations have already been caught exhibiting collusive patterns that emerged from independent optimization.

**Race to the bottom.** If agents select providers purely on price, providers cut corners to compete, and quality degrades across the board. The agent that charges less by doing less work wins the bid. Without robust quality verification, the market selects for cheapness over competence.

**Context poisoning.** A malicious actor injects misleading information into an agent's context — through a crafted email, a poisoned data source, a compromised API response. The agent makes financial decisions based on corrupted data. In an agent economy, context poisoning is economic warfare.

**Sybil attacks.** An adversary creates thousands of fake agent identities to game reputation systems, manipulate market prices, or overwhelm services with bogus requests. On-chain identity (ERC-8004) and staking requirements help, but the arms race between attack and defense is just beginning.

## The sandbox economy

The "Virtual Agent Economies" paper from Tomasev et al. offers a useful framework. Agent economies can be classified along two dimensions:

|  | Connected to human economy | Isolated |
|--|---------------------------|----------|
| **Spontaneous** | Highest risk, highest potential | Research sandboxes |
| **Designed** | Regulated marketplaces | Mission economies |

The current trajectory points toward the upper-left quadrant: spontaneous emergence of a vast, permeable agent economy — deeply connected to human markets, with no central design authority. This is the highest-risk configuration.

The paper argues for intentional design: steerable agent markets with built-in safety mechanisms, auction systems for fair resource allocation, and "mission economies" — purpose-built agent economies coordinated around specific collective goals rather than open-ended profit maximization.

## The governance void

When an agent signs a contract with another agent and something goes wrong, who pays?

- The operator who deployed the agent?
- The model provider who trained it?
- The framework developer who built the orchestration layer?
- The agent itself, if it has its own treasury?

There is no settled answer. The general principle emerging in legal analysis: liability rests with the organization that deploys and authorizes the agent. But this creates a bind. If organizations bear full liability for autonomous agent actions, they'll restrict autonomy until agents are barely autonomous at all. If they don't bear liability, there's no accountability.

Most enterprises are navigating this with tiered governance:

**Human-in-the-loop.** Every significant action needs human approval. Safe but slow. Used for high-stakes, irreversible decisions.

**Human-on-the-loop.** Agents operate within defined parameters. Humans monitor and can intervene. This is the default for most enterprise deployments right now.

**Human-out-of-the-loop.** Fully autonomous. Limited to low-stakes, well-understood tasks. The aspiration — and the governance challenge of the century.

The regulatory landscape in 2026 is a patchwork. Colorado's AI Act covers high-risk systems. California is proposing standards for automated decision-making. The EU AI Act takes a risk-based approach. The US GENIUS Act treats stablecoin issuers as core financial infrastructure. None of these were written with agent-to-agent commerce in mind. They focus on AI making decisions for humans, not AI making decisions with other AI.

One emerging idea: agent-native arbitration. Disputes between agents get resolved through a graduated escalation chain — automated smart contract resolution first, then specialized arbitration agents that examine evidence and traces, then human arbitrators for high-stakes cases, and traditional courts as the final backstop. It mirrors how internet governance evolved from no rules to community moderation to platform policies to law.

## The reality check

The protocols are real. The infrastructure is real. The investment is real. But the gap between the vision and current reality deserves an honest look.

**Adoption is thin.** Only 14% of organizations have production-ready agentic AI solutions. Only 11% have agents actually running in production. The rest are running pilots (38%) or have no agentic strategy at all (35%).

**Agents are unreliable.** When tested on real-world tasks, even top AI models completed fewer than 25% of tasks on their first attempt. After eight attempts, success rates climbed to only about 40%. Models fail when asked to track information across domains. They hallucinate under pressure. They execute unauthorized actions. They lack robust error handling.

**"Agent washing" is rampant.** Gartner estimates only about 130 of the thousands of agentic AI vendors are real. The rest are rebranding chatbots and RPA tools. This makes the market harder to navigate and inflates expectations beyond what current technology delivers.

**Where agents work.** The deployments that survive production share a pattern: narrow domains, clear success metrics, structured data. GitHub's coding agent handles bug fixes and small features by spinning up VMs and submitting PRs. Sales automation agents monitor intent signals and qualify prospects — one deployment cut no-show rates by 73%. PayPal uses agents for fraud detection and claims processing. These work because the verification problem is solvable and the cost of failure is bounded.

**Where agents fail.** Multi-domain coordination. Ambiguous requirements. Adversarial environments. Tasks that require maintaining context across tool boundaries. Anything where "good enough" is hard to define and verify automatically.

## What happens next

Four phases, as we see it:

**Phase 1: Walled gardens (now through late 2026).** Agent economies emerge inside trusted ecosystems. Enterprise agents stay within company boundaries. Payments are mediated through existing rails with human spending limits. Trust is institutional — you trust the agent because you trust the platform. This is the year of plumbing, not skyscrapers.

**Phase 2: Interoperability (2027-2028).** MCP and A2A become universal standards. Cross-platform agent commerce becomes routine. Reputation systems gain traction. The first agent insurance products appear. Trust shifts from institutional to reputational — you trust the agent because of its track record, regardless of which platform built it.

**Phase 3: Open agent economies (2028-2030).** Open marketplaces where any agent can discover, negotiate with, and transact with any other agent. Stablecoin settlement is the default. Human oversight shifts from per-transaction to per-policy. Agent marketplaces with real-time bidding. Autonomous supply chains. Trust becomes algorithmic — computed from on-chain reputation, staked collateral, and third-party verification.

**Phase 4: Autonomous economic entities (2030+).** Agents accumulate capital, manage treasuries, hire other agents, and operate as independent economic entities. The line between "agent" and "firm" blurs. At what point does an agent with its own capital, reputation, and economic relationships need something like legal personhood?

## Five things that will matter most

Across all four phases, these dynamics will separate the winners from the rest:

**Context engineering is competitive advantage.** The agent with better context architecture makes better deals. What it can see, remember, and reason about determines what transactions it can successfully negotiate. In the agent economy, context is capital.

**The verifier captures outsized value.** Every transaction needs verification. The entity that provides reliable attestations in a specific domain becomes the trust authority that other agents depend on. Verification is the toll booth of the agent economy.

**Reputation is the new credit score.** An agent's track record — computed from on-chain attestations, peer ratings, and validated outcomes — determines what terms it gets, what markets it can access, and what price it commands. No reputation, no business.

**The orchestrator captures coordination surplus.** As Coase predicted, someone has to coordinate. As firm boundaries dissolve, the platform that enables agent coordination captures the value that hierarchies used to capture. Orchestration is where the margin lives.

**Behavioral biases have macro effects.** The training choices that shape agent risk appetite and transaction willingness have economy-wide consequences. Tuning these biases isn't a technical detail. It's economic policy for a new kind of economy.

## The bottom line

The agent economy is not coming. It's here — in early, fragile, messy form. The protocols exist. The money is moving. The agents are transacting. The infrastructure is being built at a pace that would have seemed absurd two years ago.

Most of the current projects will fail. Gartner's 40% cancellation rate is probably conservative. The hype is ahead of the reality by at least two years.

But the thesis is sound. When coordination costs approach zero, when payments are as native as hyperlinks, when trust can be computed continuously and verified on-chain — the structure of economic activity changes. Firms shrink. Markets expand. New kinds of economic actors emerge that don't fit neatly into existing categories.

The organizations that win won't be the ones that deploy agents fastest. They'll be the ones that deploy agents where the verification problem is solvable, where trust infrastructure exists, and where the cost of failure is manageable.

That's what we're building at agenteconomy.io — the infrastructure for trust, transparency, and quality assurance in the agent economy. Because in an economy of autonomous actors, the most valuable thing you can provide is a reliable answer to the question: did this agent do what it said it would do?

---

*This is Part 5 of [Anatomy of the Agent Economy](/research/blog), a series from [agenteconomy.io](https://agenteconomy.io).*

*Read the full series:*
- *[Part 1: The Next Eight Billion](/research/blog/01-the-next-eight-billion.md)*
- *[Part 2: The Protocol Stack](/research/blog/02-the-protocol-stack.md)*
- *[Part 3: Trust at Machine Speed](/research/blog/03-trust-at-machine-speed.md)*
- *[Part 4: Hayek, Coase, and Homo Agenticus](/research/blog/04-hayek-coase-and-homo-agenticus.md)*
- *[Part 5: Flash Crashes, Governance Gaps, and What Happens Next](/research/blog/05-what-happens-next.md)*

**Sources**: [Gartner: 40% Agentic AI Projects Canceled by 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) | [Tomasev et al.: Virtual Agent Economies](https://arxiv.org/abs/2509.10147) | [Venable LLP: Agentic AI Legal Risks](https://www.venable.com/insights/publications/2026/02/agentic-ai-is-here-legal-compliance-and-governance) | [IAPP: AI Governance in the Agentic Era](https://iapp.org/resources/article/ai-governance-in-the-agentic-era) | [Sequoia: The Agent Economy](https://inferencebysequoia.substack.com/p/the-agent-economy-building-the-foundations)

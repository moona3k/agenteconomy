"""Portfolio manager — tracks budget, ROI, and provider switching."""
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Transaction:
    timestamp: float
    seller_name: str
    team_name: str
    service_category: str
    plan_id: str
    tool_name: str
    query: str
    credits_used: int
    quality_score: float  # 0-10
    response_length: int
    latency_ms: float
    success: bool

    @property
    def roi(self) -> float:
        """ROI = quality / cost. Higher is better."""
        if self.credits_used == 0:
            return float('inf') if self.success else 0
        return (self.quality_score * 100) / self.credits_used


@dataclass
class ProviderProfile:
    name: str
    team: str
    category: str
    plan_id: str
    endpoint: str
    transactions: list = field(default_factory=list)

    @property
    def avg_roi(self) -> float:
        if not self.transactions:
            return 0
        return sum(t.roi for t in self.transactions) / len(self.transactions)

    @property
    def avg_quality(self) -> float:
        if not self.transactions:
            return 0
        return sum(t.quality_score for t in self.transactions) / len(self.transactions)

    @property
    def total_spent(self) -> int:
        return sum(t.credits_used for t in self.transactions)

    @property
    def success_rate(self) -> float:
        if not self.transactions:
            return 0
        return sum(1 for t in self.transactions if t.success) / len(self.transactions)


class Portfolio:
    """Manages budget allocation, ROI tracking, and provider switching."""

    def __init__(self, total_budget: float, max_per_tx: float):
        self.total_budget = total_budget
        self.max_per_tx = max_per_tx
        self.spent = 0.0
        self.providers: dict[str, ProviderProfile] = {}
        self.decisions: list[dict] = []
        self.switches: list[dict] = []

    @property
    def remaining(self) -> float:
        return self.total_budget - self.spent

    def log_decision(self, decision_type: str, message: str, data: Optional[dict] = None):
        entry = {
            "timestamp": time.time(),
            "type": decision_type,
            "message": message,
            "data": data or {},
        }
        self.decisions.append(entry)
        prefix = f"[{decision_type}]"
        print(f"{prefix} {message}")
        return entry

    def can_spend(self, amount: float) -> tuple[bool, str]:
        if amount > self.remaining:
            return False, f"Insufficient budget: need {amount}, have {self.remaining:.2f}"
        if amount > self.max_per_tx:
            return False, f"Exceeds per-transaction limit: {amount} > {self.max_per_tx}"
        return True, "OK"

    def record_transaction(self, tx: Transaction):
        """Record a transaction and update provider profile."""
        key = f"{tx.team_name}:{tx.seller_name}"
        if key not in self.providers:
            self.providers[key] = ProviderProfile(
                name=tx.seller_name,
                team=tx.team_name,
                category=tx.service_category,
                plan_id=tx.plan_id,
                endpoint="",
            )
        self.providers[key].transactions.append(tx)
        self.spent += tx.credits_used * 0.01  # approximate USDC conversion

        self.log_decision(
            "PURCHASE",
            f"Bought from {tx.seller_name} [{tx.team_name}]: "
            f"quality={tx.quality_score}/10, cost={tx.credits_used}cr -> ROI={tx.roi:.0f}",
            {"seller": tx.seller_name, "team": tx.team_name, "roi": tx.roi, "credits": tx.credits_used},
        )

    def should_switch(self, category: str) -> Optional[dict]:
        """Check if we should switch providers in a category based on ROI."""
        cat_providers = [
            (k, p) for k, p in self.providers.items()
            if p.category == category and len(p.transactions) >= 1
        ]
        if len(cat_providers) < 2:
            return None

        cat_providers.sort(key=lambda x: -x[1].avg_roi)
        best_key, best = cat_providers[0]

        for key, provider in cat_providers[1:]:
            if provider.avg_roi > 0 and best.avg_roi / provider.avg_roi > 2:
                switch = {
                    "from": provider.name,
                    "to": best.name,
                    "reason": f"{best.name} has {best.avg_roi/provider.avg_roi:.1f}x better ROI",
                    "from_roi": provider.avg_roi,
                    "to_roi": best.avg_roi,
                }
                self.switches.append(switch)
                self.log_decision(
                    "SWITCH",
                    f"Switching from {provider.name} to {best.name} ({switch['reason']})",
                    switch,
                )
                return switch
        return None

    def get_best_provider(self, category: str) -> Optional[ProviderProfile]:
        """Get the best ROI provider in a category."""
        cat_providers = [
            p for p in self.providers.values()
            if p.category == category and p.avg_roi > 0
        ]
        if not cat_providers:
            return None
        return max(cat_providers, key=lambda p: p.avg_roi)

    def get_top_providers(self, n: int = 3) -> list:
        """Get top N providers by average quality."""
        ranked = sorted(self.providers.values(), key=lambda p: -p.avg_quality)
        return ranked[:n]

    @property
    def total_transactions(self) -> int:
        return sum(len(p.transactions) for p in self.providers.values())

    def get_report(self) -> str:
        """Generate comprehensive investment report for hackathon judges."""
        import datetime

        total_txns = self.total_transactions
        total_credits = sum(p.total_spent for p in self.providers.values())
        avg_quality = (
            sum(p.avg_quality * len(p.transactions) for p in self.providers.values()) / total_txns
            if total_txns > 0 else 0
        )
        overall_success = (
            sum(sum(1 for t in p.transactions if t.success) for p in self.providers.values()) / total_txns
            if total_txns > 0 else 0
        )

        # Categorize decisions
        thesis_decisions = [d for d in self.decisions if d["type"] == "THESIS"]
        adversarial_decisions = [d for d in self.decisions if d["type"] == "ADVERSARIAL"]
        adversarial_passed = sum(1 for d in adversarial_decisions if "PASSED" in d["message"])
        adversarial_failed = sum(1 for d in adversarial_decisions if "FAILED" in d["message"])
        review_decisions = [d for d in self.decisions if d["type"] == "REVIEW"]
        explore_decisions = [d for d in self.decisions if d["type"] == "EXPLORE"]
        intel_decisions = [d for d in self.decisions if d["type"] == "INTEL"]

        # Category breakdown
        cat_stats: dict[str, dict] = {}
        for p in self.providers.values():
            cat = p.category
            if cat not in cat_stats:
                cat_stats[cat] = {"txns": 0, "credits": 0, "providers": 0}
            cat_stats[cat]["txns"] += len(p.transactions)
            cat_stats[cat]["credits"] += p.total_spent
            cat_stats[cat]["providers"] += 1

        # Unique external teams
        external_teams = set(
            p.team for p in self.providers.values() if p.team != "Full Stack Agents"
        )

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "=" * 72,
            "THE FUND -- INVESTMENT REPORT",
            "Intelligence-Driven Autonomous Buyer",
            f"Generated: {now}",
            "=" * 72,
            "",
            "INVESTMENT THESIS",
            "-" * 72,
            "",
            "  \"Markets are not given; they are made.\"",
            "",
            "  The Fund operates on a single conviction: the most valuable thing a",
            "  buyer can do is not just consume services but build the information",
            "  infrastructure that makes consumption rational. Every review we submit",
            "  is a brick in the epistemic foundation of the marketplace. Every",
            "  adversarial test is a stress inoculation that makes the ecosystem",
            "  antifragile. Every reputation check before a purchase is a contribution",
            "  to the Hayekian price signal network.",
            "",
            "  Nine frameworks ground every decision:",
            "    Akerlof (1970)  -- Reviews prevent market collapse to lemons",
            "    Hayek (1945)    -- Our measurements are decentralized price signals",
            "    Coase (1937)    -- We buy capabilities, never build them",
            "    Soros           -- Our reviews change the data we read (reflexivity)",
            "    Taleb           -- Adversarial testing is the economy's immune system",
            "    Hurwicz (2007)  -- Honest signals make truth-telling dominant strategy",
            "    Ostrom (2009)   -- Reputation is a commons we govern by participation",
            "    Kyle (1985)     -- Informed purchasing is a public good",
            "    Principal-Agent -- Transparency solves the alignment problem",
            "",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 72,
            "",
            f"  Total transactions:    {total_txns}",
            f"  Total credits spent:   {total_credits}",
            f"  USDC equivalent:       {self.spent:.2f}",
            f"  Unique providers:      {len(self.providers)}",
            f"  External teams tested: {len(external_teams)}",
            f"  Provider switches:     {len(self.switches)}",
            f"  Average quality:       {avg_quality:.1f}/10",
            f"  Overall success rate:  {overall_success:.0%}",
            "",
            f"  Reviews submitted:     {len(review_decisions)}",
            f"  Adversarial tests:     {len(adversarial_decisions)}",
            f"    Passed:              {adversarial_passed}",
            f"    Failed:              {adversarial_failed}",
            f"  Intelligence queries:  {len(intel_decisions)}",
            f"  External explorations: {len(explore_decisions)}",
            "",
            "",
            "FIVE-PHASE CYCLE",
            "-" * 72,
            "",
            "  Each 45-second cycle follows a deliberate sequence:",
            "",
            "  1. INTELLIGENCE (Hayek, Kyle)",
            "     Query Oracle for marketplace leaderboard and search results.",
            "     Check Underwriter for reputation of top-ranked services.",
            "     -> Builds the information base for all subsequent decisions.",
            "",
            "  2. INFORMED PURCHASING (Coase, Kyle)",
            "     Cross-compare services head-to-head via Oracle.",
            "     Buy from Amplifier, Gold Star, Architect -- with purpose, not randomly.",
            "     -> Intelligence gathered in Phase 1 determines what we compare and check.",
            "",
            "  3. ADVERSARIAL TESTING (Taleb)",
            "     Send one edge case per cycle: empty strings, SQL injection, XSS,",
            "     5000-char floods, unicode, null values, boolean injection.",
            "     -> Failures trigger incident claims with The Underwriter.",
            "     -> Services that survive become antifragile.",
            "",
            "  4. EXTERNAL EXPLORATION (Akerlof) -- every 5th cycle",
            "     Use Oracle intelligence to prioritize which external sellers to try.",
            "     Check reputation BEFORE buying. Subscribe, probe, review.",
            "     -> Honest reviews prevent the marketplace from collapsing to lemons.",
            "",
            "  5. FEEDBACK LOOP (Soros, Ostrom, Hurwicz)",
            "     Submit reviews for every purchase. These reviews change the",
            "     reputation data we read next cycle -- a reflexive loop.",
            "     Periodically measure our impact on the reputation leaderboard.",
            "     Nominate top performers for Gold Star certification.",
            "",
            "",
            "SPENDING BY CATEGORY",
            "-" * 72,
            "",
        ]

        for cat in sorted(cat_stats.keys()):
            s = cat_stats[cat]
            lines.append(f"  {cat:20s}  {s['txns']:4d} txns  {s['credits']:4d} credits  {s['providers']} providers")

        lines += [
            "",
            "",
            "PROVIDER PERFORMANCE (ranked by ROI)",
            "-" * 72,
            "",
        ]

        for key, p in sorted(self.providers.items(), key=lambda x: -x[1].avg_roi):
            tool_counts: dict[str, int] = {}
            for t in p.transactions:
                tool_counts[t.tool_name] = tool_counts.get(t.tool_name, 0) + 1

            avg_latency = (
                sum(t.latency_ms for t in p.transactions) / len(p.transactions)
                if p.transactions else 0
            )

            lines.append(f"  {p.name} [{p.team}]")
            lines.append(f"    Category:     {p.category}")
            lines.append(f"    Transactions: {len(p.transactions)}")
            lines.append(f"    Avg Quality:  {p.avg_quality:.1f}/10")
            lines.append(f"    Avg ROI:      {p.avg_roi:.0f}")
            lines.append(f"    Avg Latency:  {avg_latency:.0f}ms")
            lines.append(f"    Credits Spent:{p.total_spent}")
            lines.append(f"    Success Rate: {p.success_rate:.0%}")
            if tool_counts:
                lines.append(f"    Tools:        {', '.join(f'{k} ({v})' for k, v in sorted(tool_counts.items(), key=lambda x: -x[1]))}")
            lines.append("")

        if self.switches:
            lines += [
                "",
                "PROVIDER SWITCHING DECISIONS",
                "-" * 72,
                "",
            ]
            for s in self.switches:
                lines.append(f"  {s['from']} -> {s['to']}")
                lines.append(f"    Reason: {s['reason']}")
                lines.append(f"    ROI improvement: {s['from_roi']:.0f} -> {s['to_roi']:.0f}")
                lines.append("")

        if adversarial_decisions:
            lines += [
                "",
                "ADVERSARIAL TEST RESULTS",
                "-" * 72,
                "",
            ]
            for d in adversarial_decisions:
                lines.append(f"  {d['message']}")
            lines.append("")

        # Key thesis moments from the log
        lines += [
            "",
            "THESIS-DRIVEN DECISION LOG (last 30)",
            "-" * 72,
            "",
        ]
        thesis_and_key = [
            d for d in self.decisions
            if d["type"] in ("THESIS", "ADVERSARIAL", "SWITCH", "EXPLORE", "FEEDBACK", "INTEL")
        ]
        for d in thesis_and_key[-30:]:
            lines.append(f"  [{d['type']:12s}] {d['message']}")

        lines += [
            "",
            "",
            "REFLEXIVITY EVIDENCE (Soros)",
            "-" * 72,
            "",
            "  The Fund reads reputation data from The Underwriter, makes purchasing",
            "  decisions based on that data, and submits reviews back to The Underwriter.",
            "  The reputation data read in cycle N+1 reflects the reviews submitted in",
            "  cycle N. This is not a bug -- it is the generative engine of the economy.",
            "",
            f"  Reviews submitted this session:   {len(review_decisions)}",
            f"  Reputation checks performed:      {sum(1 for d in self.decisions if d['type'] == 'INTEL')}",
            f"  Feedback measurements taken:      {sum(1 for d in self.decisions if d['type'] == 'FEEDBACK')}",
            "",
            "",
            "=" * 72,
            "  The Fund does not merely observe the agent economy -- it constitutes it.",
            "  Our reviews change reputation. Our purchases create revenue signals.",
            "  Our switching changes the competitive landscape. We are not passive",
            "  allocators of capital; we are active participants in a reflexive system",
            "  where observation and reality are entangled.",
            "=" * 72,
        ]

        return "\n".join(lines)

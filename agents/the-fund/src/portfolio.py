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

    def get_report(self) -> str:
        """Generate investment report for judges."""
        lines = [
            "=" * 60,
            "THE FUND — INVESTMENT REPORT",
            "=" * 60,
            f"",
            f"Budget: {self.spent:.2f} / {self.total_budget:.2f} USDC spent",
            f"Remaining: {self.remaining:.2f} USDC",
            f"Providers used: {len(self.providers)}",
            f"Total transactions: {sum(len(p.transactions) for p in self.providers.values())}",
            f"Provider switches: {len(self.switches)}",
            f"",
            "--- PROVIDER PERFORMANCE ---",
        ]

        for key, p in sorted(self.providers.items(), key=lambda x: -x[1].avg_roi):
            lines.append(f"")
            lines.append(f"  {p.name} [{p.team}] ({p.category})")
            lines.append(f"    Transactions: {len(p.transactions)}")
            lines.append(f"    Avg Quality: {p.avg_quality:.1f}/10")
            lines.append(f"    Avg ROI: {p.avg_roi:.0f}")
            lines.append(f"    Total Spent: {p.total_spent} credits")
            lines.append(f"    Success Rate: {p.success_rate:.0%}")

        if self.switches:
            lines.append(f"")
            lines.append("--- SWITCHING DECISIONS ---")
            for s in self.switches:
                lines.append(f"  {s['from']} -> {s['to']}: {s['reason']}")

        lines.append(f"")
        lines.append("--- DECISION LOG ---")
        for d in self.decisions[-20:]:  # Last 20 decisions
            lines.append(f"  [{d['type']}] {d['message']}")

        return "\n".join(lines)

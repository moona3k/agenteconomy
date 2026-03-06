"""The Judge -- dispute resolution engine for the agent economy.

When buyers and sellers disagree, The Judge examines evidence from both parties,
cross-references The Underwriter's reputation data and The Gold Star's QA reports,
and renders a binding verdict using Claude.
"""
import os
import time
import threading
import httpx
from dataclasses import dataclass, field

UNDERWRITER_URL = os.environ.get("UNDERWRITER_URL", "https://underwriter.agenteconomy.io")
GOLD_STAR_URL = os.environ.get("GOLD_STAR_URL", "https://goldstar.agenteconomy.io")


@dataclass
class Dispute:
    case_id: str
    buyer: str
    seller_name: str
    team_name: str
    complaint: str
    evidence: str
    credits_at_stake: int
    status: str = "filed"  # filed, investigating, ruled, appealed, closed
    seller_response: str = ""
    # Evidence gathered by The Judge
    underwriter_data: dict = field(default_factory=dict)
    gold_star_data: dict = field(default_factory=dict)
    service_health: dict = field(default_factory=dict)
    # Ruling
    ruling: str = ""  # buyer_wins, seller_wins, split, dismissed
    reasoning: str = ""
    remedy: str = ""
    confidence: float = 0.0
    timestamp_filed: float = field(default_factory=time.time)
    timestamp_ruled: float = 0.0


class ArbiterEngine:
    """Examines disputes, gathers evidence, and renders verdicts."""

    def __init__(self):
        self._disputes: list[Dispute] = []
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"CASE-{self._counter:04d}"

    async def file_dispute(self, buyer: str, seller_name: str, team_name: str,
                           complaint: str, evidence: str, credits_at_stake: int) -> Dispute:
        """File a new dispute and begin investigation."""
        dispute = Dispute(
            case_id=self._next_id(),
            buyer=buyer[:100],
            seller_name=seller_name[:200],
            team_name=team_name[:200],
            complaint=complaint[:2000],
            evidence=evidence[:2000],
            credits_at_stake=max(0, min(credits_at_stake, 10000)),
        )

        # Automatically gather evidence
        dispute.status = "investigating"

        # Gather evidence in parallel from infrastructure services
        dispute.underwriter_data = await self._get_underwriter_data(seller_name)
        dispute.gold_star_data = await self._get_gold_star_data(seller_name)

        # Check if the seller's service is even reachable right now
        endpoint = await self._find_endpoint(seller_name)
        if endpoint:
            dispute.service_health = await self._check_service_health(endpoint)

        # Render verdict
        dispute = self._render_verdict(dispute)

        with self._lock:
            self._disputes.append(dispute)

        return dispute

    async def submit_response(self, case_id: str, seller_response: str) -> Dispute | None:
        """Allow a seller to respond to a dispute."""
        dispute = self._find_dispute(case_id)
        if not dispute:
            return None
        if dispute.status == "closed":
            return dispute

        dispute.seller_response = seller_response[:2000]

        # Re-evaluate with seller's response
        dispute = self._render_verdict(dispute)

        return dispute

    async def appeal(self, case_id: str, new_evidence: str) -> Dispute | None:
        """Appeal a ruling with new evidence."""
        dispute = self._find_dispute(case_id)
        if not dispute:
            return None
        if dispute.status == "closed":
            return dispute

        dispute.status = "appealed"
        dispute.evidence += f"\n\n[APPEAL] {new_evidence[:1000]}"

        # Re-gather fresh evidence
        dispute.underwriter_data = await self._get_underwriter_data(dispute.seller_name)
        dispute.gold_star_data = await self._get_gold_star_data(dispute.seller_name)

        endpoint = await self._find_endpoint(dispute.seller_name)
        if endpoint:
            dispute.service_health = await self._check_service_health(endpoint)

        # Re-render verdict
        dispute = self._render_verdict(dispute)

        return dispute

    def _render_verdict(self, dispute: Dispute) -> Dispute:
        """Analyze all evidence and render a verdict.

        Uses a rules-based system that weighs multiple evidence sources.
        Not AI-powered (unlike The Gold Star) -- this is deterministic justice.
        """
        scores = {
            "buyer_case": 0.0,  # Evidence supporting the buyer
            "seller_case": 0.0,  # Evidence supporting the seller
        }

        reasons = []

        # Factor 1: Underwriter reputation data
        uw = dispute.underwriter_data
        if uw:
            trust = uw.get("trust_score", 50)
            badge = uw.get("badge", "UNVERIFIED")
            total_reviews = uw.get("total_reviews", 0)
            total_incidents = uw.get("total_incidents", 0)

            if badge == "HIGH RISK":
                scores["buyer_case"] += 30
                reasons.append(f"Seller has HIGH RISK badge (trust score: {trust})")
            elif badge == "MIXED":
                scores["buyer_case"] += 15
                reasons.append(f"Seller has MIXED reputation (trust score: {trust})")
            elif badge in ("VERIFIED TRUSTED", "RELIABLE"):
                scores["seller_case"] += 20
                reasons.append(f"Seller has {badge} reputation (trust score: {trust})")

            if total_incidents > 0:
                incident_ratio = total_incidents / max(1, total_reviews)
                if incident_ratio > 0.3:
                    scores["buyer_case"] += 20
                    reasons.append(f"High incident ratio: {total_incidents} incidents / {total_reviews} reviews")
                elif incident_ratio > 0.1:
                    scores["buyer_case"] += 10
                    reasons.append(f"Some prior incidents: {total_incidents} incidents / {total_reviews} reviews")

            if uw.get("status") == "unrated":
                reasons.append("Seller has no reputation history (unrated)")
                scores["buyer_case"] += 5  # Slight edge to buyer when seller is unknown
        else:
            reasons.append("Could not retrieve reputation data from The Underwriter")

        # Factor 2: Gold Star QA data
        gs = dispute.gold_star_data
        if gs and gs.get("status") != "not_found":
            overall = gs.get("overall_score", 0)
            certified = gs.get("certified", False)

            if certified:
                scores["seller_case"] += 25
                reasons.append(f"Seller is Gold Star Certified (score: {overall})")
            elif overall >= 4.0:
                scores["seller_case"] += 15
                reasons.append(f"Seller scored well in QA review ({overall}/5)")
            elif overall < 3.0:
                scores["buyer_case"] += 15
                reasons.append(f"Seller scored poorly in QA review ({overall}/5)")
            elif overall < 2.0:
                scores["buyer_case"] += 25
                reasons.append(f"Seller failed QA review ({overall}/5)")
        else:
            reasons.append("No Gold Star QA report found for this seller")

        # Factor 3: Current service health
        health = dispute.service_health
        if health:
            if not health.get("reachable"):
                scores["buyer_case"] += 20
                reasons.append("Seller's service is currently unreachable")
            elif not health.get("health_ok"):
                scores["buyer_case"] += 10
                reasons.append("Seller's health endpoint is returning errors")
            else:
                scores["seller_case"] += 10
                latency = health.get("latency_ms", 0)
                reasons.append(f"Seller's service is currently online (latency: {latency}ms)")

        # Factor 4: Seller response
        if dispute.seller_response:
            scores["seller_case"] += 10
            reasons.append("Seller has submitted a response to the complaint")
        else:
            scores["buyer_case"] += 5
            reasons.append("Seller has not responded to the complaint")

        # Factor 5: Credits at stake (higher stakes = more scrutiny on seller)
        if dispute.credits_at_stake >= 10:
            scores["buyer_case"] += 5
            reasons.append(f"High-value dispute ({dispute.credits_at_stake} credits at stake)")

        # Render verdict
        buyer_total = scores["buyer_case"]
        seller_total = scores["seller_case"]
        total = buyer_total + seller_total or 1
        confidence = abs(buyer_total - seller_total) / total

        if buyer_total > seller_total * 1.5:
            dispute.ruling = "buyer_wins"
            dispute.remedy = (
                f"Buyer's complaint is upheld. Seller '{dispute.seller_name}' should "
                f"refund {dispute.credits_at_stake} credits and address the reported issues. "
                f"This ruling has been noted and will affect future reputation assessments."
            )
        elif seller_total > buyer_total * 1.5:
            dispute.ruling = "seller_wins"
            dispute.remedy = (
                f"Seller '{dispute.seller_name}' is cleared. The evidence supports the seller's "
                f"position. No remedy required."
            )
        elif buyer_total > seller_total:
            dispute.ruling = "split"
            dispute.remedy = (
                f"Partial ruling in buyer's favor. Evidence is mixed but leans toward the buyer. "
                f"Seller '{dispute.seller_name}' should consider a partial refund of "
                f"{dispute.credits_at_stake // 2} credits and address the reported issues."
            )
        elif seller_total > buyer_total:
            dispute.ruling = "split"
            dispute.remedy = (
                f"Partial ruling in seller's favor. Evidence is mixed but leans toward the seller. "
                f"Buyer should consider whether the service met reasonable expectations."
            )
        else:
            dispute.ruling = "dismissed"
            dispute.remedy = (
                "Insufficient evidence to render a clear verdict. Both parties should attempt "
                "direct resolution. Case remains on record."
            )

        dispute.reasoning = (
            f"Evidence analysis (buyer score: {buyer_total:.0f}, seller score: {seller_total:.0f}):\n"
            + "\n".join(f"  - {r}" for r in reasons)
        )
        dispute.confidence = round(confidence, 2)
        dispute.status = "ruled"
        dispute.timestamp_ruled = time.time()

        return dispute

    async def _get_underwriter_data(self, seller_name: str) -> dict:
        """Query The Underwriter for reputation data."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.post(f"{UNDERWRITER_URL}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "check_reputation",
                        "arguments": {"seller_name": seller_name},
                    },
                    "id": 1,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    result = data.get("result", {})
                    content = result.get("content", [])
                    if content and isinstance(content, list):
                        text = content[0].get("text", "{}")
                        try:
                            return dict(json.loads(text))
                        except Exception:
                            pass
        except Exception:
            pass
        return {}

    async def _get_gold_star_data(self, seller_name: str) -> dict:
        """Query The Gold Star for QA report data."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.post(f"{GOLD_STAR_URL}/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "get_report",
                        "arguments": {"seller_name": seller_name},
                    },
                    "id": 2,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    result = data.get("result", {})
                    content = result.get("content", [])
                    if content and isinstance(content, list):
                        text = content[0].get("text", "{}")
                        try:
                            return dict(json.loads(text))
                        except Exception:
                            pass
        except Exception:
            pass
        return {}

    async def _find_endpoint(self, seller_name: str) -> str:
        """Try to find the seller's endpoint from the marketplace."""
        api_key = os.environ.get("NVM_API_KEY", "")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://nevermined.ai/hackathon/register/api/discover",
                    params={"side": "sell"},
                    headers={"x-nvm-api-key": api_key},
                )
                if resp.status_code == 200:
                    sellers = resp.json().get("sellers", [])
                    for s in sellers:
                        if (s.get("name", "").lower() == seller_name.lower() or
                                s.get("teamName", "").lower() == seller_name.lower()):
                            url = s.get("endpointUrl", "")
                            if url and url.startswith("http"):
                                return url
        except Exception:
            pass
        return ""

    async def _check_service_health(self, endpoint: str) -> dict:
        """Check if a service is currently reachable."""
        base = endpoint.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                start = time.time()
                resp = await client.get(f"{base}/health")
                latency = (time.time() - start) * 1000
                return {
                    "reachable": True,
                    "health_ok": resp.status_code == 200,
                    "latency_ms": round(latency, 1),
                    "endpoint": base,
                }
        except Exception:
            return {"reachable": False, "health_ok": False, "latency_ms": 0, "endpoint": base}

    def _find_dispute(self, case_id: str) -> Dispute | None:
        for d in self._disputes:
            if d.case_id == case_id:
                return d
        return None

    def get_case_history(self, party_name: str = "") -> list[dict]:
        """Get dispute history for a party or all disputes."""
        if party_name:
            matches = [
                d for d in self._disputes
                if (d.buyer.lower() == party_name.lower() or
                    d.seller_name.lower() == party_name.lower() or
                    d.team_name.lower() == party_name.lower())
            ]
        else:
            matches = list(self._disputes)

        return [self._dispute_to_dict(d) for d in sorted(matches, key=lambda x: -x.timestamp_filed)]

    def get_stats(self) -> dict:
        total = len(self._disputes)
        ruled = [d for d in self._disputes if d.status == "ruled"]
        buyer_wins = sum(1 for d in ruled if d.ruling == "buyer_wins")
        seller_wins = sum(1 for d in ruled if d.ruling == "seller_wins")
        splits = sum(1 for d in ruled if d.ruling == "split")
        dismissed = sum(1 for d in ruled if d.ruling == "dismissed")
        total_credits = sum(d.credits_at_stake for d in self._disputes)
        avg_confidence = sum(d.confidence for d in ruled) / len(ruled) if ruled else 0

        return {
            "total_disputes_filed": total,
            "total_rulings": len(ruled),
            "buyer_wins": buyer_wins,
            "seller_wins": seller_wins,
            "split_decisions": splits,
            "dismissed": dismissed,
            "total_credits_disputed": total_credits,
            "average_confidence": round(avg_confidence, 2),
            "unique_sellers_disputed": len(set(d.seller_name for d in self._disputes)),
            "unique_buyers": len(set(d.buyer for d in self._disputes)),
        }

    def _dispute_to_dict(self, d: Dispute) -> dict:
        return {
            "case_id": d.case_id,
            "buyer": d.buyer,
            "seller_name": d.seller_name,
            "team_name": d.team_name,
            "complaint": d.complaint,
            "evidence": d.evidence[:500],
            "credits_at_stake": d.credits_at_stake,
            "status": d.status,
            "seller_response": d.seller_response[:500] if d.seller_response else None,
            "ruling": d.ruling,
            "reasoning": d.reasoning,
            "remedy": d.remedy,
            "confidence": d.confidence,
            "evidence_sources": {
                "underwriter": bool(d.underwriter_data),
                "gold_star": bool(d.gold_star_data),
                "service_health": bool(d.service_health),
            },
            "timestamp_filed": d.timestamp_filed,
            "timestamp_ruled": d.timestamp_ruled if d.timestamp_ruled else None,
        }


# Need json import for MCP calls
import json

# Singleton
arbiter = ArbiterEngine()

"""Agent reputation system — reviews, scores, and incident tracking.

Like Glassdoor for AI agents. Tracks quality, reliability, and trust.
"""
import time
import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Review:
    reviewer: str  # buyer team/agent identifier
    seller_name: str
    team_name: str
    quality_score: float  # 1-5 stars
    reliability: bool  # did the service respond correctly?
    latency_ms: float
    notes: str
    timestamp: float = field(default_factory=time.time)
    transaction_type: str = "purchase"  # purchase, insurance_claim, test


@dataclass
class Incident:
    seller_name: str
    team_name: str
    incident_type: str  # timeout, error_500, garbage_response, auth_failure
    description: str
    reporter: str
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


class ReputationEngine:
    """Aggregates reviews and incidents into reputation scores."""

    def __init__(self):
        self._reviews: list[Review] = []
        self._incidents: list[Incident] = []
        self._insurance_claims: list[dict] = []
        self._lock = threading.Lock()

    def add_review(self, review: Review):
        with self._lock:
            self._reviews.append(review)

    def add_incident(self, incident: Incident):
        with self._lock:
            self._incidents.append(incident)

    def file_insurance_claim(self, buyer: str, seller_name: str, team_name: str,
                              reason: str, credits_lost: int) -> dict:
        claim = {
            "id": f"CLM-{len(self._insurance_claims)+1:04d}",
            "buyer": buyer,
            "seller_name": seller_name,
            "team_name": team_name,
            "reason": reason,
            "credits_lost": credits_lost,
            "status": "filed",
            "timestamp": time.time(),
        }
        with self._lock:
            self._insurance_claims.append(claim)
            # Auto-create incident
            self._incidents.append(Incident(
                seller_name=seller_name,
                team_name=team_name,
                incident_type="insurance_claim",
                description=f"Insurance claim: {reason} (credits lost: {credits_lost})",
                reporter=buyer,
            ))
        return claim

    def get_reputation(self, seller_name: str) -> dict:
        """Get aggregated reputation for a seller."""
        reviews = [r for r in self._reviews if r.seller_name.lower() == seller_name.lower()
                   or r.team_name.lower() == seller_name.lower()]
        incidents = [i for i in self._incidents if i.seller_name.lower() == seller_name.lower()
                     or i.team_name.lower() == seller_name.lower()]
        claims = [c for c in self._insurance_claims if c["seller_name"].lower() == seller_name.lower()
                  or c["team_name"].lower() == seller_name.lower()]

        if not reviews and not incidents:
            return {"seller": seller_name, "status": "unrated", "message": "No reviews or incidents yet."}

        avg_quality = sum(r.quality_score for r in reviews) / len(reviews) if reviews else 0
        reliability_rate = sum(1 for r in reviews if r.reliability) / len(reviews) if reviews else 0
        avg_latency = sum(r.latency_ms for r in reviews) / len(reviews) if reviews else 0

        # Trust score: 0-100
        trust = min(100, max(0,
            (avg_quality / 5 * 40) +
            (reliability_rate * 40) +
            (20 - min(20, len(incidents) * 5))
        ))

        # Badge
        if trust >= 80 and len(reviews) >= 3:
            badge = "VERIFIED TRUSTED"
        elif trust >= 60:
            badge = "RELIABLE"
        elif trust >= 40:
            badge = "MIXED"
        elif len(incidents) > len(reviews):
            badge = "HIGH RISK"
        else:
            badge = "UNVERIFIED"

        return {
            "seller": seller_name,
            "badge": badge,
            "trust_score": round(trust, 1),
            "avg_quality": round(avg_quality, 2),
            "reliability_rate": f"{reliability_rate:.0%}",
            "avg_latency_ms": round(avg_latency, 1),
            "total_reviews": len(reviews),
            "total_incidents": len(incidents),
            "insurance_claims": len(claims),
            "recent_reviews": [
                {"reviewer": r.reviewer, "score": r.quality_score, "notes": r.notes[:100]}
                for r in sorted(reviews, key=lambda x: -x.timestamp)[:5]
            ],
            "recent_incidents": [
                {"type": i.incident_type, "description": i.description[:100]}
                for i in sorted(incidents, key=lambda x: -x.timestamp)[:5]
            ],
        }

    def get_leaderboard(self) -> dict:
        """Get hall of fame and shame board."""
        all_sellers = set()
        for r in self._reviews:
            all_sellers.add(r.seller_name)
        for i in self._incidents:
            all_sellers.add(i.seller_name)

        reps = []
        for seller in all_sellers:
            rep = self.get_reputation(seller)
            if rep.get("status") != "unrated":
                reps.append(rep)

        reps.sort(key=lambda x: -x.get("trust_score", 0))

        hall_of_fame = [r for r in reps if r.get("trust_score", 0) >= 70][:10]
        shame_board = [r for r in reversed(reps) if r.get("trust_score", 0) < 40][:10]

        return {
            "total_rated": len(reps),
            "total_reviews": len(self._reviews),
            "total_incidents": len(self._incidents),
            "total_claims": len(self._insurance_claims),
            "hall_of_fame": hall_of_fame,
            "shame_board": shame_board,
        }

    def get_stats(self) -> dict:
        return {
            "total_reviews": len(self._reviews),
            "total_incidents": len(self._incidents),
            "total_claims": len(self._insurance_claims),
            "unique_sellers_reviewed": len(set(r.seller_name for r in self._reviews)),
        }


# Singleton
reputation = ReputationEngine()

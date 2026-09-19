from typing import Dict
from loguru import logger

class ARIAInfluencerScorer:
    PLATFORM_WEIGHTS = {"instagram": 0.40, "tiktok": 0.35, "youtube": 0.25}
    JORDAN_CITIES = ["amman", "zarqa", "irbid", "aqaba", "madaba", "salt"]

    def _tier_bonus(self, followers: int) -> float:
        if followers < 1000: return 0.3
        if followers < 10000: return 0.7
        if followers < 100000: return 1.2
        if followers < 500000: return 1.0
        if followers < 1000000: return 0.85
        return 0.70

    def calculate_engagement_score(self, data: Dict) -> float:
        score = 0.0
        for platform, weight in self.PLATFORM_WEIGHTS.items():
            followers = data.get(f"{platform}_followers", 0) or data.get(f"{platform}_subscribers", 0)
            eng_rate = data.get(f"{platform}_engagement_rate", 0)
            if not followers: continue
            score += weight * min(eng_rate * 10, 100) * self._tier_bonus(followers)
        return round(min(score * 30, 30), 2)

    def calculate_authenticity_score(self, data: Dict) -> float:
        score = 25.0
        ig_followers = data.get("instagram_followers", 0)
        ig_following = data.get("instagram_following", 1) or 1
        ratio = ig_followers / ig_following
        if ratio < 0.1: score -= 10
        elif ratio < 0.5: score -= 5
        elif ratio > 100: score -= 3
        if data.get("monthly_growth_rate", 0) > 50: score -= 8
        age = data.get("account_age_days", 365)
        if age < 90: score -= 7
        elif age < 180: score -= 3
        return round(max(score, 0), 2)

    def calculate_reliability_score(self, data: Dict) -> float:
        total = data.get("campaigns_total", 0)
        if not total: return 10.0
        completed = data.get("campaigns_completed", 0)
        on_time = data.get("on_time_deliveries", 0)
        disputes = data.get("disputes_raised", 0)
        score = (completed / total * 8) + (on_time / max(completed, 1) * 7) - disputes * 2
        return round(min(max(score, 0), 15), 2)

    def calculate_relevance(self, data: Dict, niche: str) -> float:
        inf_niche = (data.get("niche") or "").lower()
        niche = niche.lower()
        niche_score = 8.0 if inf_niche == niche else (6.0 if niche in inf_niche or inf_niche in niche else 2.0)
        city = (data.get("city") or "").lower()
        location_bonus = 2.0 if any(c in city for c in self.JORDAN_CITIES) else 0.5
        return round(min(niche_score + location_bonus, 10), 2)

    def compute_aria_score(self, data: Dict, niche: str = "general", content_quality: float = 70.0) -> Dict:
        eng = self.calculate_engagement_score(data)
        auth = self.calculate_authenticity_score(data)
        cq = round((content_quality / 100) * 20, 2)
        rel = self.calculate_reliability_score(data)
        rev = self.calculate_relevance(data, niche)
        total = eng + auth + cq + rel + rev
        tier = ("PLATINUM" if total >= 85 else "GOLD" if total >= 70 else "SILVER" if total >= 55 else "BRONZE" if total >= 40 else "UNRANKED")
        insights = {
            "PLATINUM": "مؤثر ممتاز للسوق الأردني",
            "GOLD": "مؤثر جيد - مناسب للحملات التجارية",
            "SILVER": "مؤثر متوسط - مناسب للميزانيات المحدودة",
            "BRONZE": "مؤثر ناشئ",
            "UNRANKED": "يحتاج مزيدا من البيانات",
        }
        logger.info(f"[ARIA::SCORER] Score={total:.1f} | Tier={tier}")
        return {
            "aria_score": round(total, 2), "tier": tier,
            "breakdown": {"engagement": eng, "authenticity": auth, "content_quality": cq, "reliability": rel, "relevance": rev},
            "max_possible": {"engagement": 30, "authenticity": 25, "content_quality": 20, "reliability": 15, "relevance": 10},
            "jordan_insight": insights[tier],
        }

scorer = ARIAInfluencerScorer()

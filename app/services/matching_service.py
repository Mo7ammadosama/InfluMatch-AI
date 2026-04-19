"""
WaslAI.jo — AI Matching Service
Connects Campaigns ↔ Influencers using RAG + scoring
"""
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.influencer import Influencer
from app.models.campaign import Campaign


class MatchingService:

    async def score_influencer_for_campaign(
        self,
        influencer: Influencer,
        campaign: Campaign,
    ) -> float:
        score = 0.0

        # Category match (30 pts)
        if campaign.target_categories:
            overlap = set(influencer.content_categories) & set(campaign.target_categories)
            score += (len(overlap) / len(campaign.target_categories)) * 30

        # Follower threshold (20 pts)
        if influencer.total_followers >= campaign.min_followers:
            score += 20

        # Engagement rate (25 pts)
        if influencer.avg_engagement_rate >= campaign.min_engagement_rate:
            ratio = min(influencer.avg_engagement_rate / max(campaign.min_engagement_rate, 0.001), 2.0)
            score += min(ratio * 12.5, 25)

        # Language match (10 pts)
        if campaign.preferred_languages:
            lang_overlap = set(influencer.languages) & set(campaign.preferred_languages)
            score += (len(lang_overlap) / len(campaign.preferred_languages)) * 10

        # City match (5 pts)
        if campaign.target_cities and influencer.city in campaign.target_cities:
            score += 5

        # Platform match (10 pts)
        if campaign.required_platforms:
            influencer_platforms = set(influencer.social_platforms.keys())
            platform_overlap = influencer_platforms & set(campaign.required_platforms)
            score += (len(platform_overlap) / len(campaign.required_platforms)) * 10

        return round(score, 2)

    async def find_matches(
        self,
        campaign: Campaign,
        db: AsyncSession,
        top_k: int = 10,
    ) -> list[dict]:
        result = await db.execute(
            select(Influencer).where(
                Influencer.is_available == True,
                Influencer.total_followers >= campaign.min_followers,
            )
        )
        influencers = result.scalars().all()

        scored = []
        for inf in influencers:
            score = await self.score_influencer_for_campaign(inf, campaign)
            if score > 0:
                scored.append({"influencer": inf, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"Matched {len(scored)} influencers for campaign {campaign.id}")
        return scored[:top_k]


matching_service = MatchingService()

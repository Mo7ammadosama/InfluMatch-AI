from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel
from ...core.database import get_db
from ...models.influencer import Influencer
from ...models.user import User
from ...services.scoring.influencer_scorer import ARIAInfluencerScorer
from ..dependencies.auth_deps import get_current_user
from loguru import logger

router = APIRouter(prefix="/influencers", tags=["Influencers"])
scorer = ARIAInfluencerScorer()

class InfluencerCreate(BaseModel):
    niche               : Optional[str] = None
    city                : str = "Amman"
    bio_ar              : Optional[str] = None
    bio_en              : Optional[str] = None
    instagram_handle    : Optional[str] = None
    instagram_followers : int = 0
    tiktok_handle       : Optional[str] = None
    tiktok_followers    : int = 0
    rate_per_post       : float = 0.0
    rate_per_story      : float = 0.0
    rate_per_reel       : float = 0.0

class InfluencerUpdate(BaseModel):
    niche                      : Optional[str]   = None
    city                       : Optional[str]   = None
    bio_ar                     : Optional[str]   = None
    bio_en                     : Optional[str]   = None
    instagram_handle           : Optional[str]   = None
    instagram_followers        : Optional[int]   = None
    instagram_engagement_rate  : Optional[float] = None
    tiktok_handle              : Optional[str]   = None
    tiktok_followers           : Optional[int]   = None
    tiktok_engagement_rate     : Optional[float] = None
    rate_per_post              : Optional[float] = None
    rate_per_story             : Optional[float] = None
    rate_per_reel              : Optional[float] = None
    is_available               : Optional[bool]  = None

@router.post("/", status_code=201)
async def create_influencer_profile(
    data: InfluencerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create influencer profile"""
    existing = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Influencer profile already exists")
    influencer = Influencer(user_id=current_user.id, **data.model_dump())
    db.add(influencer)
    await db.flush()
    logger.success(f"[ARIA::INFLUENCERS] Profile created: {influencer.id}")
    return {"id": influencer.id}

@router.get("/me")
async def get_my_influencer_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get logged-in influencer's profile + ARIA score"""
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    inf = result.scalar_one_or_none()
    if not inf:
        return {
            "profile_exists": False,
            "aria_score": 0.0,
            "aria_tier": "UNRANKED",
            "instagram_followers": 0,
            "tiktok_followers": 0,
            "instagram_engagement_rate": 0.0,
            "campaigns_completed": 0,
            "engagement_score": 0.0,
            "authenticity_score": 0.0,
            "relevance_score": 0.0,
            "delivery_score": 0.0,
        }
    return {
        "profile_exists": True,
        "id": inf.id,
        "niche": inf.niche,
        "city": inf.city,
        "aria_score": inf.aria_score,
        "aria_tier": inf.aria_tier,
        "instagram_followers": inf.instagram_followers,
        "instagram_handle": inf.instagram_handle,
        "instagram_engagement_rate": inf.instagram_engagement_rate,
        "tiktok_followers": inf.tiktok_followers,
        "tiktok_handle": inf.tiktok_handle,
        "youtube_subscribers": inf.youtube_subscribers,
        "campaigns_completed": inf.campaigns_completed,
        "campaigns_total": inf.campaigns_total,
        "on_time_deliveries": inf.on_time_deliveries,
        "engagement_score": inf.engagement_score,
        "authenticity_score": inf.authenticity_score,
        "relevance_score": inf.relevance_score,
        "delivery_score": inf.delivery_score,
        "rate_per_post": inf.rate_per_post,
        "rate_per_story": inf.rate_per_story,
        "rate_per_reel": inf.rate_per_reel,
        "is_available": inf.is_available,
    }

@router.patch("/me")
async def update_my_influencer_profile(
    data: InfluencerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update logged-in influencer's profile + auto-rescore ARIA"""
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    inf = result.scalar_one_or_none()
    if not inf:
        raise HTTPException(status_code=404, detail="Influencer profile not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(inf, field, value)

    # Auto-rescore after profile update
    score_result = scorer.compute_aria_score(
        data={
            "instagram_followers"       : inf.instagram_followers,
            "tiktok_followers"          : inf.tiktok_followers,
            "instagram_engagement_rate" : inf.instagram_engagement_rate or 3.5,
            "tiktok_engagement_rate"    : inf.tiktok_engagement_rate or 5.2,
            "city"                      : inf.city or "amman",
            "niche"                     : inf.niche or "general",
            "campaigns_completed"       : inf.campaigns_completed,
            "campaigns_total"           : inf.campaigns_total or 1,
            "on_time_deliveries"        : inf.on_time_deliveries,
            "disputes_raised"           : inf.disputes_raised,
            "monthly_growth_rate"       : inf.monthly_growth_rate,
            "account_age_days"          : inf.account_age_days,
        },
        niche=inf.niche or "general"
    )
    inf.aria_score         = score_result["aria_score"]
    inf.aria_tier          = score_result["tier"]
    inf.engagement_score   = score_result["breakdown"].get("engagement_score", 0)
    inf.authenticity_score = score_result["breakdown"].get("authenticity_score", 0)
    inf.relevance_score    = score_result["breakdown"].get("relevance_score", 0)
    inf.delivery_score     = score_result["breakdown"].get("reliability_score", 0)

    from datetime import datetime
    inf.last_scored_at = datetime.utcnow()

    await db.commit()
    logger.success(f"[ARIA::INFLUENCERS] Profile updated & rescored: {inf.id} | Score: {inf.aria_score}")
    return {
        "message"   : "Profile updated and rescored",
        "aria_score": inf.aria_score,
        "aria_tier" : inf.aria_tier,
    }


@router.get("/")
async def list_influencers(
    niche       : Optional[str]  = Query(None),
    min_score   : Optional[float]= Query(None),
    city        : Optional[str]  = Query(None),
    skip        : int            = 0,
    limit       : int            = 20,
    db          : AsyncSession   = Depends(get_db)
):
    """List influencers with ARIA scoring filters"""
    query = select(Influencer)

    if niche:
        query = query.where(Influencer.niche.ilike(f"%{niche}%"))
    if min_score:
        query = query.where(Influencer.aria_score >= min_score)
    if city:
        query = query.where(Influencer.city.ilike(f"%{city}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/match")
async def match_influencers(
    brief      : str,
    budget_jod : float,
    city       : Optional[str] = None,
    top_k      : int           = 10,
    db         : AsyncSession  = Depends(get_db),
):
    """AI-powered influencer matching using vector similarity + ARIA score"""
    from ...services.ai.matching_engine import ARIAMatchingEngine
    engine = ARIAMatchingEngine()
    brief_full = f"{brief} budget:{budget_jod} JOD" + (f" city:{city}" if city else "")
    try:
        results = engine.match(brief_full, top_k=top_k)
        logger.info(f"[ARIA::INFLUENCERS] Match query | results={len(results)}")
        return {"matches": results, "total": len(results), "brief": brief}
    except Exception as exc:
        logger.error(f"[ARIA::INFLUENCERS] Match failed: {exc}")
        return {"matches": [], "total": 0, "brief": brief, "error": str(exc)}


@router.post("/smart-search")
async def smart_search(
    payload : dict,
    db      : AsyncSession = Depends(get_db),
):
    """Natural language influencer search with ARIA scoring + niche/city boost"""
    brief       = payload.get("brief", "")
    budget_max  = float(payload.get("budget_max", 9999) or 9999)
    city_filter = payload.get("city", "")
    top_k       = int(payload.get("top_k", 10) or 10)

    stmt = select(Influencer).where(Influencer.is_available == True)
    if city_filter:
        stmt = stmt.where(Influencer.city.ilike(f"%{city_filter}%"))
    if budget_max < 9999:
        stmt = stmt.where(
            (Influencer.rate_per_post == None) | (Influencer.rate_per_post <= budget_max)
        )

    result  = await db.execute(stmt.limit(50))
    all_inf = result.scalars().all()

    if not all_inf:
        return {"results": [], "total": 0, "brief": brief}

    scored = []
    brief_lower = brief.lower()
    for inf in all_inf:
        score = float(inf.aria_score or 0)
        if brief_lower and inf.niche and inf.niche.lower() in brief_lower:
            score += 20
        if city_filter and inf.city and city_filter.lower() in inf.city.lower():
            score += 15
        scored.append({
            "id"                       : inf.id,
            "instagram_handle"         : inf.instagram_handle,
            "tiktok_handle"            : inf.tiktok_handle,
            "niche"                    : inf.niche,
            "city"                     : inf.city,
            "aria_score"               : inf.aria_score,
            "aria_tier"                : inf.aria_tier,
            "instagram_followers"      : inf.instagram_followers,
            "tiktok_followers"         : inf.tiktok_followers,
            "instagram_engagement_rate": inf.instagram_engagement_rate,
            "rate_per_post"            : inf.rate_per_post,
            "is_available"             : inf.is_available,
            "audience_gender_split"    : inf.audience_gender_split,
            "audience_age_split"       : inf.audience_age_split,
            "match_score"              : round(score, 1),
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return {"results": scored[:top_k], "total": len(scored), "brief": brief}


@router.post("/{influencer_id}/rescore")
async def rescore_influencer(
    influencer_id   : int,
    campaign_niche  : str = "general",
    db              : AsyncSession = Depends(get_db)
):
    """Trigger ARIA rescoring for a specific influencer"""
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer_id)
    )
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    score_result = scorer.compute_aria_score(
        data={
            "instagram_followers"       : influencer.instagram_followers,
            "tiktok_followers"          : influencer.tiktok_followers,
            "instagram_engagement_rate" : influencer.instagram_engagement_rate or 3.5,
            "tiktok_engagement_rate"    : influencer.tiktok_engagement_rate or 5.2,
            "city"                      : influencer.city or "amman",
            "niche"                     : influencer.niche or campaign_niche,
            "campaigns_completed"       : influencer.campaigns_completed,
            "campaigns_total"           : influencer.campaigns_total or 1,
            "on_time_deliveries"        : influencer.on_time_deliveries,
            "disputes_raised"           : influencer.disputes_raised,
            "monthly_growth_rate"       : influencer.monthly_growth_rate,
            "account_age_days"          : influencer.account_age_days,
        },
        niche=campaign_niche
    )

    # Persist updated score
    influencer.aria_score         = score_result["aria_score"]
    influencer.aria_tier          = score_result["tier"]
    influencer.engagement_score   = score_result["breakdown"].get("engagement_score", 0)
    influencer.authenticity_score = score_result["breakdown"].get("authenticity_score", 0)
    influencer.relevance_score    = score_result["breakdown"].get("relevance_score", 0)
    influencer.delivery_score     = score_result["breakdown"].get("reliability_score", 0)
    influencer.score_metadata     = score_result

    from datetime import datetime
    influencer.last_scored_at = datetime.utcnow()

    await db.commit()
    logger.success(
        f"[ARIA::INFLUENCERS] Rescored {influencer_id} | "
        f"Score: {score_result['aria_score']} | Tier: {score_result['tier']}"
    )
    return score_result
# ============================================================
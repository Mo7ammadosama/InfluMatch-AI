from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import os
from ...core.database import get_db
from ...models.campaign import Campaign, CampaignStatus, CampaignInfluencer
from ...models.campaign_report import CampaignReport, ReportStatus
from ...models.user import User, UserRole
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...schemas.campaign import CampaignCreate, CampaignResponse
from ...agents.guardian_agent import GuardianAgent
from ...services.escrow.escrow_engine import EscrowEngine
from ..dependencies.auth_deps import get_current_user, get_optional_user
from loguru import logger

_UPLOAD_ROOT = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "data", "uploads"
)
_ALLOWED_TYPES  = {"image/png", "image/jpeg", "application/pdf"}
_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router  = APIRouter(prefix="/campaigns", tags=["Campaigns"])
escrow  = EscrowEngine()

@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign — merchant resolved from JWT"""
    m_res = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = m_res.scalar_one_or_none()
    if not merchant:
        raise HTTPException(
            status_code=400,
            detail="Merchant profile not found. Create a merchant profile first."
        )

    campaign = Campaign(
        merchant_id             = merchant.id,
        title_ar                = data.title_ar,
        title_en                = data.title_en,
        description_ar          = data.description_ar,
        description_en          = data.description_en,
        niche                   = data.niche,
        total_budget            = data.total_budget,
        budget_per_influencer   = data.budget_per_influencer,
        start_date              = data.start_date,
        end_date                = data.end_date,
        submission_deadline     = data.submission_deadline,
        required_deliverables   = data.required_deliverables,
        hashtags                = data.hashtags,
        status                  = CampaignStatus.DRAFT
    )

    db.add(campaign)
    await db.flush()

    logger.success(f"[ARIA::CAMPAIGNS] Created campaign: {campaign.id} | merchant={merchant.id} | {data.title_ar}")
    return campaign


@router.get("/my")
async def list_my_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Influencer: campaigns they are assigned to via CampaignInfluencer join table"""
    inf_res = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    influencer = inf_res.scalar_one_or_none()
    if not influencer:
        return []

    assignments_res = await db.execute(
        select(CampaignInfluencer).where(CampaignInfluencer.influencer_id == influencer.id)
    )
    assignments = assignments_res.scalars().all()
    if not assignments:
        return []

    campaign_ids = [a.campaign_id for a in assignments]
    assignment_map = {a.campaign_id: a for a in assignments}

    campaigns_res = await db.execute(
        select(Campaign).where(Campaign.id.in_(campaign_ids))
    )
    campaigns = campaigns_res.scalars().all()

    return [
        {
            "id"               : c.id,
            "title_ar"         : c.title_ar,
            "title_en"         : c.title_en,
            "niche"            : c.niche,
            "total_budget"     : float(c.total_budget or 0),
            "status"           : c.status.value if c.status else "draft",
            "start_date"       : c.start_date.isoformat() if c.start_date else None,
            "end_date"         : c.end_date.isoformat() if c.end_date else None,
            "assignment_status": assignment_map[c.id].status if c.id in assignment_map else None,
            "agreed_rate_jod"  : float(assignment_map[c.id].agreed_rate_jod or 0) if c.id in assignment_map else 0,
        }
        for c in campaigns
    ]


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    status: CampaignStatus = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """List campaigns — role-based filtering: admin=all, merchant=own, influencer/public=active"""
    query = select(Campaign)

    if current_user:
        role = current_user.role
        if role == UserRole.MERCHANT:
            m_res = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
            merchant = m_res.scalar_one_or_none()
            if not merchant:
                return []
            query = query.where(Campaign.merchant_id == merchant.id)
        elif role == UserRole.INFLUENCER:
            if not status:
                query = query.where(Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.DRAFT]))
        # ADMIN — no filter, sees all
    else:
        # Unauthenticated: active/draft only
        if not status:
            query = query.where(Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.DRAFT]))

    if status:
        query = query.where(Campaign.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activate campaign → fund escrow → schedule Guardian jobs"""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = CampaignStatus.ACTIVE

    # Fund escrow
    escrow_tx = await escrow.fund_escrow(
        db, campaign_id, campaign.merchant_id, campaign.total_budget
    )

    logger.success(f"[ARIA::CAMPAIGNS] Activated: {campaign_id} | Escrow: {escrow_tx.id}")

    try:
        from ...services.notifications.notification_service import NotificationService
        # Resolve merchant's real email
        merchant_user_res = await db.execute(
            select(User).join(Merchant, Merchant.user_id == User.id)
            .where(Merchant.id == campaign.merchant_id)
        )
        merchant_user = merchant_user_res.scalar_one_or_none()
        merchant_email = merchant_user.email if merchant_user else "platform@influmatch.jo"
        NotificationService().notify_campaign_accepted(
            merchant_email, "+962790000000", campaign.title_ar or campaign.title_en or ""
        )
    except Exception as exc:
        logger.warning(f"[ARIA::CAMPAIGNS] Notification failed: {exc}")

    return {
        "campaign_id"   : campaign_id,
        "status"        : "ACTIVE",
        "escrow_id"     : escrow_tx.id,
        "amount_locked" : escrow_tx.gross_amount,
        "currency"      : "JOD"
    }


@router.post("/{campaign_id}/upload-report", status_code=201)
async def upload_campaign_report(
    campaign_id : int,
    file        : UploadFile = File(...),
    db          : AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Influencer uploads campaign delivery proof (image or PDF, max 10 MB)"""
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail=f"File type not allowed: {file.content_type}")

    contents = await file.read()
    if len(contents) > _MAX_SIZE_BYTES:
        raise HTTPException(status_code=422, detail="File exceeds 10 MB limit")

    # Verify campaign exists
    res = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Resolve influencer from JWT
    inf_res = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    influencer = inf_res.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=400, detail="Influencer profile not found. Create your profile first.")

    # Save file
    upload_dir = os.path.normpath(os.path.join(_UPLOAD_ROOT, str(campaign_id)))
    os.makedirs(upload_dir, exist_ok=True)
    ts        = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace(" ", "_") if file.filename else "upload"
    file_path = os.path.join(upload_dir, f"{ts}_{safe_name}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # Record in DB using real influencer_id from JWT
    report = CampaignReport(
        campaign_id   = campaign_id,
        influencer_id = influencer.id,
        file_path     = file_path,
        status        = ReportStatus.PENDING,
    )
    db.add(report)
    await db.flush()
    logger.success(f"[ARIA::CAMPAIGNS] Report uploaded campaign={campaign_id} | influencer={influencer.id} | file={safe_name}")

    try:
        from ...services.notifications.notification_service import NotificationService
        # Get merchant email from campaign
        campaign_res = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        camp = campaign_res.scalar_one_or_none()
        if camp:
            merchant_user_res = await db.execute(
                select(User).join(Merchant, Merchant.user_id == User.id)
                .where(Merchant.id == camp.merchant_id)
            )
            merchant_user = merchant_user_res.scalar_one_or_none()
            merchant_email = merchant_user.email if merchant_user else "platform@influmatch.jo"
        else:
            merchant_email = "platform@influmatch.jo"
        NotificationService().notify_milestone_released(merchant_email, "تقرير جديد من المؤثر", 0.0)
    except Exception as exc:
        logger.warning(f"[ARIA::CAMPAIGNS] Notification failed: {exc}")

    return {
        "report_id"   : report.id,
        "campaign_id" : campaign_id,
        "influencer_id": influencer.id,
        "file_name"   : safe_name,
        "status"      : "PENDING",
        "uploaded_at" : report.uploaded_at.isoformat(),
    }


@router.get("/{campaign_id}/reports")
async def get_campaign_reports(campaign_id: int, db: AsyncSession = Depends(get_db)):
    """List all uploaded reports for a campaign (merchant/admin view)"""
    res = await db.execute(
        select(CampaignReport).where(CampaignReport.campaign_id == campaign_id)
    )
    reports = res.scalars().all()
    return [
        {
            "id"           : r.id,
            "campaign_id"  : r.campaign_id,
            "influencer_id": r.influencer_id,
            "file_path"    : r.file_path,
            "status"       : r.status,
            "uploaded_at"  : r.uploaded_at.isoformat() if r.uploaded_at else None,
        }
        for r in reports
    ]
# ============================================================

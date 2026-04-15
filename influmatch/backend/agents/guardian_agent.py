from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from loguru import logger
import json

class GuardianAgent:
    def __init__(self, db_session_factory=None):
        self.scheduler = AsyncIOScheduler(
            job_defaults={"coalesce": True, "max_instances": 3, "misfire_grace_time": 300}
        )
        self.db_factory = db_session_factory
        self._setup_system_jobs()

    def _setup_system_jobs(self):
        self.scheduler.add_job(self._daily_scoring, CronTrigger(hour=2, minute=0), id="daily_scoring", replace_existing=True)
        self.scheduler.add_job(self._check_deadlines, CronTrigger(hour="*/6"), id="deadline_monitor", replace_existing=True)
        self.scheduler.add_job(self._process_escrow, CronTrigger(hour=9, minute=0), id="escrow_processor", replace_existing=True)
        self.scheduler.add_job(self._weekly_report, CronTrigger(day_of_week="sun", hour=8), id="weekly_report", replace_existing=True)
        logger.success("[ARIA::GUARDIAN] System jobs registered")

    def schedule_campaign_job(self, campaign_id: int, event: str, run_at: datetime) -> str:
        handlers = {
            "start": self._on_campaign_start, "deadline": self._on_deadline,
            "review": self._on_review, "payment": self._on_payment, "expire": self._on_expire,
        }
        handler = handlers.get(event)
        if not handler:
            return None
        job_id = f"campaign_{campaign_id}_{event}"
        self.scheduler.add_job(handler, DateTrigger(run_date=run_at), id=job_id, args=[campaign_id], replace_existing=True)
        logger.info(f"[ARIA::GUARDIAN] Scheduled {job_id} at {run_at}")
        return job_id

    async def _daily_scoring(self):
        logger.info("[ARIA::GUARDIAN] Running daily ARIA scoring...")
        if not self.db_factory:
            logger.warning("[ARIA::GUARDIAN] No DB factory — skipping scoring")
            return
        try:
            from ..models.influencer import Influencer
            from ..services.scoring.influencer_scorer import ARIAInfluencerScorer
            from sqlalchemy import select
            scorer = ARIAInfluencerScorer()
            async with self.db_factory() as db:
                result = await db.execute(select(Influencer))
                influencers = result.scalars().all()
                count = 0
                for inf in influencers:
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
                        niche=inf.niche or "general",
                    )
                    inf.aria_score = score_result["aria_score"]
                    inf.aria_tier  = score_result["tier"]
                    count += 1
                await db.commit()
            logger.success(f"[ARIA::GUARDIAN] Daily scoring complete | updated={count} influencers")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] Daily scoring failed: {exc}")

    async def _check_deadlines(self):
        logger.info("[ARIA::GUARDIAN] Checking campaign deadlines and milestone due dates...")
        if not self.db_factory:
            return
        try:
            from ..models.campaign import Campaign, CampaignStatus
            from ..models.milestone import CampaignMilestone, MilestoneStatus
            from sqlalchemy import select
            now = datetime.utcnow()
            async with self.db_factory() as db:
                res = await db.execute(
                    select(Campaign).where(
                        Campaign.status == CampaignStatus.IN_PROGRESS,
                        Campaign.end_date < now,
                    )
                )
                overdue = res.scalars().all()
                for campaign in overdue:
                    campaign.status = CampaignStatus.UNDER_REVIEW
                    logger.warning(f"[ARIA::GUARDIAN] Campaign {campaign.id} moved to UNDER_REVIEW (deadline passed)")

                ms_res = await db.execute(
                    select(CampaignMilestone).where(
                        CampaignMilestone.status == MilestoneStatus.PENDING,
                        CampaignMilestone.due_date < now,
                    )
                )
                overdue_ms = ms_res.scalars().all()
                for ms in overdue_ms:
                    logger.warning(f"[ARIA::GUARDIAN] Overdue milestone={ms.id} campaign={ms.campaign_id} title={ms.title}")

                await db.commit()
            logger.info(f"[ARIA::GUARDIAN] Deadline check done | campaigns={len(overdue)} | milestones={len(overdue_ms)}")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] Deadline check failed: {exc}")

    async def _process_escrow(self):
        logger.info("[ARIA::GUARDIAN] Processing auto escrow releases...")
        if not self.db_factory:
            return
        try:
            from ..models.escrow import EscrowTransaction, EscrowStatus
            from ..services.escrow.escrow_engine import EscrowEngine
            from ..services.notifications.notification_service import NotificationService
            from ..core.config import get_settings
            from sqlalchemy import select
            settings = get_settings()
            engine   = EscrowEngine()
            ns       = NotificationService()
            cutoff   = datetime.utcnow() - timedelta(days=settings.escrow_release_days)
            async with self.db_factory() as db:
                res = await db.execute(
                    select(EscrowTransaction).where(
                        EscrowTransaction.status == EscrowStatus.FUNDED,
                        EscrowTransaction.created_at < cutoff,
                    )
                )
                pending = res.scalars().all()
                for tx in pending:
                    try:
                        result = await engine.release_to_influencer(db, tx.id, "guardian_agent")
                        ns.notify_payment_transferred("influencer@platform.jo", float(result.get("net_amount", 0)))
                        logger.success(f"[ARIA::GUARDIAN] Auto-released escrow={tx.id}")
                    except Exception as exc:
                        logger.error(f"[ARIA::GUARDIAN] Auto-release failed escrow={tx.id}: {exc}")
            logger.info(f"[ARIA::GUARDIAN] Escrow processing done | processed={len(pending)}")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] Escrow processing failed: {exc}")

    async def _weekly_report(self):
        logger.info("[ARIA::GUARDIAN] Generating weekly report...")
        if not self.db_factory:
            logger.info("[ARIA::GUARDIAN] Weekly report (no DB): stub mode")
            return
        try:
            from ..models.campaign import Campaign, CampaignStatus
            from ..models.escrow import EscrowTransaction, EscrowStatus
            from ..models.user import User
            from sqlalchemy import select, func
            now  = datetime.utcnow()
            week = now - timedelta(days=7)
            async with self.db_factory() as db:
                total_campaigns = (await db.execute(select(func.count(Campaign.id)))).scalar() or 0
                total_volume    = (await db.execute(
                    select(func.sum(EscrowTransaction.gross_amount))
                )).scalar() or 0.0
                new_users_7d    = (await db.execute(
                    select(func.count(User.id)).where(User.created_at >= week)
                )).scalar() or 0
                disputes_open   = (await db.execute(
                    select(func.count(EscrowTransaction.id)).where(
                        EscrowTransaction.status == EscrowStatus.DISPUTED
                    )
                )).scalar() or 0

            report = {
                "generated_at"    : now.isoformat(),
                "total_campaigns" : total_campaigns,
                "total_volume_jod": round(float(total_volume), 3),
                "new_users_7d"    : new_users_7d,
                "disputes_open"   : disputes_open,
            }
            logger.success(f"[ARIA::GUARDIAN] Weekly report: {json.dumps(report)}")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] Weekly report failed: {exc}")
    async def _on_campaign_start(self, cid):
        if not self.db_factory:
            logger.info(f"[ARIA::GUARDIAN] Campaign {cid} STARTED (no DB)")
            return
        try:
            from ..models.booking import Booking, BookingStatus
            from ..services.notifications.notification_service import NotificationService
            from sqlalchemy import select
            async with self.db_factory() as session:
                bookings_q = await session.execute(
                    select(Booking).where(
                        Booking.campaign_id == cid,
                        Booking.status == BookingStatus.CONFIRMED,
                    )
                )
                bookings = bookings_q.scalars().all()
                ns = NotificationService()
                for b in bookings:
                    ns.send_whatsapp("", f"تذكير: يجب رفع محتوى الحملة #{cid} قبل الموعد النهائي")
                logger.info(f"[ARIA::GUARDIAN] Campaign #{cid} started — notified {len(bookings)} influencers")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] _on_campaign_start failed cid={cid}: {exc}")

    async def _on_deadline(self, cid):
        if not self.db_factory:
            logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} DEADLINE (no DB)")
            return
        try:
            from ..models.booking import Booking, BookingStatus
            from sqlalchemy import select
            async with self.db_factory() as session:
                result = await session.execute(
                    select(Booking).where(
                        Booking.campaign_id == cid,
                        Booking.status == BookingStatus.CONFIRMED,
                    )
                )
                overdue = result.scalars().all()
                for b in overdue:
                    logger.warning(f"[ARIA::GUARDIAN] Booking #{b.id} overdue — content not submitted")
                logger.info(f"[ARIA::GUARDIAN] Deadline check campaign #{cid} — {len(overdue)} overdue")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] _on_deadline failed cid={cid}: {exc}")

    async def _on_review(self, cid):
        if not self.db_factory:
            logger.info(f"[ARIA::GUARDIAN] Campaign {cid} REVIEW (no DB)")
            return
        try:
            from ..models.booking import Booking, BookingStatus
            from sqlalchemy import select
            async with self.db_factory() as session:
                result = await session.execute(
                    select(Booking).where(
                        Booking.campaign_id == cid,
                        Booking.status == BookingStatus.CONTENT_SUBMITTED,
                    )
                )
                pending = result.scalars().all()
                logger.info(f"[ARIA::GUARDIAN] Review triggered campaign #{cid} — {len(pending)} pending")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] _on_review failed cid={cid}: {exc}")

    async def _on_payment(self, cid):
        if not self.db_factory:
            logger.info(f"[ARIA::GUARDIAN] Campaign {cid} PAYMENT RELEASE (no DB)")
            return
        try:
            from ..models.booking import Booking, BookingStatus
            from ..services.escrow.escrow_engine import EscrowEngine
            from sqlalchemy import select
            async with self.db_factory() as session:
                result = await session.execute(
                    select(Booking).where(
                        Booking.campaign_id == cid,
                        Booking.status == BookingStatus.CONTENT_APPROVED,
                    )
                )
                approved = result.scalars().all()
                engine   = EscrowEngine()
                released = 0
                for b in approved:
                    try:
                        if b.escrow_id:
                            await engine.release_to_influencer(session, b.escrow_id, "guardian_agent")
                            b.status = BookingStatus.RELEASED
                            session.add(b)
                            released += 1
                    except Exception as exc:
                        logger.error(f"[ARIA::GUARDIAN] Auto-release failed booking #{b.id}: {exc}")
                await session.commit()
                logger.success(f"[ARIA::GUARDIAN] Auto-payment campaign #{cid} — released {released}/{len(approved)} bookings")
        except Exception as exc:
            logger.error(f"[ARIA::GUARDIAN] _on_payment failed cid={cid}: {exc}")

    async def _on_expire(self, cid):
        logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} EXPIRED")

    def start(self):
        self.scheduler.start()
        logger.success("[ARIA::GUARDIAN] Guardian Agent ONLINE")

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
        logger.info("[ARIA::GUARDIAN] Guardian Agent shutdown")

guardian = GuardianAgent()

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from loguru import logger

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

    async def _daily_scoring(self): logger.info("[ARIA::GUARDIAN] Running daily scoring...")
    async def _check_deadlines(self): logger.info("[ARIA::GUARDIAN] Checking deadlines...")
    async def _process_escrow(self): logger.info("[ARIA::GUARDIAN] Processing escrow releases...")
    async def _weekly_report(self): logger.info("[ARIA::GUARDIAN] Generating weekly report...")
    async def _on_campaign_start(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} STARTED")
    async def _on_deadline(self, cid): logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} DEADLINE")
    async def _on_review(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} REVIEW")
    async def _on_payment(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} PAYMENT RELEASE")
    async def _on_expire(self, cid): logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} EXPIRED")

    def start(self):
        self.scheduler.start()
        logger.success("[ARIA::GUARDIAN] Guardian Agent ONLINE")

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
        logger.info("[ARIA::GUARDIAN] Guardian Agent shutdown")

guardian = GuardianAgent()

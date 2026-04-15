import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx
from loguru import logger
from ...core.config import get_settings

settings = get_settings()


class NotificationService:

    def send_email(self, to: str, subject: str, body_ar: str, body_en: str) -> bool:
        html = f"""
        <html><body dir="rtl">
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                    background:#f9f9f9;border-radius:10px;padding:20px;">
            <div style="background:#533483;border-radius:8px;padding:12px;text-align:center;">
                <h2 style="color:white;margin:0;">InfluMatch.jo</h2>
            </div>
            <div style="padding:20px;color:#1a1a2e;direction:rtl;text-align:right;">
                <p style="font-size:16px;">{body_ar}</p>
            </div>
            <div style="padding:0 20px 20px;color:#555;direction:ltr;text-align:left;
                        border-top:1px solid #ddd;margin-top:12px;">
                <p style="font-size:13px;">{body_en}</p>
            </div>
            <p style="text-align:center;color:#aaa;font-size:11px;">
                InfluMatch.jo | Jordan Influencer Platform
            </p>
        </div>
        </body></html>
        """
        if not settings.smtp_user or settings.smtp_pass in ("", "your_smtp_password"):
            logger.info(f"[ARIA::NOTIFY] Email stub to={to} | subject={subject}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = settings.smtp_user
            msg["To"]      = to
            msg.attach(MIMEText(html, "html", "utf-8"))

            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_pass)
                server.sendmail(settings.smtp_user, to, msg.as_string())
            logger.success(f"[ARIA::NOTIFY] Email sent to={to}")
            return True
        except Exception as exc:
            logger.error(f"[ARIA::NOTIFY] Email failed to={to}: {exc}")
            return False

    def send_whatsapp(self, phone: str, message: str) -> bool:
        if settings.whatsapp_token == "stub_token":
            logger.info(f"[ARIA::NOTIFY] WhatsApp stub phone={phone} | msg={message[:60]}")
            return True
        try:
            r = httpx.post(
                settings.whatsapp_api_url,
                json={"phone": phone, "message": message},
                headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
                timeout=10,
            )
            ok = r.status_code == 200
            if ok:
                logger.success(f"[ARIA::NOTIFY] WhatsApp sent phone={phone}")
            else:
                logger.warning(f"[ARIA::NOTIFY] WhatsApp failed phone={phone} status={r.status_code}")
            return ok
        except Exception as exc:
            logger.error(f"[ARIA::NOTIFY] WhatsApp error: {exc}")
            return False

    def notify_campaign_accepted(self, merchant_email: str, influencer_phone: str, campaign_title: str):
        self.send_email(
            to       = merchant_email,
            subject  = f"InfluMatch.jo — تم قبول الحملة: {campaign_title}",
            body_ar  = f"تهانينا! تم قبول حملتك <b>{campaign_title}</b> من قِبَل المؤثر.",
            body_en  = f"Your campaign <b>{campaign_title}</b> has been accepted by the influencer.",
        )
        self.send_whatsapp(influencer_phone, f"تم قبول الحملة: {campaign_title} | InfluMatch.jo")

    def notify_payment_transferred(self, influencer_email: str, amount_jod: float):
        self.send_email(
            to       = influencer_email,
            subject  = "InfluMatch.jo — تم تحويل مستحقاتك",
            body_ar  = f"تم إصدار دفعة بقيمة <b>{amount_jod:.3f} JOD</b> إلى حسابك.",
            body_en  = f"A payment of <b>{amount_jod:.3f} JOD</b> has been released to your account.",
        )

    def notify_dispute_raised(self, merchant_email: str, influencer_email: str, campaign_title: str):
        for email in [merchant_email, influencer_email]:
            self.send_email(
                to       = email,
                subject  = f"InfluMatch.jo — نزاع مرفوع: {campaign_title}",
                body_ar  = f"تم رفع نزاع بشأن الحملة <b>{campaign_title}</b>. سيقوم فريق ARIA بالمراجعة خلال 48 ساعة.",
                body_en  = f"A dispute was raised for campaign <b>{campaign_title}</b>. ARIA team will review within 48h.",
            )

    def notify_milestone_released(self, influencer_email: str, milestone_title: str, amount_jod: float):
        self.send_email(
            to       = influencer_email,
            subject  = f"InfluMatch.jo — تم إصدار مرحلة: {milestone_title}",
            body_ar  = f"تم إصدار مرحلة <b>{milestone_title}</b> بقيمة <b>{amount_jod:.3f} JOD</b>.",
            body_en  = f"Milestone <b>{milestone_title}</b> released: <b>{amount_jod:.3f} JOD</b>.",
        )

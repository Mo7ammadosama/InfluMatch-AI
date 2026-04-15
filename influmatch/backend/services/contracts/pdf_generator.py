import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from loguru import logger

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _ARABIC_SUPPORT = True
except ImportError:
    _ARABIC_SUPPORT = False
    logger.warning("[ARIA::PDF] arabic-reshaper or python-bidi not installed — Arabic text may not display correctly")


def _rtl(text: str) -> str:
    if not _ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# Colour palette
PURPLE      = HexColor("#533483")
DARK_BG     = HexColor("#0a0a1a")
ACCENT      = HexColor("#7c3aed")
LIGHT_GREY  = HexColor("#e8e8f0")
TEXT_DARK   = HexColor("#1a1a2e")
GREEN       = HexColor("#00c853")


class ContractPDFGenerator:
    PAGE_W, PAGE_H = A4

    def generate(
        self,
        contract_text : str,
        merchant_name : str,
        influencer_name: str,
        amount_jod    : float,
        campaign_title: str,
    ) -> bytes:
        buf    = io.BytesIO()
        c      = canvas.Canvas(buf, pagesize=A4)
        w, h   = self.PAGE_W, self.PAGE_H

        self._draw_background(c, w, h)
        self._draw_watermark(c, w, h)
        self._draw_header(c, w, h)
        y = self._draw_meta(c, w, h, merchant_name, influencer_name, amount_jod, campaign_title)
        y = self._draw_body(c, w, h, contract_text, y)
        self._draw_signatures(c, w, h)
        self._draw_footer(c, w, h)

        c.showPage()
        c.save()
        pdf_bytes = buf.getvalue()
        logger.success(f"[ARIA::PDF] Generated {len(pdf_bytes)} bytes | campaign={campaign_title}")
        return pdf_bytes

    def _draw_background(self, c: canvas.Canvas, w: float, h: float):
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=True, stroke=False)
        c.setFillColor(PURPLE)
        c.rect(0, h - 2.5*cm, w, 2.5*cm, fill=True, stroke=False)
        c.setFillColor(PURPLE)
        c.rect(0, 0, w, 1.2*cm, fill=True, stroke=False)

    def _draw_watermark(self, c: canvas.Canvas, w: float, h: float):
        c.saveState()
        c.setFillColor(HexColor("#f0eef8"))
        c.setFont("Helvetica-Bold", 52)
        c.translate(w / 2, h / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, "InfluMatch.jo VERIFIED")
        c.restoreState()

    def _draw_header(self, c: canvas.Canvas, w: float, h: float):
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(w / 2, h - 1.5*cm, "InfluMatch.jo")
        c.setFont("Helvetica", 10)
        title_ar = _rtl("منصة InfluMatch.jo — وثيقة رسمية | Official Contract Document")
        c.drawCentredString(w / 2, h - 2.1*cm, title_ar)

    def _draw_meta(self, c: canvas.Canvas, w: float, h: float,
                   merchant: str, influencer: str, amount: float, campaign: str) -> float:
        y = h - 3.5*cm
        c.setFillColor(LIGHT_GREY)
        c.roundRect(1.5*cm, y - 2.2*cm, w - 3*cm, 2*cm, 8, fill=True, stroke=False)

        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 9)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

        labels = [
            (f"Campaign: {campaign}", 2*cm, y - 0.7*cm),
            (f"Merchant: {merchant}",  2*cm, y - 1.2*cm),
            (f"Influencer: {influencer}", w/2, y - 0.7*cm),
            (f"Amount: {amount:.3f} JOD | Date: {date_str}", w/2, y - 1.2*cm),
        ]
        for text, x, yy in labels:
            c.drawString(x, yy, text)

        return y - 2.8*cm

    def _draw_body(self, c: canvas.Canvas, w: float, h: float,
                   text: str, start_y: float) -> float:
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica", 8.5)

        lines = text.split("\n") if text else ["[No contract text provided]"]
        y = start_y
        left_margin  = 1.8*cm
        right_margin = w - 1.8*cm
        line_height  = 0.45*cm
        bottom_limit = 3*cm

        for raw_line in lines:
            if y < bottom_limit:
                c.showPage()
                self._draw_background(c, w, h)
                self._draw_watermark(c, w, h)
                self._draw_footer(c, w, h)
                y = h - 2*cm

            display = _rtl(raw_line) if any("\u0600" <= ch <= "\u06FF" for ch in raw_line) else raw_line
            c.drawString(left_margin, y, display[:120])
            y -= line_height

        return y

    def _draw_signatures(self, c: canvas.Canvas, w: float, h: float):
        y = 4.5*cm
        c.setFillColor(LIGHT_GREY)
        c.roundRect(1.5*cm, y - 0.5*cm, w - 3*cm, 2*cm, 6, fill=True, stroke=False)

        c.setStrokeColor(PURPLE)
        c.setLineWidth(0.5)
        seg_w = (w - 3*cm) / 3
        x0    = 1.5*cm

        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 8)
        for i, label in enumerate([_rtl("توقيع التاجر"), _rtl("توقيع المؤثر"), _rtl("ختم المنصة")]):
            cx = x0 + seg_w * i + seg_w / 2
            c.drawCentredString(cx, y + 1.2*cm, label)
            c.line(cx - seg_w*0.35, y + 0.3*cm, cx + seg_w*0.35, y + 0.3*cm)

        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x0 + seg_w * 2 + seg_w / 2, y + 0.6*cm, "ARIA VERIFIED")

    def _draw_footer(self, c: canvas.Canvas, w: float, h: float):
        c.setFillColor(white)
        c.setFont("Helvetica", 7)
        footer = _rtl("وفقاً لقانون المعاملات الإلكترونية الأردني رقم 15 لسنة 2015  |  influmatch.jo")
        c.drawCentredString(w / 2, 0.4*cm, footer)

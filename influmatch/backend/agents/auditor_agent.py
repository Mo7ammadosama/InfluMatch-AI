import json, base64, re
from typing import Dict, Optional
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from backend.core.config import get_settings

settings = get_settings()

AUDIT_SYSTEM = '''You are ARIA AI Auditor for WaslAI.jo Jordan.
Respond ONLY with a valid JSON object — no markdown, no code fences, no extra text.
Use this exact schema:
{"audit_passed":true,"overall_score":85,"checks":{"brand_mentioned":true,"hashtags_present":true,"content_quality":80,"engagement_authentic":true,"platform_compliant":true},"issues_found":[],"recommendations":[],"arabic_caption_quality":80,"rejection_reason":null,"confidence":0.9}

Scoring guide for overall_score (0-100):
- 80-100: Brand clearly mentioned, 3+ relevant hashtags, good quality Arabic/English caption
- 60-79: Brand or hashtags partially present
- 40-59: Missing brand or hashtags
- 0-39: Spam, irrelevant, or empty content
Set audit_passed=true when overall_score >= 60.'''


def _parse_json_response(text: str) -> Dict:
    """Robustly parse JSON from model response, handling code fences."""
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    return json.loads(text)


class AIAuditorAgent:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def audit_content_submission(self, submission: Dict, campaign_requirements: Dict) -> Dict:
        logger.info(f"[ARIA::AUDITOR] Auditing | platform={submission.get('platform')}")
        text_audit = await self._audit_caption(submission.get("caption", ""), campaign_requirements)
        logger.info(f"[ARIA::AUDITOR] Text audit score={text_audit.get('overall_score')} passed={text_audit.get('audit_passed')}")
        visual_audit = None
        if submission.get("content_url"):
            visual_audit = await self._audit_visual(submission["content_url"], campaign_requirements)
        final = self._final_decision(text_audit, visual_audit)
        logger.success(f"[ARIA::AUDITOR] Verdict: {final['verdict']} | score={final['combined_score']}")
        return {"submission_id": submission.get("id"), "text_audit": text_audit, "visual_audit": visual_audit, "final_decision": final}

    async def _audit_caption(self, caption: str, req: Dict) -> Dict:
        if not caption or not caption.strip():
            return {"audit_passed": False, "overall_score": 0, "error": "Empty caption"}
        prompt = (
            f"Audit this influencer caption for a WaslAI.jo campaign:\n\n"
            f"CAPTION:\n{caption}\n\n"
            f"CAMPAIGN REQUIREMENTS:\n"
            f"- Brand: {req.get('brand_name_en') or 'WaslAI'}\n"
            f"- Niche: {req.get('niche', 'general')}\n"
            f"- Required hashtags: {req.get('hashtags', [])}\n\n"
            f"Score the caption honestly. If it has a brand mention and hashtags, score 75+."
        )
        try:
            resp = self._get_client().messages.create(
                model=settings.claude_model, max_tokens=512,
                system=AUDIT_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.content[0].text
            logger.debug(f"[ARIA::AUDITOR] Raw caption audit response: {raw[:200]}")
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"[ARIA::AUDITOR] Caption audit failed: {e}")
            return {"audit_passed": False, "overall_score": 0, "error": str(e)}

    async def _audit_visual(self, image_url: str, req: Dict) -> Dict:
        """Skip visual audit for non-image URLs (Instagram pages, etc.)"""
        # Only attempt visual audit for direct image URLs
        if not any(image_url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
            logger.info(f"[ARIA::AUDITOR] Skipping visual audit for non-image URL")
            return {"audit_passed": True, "overall_score": 80, "visual_audit_skipped": True}
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.get(image_url, timeout=15)
                img_data = base64.b64encode(r.content).decode()
                content_type = r.headers.get("content-type", "image/jpeg")
            prompt = f"Analyze image for brand compliance. Brand: {req.get('brand_name_en') or 'WaslAI'}. Niche: {req.get('niche', 'general')}."
            resp = self._get_client().messages.create(
                model=settings.claude_model, max_tokens=512,
                system=AUDIT_SYSTEM,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": content_type, "data": img_data}},
                    {"type": "text", "text": prompt}
                ]}]
            )
            return _parse_json_response(resp.content[0].text)
        except Exception as e:
            logger.error(f"[ARIA::AUDITOR] Visual audit error: {e}")
            return {"audit_passed": True, "overall_score": 80, "visual_audit_skipped": True}

    def _final_decision(self, text_audit: Dict, visual_audit: Optional[Dict]) -> Dict:
        t_score = float(text_audit.get("overall_score", 0) or 0)
        v_score = float(visual_audit.get("overall_score", 80) if visual_audit else 80)
        combined = (t_score * 0.6) + (v_score * 0.4)
        t_pass = text_audit.get("audit_passed", False)
        v_pass = visual_audit.get("audit_passed", True) if visual_audit else True
        return {
            "verdict": "APPROVED" if (t_pass and v_pass and combined >= 65) else "REJECTED",
            "combined_score": round(combined, 2),
            "requires_human_review": 55 <= combined < 65,
            "auto_approved": combined >= 85,
        }


auditor = AIAuditorAgent()

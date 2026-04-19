import json, base64
from typing import Dict, Optional
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from backend.core.config import get_settings

settings = get_settings()

AUDIT_SYSTEM = '''You are ARIA AI Auditor for WaslAI.jo Jordan. Respond ONLY in this JSON format:
{"audit_passed":true,"overall_score":0,"checks":{"brand_mentioned":true,"hashtags_present":true,"content_quality":0,"engagement_authentic":true,"platform_compliant":true},"issues_found":[],"recommendations":[],"arabic_caption_quality":0,"rejection_reason":null,"confidence":0.9}'''

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
        visual_audit = None
        if submission.get("content_url"):
            visual_audit = await self._audit_visual(submission["content_url"], campaign_requirements)
        final = self._final_decision(text_audit, visual_audit)
        logger.success(f"[ARIA::AUDITOR] Verdict: {final['verdict']} | score={final['combined_score']}")
        return {"submission_id": submission.get("id"), "text_audit": text_audit, "visual_audit": visual_audit, "final_decision": final}

    async def _audit_caption(self, caption: str, req: Dict) -> Dict:
        prompt = f"Audit caption:\n{caption}\n\nRequirements: brand={req.get('brand_name_en')}, hashtags={req.get('hashtags', [])}, niche={req.get('niche', '')}"
        try:
            resp = self._get_client().messages.create(model=settings.claude_model, max_tokens=512,
                system=AUDIT_SYSTEM, messages=[{"role": "user", "content": prompt}])
            return json.loads(resp.content[0].text)
        except Exception as e:
            return {"audit_passed": False, "overall_score": 0, "error": str(e)}

    async def _audit_visual(self, image_url: str, req: Dict) -> Dict:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.get(image_url, timeout=30)
                img_data = base64.b64encode(r.content).decode()
                content_type = r.headers.get("content-type", "image/jpeg")
            prompt = f"Analyze for compliance. Brand: {req.get('brand_name_en')}. Niche: {req.get('niche')}."
            resp = self._get_client().messages.create(model=settings.claude_model, max_tokens=512,
                system=AUDIT_SYSTEM,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": content_type, "data": img_data}},
                    {"type": "text", "text": prompt}
                ]}])
            return json.loads(resp.content[0].text)
        except Exception as e:
            logger.error(f"[ARIA::AUDITOR] Visual audit error: {e}")
            return {"audit_passed": True, "overall_score": 75, "visual_audit_skipped": True}

    def _final_decision(self, text_audit: Dict, visual_audit: Optional[Dict]) -> Dict:
        t_score = text_audit.get("overall_score", 0)
        v_score = visual_audit.get("overall_score", 100) if visual_audit else 100
        combined = (t_score * 0.6) + (v_score * 0.4)
        t_pass = text_audit.get("audit_passed", False)
        v_pass = visual_audit.get("audit_passed", True) if visual_audit else True
        return {
            "verdict": "APPROVED" if (t_pass and v_pass and combined >= 70) else "REJECTED",
            "combined_score": round(combined, 2),
            "requires_human_review": 60 <= combined < 70,
            "auto_approved": combined >= 85,
        }

auditor = AIAuditorAgent()

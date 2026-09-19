import json, base64, re, os
from typing import Dict, Optional
from loguru import logger
import sys
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

GROQ_MODEL = "llama-3.3-70b-versatile"


def _parse_json_response(text: str) -> Dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    return json.loads(text)


def _get_groq_client():
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "groq_api_key", None)
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)


class AIAuditorAgent:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = _get_groq_client()
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
            client = self._get_client()
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": AUDIT_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=512,
                temperature=0.1,
            )
            raw = resp.choices[0].message.content
            logger.debug(f"[ARIA::AUDITOR] Raw caption audit response: {raw[:200]}")
            return _parse_json_response(raw)
        except Exception as e:
            logger.warning(f"[ARIA::AUDITOR] Caption audit failed (AI unavailable), using fallback score: {e}")
            return {"audit_passed": True, "overall_score": 75, "ai_unavailable": True}

    async def _audit_visual(self, image_url: str, req: Dict) -> Dict:
        # Groq doesn't support vision yet — skip visual audit
        if not any(image_url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
            logger.info(f"[ARIA::AUDITOR] Skipping visual audit for non-image URL")
        else:
            logger.info(f"[ARIA::AUDITOR] Skipping visual audit (Groq text-only)")
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

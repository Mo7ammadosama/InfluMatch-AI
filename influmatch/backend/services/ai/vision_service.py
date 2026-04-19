"""VisionService — thin wrapper around AIAuditorAgent's visual audit capability."""
from ...agents.auditor_agent import AIAuditorAgent


class VisionService:
    def __init__(self):
        self._auditor = AIAuditorAgent()

    async def analyze_content(self, image_url: str, requirements: dict) -> dict:
        """Analyze an image for brand compliance and content quality.

        Returns the raw visual audit dict from the AuditorAgent, including
        keys: overall_score, brand_compliance, content_quality, recommendations.
        """
        return await self._auditor._audit_visual(image_url, requirements)

    async def score_content_quality(self, content_url: str, brief: str) -> float:
        """Return a 0–100 quality score for the given content URL."""
        result = await self.analyze_content(content_url, {"niche": brief})
        return float(result.get("overall_score", 70))


vision_service = VisionService()

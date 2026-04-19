"""
WaslAI.jo — Claude API Client
Primary LLM: claude-opus-4-6 | Fallback: OpenAI GPT-4o
"""
from loguru import logger
from app.config import settings


class ClaudeClient:
    def __init__(self):
        self._client = None
        self._openai_client = None

    def _get_claude(self):
        if not self._client:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def _get_openai(self):
        if not self._openai_client:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        use_fallback: bool = False,
    ) -> str:
        max_tokens = max_tokens or settings.claude_max_tokens

        if not use_fallback:
            try:
                client = self._get_claude()
                kwargs = {
                    "model": settings.claude_model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system:
                    kwargs["system"] = system

                response = client.messages.create(**kwargs)
                logger.debug(f"Claude response | tokens={response.usage.output_tokens}")
                return response.content[0].text
            except Exception as e:
                logger.warning(f"Claude failed, switching to OpenAI fallback: {e}")
                use_fallback = True

        if use_fallback:
            client = self._get_openai()
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=max_tokens,
            )
            logger.debug(f"OpenAI fallback response | model={settings.openai_model}")
            return response.choices[0].message.content

    async def generate_campaign_brief(self, campaign_data: dict) -> str:
        system = (
            "You are an expert marketing strategist for the Jordan market. "
            "Generate concise, actionable campaign briefs in both Arabic and English. "
            "Focus on Jordan-specific market insights, local influencer culture, and JOD pricing."
        )
        prompt = f"""Generate a marketing campaign brief for:
Campaign: {campaign_data.get('title')}
Budget: {campaign_data.get('total_budget_jod')} JOD
Target: {campaign_data.get('target_categories')}
Required Platforms: {campaign_data.get('required_platforms')}
Min Followers: {campaign_data.get('min_followers'):,}
Description: {campaign_data.get('description')}

Provide: 1) Campaign summary (EN+AR), 2) Key message, 3) Content guidelines, 4) Success metrics."""

        return await self.complete(prompt, system=system, max_tokens=1024)


claude_client = ClaudeClient()

# ============================================================
# COMPONENT 25: backend/services/ai/llm_service.py
# Unified LLM service — Claude primary + GPT-4o fallback
# ============================================================

from anthropic import Anthropic
from typing import Optional, List, Dict
from loguru import logger
from ...core.config import get_settings

settings = get_settings()


class ARIALLMService:
    """
    Unified LLM Service
    Primary  : claude-opus-4-5 (Anthropic)
    Fallback : GPT-4o (OpenAI) — activates on primary failure
    """

    def __init__(self):
        self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        self._openai_client   = None  # Lazy init

    @property
    def openai_client(self):
        """Lazy OpenAI client initialization"""
        if self._openai_client is None and getattr(settings, "openai_api_key", None):
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.warning("[ARIA::LLM] OpenAI not available — fallback disabled")
        return self._openai_client

    async def generate(
        self,
        system_prompt : str,
        user_message  : str,
        max_tokens    : int           = 2048,
        temperature   : float         = 0.7,
        history       : List[Dict]    = None,
        force_provider: Optional[str] = None
    ) -> Dict:
        """
        Generate text with automatic fallback.
        Returns: {text, provider, tokens_used, success}
        """
        messages = list(history or [])
        messages.append({"role": "user", "content": user_message})

        # Try Claude first (unless forced to OpenAI)
        if force_provider != "openai":
            try:
                result = self._call_claude(system_prompt, messages, max_tokens)
                logger.debug(
                    f"[ARIA::LLM] Claude response | Tokens: {result['tokens_used']}"
                )
                return result
            except Exception as e:
                logger.warning(f"[ARIA::LLM] Claude failed: {e} — trying fallback")

        # Fallback to GPT-4o
        if self.openai_client:
            try:
                result = self._call_openai(system_prompt, messages, max_tokens)
                logger.info(
                    f"[ARIA::LLM] GPT-4o fallback used | Tokens: {result['tokens_used']}"
                )
                return result
            except Exception as e:
                logger.error(f"[ARIA::LLM] Both providers failed: {e}")

        raise RuntimeError("[ARIA::LLM] All LLM providers failed — check API keys")

    def _call_claude(
        self,
        system    : str,
        messages  : List[Dict],
        max_tokens: int
    ) -> Dict:
        response = self.anthropic_client.messages.create(
            model      = "claude-opus-4-5",
            max_tokens = max_tokens,
            system     = system,
            messages   = messages
        )
        return {
            "text"        : response.content[0].text,
            "provider"    : "claude-opus-4-5",
            "tokens_used" : response.usage.output_tokens,
            "success"     : True
        }

    def _call_openai(
        self,
        system    : str,
        messages  : List[Dict],
        max_tokens: int
    ) -> Dict:
        oai_messages = [{"role": "system", "content": system}] + messages
        response = self.openai_client.chat.completions.create(
            model      = "gpt-4o",
            messages   = oai_messages,
            max_tokens = max_tokens
        )
        return {
            "text"        : response.choices[0].message.content,
            "provider"    : "gpt-4o-fallback",
            "tokens_used" : response.usage.completion_tokens,
            "success"     : True
        }

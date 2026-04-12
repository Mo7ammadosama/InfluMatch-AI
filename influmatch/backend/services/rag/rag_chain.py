from loguru import logger
from typing import Optional
from .vector_store import InfluMatchVectorStore
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.core.config import get_settings

settings = get_settings()

class SmartContractRAG:
    def __init__(self):
        self.vector_store = InfluMatchVectorStore()
        self._client = None

    def _get_client(self):
        if not self._client:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate_contract(self, merchant_name: str, influencer_name: str,
                                 campaign_details: dict, language: str = "ar") -> str:
        query = f"contract influencer merchant {campaign_details.get('niche', '')}"
        ctx = self.vector_store.semantic_search(query, "contract", top_k=3)
        ctx += self.vector_store.semantic_search(query, "policy", top_k=2)
        context_text = "\n\n".join([r["text"] for r in ctx]) if ctx else "No prior contracts loaded."
        lang_instr = "Generate the contract in Arabic (RTL)." if language == "ar" else "Generate in English."
        system = f"You are ARIA legal AI for InfluMatch.jo Jordan. {lang_instr}\n\nContext:\n{context_text}"
        user_msg = f"Contract between Merchant: {merchant_name} and Influencer: {influencer_name}\nCampaign: {campaign_details}"
        client = self._get_client()
        resp = client.messages.create(model=settings.claude_model, max_tokens=4096,
            system=system, messages=[{"role": "user", "content": user_msg}])
        logger.success(f"[ARIA::RAG] Contract generated | lang={language}")
        return resp.content[0].text

    async def answer_policy_question(self, question: str, language: str = "ar") -> str:
        ctx = self.vector_store.semantic_search(question, "policy", top_k=4)
        context_text = "\n\n".join([r["text"] for r in ctx]) if ctx else ""
        lang_instr = "Reply in Arabic." if language == "ar" else "Reply in English."
        system = f"You are ARIA platform advisor for InfluMatch.jo Jordan. {lang_instr}\nContext:\n{context_text}"
        client = self._get_client()
        resp = client.messages.create(model=settings.claude_model, max_tokens=1024,
            system=system, messages=[{"role": "user", "content": question}])
        return resp.content[0].text

rag_chain = SmartContractRAG()

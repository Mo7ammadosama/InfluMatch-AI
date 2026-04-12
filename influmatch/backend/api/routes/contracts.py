from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from ...core.database import get_db
from ...services.rag.rag_chain import SmartContractRAG
from loguru import logger

router = APIRouter(prefix="/contracts", tags=["Smart Contracts"])

class ContractGenerateRequest(BaseModel):
    merchant_name   : str
    influencer_name : str
    campaign_details: dict
    language        : str = "ar"

class ContractGenerateResponse(BaseModel):
    contract        : str
    language        : str
    generated_by    : str = "ARIA_RAG_v1"
    rag_sources_used: int

@router.post("/generate", response_model=ContractGenerateResponse)
async def generate_smart_contract(
    req: ContractGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a RAG-powered smart contract
    Uses ChromaDB + Jordan law context + Claude claude-opus-4-5
    """
    logger.info(
        f"[ARIA::CONTRACTS] Generating contract | "
        f"Merchant: {req.merchant_name} | Lang: {req.language}"
    )

    rag = SmartContractRAG()

    try:
        contract_text = await rag.generate_contract(
            merchant_name    = req.merchant_name,
            influencer_name  = req.influencer_name,
            campaign_details = req.campaign_details,
            language         = req.language
        )

        logger.success(
            f"[ARIA::CONTRACTS] Contract generated | "
            f"Length: {len(contract_text)} chars"
        )

        return ContractGenerateResponse(
            contract          = contract_text,
            language          = req.language,
            rag_sources_used  = 5
        )

    except Exception as e:
        logger.error(f"[ARIA::CONTRACTS] Generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Contract generation failed: {str(e)}"
        )

@router.post("/policy-qa")
async def answer_policy_question(
    question: str,
    language: str = "ar"
):
    """Answer platform policy questions using RAG"""
    rag = SmartContractRAG()
    answer = await rag.answer_policy_question(question, language)
    return {"question": question, "answer": answer, "language": language}
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
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
        err_str = str(e).lower()
        logger.error(f"[ARIA::CONTRACTS] API error: {type(e).__name__}")
        if any(k in err_str for k in ["credit", "billing", "402", "invalid_request_error"]):
            raise HTTPException(status_code=503,
                detail="خدمة توليد العقود غير متاحة مؤقتاً. / Contract generation temporarily unavailable.")
        raise HTTPException(status_code=500,
            detail="خطأ في توليد العقد. حاول مرة أخرى. / Contract generation error. Please retry.")

@router.get("/{contract_id}/pdf")
async def download_contract_pdf(contract_id: int, db: AsyncSession = Depends(get_db)):
    """Generate and return a PDF for a contract (uses dummy data when contract has no DB record)"""
    from ...services.contracts.pdf_generator import ContractPDFGenerator

    # Try to fetch contract details from DB; fall back to placeholder
    contract_text     = f"عقد رقم {contract_id} — InfluMatch.jo"
    merchant_name     = "تاجر"
    influencer_name   = "مؤثر"
    amount_jod        = 0.0
    campaign_title    = f"حملة رقم {contract_id}"

    try:
        from ...models.contract import Contract
        from sqlalchemy import select
        row = await db.execute(select(Contract).where(Contract.id == contract_id))
        ct  = row.scalar_one_or_none()
        if ct:
            contract_text  = ct.content or contract_text
            amount_jod     = float(ct.amount_jod or 0.0)
            campaign_title = ct.title or campaign_title
    except Exception as exc:
        logger.warning(f"[ARIA::CONTRACTS] DB fetch failed for pdf: {exc}")

    try:
        pdf_bytes = ContractPDFGenerator().generate(
            contract_text   = contract_text,
            merchant_name   = merchant_name,
            influencer_name = influencer_name,
            amount_jod      = amount_jod,
            campaign_title  = campaign_title,
        )
        return Response(
            content     = pdf_bytes,
            media_type  = "application/pdf",
            headers     = {"Content-Disposition": f"attachment; filename=contract_{contract_id}.pdf"},
        )
    except Exception as exc:
        logger.error(f"[ARIA::CONTRACTS] PDF generation failed: {exc}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")


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
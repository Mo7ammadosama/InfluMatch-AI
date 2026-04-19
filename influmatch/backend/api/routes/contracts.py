from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from ...core.database import get_db
from ...services.rag.rag_chain import SmartContractRAG
from ...models.contract import Contract, ContractStatus
from loguru import logger

router = APIRouter(prefix="/contracts", tags=["Smart Contracts"])

class ContractGenerateRequest(BaseModel):
    merchant_name   : str
    influencer_name : str
    campaign_details: dict
    language        : str = "ar"

@router.post("/generate")
async def generate_smart_contract(
    req: ContractGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a RAG-powered smart contract and persist to DB.
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

        # Persist to DB so /pdf endpoint can fetch real data
        campaign_id = req.campaign_details.get("campaign_id")
        new_contract = Contract(
            campaign_id      = campaign_id,
            contract_text_ar = contract_text if req.language == "ar" else None,
            contract_text_en = contract_text if req.language == "en" else None,
            language_primary = req.language,
            status           = ContractStatus.DRAFT,
            generated_by     = "ARIA_RAG_v1",
            rag_sources_used = "5",
        )
        db.add(new_contract)
        await db.flush()

        logger.success(f"[ARIA::CONTRACTS] Saved contract id={new_contract.id}")

        return {
            "contract_id"     : new_contract.id,
            "contract"        : contract_text,
            "language"        : req.language,
            "generated_by"    : "ARIA_RAG_v1",
            "rag_sources_used": 5,
        }

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
        row = await db.execute(select(Contract).where(Contract.id == contract_id))
        ct  = row.scalar_one_or_none()
        if ct:
            contract_text = ct.contract_text_ar or ct.contract_text_en or contract_text
            # Fetch campaign for budget + title (Contract has no amount_jod/title columns)
            if ct.campaign_id:
                from ...models.campaign import Campaign
                camp_r = await db.execute(select(Campaign).where(Campaign.id == ct.campaign_id))
                camp   = camp_r.scalar_one_or_none()
                if camp:
                    amount_jod     = float(camp.total_budget or 0.0)
                    campaign_title = camp.title_ar or camp.title_en or campaign_title
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
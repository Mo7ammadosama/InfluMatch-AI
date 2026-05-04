"""
WaslAI.jo — Contracts Router
Contract generation and platform policy Q&A.
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.models.user import User
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

PLATFORM_POLICIES = """
WaslAI.jo Platform Policies (Jordan B2B Influencer Marketing):

1. PAYMENT & ESCROW
   - All deal payments are held in escrow until content is approved.
   - Platform fee: 10% of the agreed deal amount.
   - VAT: 16% applies to the platform fee (Jordan standard rate).
   - Refunds are issued within 5 business days upon approved cancellation.

2. CONTENT & DELIVERABLES
   - Influencer must submit content within the agreed timeline.
   - Merchant has 72 hours to approve/reject submitted content.
   - Up to 2 revision rounds are included per deal.

3. DISPUTES
   - Either party may raise a dispute within 7 days of content submission.
   - Admin review takes up to 3 business days.
   - Final resolution is binding and funds released accordingly.

4. PRIVACY & DATA
   - User data is stored in Jordan and subject to Jordanian data-protection law.
   - Influencer personal data is never sold to third parties.

5. INTELLECTUAL PROPERTY
   - Merchant receives a non-exclusive license to use approved campaign content.
   - Original copyright remains with the influencer/content creator.
"""


class ContractRequest(BaseModel):
    deal_id: str | None = None
    influencer_name: str
    merchant_name: str
    campaign_title: str
    agreed_amount_jod: float
    deliverables: str
    deadline: str | None = None


class PolicyQARequest(BaseModel):
    question: str
    language: str = "en"


@router.post("/generate")
async def generate_contract(
    payload: ContractRequest,
    current_user: User = Depends(get_current_user),
):
    contract_text = f"""
INFLUENCER MARKETING AGREEMENT
================================
Platform: WaslAI.jo (Jordan)
Date: {__import__('datetime').date.today().isoformat()}

PARTIES
-------
Merchant : {payload.merchant_name}
Influencer: {payload.influencer_name}

CAMPAIGN
--------
Title        : {payload.campaign_title}
Agreed Fee   : {payload.agreed_amount_jod:.3f} JOD (excl. VAT)
Platform Fee : {payload.agreed_amount_jod * 0.10:.3f} JOD (10%)
Deliverables : {payload.deliverables}
Deadline     : {payload.deadline or 'As agreed'}

TERMS
-----
1. Payment is held in WaslAI.jo escrow until content approval.
2. Influencer retains copyright; merchant receives non-exclusive usage licence.
3. Dispute resolution follows WaslAI.jo platform policy.
4. Governing law: Hashemite Kingdom of Jordan.

SIGNATURES
----------
Merchant  : _________________________
Influencer: _________________________
""".strip()

    return {
        "deal_id": payload.deal_id,
        "contract_text": contract_text,
        "status": "generated",
    }


@router.post("/policy-qa")
async def policy_qa(
    question: str = Query(...),
    language: str = Query("en"),
    current_user: User = Depends(get_current_user),
):
    q = question.lower()

    keywords = {
        "payment": ["payment", "دفع", "escrow", "ضمان"],
        "dispute": ["dispute", "نزاع", "conflict"],
        "content": ["content", "محتوى", "deliverable", "revision"],
        "privacy": ["privacy", "خصوصية", "data", "بيانات"],
        "ip": ["copyright", "حقوق", "intellectual", "license"],
        "refund": ["refund", "استرداد", "cancel"],
    }

    matched_sections = []
    for section, kws in keywords.items():
        if any(kw in q for kw in kws):
            matched_sections.append(section)

    if matched_sections:
        answer = f"Based on WaslAI.jo platform policies regarding {', '.join(matched_sections)}:\n\n{PLATFORM_POLICIES}"
    else:
        answer = PLATFORM_POLICIES

    if language == "ar":
        answer = f"سياسات منصة WaslAI.jo (الإجابة بالعربية قريبًا):\n\n{answer}"

    return {"question": question, "answer": answer, "language": language}

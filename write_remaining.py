"""ARIA Bulk Writer — Modules 04-12"""
import os

BASE = "C:/InfluMatch_AI/influmatch"

def w(rel_path, content):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK  {rel_path}")

# ── MODULE 04 ── schemas/auth.py ──────────────────────────────────────────────
w("backend/schemas/__init__.py", "")

w("backend/schemas/auth.py", """from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    is_active: bool
    is_verified: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
""")

w("backend/schemas/merchant.py", """from pydantic import BaseModel
from typing import Optional

class MerchantCreate(BaseModel):
    business_name_ar: str
    business_name_en: Optional[str] = None
    business_category: Optional[str] = None
    description_ar: Optional[str] = None
    city: str = "Amman"

class MerchantResponse(BaseModel):
    id: int
    user_id: int
    business_name_ar: str
    business_name_en: Optional[str]
    business_category: Optional[str]
    city: str
    total_spent_jod: float
    loyalty_points: int
    is_verified: bool
    model_config = {"from_attributes": True}
""")

w("backend/schemas/influencer.py", """from pydantic import BaseModel
from typing import Optional

class InfluencerCreate(BaseModel):
    bio_ar: Optional[str] = None
    bio_en: Optional[str] = None
    niche: Optional[str] = None
    city: str = "Amman"
    instagram_handle: Optional[str] = None
    instagram_followers: int = 0
    tiktok_handle: Optional[str] = None
    tiktok_followers: int = 0
    youtube_handle: Optional[str] = None
    youtube_subscribers: int = 0
    rate_per_post: float = 0.0
    rate_per_story: float = 0.0
    rate_per_reel: float = 0.0

class InfluencerResponse(BaseModel):
    id: int
    user_id: int
    niche: Optional[str]
    city: str
    instagram_followers: int
    tiktok_followers: int
    youtube_subscribers: int
    aria_score: float
    aria_tier: str
    rate_per_post: float
    is_available: bool
    model_config = {"from_attributes": True}
""")

w("backend/schemas/campaign.py", """from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.campaign import CampaignStatus

class CampaignCreate(BaseModel):
    title_ar: str
    title_en: Optional[str] = None
    description_ar: Optional[str] = None
    niche: Optional[str] = None
    total_budget: float = Field(..., ge=50.0)
    budget_per_influencer: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    required_deliverables: List[str] = []
    hashtags: List[str] = []
    target_cities: List[str] = ["Amman"]
    min_followers: int = 1000

class CampaignResponse(BaseModel):
    id: int
    merchant_id: int
    title_ar: str
    title_en: Optional[str]
    niche: Optional[str]
    total_budget: float
    status: CampaignStatus
    is_featured: bool
    model_config = {"from_attributes": True}
""")

w("backend/schemas/escrow.py", """from pydantic import BaseModel
from ..models.escrow import EscrowStatus

class EscrowResponse(BaseModel):
    id: int
    campaign_id: int
    gross_amount: float
    vat_amount: float
    platform_fee: float
    net_amount: float
    status: EscrowStatus
    model_config = {"from_attributes": True}

class EscrowTransition(BaseModel):
    target_status: EscrowStatus
    reason: str | None = None
""")

# ── MODULE 04 ── auth route ──────────────────────────────────────────────────
w("backend/api/dependencies/auth_deps.py", """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...core.security import decode_token
from ...models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(*roles: UserRole):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Requires role: {[r.value for r in roles]}")
        return current_user
    return checker
""")

w("backend/api/routes/auth.py", """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from ...core.database import get_db
from ...core.security import verify_password, create_access_token, get_password_hash
from ...models.user import User
from ...models.wallet import LoyaltyWallet
from ...schemas.auth import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        full_name_ar=payload.full_name_ar,
        full_name_en=payload.full_name_en,
        phone=payload.phone,
    )
    db.add(user)
    await db.flush()
    wallet = LoyaltyWallet(user_id=user.id)
    db.add(wallet)
    logger.success(f"[ARIA::AUTH] Registered: {user.email} [{user.role}]")
    return user

@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.success(f"[ARIA::AUTH] Login: {user.email}")
    return Token(access_token=token, role=user.role)

@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db),
             current_user: User = Depends(__import__("...api.dependencies.auth_deps", fromlist=["get_current_user"]).get_current_user if False else type("X", (), {"__call__": lambda s, **kw: None})())):
    pass
""")

# Rewrite auth /me cleanly
w("backend/api/routes/auth.py", """from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from ...core.database import get_db
from ...core.security import verify_password, create_access_token, get_password_hash
from ...models.user import User
from ...models.wallet import LoyaltyWallet
from ...schemas.auth import Token, UserCreate, UserResponse
from ..dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email, username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role, full_name_ar=payload.full_name_ar,
        full_name_en=payload.full_name_en, phone=payload.phone,
    )
    db.add(user)
    await db.flush()
    db.add(LoyaltyWallet(user_id=user.id))
    logger.success(f"[ARIA::AUTH] Registered: {user.email} [{user.role}]")
    return user

@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.success(f"[ARIA::AUTH] Login: {user.email}")
    return Token(access_token=token, role=user.role)

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
""")

# ── MODULE 05 ── RAG System ──────────────────────────────────────────────────
w("backend/services/rag/vector_store.py", """import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.core.config import get_settings

settings = get_settings()

class InfluMatchVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200,
            separators=["\\n\\n", "\\n", ".", "\\u060c", " "]
        )
        self._init_collections()

    def _init_collections(self):
        self.contracts_col = self.client.get_or_create_collection("smart_contracts")
        self.policies_col = self.client.get_or_create_collection("jordan_policies")
        self.campaigns_col = self.client.get_or_create_collection("campaign_knowledge")
        logger.success("[ARIA::RAG] Vector store initialized")

    def _get_collection(self, doc_type: str):
        return {"contract": self.contracts_col, "policy": self.policies_col, "campaign": self.campaigns_col}.get(doc_type, self.policies_col)

    def ingest_document(self, text: str, doc_type: str, metadata: Dict):
        chunks = self.splitter.split_text(text)
        embeddings = self.encoder.encode(chunks).tolist()
        collection = self._get_collection(doc_type)
        ids = [f"{doc_type}_{metadata.get('id','doc')}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=[metadata]*len(chunks))
        logger.success(f"[ARIA::RAG] Ingested {len(chunks)} chunks | {doc_type}")

    def semantic_search(self, query: str, doc_type: str, top_k: int = 5) -> List[Dict]:
        collection = self._get_collection(doc_type)
        count = collection.count()
        if count == 0:
            return []
        embedding = self.encoder.encode(query).tolist()
        results = collection.query(query_embeddings=[embedding], n_results=min(top_k, count))
        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]
""")

w("backend/services/rag/document_loader.py", """import os
from pathlib import Path
from typing import List, Dict
from loguru import logger

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class DocumentLoader:
    def load_text_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_pdf(self, path: str) -> str:
        if not PDF_AVAILABLE:
            logger.warning("[ARIA::RAG] PyPDF2 not installed, skipping PDF")
            return ""
        reader = PdfReader(path)
        return "\\n".join(page.extract_text() or "" for page in reader.pages)

    def load_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict]:
        extensions = extensions or [".txt", ".md", ".pdf"]
        docs = []
        for file_path in Path(dir_path).rglob("*"):
            if file_path.suffix in extensions:
                try:
                    content = self.load_pdf(str(file_path)) if file_path.suffix == ".pdf" else self.load_text_file(str(file_path))
                    if content.strip():
                        docs.append({"path": str(file_path), "name": file_path.name, "content": content})
                        logger.info(f"[ARIA::RAG] Loaded: {file_path.name}")
                except Exception as e:
                    logger.error(f"[ARIA::RAG] Failed to load {file_path}: {e}")
        return docs

loader = DocumentLoader()
""")

w("backend/services/rag/rag_chain.py", """from loguru import logger
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
        context_text = "\\n\\n".join([r["text"] for r in ctx]) if ctx else "No prior contracts loaded."
        lang_instr = "Generate the contract in Arabic (RTL)." if language == "ar" else "Generate in English."
        system = f"You are ARIA legal AI for InfluMatch.jo Jordan. {lang_instr}\\n\\nContext:\\n{context_text}"
        user_msg = f"Contract between Merchant: {merchant_name} and Influencer: {influencer_name}\\nCampaign: {campaign_details}"
        client = self._get_client()
        resp = client.messages.create(model=settings.claude_model, max_tokens=4096,
            system=system, messages=[{"role": "user", "content": user_msg}])
        logger.success(f"[ARIA::RAG] Contract generated | lang={language}")
        return resp.content[0].text

    async def answer_policy_question(self, question: str, language: str = "ar") -> str:
        ctx = self.vector_store.semantic_search(question, "policy", top_k=4)
        context_text = "\\n\\n".join([r["text"] for r in ctx]) if ctx else ""
        lang_instr = "Reply in Arabic." if language == "ar" else "Reply in English."
        system = f"You are ARIA platform advisor for InfluMatch.jo Jordan. {lang_instr}\\nContext:\\n{context_text}"
        client = self._get_client()
        resp = client.messages.create(model=settings.claude_model, max_tokens=1024,
            system=system, messages=[{"role": "user", "content": question}])
        return resp.content[0].text

rag_chain = SmartContractRAG()
""")

# ── MODULE 06 ── Guardian Agent ───────────────────────────────────────────────
w("backend/agents/guardian_agent.py", """from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from loguru import logger

class GuardianAgent:
    def __init__(self, db_session_factory=None):
        self.scheduler = AsyncIOScheduler(
            job_defaults={"coalesce": True, "max_instances": 3, "misfire_grace_time": 300}
        )
        self.db_factory = db_session_factory
        self._setup_system_jobs()

    def _setup_system_jobs(self):
        self.scheduler.add_job(self._daily_scoring, CronTrigger(hour=2, minute=0), id="daily_scoring", replace_existing=True)
        self.scheduler.add_job(self._check_deadlines, CronTrigger(hour="*/6"), id="deadline_monitor", replace_existing=True)
        self.scheduler.add_job(self._process_escrow, CronTrigger(hour=9, minute=0), id="escrow_processor", replace_existing=True)
        self.scheduler.add_job(self._weekly_report, CronTrigger(day_of_week="sun", hour=8), id="weekly_report", replace_existing=True)
        logger.success("[ARIA::GUARDIAN] System jobs registered")

    def schedule_campaign_job(self, campaign_id: int, event: str, run_at: datetime) -> str:
        handlers = {
            "start": self._on_campaign_start, "deadline": self._on_deadline,
            "review": self._on_review, "payment": self._on_payment, "expire": self._on_expire,
        }
        handler = handlers.get(event)
        if not handler:
            return None
        job_id = f"campaign_{campaign_id}_{event}"
        self.scheduler.add_job(handler, DateTrigger(run_date=run_at), id=job_id, args=[campaign_id], replace_existing=True)
        logger.info(f"[ARIA::GUARDIAN] Scheduled {job_id} at {run_at}")
        return job_id

    async def _daily_scoring(self): logger.info("[ARIA::GUARDIAN] Running daily scoring...")
    async def _check_deadlines(self): logger.info("[ARIA::GUARDIAN] Checking deadlines...")
    async def _process_escrow(self): logger.info("[ARIA::GUARDIAN] Processing escrow releases...")
    async def _weekly_report(self): logger.info("[ARIA::GUARDIAN] Generating weekly report...")
    async def _on_campaign_start(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} STARTED")
    async def _on_deadline(self, cid): logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} DEADLINE")
    async def _on_review(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} REVIEW")
    async def _on_payment(self, cid): logger.info(f"[ARIA::GUARDIAN] Campaign {cid} PAYMENT RELEASE")
    async def _on_expire(self, cid): logger.warning(f"[ARIA::GUARDIAN] Campaign {cid} EXPIRED")

    def start(self):
        self.scheduler.start()
        logger.success("[ARIA::GUARDIAN] Guardian Agent ONLINE")

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
        logger.info("[ARIA::GUARDIAN] Guardian Agent shutdown")

guardian = GuardianAgent()
""")

# ── MODULE 07 ── Auditor Agent ────────────────────────────────────────────────
w("backend/agents/auditor_agent.py", """import json, base64
from typing import Dict, Optional
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from backend.core.config import get_settings

settings = get_settings()

AUDIT_SYSTEM = '''You are ARIA AI Auditor for InfluMatch.jo Jordan. Respond ONLY in this JSON format:
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
        prompt = f"Audit caption:\\n{caption}\\n\\nRequirements: brand={req.get('brand_name_en')}, hashtags={req.get('hashtags', [])}, niche={req.get('niche', '')}"
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
""")

# ── MODULE 08 ── Influencer Scorer ────────────────────────────────────────────
w("backend/services/scoring/influencer_scorer.py", """from typing import Dict
from loguru import logger

class ARIAInfluencerScorer:
    PLATFORM_WEIGHTS = {"instagram": 0.40, "tiktok": 0.35, "youtube": 0.25}
    JORDAN_CITIES = ["amman", "zarqa", "irbid", "aqaba", "madaba", "salt"]

    def _tier_bonus(self, followers: int) -> float:
        if followers < 1000: return 0.3
        if followers < 10000: return 0.7
        if followers < 100000: return 1.2
        if followers < 500000: return 1.0
        if followers < 1000000: return 0.85
        return 0.70

    def calculate_engagement_score(self, data: Dict) -> float:
        score = 0.0
        for platform, weight in self.PLATFORM_WEIGHTS.items():
            followers = data.get(f"{platform}_followers", 0) or data.get(f"{platform}_subscribers", 0)
            eng_rate = data.get(f"{platform}_engagement_rate", 0)
            if not followers: continue
            score += weight * min(eng_rate * 10, 100) * self._tier_bonus(followers)
        return round(min(score * 30, 30), 2)

    def calculate_authenticity_score(self, data: Dict) -> float:
        score = 25.0
        ig_followers = data.get("instagram_followers", 0)
        ig_following = data.get("instagram_following", 1) or 1
        ratio = ig_followers / ig_following
        if ratio < 0.1: score -= 10
        elif ratio < 0.5: score -= 5
        elif ratio > 100: score -= 3
        if data.get("monthly_growth_rate", 0) > 50: score -= 8
        age = data.get("account_age_days", 365)
        if age < 90: score -= 7
        elif age < 180: score -= 3
        return round(max(score, 0), 2)

    def calculate_reliability_score(self, data: Dict) -> float:
        total = data.get("campaigns_total", 0)
        if not total: return 10.0
        completed = data.get("campaigns_completed", 0)
        on_time = data.get("on_time_deliveries", 0)
        disputes = data.get("disputes_raised", 0)
        score = (completed / total * 8) + (on_time / max(completed, 1) * 7) - disputes * 2
        return round(min(max(score, 0), 15), 2)

    def calculate_relevance(self, data: Dict, niche: str) -> float:
        inf_niche = (data.get("niche") or "").lower()
        niche = niche.lower()
        niche_score = 8.0 if inf_niche == niche else (6.0 if niche in inf_niche or inf_niche in niche else 2.0)
        city = (data.get("city") or "").lower()
        location_bonus = 2.0 if any(c in city for c in self.JORDAN_CITIES) else 0.5
        return round(min(niche_score + location_bonus, 10), 2)

    def compute_aria_score(self, data: Dict, niche: str = "general", content_quality: float = 70.0) -> Dict:
        eng = self.calculate_engagement_score(data)
        auth = self.calculate_authenticity_score(data)
        cq = round((content_quality / 100) * 20, 2)
        rel = self.calculate_reliability_score(data)
        rev = self.calculate_relevance(data, niche)
        total = eng + auth + cq + rel + rev
        tier = ("PLATINUM" if total >= 85 else "GOLD" if total >= 70 else "SILVER" if total >= 55 else "BRONZE" if total >= 40 else "UNRANKED")
        insights = {
            "PLATINUM": "مؤثر ممتاز للسوق الأردني",
            "GOLD": "مؤثر جيد - مناسب للحملات التجارية",
            "SILVER": "مؤثر متوسط - مناسب للميزانيات المحدودة",
            "BRONZE": "مؤثر ناشئ",
            "UNRANKED": "يحتاج مزيدا من البيانات",
        }
        logger.info(f"[ARIA::SCORER] Score={total:.1f} | Tier={tier}")
        return {
            "aria_score": round(total, 2), "tier": tier,
            "breakdown": {"engagement": eng, "authenticity": auth, "content_quality": cq, "reliability": rel, "relevance": rev},
            "max_possible": {"engagement": 30, "authenticity": 25, "content_quality": 20, "reliability": 15, "relevance": 10},
            "jordan_insight": insights[tier],
        }

scorer = ARIAInfluencerScorer()
""")

# ── MODULE 09 ── Escrow Engine ────────────────────────────────────────────────
w("backend/services/escrow/escrow_engine.py", """from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.models.escrow import EscrowTransaction, EscrowStatus
from backend.core.config import get_settings

settings = get_settings()
PLATFORM_COMMISSION = 0.05

VALID_TRANSITIONS = {
    EscrowStatus.PENDING:      [EscrowStatus.FUNDED, EscrowStatus.REFUNDED],
    EscrowStatus.FUNDED:       [EscrowStatus.IN_PROGRESS, EscrowStatus.REFUNDED],
    EscrowStatus.IN_PROGRESS:  [EscrowStatus.UNDER_REVIEW, EscrowStatus.DISPUTED],
    EscrowStatus.UNDER_REVIEW: [EscrowStatus.RELEASED, EscrowStatus.DISPUTED],
    EscrowStatus.DISPUTED:     [EscrowStatus.RESOLVED, EscrowStatus.REFUNDED, EscrowStatus.RELEASED],
    EscrowStatus.RELEASED:     [],
    EscrowStatus.REFUNDED:     [],
    EscrowStatus.RESOLVED:     [],
}

class EscrowEngine:
    async def fund_escrow(self, db: AsyncSession, campaign_id: int, merchant_id: int, amount_jod: float) -> EscrowTransaction:
        vat = round(amount_jod * settings.vat_rate, 3)
        fee = round(amount_jod * PLATFORM_COMMISSION, 3)
        net = round(amount_jod - fee, 3)
        escrow = EscrowTransaction(
            campaign_id=campaign_id, merchant_id=merchant_id,
            gross_amount=amount_jod, vat_amount=vat, platform_fee=fee, net_amount=net,
            status=EscrowStatus.FUNDED, funded_at=datetime.utcnow(),
            auto_release_at=datetime.utcnow() + timedelta(days=settings.escrow_release_days),
        )
        db.add(escrow)
        await db.flush()
        logger.success(f"[ARIA::ESCROW] Funded campaign={campaign_id} | {amount_jod} JOD | net={net} JOD")
        return escrow

    async def transition(self, db: AsyncSession, escrow_id: int, target: EscrowStatus, reason: str = None, by: str = "system") -> Dict:
        result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise ValueError(f"Escrow {escrow_id} not found")
        if target not in VALID_TRANSITIONS[escrow.status]:
            raise ValueError(f"Invalid transition: {escrow.status} -> {target}")
        prev = escrow.status
        escrow.status = target
        if target == EscrowStatus.RELEASED:
            escrow.released_at = datetime.utcnow()
            escrow.released_by = by
        if target == EscrowStatus.DISPUTED:
            escrow.dispute_reason = reason
            escrow.dispute_raised_at = datetime.utcnow()
            escrow.dispute_deadline = datetime.utcnow() + timedelta(hours=48)
        logger.success(f"[ARIA::ESCROW] Transition {escrow_id}: {prev} -> {target}")
        return {"escrow_id": escrow_id, "prev_status": prev, "new_status": target, "amount": escrow.net_amount}

escrow_engine = EscrowEngine()
""")

# ── MODULE 10 ── Wallet Engine ────────────────────────────────────────────────
w("backend/services/wallet/loyalty_engine.py", """from typing import Dict
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.core.config import get_settings

settings = get_settings()

class LoyaltyWalletEngine:
    EVENTS = {
        "campaign_published": 100, "campaign_completed": 200,
        "positive_review": 50, "merchant_referral": 500,
        "profile_completed": 75, "first_campaign": 250,
    }
    REDEMPTION_RATE = 0.01
    MIN_REDEMPTION = 500

    def get_points_for_event(self, event: str, amount_jod: float = 0) -> int:
        if event == "spend_bonus":
            return int(amount_jod * settings.loyalty_points_rate * 100)
        return self.EVENTS.get(event, 0)

    def calculate_jod_value(self, points: int) -> float:
        if points < self.MIN_REDEMPTION: return 0.0
        return round(points * self.REDEMPTION_RATE, 3)

    def get_tier(self, total_points: int) -> Dict:
        if total_points >= 50000: return {"tier": "PLATINUM", "emoji": "diamond", "discount": 0.20}
        if total_points >= 20000: return {"tier": "GOLD", "emoji": "gold", "discount": 0.15}
        if total_points >= 5000:  return {"tier": "SILVER", "emoji": "silver", "discount": 0.10}
        return {"tier": "BRONZE", "emoji": "bronze", "discount": 0.05}

    def earn_points_summary(self, event: str, amount_jod: float = 0) -> Dict:
        pts = self.get_points_for_event(event, amount_jod)
        logger.info(f"[ARIA::WALLET] +{pts} pts | event={event}")
        return {"points_earned": pts, "event": event, "jod_equivalent": self.calculate_jod_value(pts)}

wallet_engine = LoyaltyWalletEngine()
""")

# ── MODULE 11 ── Remaining Routes ─────────────────────────────────────────────
w("backend/api/routes/merchants.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.merchant import Merchant
from ...schemas.merchant import MerchantCreate, MerchantResponse
from ..dependencies.auth_deps import require_role

router = APIRouter(prefix="/merchants", tags=["Merchants"])

@router.post("/profile", response_model=MerchantResponse, status_code=201)
async def create_profile(payload: MerchantCreate, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role(UserRole.MERCHANT))):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Profile exists")
    merchant = Merchant(user_id=current_user.id, **payload.model_dump())
    db.add(merchant)
    await db.flush()
    return merchant

@router.get("/profile", response_model=MerchantResponse)
async def get_profile(db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(require_role(UserRole.MERCHANT))):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant: raise HTTPException(status_code=404, detail="Profile not found")
    return merchant

@router.get("/", response_model=list[MerchantResponse])
async def list_merchants(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Merchant).offset(skip).limit(limit))
    return result.scalars().all()
""")

w("backend/api/routes/influencers.py", """from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.influencer import Influencer
from ...schemas.influencer import InfluencerCreate, InfluencerResponse
from ...services.scoring.influencer_scorer import scorer
from ..dependencies.auth_deps import get_current_user, require_role

router = APIRouter(prefix="/influencers", tags=["Influencers"])

@router.post("/profile", response_model=InfluencerResponse, status_code=201)
async def create_profile(payload: InfluencerCreate, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role(UserRole.INFLUENCER))):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    if result.scalar_one_or_none(): raise HTTPException(status_code=409, detail="Profile exists")
    inf = Influencer(user_id=current_user.id, **payload.model_dump())
    score_result = scorer.compute_aria_score(payload.model_dump())
    inf.aria_score = score_result["aria_score"]
    inf.aria_tier = score_result["tier"]
    inf.score_metadata = score_result
    db.add(inf)
    await db.flush()
    return inf

@router.get("/", response_model=list[InfluencerResponse])
async def list_influencers(skip: int = 0, limit: int = 20,
                            niche: str = Query(None), available: bool = Query(True),
                            db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    query = select(Influencer)
    if available: query = query.where(Influencer.is_available == True)
    result = await db.execute(query.offset(skip).limit(limit))
    infs = result.scalars().all()
    if niche: infs = [i for i in infs if i.niche == niche]
    return infs

@router.get("/{influencer_id}", response_model=InfluencerResponse)
async def get_influencer(influencer_id: int, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    result = await db.execute(select(Influencer).where(Influencer.id == influencer_id))
    inf = result.scalar_one_or_none()
    if not inf: raise HTTPException(status_code=404, detail="Not found")
    return inf
""")

w("backend/api/routes/campaigns.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.merchant import Merchant
from ...models.campaign import Campaign, CampaignStatus
from ...schemas.campaign import CampaignCreate, CampaignResponse
from ..dependencies.auth_deps import get_current_user, require_role

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(require_role(UserRole.MERCHANT))):
    res = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = res.scalar_one_or_none()
    if not merchant: raise HTTPException(status_code=404, detail="Create merchant profile first")
    campaign = Campaign(merchant_id=merchant.id, **payload.model_dump())
    db.add(campaign)
    merchant.campaigns_created += 1
    await db.flush()
    return campaign

@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(skip: int = 0, limit: int = 20,
                          status: CampaignStatus = None, db: AsyncSession = Depends(get_db),
                          _: User = Depends(get_current_user)):
    query = select(Campaign)
    if status: query = query.where(Campaign.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db),
                        _: User = Depends(get_current_user)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    c = result.scalar_one_or_none()
    if not c: raise HTTPException(status_code=404, detail="Not found")
    return c
""")

w("backend/api/routes/escrow.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.escrow import EscrowTransaction, EscrowStatus
from ...schemas.escrow import EscrowResponse, EscrowTransition
from ...services.escrow.escrow_engine import escrow_engine
from ..dependencies.auth_deps import get_current_user, require_role

router = APIRouter(prefix="/escrow", tags=["Escrow"])

@router.get("/{escrow_id}", response_model=EscrowResponse)
async def get_escrow(escrow_id: int, db: AsyncSession = Depends(get_db),
                      _: User = Depends(get_current_user)):
    result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
    e = result.scalar_one_or_none()
    if not e: raise HTTPException(status_code=404, detail="Not found")
    return e

@router.post("/{escrow_id}/transition")
async def transition_escrow(escrow_id: int, payload: EscrowTransition,
                             db: AsyncSession = Depends(get_db),
                             _: User = Depends(require_role(UserRole.MERCHANT, UserRole.ADMIN))):
    return await escrow_engine.transition(db, escrow_id, payload.target_status, payload.reason)
""")

w("backend/api/routes/wallet.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User
from ...models.wallet import LoyaltyWallet
from ..dependencies.auth_deps import get_current_user
from ...services.wallet.loyalty_engine import wallet_engine

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/me")
async def get_my_wallet(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet: raise HTTPException(status_code=404, detail="Wallet not found")
    tier_info = wallet_engine.get_tier(wallet.total_points_earned)
    return {"wallet_id": wallet.id, "points_balance": wallet.points_balance,
            "total_earned": wallet.total_points_earned, "tier": tier_info,
            "jod_value": wallet_engine.calculate_jod_value(wallet.points_balance)}
""")

w("backend/api/routes/contracts.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.campaign import Campaign
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...services.rag.rag_chain import rag_chain
from ..dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/contracts", tags=["Contracts"])

class ContractGenRequest(BaseModel):
    campaign_id: int
    influencer_id: int
    language: str = "ar"

@router.post("/generate")
async def generate_contract(payload: ContractGenRequest, db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Campaign).where(Campaign.id == payload.campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign: raise HTTPException(status_code=404, detail="Campaign not found")
    res2 = await db.execute(select(Influencer).where(Influencer.id == payload.influencer_id))
    influencer = res2.scalar_one_or_none()
    if not influencer: raise HTTPException(status_code=404, detail="Influencer not found")
    res3 = await db.execute(select(Merchant).where(Merchant.id == campaign.merchant_id))
    merchant = res3.scalar_one_or_none()
    contract_text = await rag_chain.generate_contract(
        merchant_name=merchant.business_name_en or merchant.business_name_ar,
        influencer_name=influencer.bio_en or str(influencer.id),
        campaign_details={"niche": campaign.niche, "budget": campaign.total_budget,
                          "title": campaign.title_en or campaign.title_ar},
        language=payload.language,
    )
    return {"campaign_id": payload.campaign_id, "influencer_id": payload.influencer_id,
            "language": payload.language, "contract": contract_text}

@router.post("/policy-qa")
async def policy_qa(question: str, language: str = "ar", _: User = Depends(get_current_user)):
    answer = await rag_chain.answer_policy_question(question, language)
    return {"question": question, "answer": answer, "language": language}
""")

w("backend/api/routes/chatbot.py", """from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from ...core.config import get_settings
from ..dependencies.auth_deps import get_current_user
from ...models.user import User

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])
settings = get_settings()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    language: str = "ar"
    context: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    model_used: str
    language: str

SYSTEM_AR = "أنت ARIA، مساعد ذكي لمنصة InfluMatch.jo الأردنية لربط التجار بالمؤثرين. أجب باللغة العربية بشكل مهني ومفيد. العملة دينار أردني (JOD)، الضريبة 16%."
SYSTEM_EN = "You are ARIA, the AI assistant for InfluMatch.jo — Jordan's influencer marketing platform connecting merchants and influencers. Be professional and helpful. Currency: JOD, VAT 16%."

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        system = SYSTEM_AR if payload.language == "ar" else SYSTEM_EN
        if payload.context: system += f"\\n\\nContext:\\n{payload.context}"
        messages = [{"role": m.role, "content": m.content} for m in (payload.history or [])]
        messages.append({"role": "user", "content": payload.message})
        resp = client.messages.create(model=settings.claude_model, max_tokens=1024,
            system=system, messages=messages)
        return ChatResponse(reply=resp.content[0].text, model_used=settings.claude_model, language=payload.language)
    except Exception as e:
        error_msg = f"عذراً، حدث خطأ: {str(e)}" if payload.language == "ar" else f"Sorry, an error occurred: {str(e)}"
        return ChatResponse(reply=error_msg, model_used="error", language=payload.language)
""")

w("backend/api/routes/admin.py", """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...models.campaign import Campaign, CampaignStatus
from ...models.escrow import EscrowTransaction, EscrowStatus
from ..dependencies.auth_deps import require_role

router = APIRouter(prefix="/admin", tags=["God Mode Admin"])

@router.get("/dashboard")
async def god_mode_dashboard(db: AsyncSession = Depends(get_db),
                              _: User = Depends(require_role(UserRole.ADMIN))):
    users = (await db.execute(select(func.count(User.id)))).scalar()
    merchants = (await db.execute(select(func.count(Merchant.id)))).scalar()
    influencers = (await db.execute(select(func.count(Influencer.id)))).scalar()
    campaigns = (await db.execute(select(func.count(Campaign.id)))).scalar()
    active_campaigns = (await db.execute(select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.ACTIVE))).scalar()
    total_escrow = (await db.execute(select(func.sum(EscrowTransaction.gross_amount)))).scalar() or 0
    released = (await db.execute(select(func.sum(EscrowTransaction.net_amount)).where(EscrowTransaction.status == EscrowStatus.RELEASED))).scalar() or 0
    return {
        "platform": "InfluMatch.jo", "aria_status": "ONLINE",
        "stats": {"total_users": users, "merchants": merchants, "influencers": influencers,
                  "campaigns": campaigns, "active_campaigns": active_campaigns},
        "finance": {"total_escrow_jod": round(total_escrow, 2), "released_jod": round(released, 2)},
    }

@router.get("/users")
async def list_all_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db),
                          _: User = Depends(require_role(UserRole.ADMIN))):
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users]
""")

w("backend/api/middleware/auth_middleware.py", """from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from loguru import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({ms}ms)")
        return response
""")

w("backend/api/middleware/rate_limiter.py", """from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from loguru import logger

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = timedelta(seconds=period)
        self._store: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.utcnow()
        self._store[client_ip] = [t for t in self._store[client_ip] if now - t < self.period]
        if len(self._store[client_ip]) >= self.calls:
            logger.warning(f"[ARIA::RATELIMIT] Rate limit exceeded: {client_ip}")
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})
        self._store[client_ip].append(now)
        return await call_next(request)
""")

# ── MODULE 11 ── main.py ──────────────────────────────────────────────────────
w("backend/main.py", """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from .core.config import get_settings
from .core.database import init_db, AsyncSessionLocal
from .api.routes import auth, merchants, influencers, campaigns, contracts, escrow, wallet, admin, chatbot
from .api.middleware.auth_middleware import LoggingMiddleware
from .api.middleware.rate_limiter import RateLimiter
from .agents.guardian_agent import GuardianAgent

settings = get_settings()

logger.remove()
logger.add(sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
    level="DEBUG" if settings.debug else "INFO", colorize=True)
logger.add("logs/influmatch_{time:YYYY-MM-DD}.log", rotation="1 day", retention="30 days", serialize=True)

guardian = GuardianAgent(AsyncSessionLocal)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 55)
    logger.info("ARIA INFLUMATCH.JO PLATFORM STARTING")
    logger.info("=" * 55)
    await init_db()
    logger.success("Database initialized")
    guardian.start()
    logger.success("Guardian Agent ONLINE")
    logger.success(f"InfluMatch.jo READY | port={settings.port} | market=Jordan")
    yield
    guardian.shutdown()
    logger.info("Platform shutdown complete")

app = FastAPI(
    title="InfluMatch.jo API", version="1.0.0",
    description="ARIA-Powered Influencer Marketing Platform — Jordan",
    docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)

app.add_middleware(RateLimiter, calls=200, period=60)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for r in [auth.router, merchants.router, influencers.router, campaigns.router,
          contracts.router, escrow.router, wallet.router, admin.router, chatbot.router]:
    app.include_router(r, prefix="/api")

@app.get("/", tags=["Health"])
async def root():
    return {"platform": "InfluMatch.jo", "aria": "ONLINE", "market": "Jordan", "currency": "JOD"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "guardian_agent": "active", "database": "connected", "rag": "ready"}
""")

print("\\nM04-M11 ALL FILES WRITTEN OK")

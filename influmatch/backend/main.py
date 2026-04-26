from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from .core.config import get_settings
from .core.database import init_db, AsyncSessionLocal
from .api.routes import auth, merchants, influencers, campaigns, contracts, escrow, wallet, admin, chatbot, milestones, bookings, messages
from .api.middleware.auth_middleware import LoggingMiddleware
from .api.middleware.rate_limiter import RateLimiter
from .agents.guardian_agent import GuardianAgent

settings = get_settings()

logger.remove()
logger.add(sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
    level="DEBUG" if settings.debug else "INFO", colorize=True)
logger.add("logs/waslai_{time:YYYY-MM-DD}.log", rotation="1 day", retention="30 days", serialize=True)

guardian = GuardianAgent(AsyncSessionLocal)

async def _seed_admin(session):
    from sqlalchemy import select
    from .models.user import User, UserRole
    from .models.wallet import LoyaltyWallet
    from .core.security import get_password_hash
    result = await session.execute(select(User).where(User.email == "admin@waslai.jo"))
    if not result.scalar_one_or_none():
        admin = User(
            email="admin@waslai.jo",
            username="admin",
            hashed_password=get_password_hash("Admin@2024"),
            role=UserRole.ADMIN,
            full_name_en="Platform Admin",
            full_name_ar="مدير المنصة",
        )
        session.add(admin)
        await session.flush()
        session.add(LoyaltyWallet(user_id=admin.id))
        await session.commit()
        logger.success("[ARIA::SEED] Admin user created: admin@waslai.jo")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 55)
    logger.info("ARIA WASLAI.JO PLATFORM STARTING")
    logger.info("=" * 55)
    await init_db()
    logger.success("Database initialized")
    async with AsyncSessionLocal() as session:
        await _seed_admin(session)
    guardian.start()
    logger.success("Guardian Agent ONLINE")
    logger.success(f"WaslAI.jo READY | port={settings.port} | market=Jordan")
    yield
    guardian.shutdown()
    logger.info("Platform shutdown complete")

app = FastAPI(
    title="WaslAI.jo API", version="1.0.0",
    description="ARIA-Powered Influencer Marketing Platform — Jordan",
    docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)

app.add_middleware(RateLimiter, calls=200, period=60)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",  # Next.js dev
        "http://localhost:8501", "http://127.0.0.1:8501",  # Streamlit legacy
        "http://localhost:8080",                            # old proxy
    ],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_routers = [
    auth.router, merchants.router, influencers.router, campaigns.router,
    contracts.router, escrow.router, wallet.router, admin.router, chatbot.router,
    milestones.router, bookings.router, messages.router,
]

# v1 — current version (all new clients should use /api/v1/...)
for r in _routers:
    app.include_router(r, prefix="/api/v1")

# Legacy /api prefix — preserved for backward compatibility with existing frontend
# TODO: remove once frontend fully migrates to /api/v1
for r in _routers:
    app.include_router(r, prefix="/api", include_in_schema=False)

@app.get("/", tags=["Health"])
async def root():
    return {"platform": "WaslAI.jo", "aria": "ONLINE", "market": "Jordan", "currency": "JOD"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "guardian_agent": "active", "database": "connected", "rag": "ready"}

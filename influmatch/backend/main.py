from fastapi import FastAPI
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

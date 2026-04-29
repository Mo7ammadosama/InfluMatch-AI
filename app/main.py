"""
WaslAI.jo — FastAPI Application Entry Point
ARIA v3.0.0 | Jordan Market B2B Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from loguru import logger
import sys

from app.config import settings
from app.database import create_tables
from app.routers import auth, merchants, influencers, campaigns, deals, escrow, ai_router, wallet
from app.routers import creative_strategists, campaign_ideas
from app.middleware.logging_middleware import LoggingMiddleware


# --- Structured Logging Setup ---
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)
logger.add(
    settings.log_file,
    rotation="10 MB",
    retention="30 days",
    serialize=True,
    level="INFO",
)


# --- Lifespan (startup / shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")
    await create_tables()
    logger.info("✅ Database initialized")
    yield
    logger.info("🛑 Shutting down WaslAI.jo")


# --- Application Factory ---
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Influencer-Merchant matching platform for Jordan market",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# --- Middleware Stack ---
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Registration ---
app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["Authentication"])
app.include_router(merchants.router,   prefix="/api/v1/merchants",   tags=["Merchants"])
app.include_router(influencers.router, prefix="/api/v1/influencers", tags=["Influencers"])
app.include_router(campaigns.router,   prefix="/api/v1/campaigns",   tags=["Campaigns"])
app.include_router(deals.router,       prefix="/api/v1/deals",       tags=["Deals"])
app.include_router(escrow.router,      prefix="/api/v1/escrow",      tags=["Escrow & Finance"])
app.include_router(ai_router.router,            prefix="/api/v1/ai",                   tags=["AI Matching"])
app.include_router(wallet.router,               prefix="/api/v1/wallet",               tags=["Wallet"])
app.include_router(creative_strategists.router, prefix="/api/v1/creative-strategists", tags=["Creative Strategists"])
app.include_router(campaign_ideas.router,       prefix="/api/v1/ideas",                tags=["Campaign Ideas"])


# --- Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "currency": settings.default_currency,
        "market": "Jordan",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "WaslAI.jo API — مرحباً بك",
        "docs": "/docs",
        "health": "/health",
    }

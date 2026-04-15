"""
InfluMatch.jo — Core Configuration
Module 02 | Pydantic Settings — reads from .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "InfluMatch.jo"
    app_version: str = "1.0.0"
    debug: bool = True
    port: int = 8000

    # Security
    secret_key: str = "aria-influmatch-secret-2024-jordan"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Database
    database_url: str = "sqlite:///./influmatch.db"

    # AI Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # RAG
    chroma_persist_dir: str = "./data/chroma_db"

    # Finance
    stripe_test_key: str = ""
    escrow_release_days: int = 7
    loyalty_points_rate: float = 0.05

    # Admin
    admin_username: str = "godmode_admin"
    admin_password: str = "aria_admin_2024"

    # Jordan Market
    currency: str = "JOD"
    vat_rate: float = 0.16
    default_language: str = "ar"
    claude_model: str = "claude-sonnet-4-6"

    # Notifications — SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    # Notifications — WhatsApp
    whatsapp_api_url: str = "https://api.whatsapp.com/stub"
    whatsapp_token: str   = "stub_token"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()

"""
InfluMatch.jo — Application Configuration
Centralized settings via pydantic-settings (reads from .env)
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = "InfluMatch.jo"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = Field(..., min_length=32)
    allowed_origins: list[str] = ["http://localhost:8501", "http://localhost:8000"]
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./influmatch.db"

    # JWT Auth — accepts both JWT_* and bare aliases
    jwt_secret_key: str = Field(default="", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = 7

    # Claude AI (Primary)
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-6"
    claude_max_tokens: int = 4096

    # OpenAI (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_influencers: str = "influencers"
    chroma_collection_campaigns: str = "campaigns"

    # Stripe (Test Mode) — accepts STRIPE_SECRET_KEY or STRIPE_TEST_KEY
    stripe_secret_key: str = Field(default="", validation_alias="STRIPE_SECRET_KEY")
    stripe_test_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # Finance — Jordan Market
    default_currency: str = "JOD"
    vat_rate: float = 0.16
    escrow_fee_percent: float = 0.05
    escrow_release_days: int = 7
    min_campaign_budget_jod: float = 50.0
    platform_wallet_id: str = "platform_wallet_001"
    loyalty_points_rate: float = 0.05

    # Admin (God Mode)
    admin_username: str = "godmode_admin"
    admin_password: str = ""

    # Logging
    log_level: str = "DEBUG"
    log_file: str = "./logs/influmatch.log"

    # Frontend
    streamlit_port: int = 8501
    api_base_url: str = "http://localhost:8000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    def model_post_init(self, __context) -> None:
        # Fallback: use SECRET_KEY as JWT_SECRET_KEY if JWT_SECRET_KEY not set
        if not self.jwt_secret_key:
            object.__setattr__(self, "jwt_secret_key", self.secret_key)
        # Fallback: use STRIPE_TEST_KEY as STRIPE_SECRET_KEY if not set
        if not self.stripe_secret_key and self.stripe_test_key:
            object.__setattr__(self, "stripe_secret_key", self.stripe_test_key)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

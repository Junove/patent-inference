from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All config comes from environment variables (or a git-ignored .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    near_ai_api_key: str = ""
    # deepseek/deepseek-v4.1-flash: confirmed live on cloud-api.near.ai/v1/models, text+image
    # input, $0.30/$1.20 per M tokens in/out, ready now (resolves the FR-G3/NFR-12 open question
    # in docs/REQUIREMENTS.md -- yes, it accepts images).
    near_ai_model: str = "deepseek/deepseek-v4.1-flash"
    near_ai_base_url: str = "https://cloud-api.near.ai/v1"
    near_ai_max_tokens: int = 1200
    near_ai_retry_backoff_seconds: float = 1.0
    near_ai_job_token_cap: int = 20_000  # NFR-12 per-job cap
    near_ai_total_budget_usd: float = 20.0  # NFR-12 total spend limit
    near_ai_price_per_1k_tokens: float = 0.0012  # conservative: this model's $1.20/M output price
    database_url: str = "sqlite:///./patent.db"
    upload_dir: str = "./uploads"
    upload_max_bytes: int = 25 * 1024 * 1024  # FR-U1 per-file limit
    upload_retention_days: int = 30  # NFR-11


@lru_cache
def get_settings() -> Settings:
    return Settings()

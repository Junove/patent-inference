from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All config comes from environment variables (or a git-ignored .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    near_ai_api_key: str = ""
    near_ai_model: str = ""
    database_url: str = "sqlite:///./patent.db"
    upload_dir: str = "./uploads"
    upload_max_bytes: int = 25 * 1024 * 1024  # FR-U1 per-file limit
    upload_retention_days: int = 30  # NFR-11


@lru_cache
def get_settings() -> Settings:
    return Settings()

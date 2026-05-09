"""
Configuration management using pydantic-settings.
Loads from .env file — never hardcode secrets.
"""
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "StreamVault AI Insights"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Keys — loaded from .env
    ANTHROPIC_API_KEY: str = ""

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/db/streamvault.db"

    # Data paths
    CSV_DIR: str = str(BASE_DIR / "data" / "csv")
    PDF_DIR: str = str(BASE_DIR / "data" / "pdf")

    # Claude model
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    MAX_TOKENS: int = 2048

    # Security
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
    API_RATE_LIMIT: str = "30/minute"

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"


settings = Settings()

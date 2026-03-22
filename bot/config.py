"""
Configuration loader for the Telegram bot.

Loads secrets from environment using pydantic-settings.
Supports both local development (.env.bot.secret) and Docker (.env.docker.secret).
In Docker, environment variables are injected directly by docker-compose.yml.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this config file lives
# config.py is in bot/, so parent is the repo root
REPO_DIR = Path(__file__).resolve().parent

# Try .env.docker.secret first (for Docker deployment), then .env.bot.secret (local dev)
ENV_FILE = REPO_DIR.parent / ".env.docker.secret"
if not ENV_FILE.exists():
    ENV_FILE = REPO_DIR.parent / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API configuration
    # Default to Docker service name; localhost for local dev
    lms_api_base_url: str = "http://backend:8000"
    lms_api_key: str = ""

    # LLM API configuration
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


# Global settings instance (lazy-loaded)
_settings: BotSettings | None = None


def get_settings() -> BotSettings:
    """Get the global settings instance, loading it if necessary."""
    global _settings
    if _settings is None:
        _settings = BotSettings()
    return _settings

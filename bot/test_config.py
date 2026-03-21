#!/usr/bin/env python3
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Same logic as config.py - script is in bot/, so parent is repo root
REPO_DIR = Path(__file__).resolve().parent
ENV_FILE = REPO_DIR.parent / ".env.bot.secret"
print('ENV_FILE:', ENV_FILE, 'exists:', ENV_FILE.exists())

class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore',
    )
    bot_token: str = ''

s = TestSettings()
print('bot_token:', repr(s.bot_token))

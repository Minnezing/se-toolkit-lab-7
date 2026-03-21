"""Services for the Telegram bot.

Services handle external dependencies:
- lms_api: LMS backend API client
- llm_api: LLM API client for intent routing
"""

from .lms_api import LmsApiClient

__all__ = ["LmsApiClient"]

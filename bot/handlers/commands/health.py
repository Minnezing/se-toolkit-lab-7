"""Handler for /health command."""

from config import get_settings
from services.lms_api import LmsApiClient


def handle_health() -> str:
    """Handle /health command - checks backend status."""
    settings = get_settings()
    client = LmsApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    is_healthy, message = client.health_check()
    return message

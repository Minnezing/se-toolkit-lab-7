"""Handler for /labs command."""

from config import get_settings
from services.lms_api import LmsApiClient, ApiError


def handle_labs() -> str:
    """Handle /labs command - lists available labs."""
    settings = get_settings()
    client = LmsApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    labs = client.get_labs()
    if isinstance(labs, ApiError):
        return labs.message
    if not labs:
        return "No labs available."
    lines = ["Available labs:"]
    for lab in labs:
        lab_title = lab.get("title", "Unknown Lab")
        lines.append(f"- {lab_title}")
    return "\n".join(lines)

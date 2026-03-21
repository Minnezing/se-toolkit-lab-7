"""Handler for /scores command."""

from config import get_settings
from services.lms_api import LmsApiClient, ApiError


def handle_scores(lab_name: str) -> str:
    """Handle /scores command - shows scores for a lab.

    Args:
        lab_name: The lab identifier (e.g., "lab-04")
    """
    if not lab_name:
        return "Usage: /scores <lab-name>. Example: /scores lab-04"

    settings = get_settings()
    client = LmsApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    pass_rates = client.get_pass_rates(lab_name)

    if isinstance(pass_rates, ApiError):
        return pass_rates.message

    if not pass_rates:
        return f"No scores found for {lab_name}."

    # Extract lab number for display
    lab_display = lab_name.replace("-", " ").title()
    lines = [f"Pass rates for {lab_display}:"]

    for rate in pass_rates:
        task = rate.get("task", "Unknown Task")
        avg_score = rate.get("avg_score", 0)
        attempts = rate.get("attempts", 0)
        lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")

    return "\n".join(lines)

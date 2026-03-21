"""Handler for /help command."""


def handle_help() -> str:
    """Handle /help command - lists available commands."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Show scores for a lab"
    )

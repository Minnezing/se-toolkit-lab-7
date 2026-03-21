"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram — same function works from --test mode,
unit tests, or the actual Telegram bot.
"""

from .commands.start import handle_start
from .commands.help import handle_help
from .commands.health import handle_health
from .commands.labs import handle_labs
from .commands.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]

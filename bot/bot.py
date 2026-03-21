#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test mode: prints response to stdout
    uv run bot.py --test "hello"    # Test mode with plain text
    uv run bot.py                   # Normal mode: connects to Telegram
"""

import argparse
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent import route_intent
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_command(command: str) -> str:
    """
    Route a command string to the appropriate handler.
    
    Args:
        command: The command string (e.g., "/start", "/help", "/scores lab-04")
    
    Returns:
        The handler's response as a string
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command.startswith("/scores"):
        parts = command.split(maxsplit=1)
        lab_name = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab_name)
    else:
        # Try intent routing for unknown commands or plain text
        return route_intent(command)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with common actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Check Health", callback_data="health"),
            InlineKeyboardButton(text="📚 List Labs", callback_data="labs"),
        ],
        [
            InlineKeyboardButton(text="📈 Lab 04 Scores", callback_data="scores_lab-04"),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def start_command_handler(message: types.Message):
    """Handle /start command from Telegram."""
    response = handle_start()
    keyboard = get_start_keyboard()
    await message.answer(response, reply_markup=keyboard)


async def help_command_handler(message: types.Message):
    """Handle /help command from Telegram."""
    response = handle_help()
    await message.answer(response)


async def health_command_handler(message: types.Message):
    """Handle /health command from Telegram."""
    response = handle_health()
    await message.answer(response)


async def labs_command_handler(message: types.Message):
    """Handle /labs command from Telegram."""
    response = handle_labs()
    await message.answer(response)


async def scores_command_handler(message: types.Message):
    """Handle /scores command from Telegram."""
    # Extract lab name from command arguments
    lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    response = handle_scores(lab_name)
    await message.answer(response)


async def callback_query_handler(callback_query: types.CallbackQuery):
    """Handle inline keyboard button clicks."""
    data = callback_query.data
    
    if data == "health":
        response = handle_health()
    elif data == "labs":
        response = handle_labs()
    elif data == "help":
        response = handle_help()
    elif data.startswith("scores_"):
        lab_name = data.replace("scores_", "")
        response = handle_scores(lab_name)
    else:
        response = "Unknown action."
    
    await callback_query.answer()
    await callback_query.message.answer(response)


async def text_message_handler(message: types.Message):
    """Handle plain text messages with intent routing."""
    user_text = message.text or ""
    
    # Skip if it's a command (handled by command handlers)
    if user_text.startswith("/"):
        return
    
    # Route through intent router
    response = route_intent(user_text)
    await message.answer(response)


async def main():
    """Main bot entry point for Telegram mode."""
    settings = get_settings()
    
    if not settings.bot_token:
        logger.error("BOT_TOKEN not found in .env.bot.secret")
        sys.exit(1)
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Register command handlers
    dp.message.register(start_command_handler, CommandStart())
    dp.message.register(help_command_handler, Command("help"))
    dp.message.register(health_command_handler, Command("health"))
    dp.message.register(labs_command_handler, Command("labs"))
    dp.message.register(scores_command_handler, Command("scores"))
    
    # Register callback query handler for inline buttons
    dp.callback_query.register(callback_query_handler)
    
    # Register text message handler for plain language queries
    dp.message.register(text_message_handler)
    
    logger.info("Bot is starting...")
    await dp.start_polling(bot)


def main_cli():
    """CLI entry point that handles both --test and normal mode."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout (e.g., --test '/start' or --test 'hello')"
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print to stdout
        response = handle_command(args.test)
        print(response)
        sys.exit(0)
    else:
        # Normal mode: start Telegram bot
        import asyncio
        asyncio.run(main())


if __name__ == "__main__":
    main_cli()

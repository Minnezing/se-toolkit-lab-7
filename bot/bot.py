#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test mode: prints response to stdout
    uv run bot.py                   # Normal mode: connects to Telegram
"""

import argparse
import sys

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


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
        return f"Unknown command: {command}"


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout (e.g., --test '/start')"
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print to stdout
        response = handle_command(args.test)
        print(response)
        sys.exit(0)
    else:
        # Normal mode: start Telegram bot (not implemented yet)
        print("Normal mode not implemented yet. Use --test for testing.")
        sys.exit(0)


if __name__ == "__main__":
    main()

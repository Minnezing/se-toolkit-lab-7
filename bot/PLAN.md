# Telegram Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram bot. The bot allows users to interact with the Learning Management System through Telegram chat, providing slash commands for structured queries and natural language understanding via an LLM for flexible interactions.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point (`bot.py`)**: Handles both Telegram bot startup and CLI test mode. The `--test` flag enables offline testing without a Telegram connection.

2. **Handlers (`handlers/`)**: Pure functions that take command input and return text responses. They have no dependency on Telegram, making them testable in isolation and reusable across test mode, unit tests, and production.

3. **Services (`services/`)**: External dependency clients:
   - `lms_api.py`: HTTP client for the LMS backend with Bearer token authentication
   - `llm_api.py`: LLM client for intent routing (Task 3)

4. **Configuration (`config.py`)**: Loads secrets from `.env.bot.secret` using pydantic-settings.

## Task Breakdown

### Task 1: Scaffold (Current)
- Create project structure with `bot.py`, `handlers/`, `services/`, `config.py`
- Implement `--test` mode for offline verification
- Set up `pyproject.toml` with dependencies (aiogram, httpx, pydantic-settings)
- Create `.env.bot.secret` with bot token and API credentials

### Task 2: Backend Integration
- Implement `LmsApiClient` with methods for all 9 backend endpoints
- Wire up `/health` to call `GET /health` on the backend
- Wire up `/labs` to call `GET /items/` and filter for labs
- Wire up `/scores <lab>` to call analytics endpoints
- Add error handling for network failures and non-200 responses

### Task 3: Intent-Based Natural Language Routing
- Implement `LlmClient` for tool-based LLM calls
- Define tool descriptions for each backend endpoint
- Create intent router that passes user queries to the LLM with available tools
- The LLM decides which tool to call based on the user's intent
- Handle multi-step reasoning (LLM may chain multiple API calls)

### Task 4: Containerize and Deploy
- Create `Dockerfile` for the bot
- Add bot service to `docker-compose.yml`
- Configure Docker networking (bot talks to backend via service name, not localhost)
- Document deployment process in README

## Testing Strategy

- **Unit tests**: Test handlers in isolation with mocked services
- **Test mode**: Use `--test` flag for manual verification during development
- **Integration tests**: Verify end-to-end flow with real backend (staged for later)

## Deployment

The bot runs as a Docker container alongside the backend. Key networking considerations:
- Bot connects to backend at `http://backend:8000` (Docker service name, not localhost)
- Bot connects to LLM proxy at `http://qwen-code-api:8080` (if using Qwen Code)
- Secrets mounted via `.env.bot.secret` volume

## Success Criteria

1. All P0 commands work in test mode and return real data from backend
2. Bot responds in Telegram to slash commands
3. Natural language queries are routed to correct tools via LLM
4. Bot is containerized and deployed on the VM
5. Errors are handled gracefully with user-friendly messages

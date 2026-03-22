# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

This section explains how to deploy the bot alongside the backend on your VM using Docker Compose.

### Prerequisites

Before deploying, ensure you have:

1. **SSH access to your VM** with keys configured
2. **`.env.docker.secret`** file in the repo root with required variables:
   - `BOT_TOKEN` — your Telegram bot token from @BotFather
   - `LMS_API_KEY` — backend API key
   - `LLM_API_KEY` — LLM API key
   - `LLM_API_BASE_URL` — LLM API base URL (e.g., `http://host.docker.internal:8080`)
3. **Backend is running** and healthy (`curl -sf http://localhost:42002/docs`)

### Environment variables

The bot service requires these environment variables (set in `.env.docker.secret`):

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `LMS_API_KEY` | Backend API key for authentication | `<your-api-key>` |
| `LLM_API_KEY` | LLM API key for intent routing | `<your-llm-key>` |
| `LLM_API_BASE_URL` | LLM API base URL | `http://host.docker.internal:8080` |
| `LLM_API_MODEL` | LLM model name (optional) | `coder-model` |

> **Note**: The bot uses Docker networking to reach the backend. `LMS_API_BASE_URL` is set automatically to `http://backend:8000` in `docker-compose.yml` — do not use `localhost`.

### Deploy commands

SSH into your VM and run:

```bash
cd ~/se-toolkit-lab-7

# Stop any running bot process (from previous nohup deployment)
pkill -f "bot.py" 2>/dev/null

# Build and start all services (backend + bot)
docker compose --env-file .env.docker.secret up --build -d

# Check that all services are running
docker compose --env-file .env.docker.secret ps
```

You should see the `bot` service running alongside `backend`, `postgres`, `caddy`.

### Verify deployment

```bash
# Check bot container status
docker compose --env-file .env.docker.secret ps bot

# View bot logs (look for "Application started" and no tracebacks)
docker compose --env-file .env.docker.secret logs bot --tail 20

# Verify backend is still healthy
curl -sf http://localhost:42002/docs
```

### Test in Telegram

Send these commands to your bot:

1. `/start` — should return welcome message with inline keyboard
2. `/health` — should report backend status
3. "what labs are available?" — LLM should respond with lab list
4. "which lab has the lowest pass rate?" — LLM should chain API calls

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container exits immediately | Check logs: `docker compose logs bot`. Usually missing env var or import error |
| `/health` fails | Ensure `LMS_API_BASE_URL=http://backend:8000` (not `localhost`) |
| LLM queries fail | Ensure `LLM_API_BASE_URL` uses `host.docker.internal` |
| Build fails at `uv sync --frozen` | Ensure `uv.lock` is copied in Dockerfile |

### Stop and restart

```bash
# Stop all services
docker compose --env-file .env.docker.secret down

# Restart services
docker compose --env-file .env.docker.secret up -d

# Rebuild and restart (after code changes)
docker compose --env-file .env.docker.secret up --build -d
```

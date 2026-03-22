# Bot Dockerfile
# Uses uv for dependency management (no pip/requirements.txt)
# Build context should be the repo root (not bot/)

FROM python:3.12-slim

# Install uv
RUN pip install uv

# Set working directory to /app/bot
WORKDIR /app/bot

# Copy dependency files first (for better layer caching)
# Both pyproject.toml and uv.lock are accessible from repo root context
COPY bot/pyproject.toml ./
COPY uv.lock ./uv.lock

# Install dependencies using uv
RUN uv sync --frozen

# Copy the rest of the bot code
COPY bot .

# Set environment variables for Docker networking
# The bot uses these to reach the backend and LLM from inside Docker
ENV LMS_API_BASE_URL=http://backend:8000
ENV LLM_API_BASE_URL=http://host.docker.internal:8080

# Run the bot
CMD ["uv", "run", "bot.py"]

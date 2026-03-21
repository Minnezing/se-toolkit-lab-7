"""Intent router for natural language queries."""

import sys
from typing import Any

from config import get_settings
from services.llm_api import LlmClient, TOOLS, SYSTEM_PROMPT
from services.lms_api import ApiError


def debug_log(message: str) -> None:
    """Print debug message to stderr (visible in --test mode)."""
    print(f"[debug] {message}", file=sys.stderr)


def route_intent(user_message: str) -> str:
    """Route a natural language query to the appropriate tools and return a response.

    Args:
        user_message: The user's natural language query

    Returns:
        Formatted response string
    """
    settings = get_settings()

    # Check if LLM is configured
    if not settings.llm_api_key or not settings.llm_api_base_url:
        return "LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL in .env.bot.secret"

    client = LlmClient(
        base_url=settings.llm_api_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_api_model,
    )

    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    debug_log(f"Sending message to LLM: {user_message[:50]}...")

    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.chat(messages, tools=TOOLS)
        except Exception as e:
            debug_log(f"LLM error: {e}")
            return f"LLM error: {type(e).__name__} ({e}). The LLM service may be unavailable."

        debug_log(f"LLM response iteration {iteration}")

        # Get the assistant's message
        choice = response.get("choices", [{}])[0]
        assistant_message = choice.get("message", {})

        # Check for tool calls
        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            # No tool calls - LLM has a final answer
            content = assistant_message.get("content", "I don't have a response.")
            debug_log(f"LLM returned final answer: {content[:100]}...")
            return content

        # Add assistant message to conversation
        messages.append(assistant_message)

        # Execute each tool call
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "unknown")
            tool_args_str = function.get("arguments", "{}")

            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}

            debug_log(f"[tool] LLM called: {tool_name}({tool_args})")

            # Execute the tool
            result = client.execute_tool(tool_name, tool_args)

            # Handle ApiError results
            if isinstance(result, ApiError):
                result_str = f"Error: {result.message}"
            else:
                result_str = json.dumps(result, default=str)

            debug_log(f"[tool] Result: {result_str[:100]}...")

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", "unknown"),
                "content": result_str,
            })

        debug_log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

    return "I reached the maximum number of steps. Let me summarize what I found so far."


# Import json here to avoid issues at module level
import json

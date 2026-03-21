"""LLM API client service for intent routing."""

import json
from typing import Any

import httpx

# All 9 backend endpoints as LLM tool schemas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups. Use for questions about students or enrollment.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab. Use for questions about score ranges.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use for questions about task difficulty or pass rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use for questions about submission patterns or activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use for comparing group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab. Use for leaderboards or finding best students.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, e.g., 5",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab. Use for questions about how many students finished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to update or refresh data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System. You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tools to get the data
3. Analyze the results
4. Provide a clear, helpful answer based on the data

If the user asks about:
- Available labs: use get_items
- Scores or pass rates for a specific lab: use get_pass_rates with the lab name
- Top students: use get_top_learners
- Group comparisons: use get_groups
- Completion rates: use get_completion_rate
- Submission patterns: use get_timeline
- Student enrollment: use get_learners
- Refreshing data: use trigger_sync

For comparison questions (e.g., "which lab has the lowest pass rate"):
1. First get the list of labs with get_items
2. Then get pass rates for each lab
3. Compare and report the answer

If you don't understand the question or it's gibberish, politely explain what you can help with.
If the user just says hello, greet them back and mention you can help with lab data questions.

Always base your answers on the tool results you receive. If a tool returns an error, explain it to the user.
"""


class LlmClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> dict:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool schemas

        Returns:
            LLM response as dict
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Execute a tool by calling the appropriate backend method.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dict

        Returns:
            Tool result
        """
        # Import here to avoid circular imports
        from services.lms_api import LmsApiClient
        from config import get_settings

        settings = get_settings()
        api_client = LmsApiClient(
            base_url=settings.lms_api_base_url,
            api_key=settings.lms_api_key,
        )

        tool_methods = {
            "get_items": lambda: api_client.get_items(),
            "get_learners": lambda: api_client.get_items(),  # Same endpoint for now
            "get_scores": lambda lab="lab-04": api_client._request(
                "GET", "/analytics/scores", params={"lab": lab}
            ),
            "get_pass_rates": lambda lab="lab-04": api_client.get_pass_rates(lab),
            "get_timeline": lambda lab="lab-04": api_client._request(
                "GET", "/analytics/timeline", params={"lab": lab}
            ),
            "get_groups": lambda lab="lab-04": api_client._request(
                "GET", "/analytics/groups", params={"lab": lab}
            ),
            "get_top_learners": lambda lab="lab-04", limit=5: api_client._request(
                "GET", "/analytics/top-learners", params={"lab": lab, "limit": limit}
            ),
            "get_completion_rate": lambda lab="lab-04": api_client._request(
                "GET", "/analytics/completion-rate", params={"lab": lab}
            ),
            "trigger_sync": lambda: api_client._request("POST", "/pipeline/sync"),
        }

        method = tool_methods.get(tool_name)
        if not method:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = method(**arguments) if arguments else method()
            return result
        except Exception as e:
            return {"error": str(e)}

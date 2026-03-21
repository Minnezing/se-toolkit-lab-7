"""LMS API client service."""

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class ApiError:
    """Represents an API error with user-friendly message."""

    message: str
    details: str


class LmsApiClient:
    """Client for the LMS backend API.

    Uses Bearer token authentication with the LMS_API_KEY.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> dict | list | ApiError:
        """Make an API request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/items/")
            **kwargs: Additional arguments for httpx.request

        Returns:
            JSON response as dict/list, or ApiError on failure
        """
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            return ApiError(
                message=f"Backend error: connection refused ({self.base_url}). Check that the services are running.",
                details=str(e),
            )
        except httpx.HTTPStatusError as e:
            return ApiError(
                message=f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                details=str(e),
            )
        except httpx.TimeoutException as e:
            return ApiError(
                message=f"Backend error: request timed out ({self.base_url}).",
                details=str(e),
            )
        except Exception as e:
            return ApiError(
                message=f"Backend error: {type(e).__name__} ({e}).",
                details=str(e),
            )

    def health_check(self) -> tuple[bool, str]:
        """Check if the backend is healthy.

        Returns:
            Tuple of (is_healthy, status_message)
        """
        result = self._request("GET", "/items/")
        if isinstance(result, ApiError):
            return False, result.message
        if isinstance(result, list):
            count = len(result)
            return True, f"Backend is healthy. {count} items available."
        return True, "Backend is healthy."

    def get_items(self) -> list[dict] | ApiError:
        """Get all items from the LMS.

        Returns:
            List of items, or ApiError on failure
        """
        result = self._request("GET", "/items/")
        return result if not isinstance(result, ApiError) else result

    def get_labs(self) -> list[dict] | ApiError:
        """Get all labs from the LMS.

        Returns:
            List of lab items, or ApiError on failure
        """
        items = self.get_items()
        if isinstance(items, ApiError):
            return items
        return [item for item in items if item.get("type") == "lab"]

    def get_pass_rates(self, lab_name: str) -> list[dict] | ApiError:
        """Get pass rates for a specific lab.

        Args:
            lab_name: The lab identifier (e.g., "lab-04")

        Returns:
            List of pass rate records, or ApiError on failure
        """
        return self._request("GET", "/analytics/pass-rates", params={"lab": lab_name})

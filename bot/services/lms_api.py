"""LMS API client service."""

import httpx


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
        )

    def health_check(self) -> bool:
        """Check if the backend is healthy.
        
        Returns:
            True if backend is up, False otherwise.
        
        TODO: Implement in Task 2.
        """
        return False

    def get_items(self) -> list[dict]:
        """Get all items from the LMS.
        
        Returns:
            List of items.
        
        TODO: Implement in Task 2.
        """
        return []

    def get_scores(self, lab_name: str) -> list[dict]:
        """Get scores for a specific lab.
        
        Args:
            lab_name: The lab identifier (e.g., "lab-04")
        
        Returns:
            List of score records.
        
        TODO: Implement in Task 2.
        """
        return []

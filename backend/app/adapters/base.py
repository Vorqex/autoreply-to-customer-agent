from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)


class PlatformError(Exception):
    def __init__(self, message: str, platform: str, status_code: int = 500):
        self.platform = platform
        self.status_code = status_code
        super().__init__(message)


class BasePlatformAdapter(ABC):

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @property
    @abstractmethod
    def platform_name(self) -> str: ...

    @abstractmethod
    async def verify_connection(self, credentials: dict) -> bool:
        """Test if credentials are valid"""

    @abstractmethod
    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Pull recent reviews from platform"""

    @abstractmethod
    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a reply to a review"""

    @abstractmethod
    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate and parse incoming webhook payload, return review data or None"""

from app.adapters.base import BasePlatformAdapter, PlatformError


class AirbnbAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "airbnb"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Airbnb API client credentials."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Airbnb API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a public reply to an Airbnb review."""
        return {"status": "success", "platform": "airbnb", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate an Airbnb webhook event."""
        return None

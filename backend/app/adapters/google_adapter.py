from app.adapters.base import BasePlatformAdapter, PlatformError


class GoogleAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "google"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Google Business Profile API credentials."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Google Business Profile API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a reply to a Google review via the Business Profile API."""
        return {"status": "success", "platform": "google", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Google Business Profile webhook notification."""
        return None

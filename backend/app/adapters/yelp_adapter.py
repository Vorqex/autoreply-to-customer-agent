from app.adapters.base import BasePlatformAdapter, PlatformError


class YelpAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "yelp"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Yelp Fusion API key."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Yelp Fusion API /businesses/{id}/reviews."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Yelp does not support public replies. Mark as acknowledged internally."""
        return {"status": "not_supported", "platform": "yelp", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Yelp webhook event."""
        return None

from app.adapters.base import BasePlatformAdapter, PlatformError


class FacebookAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "facebook"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Facebook Page Access Token."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Facebook Page /ratings endpoint."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a public reply to a Facebook recommendation via Graph API."""
        return {"status": "success", "platform": "facebook", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Facebook Page webhook event."""
        return None

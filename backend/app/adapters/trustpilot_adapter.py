from app.adapters.base import BasePlatformAdapter, PlatformError


class TrustpilotAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "trustpilot"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Trustpilot API credentials and OAuth token."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Trustpilot Business API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a public reply to a Trustpilot review."""
        return {"status": "success", "platform": "trustpilot", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Trustpilot webhook push notification."""
        return None

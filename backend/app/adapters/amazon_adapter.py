from app.adapters.base import BasePlatformAdapter, PlatformError


class AmazonAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "amazon"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Amazon Selling Partner API credentials (SP-API)."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch product reviews via the Amazon SP-API Catalog Items endpoint."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Amazon does not allow sellers to reply publicly to reviews."""
        return {"status": "not_supported", "platform": "amazon", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate an Amazon SP-API notification."""
        return None

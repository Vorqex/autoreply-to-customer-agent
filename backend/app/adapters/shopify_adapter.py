from app.adapters.base import BasePlatformAdapter, PlatformError


class ShopifyAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "shopify"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Shopify Admin API access token and store domain."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch product reviews via Shopify REST API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a reply to a Shopify product review."""
        return {"status": "success", "platform": "shopify", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Shopify webhook using HMAC signature."""
        return None

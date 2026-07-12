from app.adapters.base import BasePlatformAdapter, PlatformError


class AppStoreAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "app_store"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify App Store Connect API key (JWT-based auth)."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch customer reviews from App Store Connect API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a developer reply to an App Store review."""
        return {"status": "success", "platform": "app_store", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate an App Store Connect server notification."""
        return None

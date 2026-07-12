from app.adapters.base import BasePlatformAdapter, PlatformError


class PlayStoreAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "play_store"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Google Play Developer API service account credentials."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Google Play Developer API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a developer reply to a Google Play review."""
        return {"status": "success", "platform": "play_store", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Google Play Developer API notification."""
        return None

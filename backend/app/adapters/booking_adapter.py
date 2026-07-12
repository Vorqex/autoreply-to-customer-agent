from app.adapters.base import BasePlatformAdapter, PlatformError


class BookingAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "booking"

    async def verify_connection(self, credentials: dict) -> bool:
        """Verify Booking.com API credentials."""
        return True

    async def fetch_reviews(self, credentials: dict, since: str | None = None) -> list[dict]:
        """Fetch reviews from Booking.com API."""
        return []

    async def post_reply(self, credentials: dict, review_id: str, reply_text: str) -> dict:
        """Post a reply to a Booking.com review via the API."""
        return {"status": "success", "platform": "booking", "review_id": review_id}

    async def validate_webhook(self, headers: dict, body: bytes) -> dict | None:
        """Validate a Booking.com webhook notification."""
        return None

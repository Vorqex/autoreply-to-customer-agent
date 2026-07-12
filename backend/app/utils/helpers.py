from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from uuid import uuid4


MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"prompt": 2.50 / 1_000_000, "completion": 10.00 / 1_000_000},
    "gpt-4o-mini": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000},
    "gpt-4": {"prompt": 30.00 / 1_000_000, "completion": 60.00 / 1_000_000},
    "gpt-3.5-turbo": {"prompt": 0.50 / 1_000_000, "completion": 1.50 / 1_000_000},
    "text-embedding-3-small": {"prompt": 0.02 / 1_000_000, "completion": 0.00},
    "text-embedding-3-large": {"prompt": 0.13 / 1_000_000, "completion": 0.00},
}


def generate_uuid() -> str:
    return str(uuid4())


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        pricing = MODEL_PRICING.get("gpt-4o-mini", {"prompt": 0.0, "completion": 0.0})
    prompt_cost = prompt_tokens * pricing["prompt"]
    completion_cost = completion_tokens * pricing["completion"]
    return round(prompt_cost + completion_cost, 6)


def now() -> datetime:
    return datetime.now(timezone.utc)

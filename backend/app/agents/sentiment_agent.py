from __future__ import annotations

import json
import logging
from typing import Any, NamedTuple, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class SentimentResult(NamedTuple):
    sentiment: str
    confidence: float
    reasoning: str


_SYSTEM_PROMPT = """You are a sentiment analysis expert. Analyze the given customer review and rating.

Classify the sentiment into one of these categories:
- positive: Satisfied customer, happy experience
- neutral: Balanced, neither clearly positive nor negative
- negative: Unhappy customer, complaints
- very_negative: Strong dissatisfaction, anger, frustration
- urgent: Immediate attention needed (safety, legal, health issues)
- spam: Promotional, irrelevant, fake
- toxic: Abusive, hateful, threatening
- fake: Suspicious, bot-like, inauthentic

IMPORTANT: Do NOT label constructive criticism as negative. If a customer gives honest feedback
with suggestions for improvement, classify it as neutral even if the rating is 3.

Return a JSON object with: {"sentiment": "<category>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}
"""


class SentimentAnalysisAgent:
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None) -> None:
        self.client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze(self, review_text: str, rating: int) -> SentimentResult:
        user_prompt = f"Rating: {rating}/5\n\nReview text:\n{review_text[:2000]}"

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=200,
            )

            raw = response.choices[0].message.content or ""
            data = json.loads(raw)

            sentiment = data.get("sentiment", "neutral")
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "")

            valid_sentiments = {
                "positive", "neutral", "negative", "very_negative",
                "urgent", "spam", "toxic", "fake",
            }
            if sentiment not in valid_sentiments:
                sentiment = "neutral"

            return SentimentResult(
                sentiment=sentiment,
                confidence=min(max(confidence, 0.0), 1.0),
                reasoning=reasoning,
            )

        except Exception as exc:
            logger.warning("OpenAI sentiment analysis failed: %s", exc)

            if rating >= 4:
                return SentimentResult(
                    sentiment="positive",
                    confidence=0.7,
                    reasoning="Fallback: high rating indicates positive sentiment",
                )
            elif rating == 3:
                return SentimentResult(
                    sentiment="neutral",
                    confidence=0.6,
                    reasoning="Fallback: mid rating indicates neutral sentiment",
                )
            elif rating <= 2:
                return SentimentResult(
                    sentiment="negative",
                    confidence=0.7,
                    reasoning="Fallback: low rating indicates negative sentiment",
                )

            return SentimentResult(
                sentiment="neutral",
                confidence=0.5,
                reasoning="Fallback: unable to determine sentiment",
            )

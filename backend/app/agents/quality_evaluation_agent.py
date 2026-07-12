from __future__ import annotations

import json
import logging
from typing import Any, NamedTuple, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class QualityResult(NamedTuple):
    overall_score: float
    breakdown: dict[str, float]
    passes_threshold: bool


_EVALUATION_SYSTEM_PROMPT = """You are a quality evaluation expert for customer service replies to online reviews.

Evaluate the generated reply across these dimensions, scoring each 0-100:

1. grammar: Grammar, spelling, punctuation correctness
2. brand_consistency: How well the reply matches the brand tone and guidelines
3. professionalism: Level of professional conduct and courtesy
4. empathy: Degree of understanding and empathy shown toward the customer
5. policy_compliance: Adherence to safety rules (no liability admission, no unauthorized promises)
6. context_relevance: How well the reply addresses the specific review content
7. customer_satisfaction: Likelihood that this reply satisfies the customer
8. repetition_penalty: Penalty if the reply is repetitive or uses template-like language (100 = no repetition, 0 = highly repetitive)

Return a JSON object with:
{
  "scores": {
    "grammar": <0-100>,
    "brand_consistency": <0-100>,
    "professionalism": <0-100>,
    "empathy": <0-100>,
    "policy_compliance": <0-100>,
    "context_relevance": <0-100>,
    "customer_satisfaction": <0-100>,
    "repetition_penalty": <0-100>
  },
  "overall_score": <0-100>,
  "feedback": "<brief feedback>"
}

Calculate overall_score as the weighted average of all dimensions (weighted equally by default, but context_relevance and empathy get 1.2x weight).
"""


class QualityEvaluationAgent:
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None) -> None:
        self.client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def evaluate(
        self,
        reply_text: str,
        review: Any,
        brand: Any,
        context: str,
    ) -> QualityResult:
        user_prompt = (
            f"REVIEW:\nRating: {review.rating}/5\n"
            f"Platform: {review.platform}\n"
            f"Content: {review.content[:1000]}\n\n"
            f"GENERATED REPLY:\n{reply_text[:1000]}\n\n"
            f"BRAND CONTEXT:\n{context[:1000]}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": _EVALUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=300,
            )

            raw = response.choices[0].message.content or ""
            data = json.loads(raw)

            scores_raw = data.get("scores", {})
            overall = float(data.get("overall_score", 0))

            breakdown = {
                "grammar": float(scores_raw.get("grammar", 80)),
                "brand_consistency": float(scores_raw.get("brand_consistency", 80)),
                "professionalism": float(scores_raw.get("professionalism", 80)),
                "empathy": float(scores_raw.get("empathy", 80)),
                "policy_compliance": float(scores_raw.get("policy_compliance", 80)),
                "context_relevance": float(scores_raw.get("context_relevance", 80)),
                "customer_satisfaction": float(scores_raw.get("customer_satisfaction", 80)),
                "repetition_penalty": float(scores_raw.get("repetition_penalty", 80)),
            }

            if overall == 0:
                weights = {
                    "grammar": 1.0,
                    "brand_consistency": 1.0,
                    "professionalism": 1.0,
                    "empathy": 1.2,
                    "policy_compliance": 1.0,
                    "context_relevance": 1.2,
                    "customer_satisfaction": 1.0,
                    "repetition_penalty": 1.0,
                }
                total_weight = sum(weights.values())
                overall = sum(
                    breakdown[k] * w for k, w in weights.items()
                ) / total_weight

            overall = round(min(max(overall, 0), 100), 2)
            breakdown = {k: round(min(max(v, 0), 100), 2) for k, v in breakdown.items()}
            passes = overall >= settings.AI_QUALITY_THRESHOLD * 100

            return QualityResult(
                overall_score=overall,
                breakdown=breakdown,
                passes_threshold=passes,
            )

        except Exception as exc:
            logger.warning("Quality evaluation failed: %s", exc)

            fallback_score = 50.0
            breakdown = {
                "grammar": fallback_score,
                "brand_consistency": fallback_score,
                "professionalism": fallback_score,
                "empathy": fallback_score,
                "policy_compliance": fallback_score,
                "context_relevance": fallback_score,
                "customer_satisfaction": fallback_score,
                "repetition_penalty": fallback_score,
            }

            return QualityResult(
                overall_score=fallback_score,
                breakdown=breakdown,
                passes_threshold=fallback_score >= settings.AI_QUALITY_THRESHOLD * 100,
            )

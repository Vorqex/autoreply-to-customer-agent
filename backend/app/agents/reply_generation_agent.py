from __future__ import annotations

import json
import logging
from typing import Any, NamedTuple, Optional
from uuid import UUID

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.review import Review
from app.models.brand_voice import BrandVoice
from app.models.business import Business

logger = logging.getLogger(__name__)


class GenerationResult(NamedTuple):
    reply_text: str
    reasoning_summary: str
    raw_response: dict[str, Any]


_FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Rating: 5/5\nReview: Amazing service! The staff was incredibly helpful and went above and beyond.",
    },
    {
        "role": "assistant",
        "content": """```json
{
  "reply": "Thank you so much for your wonderful review! We're thrilled to hear that our team made such a positive impression. Your kind words mean the world to us, and we look forward to serving you again soon!",
  "reasoning": "Positive review requiring gratitude-focused response",
  "sentiment": "positive"
}
```""",
    },
    {
        "role": "user",
        "content": "Rating: 2/5\nReview: The product arrived late and was damaged. Very disappointed with the quality.",
    },
    {
        "role": "assistant",
        "content": """```json
{
  "reply": "We sincerely apologize for your experience. This is certainly not the standard we aim for. Please contact our support team at support@company.com so we can make this right with a replacement or refund. Your feedback helps us improve.",
  "reasoning": "Negative review requiring apology and solution-focused response",
  "sentiment": "negative"
}
```""",
    },
    {
        "role": "user",
        "content": "Rating: 3/5\nReview: It was okay. Nothing special but got the job done. Could be better.",
    },
    {
        "role": "assistant",
        "content": """```json
{
  "reply": "Thank you for your honest feedback. We appreciate you taking the time to share your thoughts. We're always working to improve, and comments like yours help us understand where we can do better. We hope to exceed your expectations next time!",
  "reasoning": "Neutral review that acknowledges feedback without being defensive",
  "sentiment": "neutral"
}
```""",
    },
]


def _build_system_prompt(
    business: Business,
    brand: BrandVoice,
    knowledge_context: str,
    custom_instructions: Optional[str] = None,
) -> str:
    parts = [
        "You are an expert customer service reply writer for businesses responding to online reviews.",
        "",
        f"Business: {business.name or 'Unknown'}",
        f"Industry: {business.industry or 'General'}",
        f"Brand Tone: {brand.tone}",
        f"Writing Style: {brand.style}",
        f"Language: {brand.language}",
        f"Personality: {brand.personality or 'Professional and courteous'}",
    ]

    if brand.values:
        parts.append(f"Core Values: {', '.join(brand.values)}")

    if brand.keywords:
        parts.append(f"Preferred Keywords: {', '.join(brand.keywords)}")

    if brand.forbidden_terms:
        parts.append(f"Terms to AVOID: {', '.join(brand.forbidden_terms)}")

    if brand.custom_rules:
        parts.append("Additional Rules:")
        for i, rule in enumerate(brand.custom_rules, 1):
            parts.append(f"  {i}. {rule}")

    if brand.greeting_template:
        parts.append(f"\nGreeting format: {brand.greeting_template}")

    if brand.closing_template:
        parts.append(f"Closing format: {brand.closing_template}")

    if knowledge_context:
        parts.append(f"\nKnowledge Base Context:\n{knowledge_context}")

    parts.append(
        """

SAFETY RULES (ABSOLUTELY MANDATORY):
1. NEVER hallucinate facts, figures, or claims not present in the context or review
2. NEVER admit liability or fault on behalf of the business
3. NEVER make specific promises (refunds, discounts, replacements) without authorization
4. NEVER share personal contact information beyond what's in the brand profile
5. NEVER use profanity, discriminatory language, or aggressive tone
6. NEVER mention competitors by name
7. NEVER speculate about causes or make assumptions
8. Keep the response professional and solution-focused

OUTPUT FORMAT:
Respond with a JSON object exactly like this:
{
  "reply": "<your reply text here>",
  "reasoning": "<brief reasoning about the approach taken>"
}

GUIDELINES:
- For ratings 4-5: Focus on gratitude and appreciation. Thank the customer.
- For ratings 1-2: Focus on apology, empathy, and constructive resolution. Do NOT be defensive.
- For rating 3: Acknowledge feedback, show commitment to improvement.
- Match the customer's language when appropriate.
- Keep replies concise (50-200 words typically).
- Never include markdown code blocks in the reply itself.
"""
    )

    if custom_instructions:
        parts.append(f"\nCUSTOM INSTRUCTIONS:\n{custom_instructions}")

    return "\n".join(parts)


class ReplyGenerationAgent:
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None) -> None:
        self.client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(
        self,
        business_id: UUID,
        review: Review,
        brand: BrandVoice,
        knowledge: str,
        custom_instructions: Optional[str] = None,
    ) -> GenerationResult:
        business_result = None
        try:
            from sqlalchemy import select
            from app.core.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Business).where(Business.id == business_id)
                )
                business_result = result.scalar_one_or_none()
        except Exception:
            pass

        business = business_result or Business(name="Business", industry="General")

        system_prompt = _build_system_prompt(
            business, brand, knowledge, custom_instructions
        )

        user_prompt_parts = [
            f"Rating: {review.rating}/5",
            f"Platform: {review.platform}",
            f"Customer: {review.customer_name}",
            f"Language: {review.language or 'en'}",
            f"Sentiment: {review.sentiment or 'unknown'}",
            f"\nReview Title: {review.title or 'N/A'}",
            f"\nReview Text:\n{review.content[:2000]}",
        ]
        user_prompt = "\n".join(user_prompt_parts)

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        messages.extend(
            {"role": example["role"], "content": example["content"]}
            for example in _FEW_SHOT_EXAMPLES
        )

        messages.append({"role": "user", "content": user_prompt})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500,
            )

            raw_content = response.choices[0].message.content or ""
            data = json.loads(raw_content)

            reply_text = (data.get("reply") or "").strip()
            reasoning = (data.get("reasoning") or data.get("reasoning_summary") or "").strip()

            raw_response = {
                "model": settings.OPENAI_MODEL,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

            # Safety strip: remove code fences, markdown that may leak
            reply_text = reply_text.replace("```json", "").replace("```", "").strip()

            if not reply_text:
                reply_text = "Thank you for your feedback. We appreciate your business and will take your comments into consideration."
                reasoning = "Fallback: empty response from model"

            return GenerationResult(
                reply_text=reply_text,
                reasoning_summary=reasoning,
                raw_response=raw_response,
            )

        except Exception as exc:
            logger.error("Reply generation failed: %s", exc)

            fallback_reply = (
                f"Dear {review.customer_name}, thank you for your feedback. "
                "We take all reviews seriously and will use your input to improve our service. "
                "Please feel free to contact us directly if you would like to discuss further."
            )

            return GenerationResult(
                reply_text=fallback_reply,
                reasoning_summary=f"Fallback reply due to generation error: {exc}",
                raw_response={"error": str(exc), "model": settings.OPENAI_MODEL},
            )

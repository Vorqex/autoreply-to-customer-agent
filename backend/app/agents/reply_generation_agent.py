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


_TEMPLATE_RESPONSES: dict[str, str] = {
    "positive": (
        "Thank you for your wonderful feedback, {customer_name}! "
        "We're delighted to hear about your positive experience and appreciate you "
        "taking the time to share it. We look forward to serving you again soon!"
    ),
    "negative": (
        "Dear {customer_name}, thank you for sharing your feedback. We sincerely "
        "apologize for your experience and understand your frustration. We would like "
        "to learn more and make things right \u2014 please reach out to our support "
        "team directly so we can address your concerns."
    ),
    "neutral": (
        "Thank you for your honest feedback, {customer_name}. We appreciate your "
        "thoughts and are always looking for ways to improve. We hope to exceed "
        "your expectations on your next visit."
    ),
    "very_negative": (
        "Dear {customer_name}, we are truly sorry to hear about your experience. "
        "This is not the standard we strive for. Please contact our support team "
        "directly so we can address your concerns personally."
    ),
    "urgent": (
        "Dear {customer_name}, we take your concerns very seriously. Please contact "
        "us immediately so we can address this urgent matter promptly. "
        "Your satisfaction and safety are our top priorities."
    ),
}


class GenerationResult(NamedTuple):
    reply_text: str
    reasoning_summary: str
    raw_response: dict[str, Any]


_FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Rating: 5/5\nPlatform: Google\nCustomer: Sarah\nReview: Amazing service! The staff was incredibly helpful and went above and beyond.",
    },
    {
        "role": "assistant",
        "content": """{
  "reply": "Thank you so much, Sarah! We're thrilled to hear that our team made such a positive impression. Your kind words mean the world to us, and we look forward to serving you again soon!",
  "reasoning": "Positive review: express gratitude, personalize with customer name, reinforce positive experience",
  "sentiment": "positive"
}""",
    },
    {
        "role": "user",
        "content": "Rating: 2/5\nPlatform: Yelp\nCustomer: Mike\nReview: The product arrived late and was damaged. Very disappointed with the quality.",
    },
    {
        "role": "assistant",
        "content": """{
  "reply": "Mike, we sincerely apologize for your experience. This is not the standard we aim for, and we understand your frustration. We'd like to make this right - please reach out to our support team so we can arrange a replacement or refund. Your feedback helps us improve our quality control.",
  "reasoning": "Negative review: acknowledge frustration, apologize sincerely, offer actionable solution without making unauthorized promises, invite private contact",
  "sentiment": "negative"
}""",
    },
    {
        "role": "user",
        "content": "Rating: 3/5\nPlatform: Trustpilot\nCustomer: Alex\nReview: It was okay. Nothing special but got the job done. Could be better.",
    },
    {
        "role": "assistant",
        "content": """{
  "reply": "Thank you for your honest feedback, Alex. We appreciate you taking the time to share your thoughts - it helps us understand where we can improve. We're committed to making every experience special, and we hope to exceed your expectations next time you visit.",
  "reasoning": "Neutral review: acknowledge feedback, show appreciation without being defensive, express commitment to improvement",
  "sentiment": "neutral"
}""",
    },
    {
        "role": "user",
        "content": "Rating: 1/5\nPlatform: Google\nCustomer: Jamie\nReview: This place is an absolute scam. They charged me twice and refused to refund. DO NOT GO HERE. I'm reporting them to the Better Business Bureau.",
    },
    {
        "role": "assistant",
        "content": """{
  "reply": "Jamie, we are truly sorry to hear about your billing issue. This is not the experience we want any of our customers to have. We take payment concerns very seriously and would like to investigate this immediately. Please contact our billing team directly so we can review your charges and resolve this promptly.",
  "reasoning": "Very negative review: apologize sincerely, address the specific billing concern without admitting liability, offer direct resolution path, remain professional despite angry tone, DO NOT escalate or argue",
  "sentiment": "very_negative"
}""",
    },
    {
        "role": "user",
        "content": "Rating: 1/5\nPlatform: Trustpilot\nCustomer: Taylor\nReview: URGENT - I just left your store and realized I was overcharged $50. I need this fixed IMMEDIATELY. Someone call me back right now.",
    },
    {
        "role": "assistant",
        "content": """{
  "reply": "Taylor, we are extremely sorry about this billing error. We understand the urgency and want to resolve this for you as quickly as possible. Please contact our support team directly so we can review your receipt and process the correction immediately. Your time is valuable, and we appreciate you bringing this to our attention.",
  "reasoning": "Urgent review: acknowledge urgency, address the specific billing issue, provide immediate action path, stay calm and solution-oriented despite urgent tone, DO NOT make promises about exact refund amounts",
  "sentiment": "urgent"
}""",
    },
]


def _build_system_prompt(
    business: Business,
    brand: BrandVoice,
    knowledge_context: str,
    custom_instructions: Optional[str] = None,
    risk_level: str = "low",
) -> str:
    platform_guidelines = {
        "google": (
            "PLATFORM: Google Reviews\n"
            "- Expected length: 50-300 characters (concise and scannable)\n"
            "- Tone: Professional and factual. Avoid marketing language.\n"
            "- Google expects replies that directly address the reviewer's experience.\n"
            "- For negative reviews: acknowledge briefly, offer offline resolution.\n"
            "- For positive reviews: be warm but concise."
        ),
        "yelp": (
            "PLATFORM: Yelp\n"
            "- Expected length: 100-500 characters (more detail okay)\n"
            "- Tone: Authentic and personal. Yelp users value genuine responses.\n"
            "- Avoid generic templates \u2014 they stand out on Yelp.\n"
            "- For negative reviews: apologize sincerely, take conversation offline.\n"
            "- NEVER offer incentives for review changes (violates Yelp TOS)."
        ),
        "trustpilot": (
            "PLATFORM: Trustpilot\n"
            "- Expected length: 100-400 characters\n"
            "- Tone: Formal and transparent. Trustpilot users expect honesty.\n"
            "- Trustpilot replies are permanent \u2014 be thoughtful and accurate.\n"
            "- For negative reviews: acknowledge the issue publicly, offer resolution path.\n"
            "- Acknowledge both positive and negative feedback equally."
        ),
        "facebook": (
            "PLATFORM: Facebook\n"
            "- Expected length: 50-200 characters\n"
            "- Tone: Friendly and conversational. Can be slightly more casual.\n"
            "- Facebook audiences appreciate personality and warmth.\n"
            "- Keep it brief \u2014 long replies get less engagement."
        ),
        "default": (
            "PLATFORM: General\n"
            "- Expected length: 50-200 words\n"
            "- Tone: Balance professionalism with warmth.\n"
            "- Address the reviewer by name when known."
        ),
    }

    platform = (business.settings or {}).get("platform", "default") if hasattr(business, "settings") else "default"
    platform_key = platform.lower() if isinstance(platform, str) else "default"
    platform_note = platform_guidelines.get(platform_key, platform_guidelines["default"])

    risk_advisory = ""
    if risk_level == "high":
        risk_advisory = (
            "\n\u26a0\ufe0f HIGH-RISK RESPONSE \u2014 EXTREME CAUTION REQUIRED\n"
            "- Choose every word carefully. Prioritize safety over creativity.\n"
            "- Be conservative, professional, and de-escalating.\n"
            "- DO NOT speculate, admit liability, or make promises.\n"
            "- If unsure, err on the side of a shorter, safer reply."
        )
    elif risk_level == "medium":
        risk_advisory = (
            "\n\u26a0 MEDIUM-RISK RESPONSE\n"
            "- Balance empathy with professionalism.\n"
            "- Be helpful but avoid over-promising.\n"
            "- Acknowledge concerns without admitting fault."
        )

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
        sanitized_context = knowledge_context.replace("```json", "").replace("```", "")
        parts.append(f"\nKnowledge Base Context:\n{sanitized_context}")

    tone_label = (brand.tone or "professional").lower()
    brand_voice_guide = {
        "luxury": (
            "BRAND VOICE: LUXURY\n"
            "- Use sophisticated, refined language. Avoid casual contractions.\n"
            "- Be elegant and polished \u2014 words like 'pleasure', 'honored', 'discerning'.\n"
            "- Maintain exclusivity in tone without being dismissive.\n"
            "- Respond with grace and composure, even to criticism."
        ),
        "friendly": (
            "BRAND VOICE: FRIENDLY\n"
            "- Use warm, conversational language. Contractions are welcome.\n"
            "- Be approachable and personable \u2014 like a helpful neighbor.\n"
            "- Use exclamation marks sparingly for genuine enthusiasm.\n"
            "- Make the customer feel like they're talking to a friend."
        ),
        "professional": (
            "BRAND VOICE: PROFESSIONAL\n"
            "- Use polished, respectful language. Maintain formal courtesy.\n"
            "- Be clear, direct, and solution-oriented.\n"
            "- Avoid slang, casual expressions, or excessive familiarity.\n"
            "- Demonstrate competence and reliability in every response."
        ),
        "playful": (
            "BRAND VOICE: PLAYFUL\n"
            "- Use lighthearted, witty language that reflects brand personality.\n"
            "- Be engaging and fun without being unprofessional.\n"
            "- Humor is acceptable when appropriate to the context.\n"
            "- For negative reviews, dial back the playfulness \u2014 be sincere first."
        ),
    }
    voice_guide = brand_voice_guide.get(tone_label, brand_voice_guide["professional"])

    parts.append(f"""
{platform_note}

{voice_guide}

EMOTIONAL INTELLIGENCE & FRUSTRATION CALIBRATION:
- Match your empathy level to the customer's frustration:
  * Frustration: none / sentiment: positive
    -> Warm, appreciative. Reinforce their positive experience. Thank them specifically.
  * Frustration: mild / sentiment: neutral
    -> Polite, encouraging. Acknowledge their feedback, express commitment to improvement.
  * Frustration: moderate / sentiment: negative
    -> Empathetic, understanding. Apologize for their experience. Offer a solution path.
  * Frustration: high / sentiment: very_negative
    -> Highly empathetic, de-escalating. Validate their feelings. Avoid defensiveness. Offer direct contact.
  * Frustration: anger / sentiment: urgent or very_negative
    -> Calm, professional, de-escalating. DO NOT match their tone. Address the core issue directly.

- Language patterns by frustration level:
  * None/Mild: "Thank you for...", "We appreciate..."
  * Moderate: "We understand your frustration...", "We apologize for..."
  * High: "We are truly sorry...", "This is not the standard we aim for..."
  * Anger: "We hear you...", "Please contact us so we can...", avoid emotional language

ANTI-HALLUCINATION RULES (ABSOLUTELY MANDATORY):
1. NEVER invent facts, statistics, figures, claims, or policies not present in the review text or knowledge base context
2. NEVER make up specific dates, names, order numbers, or transaction details
3. NEVER claim "we've fixed this issue" or "this has been resolved" unless the review indicates the customer was already contacted
4. NEVER use "we always" or "we never" absolute statements - they create liability
5. NEVER admit liability, fault, or legal responsibility (e.g., "we admit", "it was our fault", "we are responsible")
6. NEVER promise specific outcomes like refunds, replacements, discounts, or credits without explicit authorization
7. NEVER share personal contact info (email, phone) beyond what's in the brand profile
8. NEVER mention competitors by name or compare services to competitors
9. NEVER speculate about causes or make assumptions about what happened
10. NEVER use profanity, discriminatory language, or aggressive tone
11. NEVER invent specific promotions, discounts, refund amounts, staff names, or future menu items not in the knowledge base
12. NEVER claim awards, certifications, or achievements that are not documented in the knowledge base

WHAT NOT TO SAY - EXAMPLES:
  \u2717 "We admit this was our mistake" \u2192 \u2713 "We apologize for your experience"
  \u2717 "We will refund you immediately" \u2192 \u2713 "Please contact us so we can help resolve this"
  \u2717 "This never happens" \u2192 \u2713 "This is not the standard we aim for"
  \u2717 "You're wrong about that" \u2192 \u2713 "We appreciate you bringing this to our attention"
  \u2717 "Our competitor X does it better" \u2192 NEVER mention competitors at all
  \u2717 "Here\u2019s a 20% discount code..." \u2192 \u2713 "We'd like to make this right \u2014 please contact us"
  \u2717 "Our new seasonal menu has..." \u2192 NEVER mention future offerings not in knowledge base
  \u2717 "Manager John will handle this" \u2192 NEVER use staff names not in brand profile

BRAND VOICE ENFORCEMENT:
- Every reply MUST reflect the brand's tone, style, and personality defined above
- Use preferred keywords naturally where appropriate
- NEVER use forbidden terms under any circumstances
- Ensure the reply reads like it comes from this specific business, not a generic template
- Match the brand's tone exactly. If brand tone is 'luxury', use sophisticated language.
  If 'friendly', use warm conversational language. If 'professional', be polished and direct.
- The reply should sound like it was written by a human from the brand, not by AI.

OUTPUT FORMAT - STRICT JSON:
You must respond with a valid JSON object. No markdown fences, no code blocks, no additional text.
{{
  "reply": "<your complete reply text here - plain text only, no markdown>",
  "reasoning": "<your reasoning: 1-2 sentences on approach, sentiment detected, and strategy used>"
}}

REPLY CONTENT GUIDELINES:
- For ratings 4-5: Focus on genuine gratitude and specific appreciation. Reference something specific from their review.
- For ratings 1-2: Focus on empathy, apology, and constructive resolution path. Never be defensive or argumentative.
- For rating 3: Acknowledge the balanced feedback, show commitment to improvement, encourage another visit.
- Use the customer's name naturally in the reply when provided.
- Reference specific details from the review to show you actually read it.
- Keep replies concise (50-150 words for Google, 50-200 for others).
- Use plain text only - no markdown, no HTML, no formatting in the reply.
- Do NOT include "---" dividers or extra formatting in the reply text.
- Do NOT wrap the reply in quotes.
{risk_advisory}""")

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
        risk_level: str = "low",
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

        risk_sentiment = risk_level
        if risk_level == "low" and review.sentiment in ("positive", "neutral"):
            risk_sentiment = "positive"
        temperature_map = {
            "positive": 0.7,
            "low": 0.5,
            "medium": 0.3,
            "high": 0.2,
        }
        temperature = temperature_map.get(risk_sentiment, 0.4)

        system_prompt = _build_system_prompt(
            business, brand, knowledge, custom_instructions, risk_level
        )

        sentiment_label = review.sentiment or "unknown"
        frustration_level = "unknown"
        if sentiment_label == "very_negative":
            frustration_level = "high"
        elif sentiment_label == "negative":
            frustration_level = "moderate"
        elif sentiment_label == "neutral":
            frustration_level = "mild"
        elif sentiment_label == "positive":
            frustration_level = "none"
        elif sentiment_label == "urgent":
            frustration_level = "anger"

        user_prompt_parts = [
            f"Rating: {review.rating}/5",
            f"Platform: {review.platform}",
            f"Customer: {review.customer_name}",
            f"Language: {review.language or 'en'}",
            f"Sentiment: {sentiment_label}",
            f"Frustration Level: {frustration_level}",
            f"Risk Level: {risk_level}",
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
                temperature=temperature,
                max_tokens=600,
            )

            raw_content = response.choices[0].message.content or ""
            data = json.loads(raw_content)

            reply_text = (data.get("reply") or "").strip()
            reasoning = (data.get("reasoning") or data.get("reasoning_summary") or "").strip()

            raw_response = {
                "model": settings.OPENAI_MODEL,
                "finish_reason": response.choices[0].finish_reason,
                "temperature_used": temperature,
                "risk_level": risk_level,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

            reply_text = reply_text.replace("```json", "").replace("```", "").replace("```json", "").strip()
            reply_text = reply_text.strip('"').strip("'")

            if not reply_text:
                sentiment_key = sentiment_label if sentiment_label in _TEMPLATE_RESPONSES else "neutral"
                reply_text = _TEMPLATE_RESPONSES[sentiment_key].format(
                    customer_name=review.customer_name
                )
                reasoning = "Fallback: empty response from model"

            return GenerationResult(
                reply_text=reply_text,
                reasoning_summary=reasoning,
                raw_response=raw_response,
            )

        except Exception as exc:
            logger.error("Reply generation failed: %s", exc)

            sentiment_key = sentiment_label if sentiment_label in _TEMPLATE_RESPONSES else "neutral"
            fallback_reply = _TEMPLATE_RESPONSES[sentiment_key].format(
                customer_name=review.customer_name
            )

            return GenerationResult(
                reply_text=fallback_reply,
                reasoning_summary=f"Fallback reply due to generation error: {exc}",
                raw_response={"error": str(exc), "model": settings.OPENAI_MODEL},
            )

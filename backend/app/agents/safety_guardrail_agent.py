from __future__ import annotations

import json
import logging
import re
from typing import Any, NamedTuple, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class SafetyResult(NamedTuple):
    is_safe: bool
    safety_score: float
    violations: list[str]


_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
_PROMPT_INJECTION_PATTERN = re.compile(
    r"(ignore (all )?(previous|above).*instructions|"
    r"forget (about )?(all )?(previous|above).*instructions|"
    r"system prompt|you are (now|not )|"
    r"act as|pretend to be|"
    r"disregard|override|new instructions)",
    re.IGNORECASE,
)


class SafetyGuardrailAgent:
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None) -> None:
        self.client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def check(
        self,
        reply_text: str,
        review_text: str,
        brand_context: str,
    ) -> SafetyResult:
        violations: list[str] = []
        score = 1.0
        reply_lower = reply_text.lower()

        # PII checks
        if _EMAIL_PATTERN.search(reply_text):
            violations.append("contains_email")
            score -= 0.15

        if _PHONE_PATTERN.search(reply_text):
            violations.append("contains_phone_number")
            score -= 0.15

        if _SSN_PATTERN.search(reply_text):
            violations.append("contains_ssn")
            score -= 0.3

        if _CREDIT_CARD_PATTERN.search(reply_text):
            violations.append("contains_credit_card")
            score -= 0.3

        # Prompt injection check
        if _PROMPT_INJECTION_PATTERN.search(reply_text):
            violations.append("prompt_injection_pattern")
            score -= 0.2

        # Brand voice misalignment checks
        if "forbidden_terms" in brand_context.lower():
            forbidden_match = re.search(
                r"avoid:\s*(.+?)(?:\n|$)", brand_context, re.IGNORECASE
            )
            if forbidden_match:
                forbidden_terms = [
                    t.strip().lower()
                    for t in forbidden_match.group(1).split(",")
                ]
                for term in forbidden_terms:
                    if term and term in reply_lower:
                        violations.append(f"forbidden_term_used:{term}")
                        score -= 0.1

        # Hallucination checks: look for specific claims that shouldn't be in reply
        explicit_liability = re.search(
            r"\b(we admit|we acknowledge (liability|fault)|"
            r"we are responsible for the|it is our fault|"
            r"we take full responsibility for the)\b",
            reply_lower,
        )
        if explicit_liability:
            violations.append("liability_admission")
            score -= 0.2

        specific_promises = re.search(
            r"\b(we will (refund|replace|give you|send you|offer you a free)|"
            r"you will receive|you are entitled to)\b",
            reply_lower,
        )
        if specific_promises:
            violations.append("unauthorized_promise")
            score -= 0.15

        # Toxicity check via OpenAI moderation
        try:
            moderation = await self.client.moderations.create(input=reply_text)
            if moderation.results:
                result = moderation.results[0]
                if result.flagged:
                    categories = [
                        cat
                        for cat, flagged in result.categories.model_dump().items()
                        if flagged
                    ]
                    for cat in categories:
                        violations.append(f"toxic_content:{cat}")
                        score -= 0.2
        except Exception as exc:
            logger.warning("Moderation API call failed: %s", exc)

        score = max(0.0, round(score, 2))
        is_safe = len(violations) == 0

        return SafetyResult(
            is_safe=is_safe,
            safety_score=score,
            violations=violations,
        )

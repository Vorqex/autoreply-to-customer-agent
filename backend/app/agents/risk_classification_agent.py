from __future__ import annotations

import re
from typing import NamedTuple


class RiskResult(NamedTuple):
    risk_level: str
    needs_human_review: bool
    risk_factors: list[str]


_SENSITIVE_INDUSTRIES = {"medical", "legal", "healthcare", "financial", "insurance", "pharmaceutical"}


class RiskClassificationAgent:
    async def classify(
        self,
        review_text: str,
        rating: int,
        sentiment: str,
        platform: str,
        business_industry: str,
    ) -> RiskResult:
        risk_factors: list[str] = []
        text_lower = review_text.lower()

        high_risk_sentiments = {"very_negative", "toxic", "urgent", "spam", "fake"}
        if sentiment in high_risk_sentiments:
            risk_factors.append(f"high_risk_sentiment:{sentiment}")

        if sentiment == "negative" and rating <= 2:
            risk_factors.append("negative_with_low_rating")

        # Industry-related risk
        industry_lower = business_industry.lower()
        for keyword in _SENSITIVE_INDUSTRIES:
            if keyword in industry_lower:
                risk_factors.append(f"sensitive_industry:{business_industry}")
                break

        # Mentions of minors, safety, legal issues
        if re.search(
            r"\b(child|minor|underage|kid|teenager)\b", text_lower, re.IGNORECASE
        ):
            risk_factors.append("minor_mentioned")

        if re.search(
            r"\b(safety|unsafe|dangerous|hazard|accident|injury|harm|"
            r"lawsuit|attorney|legal action|sue|suing|complaint to|"
            r"regulator|authority|police|lawyer)\b",
            text_lower,
            re.IGNORECASE,
        ):
            risk_factors.append("safety_or_legal_concern")

        # Health mentions
        if re.search(
            r"\b(health|hospital|medical|surgery|diagnosis|"
            r"prescription|medication|treatment|condition|symptom)\b",
            text_lower,
            re.IGNORECASE,
        ):
            if industry_lower not in _SENSITIVE_INDUSTRIES:
                risk_factors.append("health_mention_outside_healthcare")

        if sentiment == "spam":
            risk_factors.append("spam_detected")

        if sentiment == "toxic":
            risk_factors.append("toxic_content")

        # Financial mentions
        if re.search(
            r"\b(refund|money back|charge|billing|overcharged|"
            r"scammed|fraud|stolen|payment issue|credit card|bank)\b",
            text_lower,
            re.IGNORECASE,
        ):
            risk_factors.append("financial_concern")

        # Escalation language
        if re.search(
            r"\b(never again|warning|beware|terrible|worst|horrible|"
            r"disgusting|appalling|unacceptable)\b",
            text_lower,
            re.IGNORECASE,
        ):
            risk_factors.append("escalation_language")

        # Determine risk level
        if sentiment in ("very_negative", "toxic", "urgent", "fake") or any(
            "safety" in f or "legal" in f or "minor" in f for f in risk_factors
        ):
            risk_level = "high"
        elif (
            sentiment == "negative"
            or sentiment == "spam"
            or rating == 3
            or len(risk_factors) >= 2
        ):
            risk_level = "medium"
        else:
            risk_level = "low"

        needs_human_review = risk_level in ("medium", "high")

        return RiskResult(
            risk_level=risk_level,
            needs_human_review=needs_human_review,
            risk_factors=list(set(risk_factors)),
        )

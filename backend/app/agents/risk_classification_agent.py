from __future__ import annotations

import re
import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)


class RiskResult(NamedTuple):
    risk_level: str
    needs_human_review: bool
    risk_factors: list[str]
    risk_score: float = 0.0


_SENSITIVE_INDUSTRIES = {"medical", "legal", "healthcare", "financial", "insurance", "pharmaceutical"}
_CHILDREN_INDUSTRIES = {"education", "childcare", "daycare", "tutoring", "pediatrics", "children"}

_ESCALATION_PATTERNS = [
    r"\b(lawsuit|lawyer|sue|suing|legal action|litigation)\b",
    r"\b(attorney|complaint to|regulator|authority|police|file a complaint)\b",
    r"\b(never again|warning|beware|stay away|avoid at all costs)\b",
    r"\b(terrible|worst|horrible|disgusting|appalling|unacceptable)\b",
]

_COMPETITOR_PATTERNS = [
    r"\b(compared to|better at|unlike|switched to|went to|"
    r"using .* instead|prefer .* over|moved to)\b",
]

_FAKE_REVIEW_PATTERNS = [
    r"\b(5 stars?|5/5|perfect score)\b.{0,30}\b(amazing|incredible|loved it|the best)\b",
    r"\b(I received|I got a free|in exchange for|discount for review|"
    r"compensated for|paid review)\b",
    r"^(great|amazing|awesome|excellent|fantastic|perfect|wonderful)\s*(great|amazing|awesome)",
    r"\b(must try|highly recommend|five star|definitely recommend)\b",
    r"\b(as expected|same as always|usual great)\b.{0,20}\b(great service|good job)\b",
]

_NEGATIVE_LENGTH_RISK = re.compile(r"\b(bad|worst|terrible|horrible|awful|disgusting)\b", re.IGNORECASE)


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
        word_count = len(review_text.split())
        risk_score = 0.0

        high_risk_sentiments = {"very_negative", "toxic", "urgent", "spam", "fake"}
        if sentiment in high_risk_sentiments:
            risk_factors.append(f"high_risk_sentiment:{sentiment}")
            risk_score += 0.3 if sentiment in ("very_negative", "toxic") else 0.2

        if sentiment == "negative" and rating <= 2:
            risk_factors.append("negative_with_low_rating")
            risk_score += 0.15

        if sentiment == "negative" and word_count < 10:
            risk_factors.append("short_negative_review")
            risk_score += 0.1

        industry_lower = business_industry.lower()
        for keyword in _SENSITIVE_INDUSTRIES:
            if keyword in industry_lower:
                risk_factors.append(f"sensitive_industry:{business_industry}")
                risk_score += 0.15
                break

        for keyword in _CHILDREN_INDUSTRIES:
            if keyword in industry_lower:
                risk_factors.append(f"children_related_industry:{business_industry}")
                risk_score += 0.2
                break

        if re.search(
            r"\b(child|minor|underage|kid|teenager)\b", text_lower, re.IGNORECASE
        ):
            risk_factors.append("minor_mentioned")
            risk_score += 0.2

        if re.search(
            r"\b(safety|unsafe|dangerous|hazard|accident|injury|harm)\b",
            text_lower,
            re.IGNORECASE,
        ):
            risk_factors.append("safety_or_legal_concern")
            risk_score += 0.2

        if re.search(
            r"\b(health|hospital|medical|surgery|diagnosis|"
            r"prescription|medication|treatment|condition|symptom)\b",
            text_lower,
            re.IGNORECASE,
        ):
            if industry_lower not in _SENSITIVE_INDUSTRIES:
                risk_factors.append("health_mention_outside_healthcare")
                risk_score += 0.1

        if sentiment == "spam":
            risk_factors.append("spam_detected")
            risk_score += 0.2

        if sentiment == "toxic":
            risk_factors.append("toxic_content")
            risk_score += 0.3

        if re.search(
            r"\b(refund|money back|charge|billing|overcharged|"
            r"scammed|fraud|stolen|payment issue|credit card|bank)\b",
            text_lower,
            re.IGNORECASE,
        ):
            risk_factors.append("financial_concern")
            risk_score += 0.15

        for pattern in _ESCALATION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                risk_factors.append("escalation_language")
                risk_score += 0.15
                break

        for pattern in _COMPETITOR_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                risk_factors.append("competitor_mention")
                risk_score += 0.1
                break

        for pattern in _FAKE_REVIEW_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                risk_factors.append("potential_fake_review")
                risk_score += 0.15
                break

        if rating == 5 and word_count < 5 and sentiment == "positive":
            risk_factors.append("short_very_positive")
            risk_score += 0.05

        negative_words = _NEGATIVE_LENGTH_RISK.findall(text_lower)
        if len(negative_words) >= 2 and word_count < 15:
            risk_factors.append("brief_negative_outburst")
            risk_score += 0.1

        if word_count > 200 and sentiment in ("negative", "very_negative"):
            risk_factors.append("long_negative_vent")
            risk_score += 0.1

        if sentiment in ("very_negative", "toxic", "urgent", "fake") or any(
            "safety" in f or "legal" in f or "minor" in f or "children" in f
            for f in risk_factors
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

        risk_score = min(1.0, round(risk_score, 2))
        needs_human_review = risk_level in ("medium", "high")

        return RiskResult(
            risk_level=risk_level,
            needs_human_review=needs_human_review,
            risk_factors=list(set(risk_factors)),
            risk_score=risk_score,
        )

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, NamedTuple, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class SafetyResult(NamedTuple):
    is_safe: bool
    safety_score: float
    violations: list[dict[str, Any]]
    violation_details: dict[str, Any]


_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")

_ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+[A-Za-z0-9\s.,]+(?:street|st|avenue|ave|road|rd|"
    r"boulevard|blvd|lane|ln|drive|dr|court|ct|place|pl|way|circle|cir)\b",
    re.IGNORECASE,
)

_ZIP_CODE_PATTERN = re.compile(r"\b\d{5}(?:-\d{4})?\b")

# Additional PII patterns
_IP_ADDRESS_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)
_DOB_PATTERN = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
)
_ACCOUNT_NUMBER_PATTERN = re.compile(
    r"\b(?:account[#:\s]*\d{4,12}|acct[#:\s]*\d{4,12})\b",
    re.IGNORECASE,
)

_PROMPT_INJECTION_BASIC = re.compile(
    r"(ignore (all )?(previous|above).*instructions|"
    r"forget (about )?(all )?(previous|above).*instructions|"
    r"system prompt|you are (now|not )|"
    r"act as|pretend to be|"
    r"disregard|override|new instructions|"
    r"ignore your|forget your prompts)",
    re.IGNORECASE,
)

_PROMPT_INJECTION_ADVANCED = re.compile(
    r"(do not follow|stop following|ignore your|break character|"
    r"you are an ai|as an ai|you must (now )?|"
    r"instruction:|user instruction:|system message:|"
    r"output format:|respond in|forget your role|"
    r"you are a chatbot|you are a language model|"
    r"you are an ai assistant|you are gpt|"
    r"disregard previous|override instructions)",
    re.IGNORECASE,
)

_LIABILITY_PATTERNS = [
    re.compile(r"\b(we admit|we acknowledge (liability|fault)|we are responsible for the|it is our fault|we take full responsibility for the)\b", re.IGNORECASE),
    re.compile(r"\b(we are (at )?fault|we messed up|we screwed up|it's our mistake|the mistake was ours)\b", re.IGNORECASE),
]

_PROMISE_PATTERNS = [
    re.compile(r"\b(we will (refund|replace|give you|send you|offer you a free)|you will receive|you are entitled to)\b", re.IGNORECASE),
    re.compile(r"\b(guaranteed?|we promise|you can expect|we ensure|we guarantee)\b", re.IGNORECASE),
]

_TOXIC_KEYWORDS = {
    "critical": [
        r"\b(fuck|shit|asshole|dickhead|motherfucker|bitch|cunt)\b",
        r"\b(kill|die|hate you|stupid|idiot|moron)\b",
    ],
    "high": [
        r"\b(screw you|piss off|get lost|shut up|go away)\b",
        r"\b(terrible|worst ever|horrible|disgusting|pathetic)\b",
    ],
    "moderate": [
        r"\b(lazy|incompetent|useless|worthless|ridiculous|absurd)\b",
        r"\b(scam|scammer|fraud|liar|cheat|con artist)\b",
    ],
}

_HALLUCINATION_CLAIMS = [
    re.compile(r"\bwe have been in business for \d+ years\b", re.IGNORECASE),
    re.compile(r"\bover \d+,?\d* (happy |satisfied )?customers\b", re.IGNORECASE),
    re.compile(r"\baward-winning\b", re.IGNORECASE),
    re.compile(r"\b#1 (rated|ranked|company|service|provider)\b", re.IGNORECASE),
    re.compile(r"\bbest (in|of|rated) (the )?(city|town|area|state|country|world)\b", re.IGNORECASE),
    re.compile(r"\bnumber one\b", re.IGNORECASE),
]

_TONE_WORDS_MAP: dict[str, list[str]] = {
    "luxury": ["exquisite", "pleasure", "honored", "discerning", "privilege", "sophisticated"],
    "friendly": ["great", "wonderful", "happy", "love", "awesome", "glad"],
    "professional": ["appreciate", "regard", "sincerely", "thank you", "please", "valued"],
    "playful": ["fun", "awesome", "cool", "excited", "love", "amazing"],
}

_FORBIDDEN_PROMOTION_PATTERNS = [
    re.compile(r"\b\d+%\s*off\b", re.IGNORECASE),
    re.compile(r"\bdiscount\s*(code|promo)?\s*:?\s*[A-Z0-9]{4,}\b", re.IGNORECASE),
    re.compile(r"\bfree\s+(trial|sample|gift|consultation|shipping)\b", re.IGNORECASE),
]


class SafetyGuardrailAgent:
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None) -> None:
        self.client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def check(
        self,
        reply_text: str,
        review_text: str,
        brand_context: str,
        knowledge_base_context: str = "",
    ) -> SafetyResult:
        violations: list[dict[str, Any]] = []
        violation_details: dict[str, Any] = {
            "pii": [],
            "prompt_injection": [],
            "brand_voice": [],
            "hallucination": [],
            "toxicity": [],
            "compliance": [],
        }
        score = 100.0
        reply_lower = reply_text.lower()

        def add_violation(
            code: str,
            severity: str,
            detail: str,
            penalty: float,
            category: str = "compliance",
        ) -> None:
            entry = {
                "code": code,
                "severity": severity,
                "detail": detail,
                "penalty": penalty,
            }
            violations.append(entry)
            if category in violation_details:
                violation_details[category].append(entry)
            nonlocal score
            score -= penalty * 100

        # --- PII checks ---
        if _EMAIL_PATTERN.search(reply_text):
            add_violation("contains_email", "high", "Email address detected in reply", 0.20, "pii")

        if _PHONE_PATTERN.search(reply_text):
            add_violation("contains_phone_number", "high", "Phone number detected in reply", 0.20, "pii")

        if _SSN_PATTERN.search(reply_text):
            add_violation("contains_ssn", "critical", "Social Security Number detected in reply", 0.40, "pii")

        if _CREDIT_CARD_PATTERN.search(reply_text):
            add_violation("contains_credit_card", "critical", "Credit card number detected in reply", 0.40, "pii")

        if _ADDRESS_PATTERN.search(reply_text):
            add_violation("contains_address", "medium", "Physical address pattern detected in reply", 0.15, "pii")

        if _ZIP_CODE_PATTERN.search(reply_text):
            add_violation("contains_zip_code", "low", "ZIP code detected in reply", 0.05, "pii")

        if _IP_ADDRESS_PATTERN.search(reply_text):
            add_violation("contains_ip_address", "medium", "IP address detected in reply", 0.10, "pii")

        if _DOB_PATTERN.search(reply_text):
            add_violation("contains_dob", "high", "Date of birth pattern detected in reply", 0.20, "pii")

        if _ACCOUNT_NUMBER_PATTERN.search(reply_text):
            add_violation("contains_account_number", "high", "Account number pattern detected in reply", 0.20, "pii")

        # --- Prompt injection checks ---
        if _PROMPT_INJECTION_BASIC.search(reply_text):
            add_violation("prompt_injection_basic", "critical", "Prompt injection pattern detected (basic)", 0.30, "prompt_injection")

        if _PROMPT_INJECTION_ADVANCED.search(reply_text):
            add_violation("prompt_injection_advanced", "critical", "Prompt injection pattern detected (advanced)", 0.30, "prompt_injection")

        # --- Brand voice checks ---
        if "forbidden_terms" in brand_context.lower() or "avoid:" in brand_context.lower():
            forbidden_match = re.search(
                r"avoid:\s*(.+?)(?:\n|$)", brand_context, re.IGNORECASE
            )
            if not forbidden_match:
                forbidden_match = re.search(
                    r"forbidden_terms:\s*(.+?)(?:\n|$)", brand_context, re.IGNORECASE
                )
            if forbidden_match:
                forbidden_terms = [
                    t.strip().lower().strip(".")
                    for t in forbidden_match.group(1).split(",")
                ]
                for term in forbidden_terms:
                    if term and term in reply_lower:
                        add_violation(
                            f"forbidden_term_used:{term}",
                            "medium",
                            f"Brand forbidden term used: '{term}'",
                            0.10,
                            "brand_voice",
                        )

        brand_tone_match = re.search(r"Tone:\s*(\w+)", brand_context, re.IGNORECASE)
        if brand_tone_match:
            expected_tone = brand_tone_match.group(1).lower()
            aggressive = re.search(r"\b(angry|furious|outraged|pissed|irate)\b", reply_lower)
            if aggressive and expected_tone in ("professional", "courteous", "friendly"):
                add_violation("tone_mismatch", "medium", f"Reply tone doesn't match brand tone '{expected_tone}'", 0.10, "brand_voice")

            # Brand voice tone word consistency check
            if expected_tone in _TONE_WORDS_MAP:
                expected_words = _TONE_WORDS_MAP[expected_tone]
                matches = sum(1 for w in expected_words if w in reply_lower)
                if matches == 0 and len(reply_text.split()) >= 10:
                    add_violation(
                        f"voice_word_mismatch:{expected_tone}",
                        "low",
                        f"Reply lacks expected tone words for '{expected_tone}' brand voice",
                        0.05,
                        "brand_voice",
                    )

        # --- Hallucination checks ---
        for pattern in _HALLUCINATION_CLAIMS:
            if pattern.search(reply_lower):
                add_violation(
                    "unsubstantiated_claim",
                    "high",
                    f"Unsubstantiated claim detected: '{pattern.pattern[:80]}'",
                    0.20,
                    "hallucination",
                )

        # Check unauthorized promotion offers
        for pattern in _FORBIDDEN_PROMOTION_PATTERNS:
            match = pattern.search(reply_text)
            if match:
                add_violation(
                    "unauthorized_promotion",
                    "high",
                    f"Unauthorized promotion/discount offer detected: '{match.group()[:60]}'",
                    0.20,
                    "hallucination",
                )

        explicit_liability = any(p.search(reply_lower) for p in _LIABILITY_PATTERNS)
        if explicit_liability:
            add_violation("liability_admission", "critical", "Liability admission detected in reply", 0.25, "compliance")

        specific_promises = any(p.search(reply_lower) for p in _PROMISE_PATTERNS)
        if specific_promises:
            add_violation("unauthorized_promise", "high", "Unauthorized promise or guarantee detected", 0.20, "compliance")

        # --- Knowledge base hallucination check: verify claims against KB ---
        if knowledge_base_context:
            kb_lower = knowledge_base_context.lower()
            claim_patterns = [
                (r"\bopen\s+\d+\s+(days|hours|am|pm)\b", "hours of operation claim"),
                (r"\b(price|cost|fee)\s+(of\s+)?\$?\d+", "pricing claim"),
                (r"\bwe\s+(offer|provide|have)\s+\w+\s+(service|product|feature)\b", "service offering claim"),
                (r"\b(phone|call|contact)\s*(:|at)?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b", "contact number claim"),
            ]
            for pattern_str, label in claim_patterns:
                matches = re.finditer(pattern_str, reply_lower, re.IGNORECASE)
                for match in matches:
                    claim = match.group()[:80]
                    if claim not in kb_lower:
                        add_violation(
                            "kb_hallucination",
                            "high",
                            f"Claim not found in knowledge base: '{label}': '{claim}'",
                            0.15,
                            "hallucination",
                        )

        # --- Toxicity keyword checks (fallback when moderation API fails/unavailable) ---
        for severity_level, patterns in _TOXIC_KEYWORDS.items():
            for pattern_str in patterns:
                match = re.search(pattern_str, reply_lower, re.IGNORECASE)
                if match:
                    penalty = {"critical": 0.30, "high": 0.20, "moderate": 0.10}[severity_level]
                    add_violation(
                        f"toxic_language:{severity_level}",
                        severity_level,
                        f"Toxic language detected ({severity_level} severity): '{match.group()[:40]}'",
                        penalty,
                        "toxicity",
                    )

        # --- Toxicity check via OpenAI moderation ---
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
                        add_violation(
                            f"toxic_content:{cat}",
                            "high",
                            f"Moderation API flagged: {cat}",
                            0.25,
                            "toxicity",
                        )
        except Exception as exc:
            logger.warning("Moderation API call failed (keyword fallback applied): %s", exc)

        score = max(0.0, round(score, 2))
        is_safe = score >= (settings.SAFETY_SCORE_THRESHOLD * 100)

        return SafetyResult(
            is_safe=is_safe,
            safety_score=score,
            violations=violations,
            violation_details=violation_details,
        )

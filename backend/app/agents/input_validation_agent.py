from __future__ import annotations

import re
from typing import NamedTuple, Optional


class ValidationResult(NamedTuple):
    is_valid: bool
    risk_flags: list[str]
    clean_text: Optional[str]


_HTML_TAG_PATTERN = re.compile(r"<[^>]*>")
_SCRIPT_PATTERN = re.compile(
    r"<script[^>]*>.*?</script>|<script.*?>.*?|javascript:\s*|onerror\s*=|onload\s*=",
    re.IGNORECASE | re.DOTALL,
)
_SQL_PATTERN = re.compile(
    r"(\bSELECT\b.*\bFROM\b|\bDROP\b.*\bTABLE\b|\bUNION\b.*\bSELECT\b|"
    r"\bINSERT\b.*\bINTO\b|\bDELETE\b.*\bFROM\b|\bUPDATE\b.*\bSET\b|"
    r"--\s|;\s*DROP\s|' OR '1'='1|' OR 1=1|\bALTER\b.*\bTABLE\b)",
    re.IGNORECASE,
)
_SPAM_PATTERN = re.compile(
    r"(buy now|click here|limited offer|act now|free money|"
    r"congratulations.you.ve won|subscribe now|follow me|"
    r"check out my|visit my website|earn money online)",
    re.IGNORECASE,
)
_EXCESSIVE_CAPS_PATTERN = re.compile(r"[A-Z]{5,}")


class InputValidationAgent:
    async def validate(self, review_data: dict) -> ValidationResult:
        text = review_data.get("content") or review_data.get("review_text", "")
        risk_flags: list[str] = []

        if not text or not text.strip():
            return ValidationResult(is_valid=False, risk_flags=["blank"], clean_text=None)

        stripped = text.strip()

        if len(stripped) < 3:
            return ValidationResult(
                is_valid=False, risk_flags=["too_short"], clean_text=None
            )

        if _SCRIPT_PATTERN.search(stripped):
            risk_flags.append("injection_attempt_xss")

        if _HTML_TAG_PATTERN.search(stripped):
            risk_flags.append("contains_html")

        if _SQL_PATTERN.search(stripped):
            risk_flags.append("injection_attempt_sql")

        if _SPAM_PATTERN.search(stripped):
            risk_flags.append("spam_pattern")

        caps_count = len(_EXCESSIVE_CAPS_PATTERN.findall(stripped))
        if caps_count > 3:
            risk_flags.append("excessive_capitalization")

        words = stripped.split()
        if len(words) > 200:
            risk_flags.append("excessive_length")

        char_repeat = re.search(r"(.)\1{10,}", stripped)
        if char_repeat:
            risk_flags.append("spam_repetitive_chars")

        cleaned = re.sub(r"\s+", " ", stripped).strip()

        is_valid = len(risk_flags) == 0 or all(
            flag in ("contains_html", "excessive_capitalization")
            for flag in risk_flags
        )

        return ValidationResult(
            is_valid=is_valid, risk_flags=risk_flags, clean_text=cleaned
        )

from __future__ import annotations

import re
import logging
from typing import NamedTuple, Optional

logger = logging.getLogger(__name__)


class Severity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationFlag(NamedTuple):
    flag: str
    severity: str
    details: str


class ValidationResult(NamedTuple):
    is_valid: bool
    risk_flags: list[str]
    clean_text: Optional[str]
    flags: list[ValidationFlag] = []
    severity: str = "low"


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

_URL_ONLY_PATTERN = re.compile(
    r"^(https?://|www\.)[^\s]+(\s+(https?://|www\.)[^\s]+)*\s*$",
    re.IGNORECASE,
)

_DUPLICATE_TEXT_PATTERN = re.compile(
    r"(.+?)\1{2,}",
    re.IGNORECASE,
)

_EXCESSIVE_EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    r"\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U00002702-\U000027B0"
    r"\U000024C2-\U0001F251]{3,}"
)

_SPAM_PUNCTUATION_PATTERN = re.compile(r"([!?.]){4,}")

_COPY_PASTE_PATTERN = re.compile(
    r"\b(great|amazing|awesome|wonderful|fantastic|excellent|love it|best ever)\b.{0,50}"
    r"\b(great|amazing|awesome|wonderful|fantastic|excellent|love it|best ever)\b",
    re.IGNORECASE,
)


class InputValidationAgent:
    async def validate(self, review_data: dict) -> ValidationResult:
        text = review_data.get("content") or review_data.get("review_text", "")
        risk_flags: list[str] = []
        flags: list[ValidationFlag] = []
        highest_severity = Severity.LOW

        if not text or not text.strip():
            return ValidationResult(
                is_valid=False, risk_flags=["blank"], clean_text=None,
                flags=[ValidationFlag("blank", Severity.CRITICAL, "Review content is empty")],
                severity=Severity.CRITICAL,
            )

        stripped = text.strip()
        words = stripped.split()
        word_count = len(words)

        if len(stripped) < 3:
            return ValidationResult(
                is_valid=False, risk_flags=["too_short"], clean_text=None,
                flags=[ValidationFlag("too_short", Severity.HIGH, "Review is too short to process")],
                severity=Severity.HIGH,
            )

        if _SCRIPT_PATTERN.search(stripped):
            risk_flags.append("injection_attempt_xss")
            flags.append(ValidationFlag("injection_attempt_xss", Severity.CRITICAL, "XSS script injection detected"))
            highest_severity = Severity.CRITICAL

        if _HTML_TAG_PATTERN.search(stripped):
            risk_flags.append("contains_html")
            flags.append(ValidationFlag("contains_html", Severity.MEDIUM, "HTML tags found in content"))

        if _SQL_PATTERN.search(stripped):
            risk_flags.append("injection_attempt_sql")
            flags.append(ValidationFlag("injection_attempt_sql", Severity.CRITICAL, "SQL injection pattern detected"))
            highest_severity = Severity.CRITICAL

        if _SPAM_PATTERN.search(stripped):
            risk_flags.append("spam_pattern")
            flags.append(ValidationFlag("spam_pattern", Severity.HIGH, "Spam keyword patterns found"))

        caps_count = len(_EXCESSIVE_CAPS_PATTERN.findall(stripped))
        if caps_count > 3:
            risk_flags.append("excessive_capitalization")
            flags.append(ValidationFlag("excessive_capitalization", Severity.LOW, f"Excessive capitalization ({caps_count} instances)"))

        if word_count > 200:
            risk_flags.append("excessive_length")
            flags.append(ValidationFlag("excessive_length", Severity.MEDIUM, f"Review too long ({word_count} words)"))

        char_repeat = re.search(r"(.)\1{10,}", stripped)
        if char_repeat:
            risk_flags.append("spam_repetitive_chars")
            flags.append(ValidationFlag("spam_repetitive_chars", Severity.MEDIUM, "Repetitive character spam detected"))

        if word_count < 3:
            risk_flags.append("minimum_word_count")
            flags.append(ValidationFlag("minimum_word_count", Severity.MEDIUM, f"Review too short ({word_count} words, minimum 3)"))

        if _URL_ONLY_PATTERN.match(stripped):
            risk_flags.append("url_only_review")
            flags.append(ValidationFlag("url_only_review", Severity.HIGH, "Review contains only URLs"))

        if _EXCESSIVE_EMOJI_PATTERN.search(stripped):
            risk_flags.append("excessive_emoji")
            flags.append(ValidationFlag("excessive_emoji", Severity.MEDIUM, "Excessive emoji usage in review"))

        if _SPAM_PUNCTUATION_PATTERN.search(stripped):
            risk_flags.append("spam_punctuation")
            flags.append(ValidationFlag("spam_punctuation", Severity.MEDIUM, "Excessive punctuation spam"))

        if _DUPLICATE_TEXT_PATTERN.search(stripped):
            risk_flags.append("duplicate_text_pattern")
            flags.append(ValidationFlag("duplicate_text_pattern", Severity.MEDIUM, "Repeated text pattern detected (possible spam)"))

        if _COPY_PASTE_PATTERN.search(stripped):
            risk_flags.append("copy_paste_spam")
            flags.append(ValidationFlag("copy_paste_spam", Severity.MEDIUM, "Generic copy-paste review pattern detected"))

        cleaned = re.sub(r"\s+", " ", stripped).strip()

        is_valid = len([f for f in flags if f.severity in (Severity.CRITICAL, Severity.HIGH)]) == 0

        if not highest_severity:
            highest_severity = Severity.LOW

        return ValidationResult(
            is_valid=is_valid,
            risk_flags=risk_flags,
            clean_text=cleaned,
            flags=flags,
            severity=highest_severity,
        )

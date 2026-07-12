from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business

logger = logging.getLogger(__name__)

DEFAULT_WORKFLOW_RULES: dict[str, dict[str, Any]] = {
    "low": {
        "auto_approve": True,
        "require_human": False,
        "quality_threshold": 0.7,
        "safety_threshold": 0.8,
        "description": "Low risk: auto-approve if quality and safety meet thresholds",
    },
    "medium": {
        "auto_approve": False,
        "require_human": True,
        "quality_threshold": 0.85,
        "safety_threshold": 0.9,
        "description": "Medium risk: requires human review before publishing",
    },
    "high": {
        "auto_approve": False,
        "require_human": True,
        "quality_threshold": 0.95,
        "safety_threshold": 0.95,
        "description": "High risk: mandatory human review, cannot auto-publish",
    },
}


class ApprovalWorkflowService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_rules(self, business_id: UUID) -> dict[str, Any]:
        result = await self.db.execute(
            select(Business).where(Business.id == business_id)
        )
        business = result.scalar_one_or_none()
        if not business:
            return DEFAULT_WORKFLOW_RULES

        stored = (business.settings or {}).get("workflow_rules")
        if stored:
            merged = dict(DEFAULT_WORKFLOW_RULES)
            merged.update(stored)
            return merged
        return dict(DEFAULT_WORKFLOW_RULES)

    async def update_rules(self, business_id: UUID, rules: dict[str, Any]) -> dict[str, Any]:
        result = await self.db.execute(
            select(Business).where(Business.id == business_id)
        )
        business = result.scalar_one_or_none()
        if not business:
            raise ValueError("Business not found")

        current = business.settings or {}
        current["workflow_rules"] = rules
        business.settings = current
        await self.db.flush()
        logger.info("Workflow rules updated for business %s", business_id)
        return rules

    async def decide(
        self,
        business_id: UUID,
        risk_level: str,
        quality_score: float,
        safety_score: float,
    ) -> dict[str, Any]:
        rules = await self.get_rules(business_id)
        risk_rules = rules.get(risk_level, rules.get("medium"))

        quality_threshold = risk_rules.get("quality_threshold", 0.7)
        safety_threshold = risk_rules.get("safety_threshold", 0.8)
        quality_normalized = quality_score / 100.0 if quality_score > 1 else quality_score

        needs_review = True
        auto_approve = False
        reasons: list[str] = []

        if risk_rules.get("require_human", True):
            needs_review = True
            reasons.append(f"{risk_level}_risk_requires_review")
        else:
            needs_review = False

        if (
            quality_normalized >= quality_threshold
            and safety_score >= safety_threshold
            and risk_rules.get("auto_approve", False)
        ):
            auto_approve = True
            reasons.append("meets_quality_and_safety_thresholds")
            needs_review = False
        elif risk_rules.get("auto_approve", False):
            reasons.append("quality_or_safety_below_threshold")

        if quality_normalized < 0.5 or safety_score < 0.5:
            needs_review = True
            auto_approve = False
            reasons.append("critically_low_score_forced_review")

        return {
            "auto_approve": auto_approve,
            "needs_review": needs_review,
            "reasons": reasons,
            "risk_rules_applied": risk_rules.get("description", ""),
        }

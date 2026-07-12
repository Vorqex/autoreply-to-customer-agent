from __future__ import annotations

import logging
from typing import Any, NamedTuple, Optional
from uuid import UUID, uuid4

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.reply import Reply
from app.models.review import Review
from app.models.business import Business
from app.models.brand_voice import BrandVoice
from app.models.usage import UsageMetric
from app.agents.input_validation_agent import InputValidationAgent
from app.agents.language_detection_agent import LanguageDetectionAgent
from app.agents.sentiment_agent import SentimentAnalysisAgent
from app.agents.risk_classification_agent import RiskClassificationAgent
from app.agents.knowledge_retrieval_agent import KnowledgeRetrievalAgent
from app.agents.reply_generation_agent import ReplyGenerationAgent
from app.agents.safety_guardrail_agent import SafetyGuardrailAgent
from app.agents.quality_evaluation_agent import QualityEvaluationAgent
from app.services.brand_service import BrandVoiceService
from app.services.knowledge_service import KnowledgeService
from app.services.audit_service import AuditService
from app.utils.helpers import calculate_cost, now

logger = logging.getLogger(__name__)


class OrchestrationResult(NamedTuple):
    reply: Reply
    all_scores: dict[str, Any]
    decisions: dict[str, Any]
    pipeline_log: list[dict[str, Any]]


class AIOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        self.input_validator = InputValidationAgent()
        self.language_detector = LanguageDetectionAgent()
        self.sentiment_analyzer = SentimentAnalysisAgent(self.openai_client)
        self.risk_classifier = RiskClassificationAgent()
        self.knowledge_service = KnowledgeService(db)
        self.brand_service = BrandVoiceService(db)
        self.knowledge_retriever = KnowledgeRetrievalAgent(self.knowledge_service)
        self.reply_generator = ReplyGenerationAgent(self.openai_client)
        self.safety_guardrail = SafetyGuardrailAgent(self.openai_client)
        self.quality_evaluator = QualityEvaluationAgent(self.openai_client)
        self.audit_service = AuditService(db)

    async def _load_entities(
        self, business_id: UUID, review_id: UUID
    ) -> tuple[Review, Business, BrandVoice]:
        review_result = await self.db.execute(
            select(Review).where(Review.id == review_id, Review.business_id == business_id)
        )
        review = review_result.scalar_one_or_none()
        if not review:
            raise ValueError(f"Review {review_id} not found")

        business_result = await self.db.execute(
            select(Business).where(Business.id == business_id)
        )
        business = business_result.scalar_one_or_none()
        if not business:
            raise ValueError(f"Business {business_id} not found")

        brand = await self.brand_service.get_brand_voice(business_id)

        return review, business, brand

    async def _log_usage(
        self, business_id: UUID, metric_type: str, model: str,
        prompt_tokens: int, completion_tokens: int, duration_ms: int,
    ) -> None:
        total_tokens = prompt_tokens + completion_tokens
        cost = calculate_cost(model, prompt_tokens, completion_tokens)

        usage = UsageMetric(
            id=uuid4(),
            business_id=business_id,
            metric_type=metric_type,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            duration_ms=duration_ms,
            metadata={"source": "orchestrator"},
        )
        self.db.add(usage)

    async def process_review(
        self,
        business_id: UUID,
        review_id: UUID,
        custom_instructions: Optional[str] = None,
    ) -> OrchestrationResult:
        pipeline_log: list[dict[str, Any]] = []
        start_time = now()

        review, business, brand = await self._load_entities(business_id, review_id)

        # Step 1: Input Validation
        step_start = now()
        validation = await self.input_validator.validate(
            {"content": review.content, "rating": review.rating}
        )
        review_text = validation.clean_text or review.content
        pipeline_log.append({
            "step": "input_validation",
            "result": {"is_valid": validation.is_valid, "risk_flags": validation.risk_flags},
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 2: Language Detection
        step_start = now()
        language_result = await self.language_detector.detect(review_text)
        review.language = language_result.language_code
        pipeline_log.append({
            "step": "language_detection",
            "result": {
                "language": language_result.language,
                "confidence": language_result.confidence,
                "code": language_result.language_code,
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 3: Sentiment Analysis
        step_start = now()
        sentiment_result = await self.sentiment_analyzer.analyze(review_text, review.rating)
        review.sentiment = sentiment_result.sentiment
        review.sentiment_score = sentiment_result.confidence
        pipeline_log.append({
            "step": "sentiment_analysis",
            "result": {
                "sentiment": sentiment_result.sentiment,
                "confidence": sentiment_result.confidence,
                "reasoning": sentiment_result.reasoning,
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 4: Risk Classification
        step_start = now()
        risk_result = await self.risk_classifier.classify(
            review_text=review_text,
            rating=review.rating,
            sentiment=sentiment_result.sentiment,
            platform=review.platform,
            business_industry=business.industry or "General",
        )
        review.risk_level = risk_result.risk_level
        pipeline_log.append({
            "step": "risk_classification",
            "result": {
                "risk_level": risk_result.risk_level,
                "needs_human_review": risk_result.needs_human_review,
                "risk_factors": risk_result.risk_factors,
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 5: Knowledge Retrieval
        step_start = now()
        knowledge_result = await self.knowledge_retriever.retrieve(
            business_id=business_id,
            review_text=review_text,
            rating=review.rating,
            sentiment=sentiment_result.sentiment,
        )
        pipeline_log.append({
            "step": "knowledge_retrieval",
            "result": {
                "docs_count": len(knowledge_result.relevant_docs),
                "brand_context_length": len(knowledge_result.brand_context),
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 6: Reply Generation
        step_start = now()
        gen_result = await self.reply_generator.generate(
            business_id=business_id,
            review=review,
            brand=brand,
            knowledge=knowledge_result.brand_context,
            custom_instructions=custom_instructions,
        )
        pipeline_log.append({
            "step": "reply_generation",
            "result": {
                "reply_length": len(gen_result.reply_text),
                "reasoning": gen_result.reasoning_summary,
                "usage": gen_result.raw_response.get("usage", {}),
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 7: Safety Guardrail
        step_start = now()
        safety_result = await self.safety_guardrail.check(
            reply_text=gen_result.reply_text,
            review_text=review_text,
            brand_context=knowledge_result.brand_context,
        )
        pipeline_log.append({
            "step": "safety_guardrail",
            "result": {
                "is_safe": safety_result.is_safe,
                "safety_score": safety_result.safety_score,
                "violations": safety_result.violations,
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Step 8: Quality Evaluation
        step_start = now()
        quality_result = await self.quality_evaluator.evaluate(
            reply=gen_result.reply_text,
            review=review,
            brand=brand,
            context=knowledge_result.brand_context,
        )
        pipeline_log.append({
            "step": "quality_evaluation",
            "result": {
                "overall_score": quality_result.overall_score,
                "breakdown": quality_result.breakdown,
                "passes_threshold": quality_result.passes_threshold,
            },
            "duration_ms": int((now() - step_start).total_seconds() * 1000),
        })

        # Decisions
        decisions: dict[str, Any] = {
            "route_to_human": False,
            "reasons": [],
            "auto_approve": False,
        }

        if risk_result.risk_level == "high":
            decisions["route_to_human"] = True
            decisions["reasons"].append("high_risk")

        if not safety_result.is_safe or safety_result.safety_score < settings.SAFETY_SCORE_THRESHOLD:
            decisions["route_to_human"] = True
            decisions["reasons"].append("low_safety_score")

        if not quality_result.passes_threshold:
            decisions["route_to_human"] = True
            decisions["reasons"].append("low_quality_score")

        if validation.risk_flags and any(
            f not in ("contains_html", "excessive_capitalization")
            for f in validation.risk_flags
        ):
            decisions["route_to_human"] = True
            decisions["reasons"].append("validation_failed")

        if not decisions["route_to_human"] and risk_result.risk_level == "low" and sentiment_result.sentiment in ("positive", "neutral"):
            decisions["auto_approve"] = True

        # Determine reply status
        if decisions["route_to_human"]:
            reply_status = "pending_approval"
        elif decisions["auto_approve"]:
            reply_status = "approved"
        else:
            reply_status = "pending_approval"

        # Create Reply record
        existing_reply_result = await self.db.execute(
            select(Reply).where(Reply.review_id == review_id)
        )
        existing_reply = existing_reply_result.scalar_one_or_none()

        if existing_reply:
            existing_reply.content = gen_result.reply_text
            existing_reply.status = reply_status
            existing_reply.quality_score = quality_result.overall_score / 100
            existing_reply.safety_score = safety_result.safety_score
            existing_reply.ai_metadata = {
                "pipeline_log": pipeline_log,
                "decisions": decisions,
                "sentiment": sentiment_result.sentiment,
                "sentiment_confidence": sentiment_result.confidence,
                "risk_level": risk_result.risk_level,
                "language": language_result.language_code,
                "safety_violations": safety_result.violations,
                "quality_breakdown": quality_result.breakdown,
                "generation_usage": gen_result.raw_response.get("usage"),
            }
            reply = existing_reply
        else:
            reply = Reply(
                id=uuid4(),
                business_id=business_id,
                review_id=review_id,
                content=gen_result.reply_text,
                status=reply_status,
                quality_score=quality_result.overall_score / 100,
                safety_score=safety_result.safety_score,
                ai_metadata={
                    "pipeline_log": pipeline_log,
                    "decisions": decisions,
                    "sentiment": sentiment_result.sentiment,
                    "sentiment_confidence": sentiment_result.confidence,
                    "risk_level": risk_result.risk_level,
                    "language": language_result.language_code,
                    "safety_violations": safety_result.violations,
                    "quality_breakdown": quality_result.breakdown,
                    "generation_usage": gen_result.raw_response.get("usage"),
                },
            )
            self.db.add(reply)

        review.is_processed = True

        # Log usage
        usage_info = gen_result.raw_response.get("usage", {})
        await self._log_usage(
            business_id=business_id,
            metric_type="ai_generation",
            model=gen_result.raw_response.get("model", settings.OPENAI_MODEL),
            prompt_tokens=usage_info.get("prompt_tokens", 0),
            completion_tokens=usage_info.get("completion_tokens", 0),
            duration_ms=int((now() - start_time).total_seconds() * 1000),
        )

        # Audit log
        await self.audit_service.log_ai_decision(
            business_id=business_id,
            review_id=review_id,
            action="process_review",
            details={
                "sentiment": sentiment_result.sentiment,
                "risk_level": risk_result.risk_level,
                "safety_score": safety_result.safety_score,
                "quality_score": quality_result.overall_score,
                "route_to_human": decisions["route_to_human"],
                "auto_approve": decisions["auto_approve"],
                "pipeline_steps": len(pipeline_log),
            },
        )

        await self.db.flush()

        all_scores = {
            "sentiment_confidence": sentiment_result.confidence,
            "safety_score": safety_result.safety_score,
            "quality_score": quality_result.overall_score,
            "quality_breakdown": quality_result.breakdown,
        }

        return OrchestrationResult(
            reply=reply,
            all_scores=all_scores,
            decisions=decisions,
            pipeline_log=pipeline_log,
        )

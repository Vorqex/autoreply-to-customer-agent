from __future__ import annotations

import logging
from typing import Any, NamedTuple
from uuid import UUID

from app.services.knowledge_service import KnowledgeService
from app.services.brand_service import BrandVoiceService

logger = logging.getLogger(__name__)

_RELEVANCE_THRESHOLD = 0.4
_MAX_DOCS = 5
_MIN_DOCS = 2


class KnowledgeResult(NamedTuple):
    relevant_docs: list[dict[str, Any]]
    brand_context: str
    business_info: dict[str, Any]


class KnowledgeRetrievalAgent:
    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service
        self.brand_service = BrandVoiceService(knowledge_service.db)

    async def retrieve(
        self,
        business_id: UUID,
        review_text: str,
        rating: int,
        sentiment: str,
    ) -> KnowledgeResult:
        is_negative_review = sentiment in ("negative", "very_negative")
        is_positive_review = sentiment in ("positive",)

        negative_keywords = ""
        positive_keywords = ""

        if is_negative_review:
            negative_keywords = ("refund policy complaint resolution return exchange "
                                 "apology customer service contact support compensation")
        if is_positive_review:
            positive_keywords = ("quality service experience product features "
                                 "benefits satisfaction recommendation")

        semantic_query = f"rating: {rating}/5, sentiment: {sentiment}. {review_text[:500]}"
        keyword_query = f"{review_text[:200]} {negative_keywords or positive_keywords}"

        semantic_docs = await self.knowledge_service.search(
            business_id=business_id,
            query=semantic_query,
            limit=_MAX_DOCS,
        )

        keyword_docs = []
        if not semantic_docs or len(semantic_docs) < _MIN_DOCS:
            keyword_docs = await self.knowledge_service.search(
                business_id=business_id,
                query=keyword_query,
                limit=_MAX_DOCS - len(semantic_docs),
            )

        seen_ids = {d["id"] for d in semantic_docs}
        combined_docs = list(semantic_docs)
        for doc in keyword_docs:
            if doc["id"] not in seen_ids:
                combined_docs.append(doc)
                seen_ids.add(doc["id"])

        filtered_docs = [
            d for d in combined_docs
            if d.get("similarity", 1.0) >= _RELEVANCE_THRESHOLD
        ]

        if is_negative_review:
            faq_policy_docs = [
                d for d in filtered_docs
                if d.get("category", "").lower() in ("faq", "policy", "support", "complaint")
            ]
            other_docs = [
                d for d in filtered_docs
                if d.get("category", "").lower() not in ("faq", "policy", "support", "complaint")
            ]
            sorted_docs = faq_policy_docs + other_docs
        elif is_positive_review:
            service_docs = [
                d for d in filtered_docs
                if d.get("category", "").lower() in ("service", "product", "feature", "about")
            ]
            other_docs = [
                d for d in filtered_docs
                if d.get("category", "").lower() not in ("service", "product", "feature", "about")
            ]
            sorted_docs = service_docs + other_docs
        else:
            sorted_docs = filtered_docs

        top_docs = sorted_docs[:_MAX_DOCS]

        brand_context = await self.brand_service.get_brand_context(business_id)

        brand_voice = await self.brand_service.get_brand_voice(business_id)
        business_info = {
            "tone": brand_voice.tone,
            "style": brand_voice.style,
            "language": brand_voice.language,
            "personality": brand_voice.personality or "Professional",
            "values": brand_voice.values or [],
            "keywords": brand_voice.keywords or [],
            "forbidden_terms": brand_voice.forbidden_terms or [],
            "custom_rules": brand_voice.custom_rules or [],
        }

        if brand_voice.greeting_template:
            business_info["greeting_template"] = brand_voice.greeting_template
        if brand_voice.closing_template:
            business_info["closing_template"] = brand_voice.closing_template

        if top_docs:
            context_parts = ["RELEVANT KNOWLEDGE BASE CONTEXT:"]
            for i, doc in enumerate(top_docs, 1):
                context_parts.append(f"\n--- Document {i} ---")
                context_parts.append(f"Title: {doc['title']}")
                context_parts.append(f"Category: {doc['category']}")
                context_parts.append(f"Content: {doc['content'][:600]}")
                if doc.get("similarity", 0) > 0:
                    context_parts.append(f"Relevance: {round(doc['similarity'] * 100)}%")
                if doc.get("metadata"):
                    context_parts.append(f"Tags: {doc['metadata']}")
            context_parts.append("\n---")
            formatted_context = "\n".join(context_parts)
        else:
            formatted_context = brand_context

        return KnowledgeResult(
            relevant_docs=top_docs,
            brand_context=formatted_context,
            business_info=business_info,
        )

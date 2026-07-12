from __future__ import annotations

from typing import Any, NamedTuple
from uuid import UUID

from app.services.knowledge_service import KnowledgeService
from app.services.brand_service import BrandVoiceService


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
        relevant_docs = await self.knowledge_service.search(
            business_id=business_id,
            query=f"rating: {rating}/5, sentiment: {sentiment}. {review_text[:500]}",
            limit=5,
        )

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

        return KnowledgeResult(
            relevant_docs=relevant_docs,
            brand_context=brand_context,
            business_info=business_info,
        )

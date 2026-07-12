from __future__ import annotations

import logging
import math
from typing import Any, Optional
from uuid import UUID, uuid4

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.knowledge_base import KnowledgeBaseEntry
from app.utils.helpers import now

logger = logging.getLogger(__name__)

_openai_client: Optional[AsyncOpenAI] = None


def _get_openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_embedding(self, text: str) -> list[float]:
        client = _get_openai()
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def add_entry(
        self,
        business_id: UUID,
        category: str,
        title: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> KnowledgeBaseEntry:
        embedding = await self._generate_embedding(f"{title}\n\n{content}")
        entry = KnowledgeBaseEntry(
            id=uuid4(),
            business_id=business_id,
            category=category,
            title=title,
            content=content,
            embedding=embedding,
            extra_metadata=metadata or {},
            is_active=True,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def search(
        self, business_id: UUID, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        query_embedding = await self._generate_embedding(query)

        result = await self.db.execute(
            select(KnowledgeBaseEntry).where(
                KnowledgeBaseEntry.business_id == business_id,
                KnowledgeBaseEntry.is_active == True,
            )
        )
        entries = result.scalars().all()

        scored = []
        for entry in entries:
            if not entry.embedding:
                continue
            sim = _cosine_similarity(query_embedding, entry.embedding)
            scored.append((sim, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]

        return [
            {
                "id": str(entry.id),
                "category": entry.category,
                "title": entry.title,
                "content": entry.content,
                "metadata": entry.metadata,
                "similarity": round(score, 4),
            }
            for score, entry in top
        ]

    async def get_entries(
        self, business_id: UUID, category: Optional[str] = None
    ) -> list[KnowledgeBaseEntry]:
        query = select(KnowledgeBaseEntry).where(
            KnowledgeBaseEntry.business_id == business_id,
            KnowledgeBaseEntry.is_active == True,
        )
        if category:
            query = query.where(KnowledgeBaseEntry.category == category)
        query = query.order_by(KnowledgeBaseEntry.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_entry(
        self, business_id: UUID, entry_id: UUID, data: dict[str, Any]
    ) -> Optional[KnowledgeBaseEntry]:
        result = await self.db.execute(
            select(KnowledgeBaseEntry).where(
                KnowledgeBaseEntry.business_id == business_id,
                KnowledgeBaseEntry.id == entry_id,
            )
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        for field in ("category", "title", "content", "metadata"):
            if field in data and data[field] is not None:
                setattr(entry, field, data[field])

        if "title" in data or "content" in data:
            new_title = data.get("title", entry.title)
            new_content = data.get("content", entry.content)
            entry.embedding = await self._generate_embedding(f"{new_title}\n\n{new_content}")

        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def delete_entry(self, business_id: UUID, entry_id: UUID) -> bool:
        result = await self.db.execute(
            select(KnowledgeBaseEntry).where(
                KnowledgeBaseEntry.business_id == business_id,
                KnowledgeBaseEntry.id == entry_id,
            )
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return False
        entry.is_active = False
        await self.db.flush()
        return True

    async def get_relevant_context(
        self,
        business_id: UUID,
        review_text: str,
        rating: int,
        sentiment: str,
    ) -> str:
        search_query = f"rating: {rating}/5, sentiment: {sentiment}. {review_text[:500]}"
        results = await self.search(business_id, search_query, limit=3)

        if not results:
            return ""

        parts = ["Relevant knowledge base context:"]
        for i, doc in enumerate(results, 1):
            parts.append(f"\n[{i}] {doc['title']}")
            parts.append(f"   Category: {doc['category']}")
            parts.append(f"   {doc['content'][:600]}")
            if doc.get("metadata") and any(k for k in ["faq", "policy", "product"] if k in str(doc.get("metadata"))):
                parts.append(f"   Related: {doc['metadata']}")

        return "\n".join(parts)

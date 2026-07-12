from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BrandVoiceResponse(BaseModel):
    id: UUID
    business_id: UUID
    company_name: str
    industry: Optional[str] = None
    business_description: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = None
    language: str = "en"
    reply_length: Optional[str] = None
    greeting_style: Optional[str] = None
    closing_style: Optional[str] = None
    emoji_preference: bool = False
    professional_level: int = Field(default=3, ge=1, le=5)
    personalization_level: int = Field(default=3, ge=1, le=5)
    custom_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrandVoiceUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = None
    business_description: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = None
    language: Optional[str] = None
    reply_length: Optional[str] = None
    greeting_style: Optional[str] = None
    closing_style: Optional[str] = None
    emoji_preference: Optional[bool] = None
    professional_level: Optional[int] = Field(None, ge=1, le=5)
    personalization_level: Optional[int] = Field(None, ge=1, le=5)
    custom_instructions: Optional[str] = None

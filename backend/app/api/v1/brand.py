from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_business, get_current_user, get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.brand import BrandVoiceUpdate
from app.schemas.common import SuccessResponse
from app.services.brand_service import BrandVoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/brand", tags=["Brand Voice"])


@router.get("/")
async def get_brand_voice(
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BrandVoiceService(db)
        brand_voice = await service.get_brand_voice(business_id=business.id)
        return brand_voice
    except Exception as exc:
        logger.exception("Failed to fetch brand voice")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch brand voice")


@router.patch("/")
async def update_brand_voice(
    body: BrandVoiceUpdate,
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BrandVoiceService(db)
        data = body.model_dump(exclude_none=True, exclude_unset=True)
        brand_voice = await service.update_brand_voice(business_id=business.id, data=data)
        return SuccessResponse(message="Brand voice updated", data={"id": str(brand_voice.id)})
    except Exception as exc:
        logger.exception("Failed to update brand voice")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update brand voice")


@router.post("/reset")
async def reset_brand_voice(
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BrandVoiceService(db)
        brand_voice = await service.reset_to_defaults(business_id=business.id)
        return SuccessResponse(message="Brand voice reset to defaults", data={"id": str(brand_voice.id)})
    except Exception as exc:
        logger.exception("Failed to reset brand voice")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset brand voice")

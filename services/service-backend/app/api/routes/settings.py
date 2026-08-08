from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core import get_db, SystemSettings, User
from ...core.security import get_current_active_admin
from ...schemas.settings import SettingsResponse, UpdateSettingsRequest

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Return defaults if not set up yet
        return SettingsResponse(
            company_name="My Company",
            company_website_url=None,
            logo_url=None,
            brand_color=None
        )
    
    return settings


@router.put("", response_model=SettingsResponse)
async def update_settings(
    request: UpdateSettingsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not initialized. Run setup-admin first."
        )
    
    # Update only provided fields
    if request.company_name is not None:
        settings.company_name = request.company_name
    if request.company_website_url is not None:
        settings.company_website_url = request.company_website_url
    if request.logo_url is not None:
        settings.logo_url = request.logo_url
    if request.brand_color is not None:
        settings.brand_color = request.brand_color
    
    await db.commit()
    await db.refresh(settings)
    
    return settings

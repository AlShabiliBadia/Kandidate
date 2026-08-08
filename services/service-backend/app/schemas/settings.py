from pydantic import BaseModel, HttpUrl
from typing import Optional


class SettingsResponse(BaseModel):
    company_name: str
    company_website_url: Optional[str]
    logo_url: Optional[str]
    brand_color: Optional[str]
    
    class Config:
        from_attributes = True


class UpdateSettingsRequest(BaseModel):
    company_name: Optional[str] = None
    company_website_url: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: Optional[str] = None

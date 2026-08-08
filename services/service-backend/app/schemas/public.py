from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class PublicJobListItem(BaseModel):
    id: str
    title: str
    department: Optional[str]
    job_type: str
    workplace_type: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublicJobDetail(BaseModel):
    id: str
    title: str
    description_html: str
    department: Optional[str]
    job_type: str
    workplace_type: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubmitApplicationRequest(BaseModel):
    # Personal Info
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    headline: Optional[str] = None
    
    # Links
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    # Tracking
    tracking_link_id: Optional[str] = None
    
    # Custom question answers
    answers: dict = {}  # question_id -> answer value


class ApplicationSubmittedResponse(BaseModel):
    application_id: str
    message: str
    email_sent: bool

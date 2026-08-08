from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobQuestionCreate(BaseModel):
    label: str
    type: str  # SHORT_TEXT, LONG_TEXT, YES_NO, SELECT, FILE
    is_required: bool = False
    options: Optional[List[str]] = None
    order_index: int = 0


class JobQuestionResponse(BaseModel):
    id: str
    label: str
    type: str
    is_required: bool
    options: Optional[List[str]]
    order_index: int
    
    class Config:
        from_attributes = True


class CreateJobRequest(BaseModel):
    pipeline_id: str
    title: str
    description: str
    requirements: Optional[str] = None
    department: Optional[str] = None
    employment_type: str  # full-time, part-time, contract, internship
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    status: Optional[str] = "draft"


class UpdateJobRequest(BaseModel):
    title: Optional[str] = None
    description_html: Optional[str] = None
    department: Optional[str] = None
    job_type: Optional[str] = None
    workplace_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = None


class UpdateJobStatusRequest(BaseModel):
    status: str  # DRAFT, PUBLISHED, CLOSED


class UpdateJobQuestionsRequest(BaseModel):
    questions: List[JobQuestionCreate]


class JobResponse(BaseModel):
    id: str
    pipeline_id: str
    title: str
    description_html: str
    department: Optional[str]
    job_type: str
    workplace_type: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: str
    status: str
    created_at: datetime
    questions: List[JobQuestionResponse] = []
    
    class Config:
        from_attributes = True


class CreateTrackingLinkRequest(BaseModel):
    source: str  # e.g., "LinkedIn", "Twitter", "Indeed"


class TrackingLinkResponse(BaseModel):
    id: str
    job_id: str
    source: str
    slug: str
    click_count: int
    
    class Config:
        from_attributes = True


class JobStatsResponse(BaseModel):
    job_id: str
    total_applications: int
    applications_by_stage: dict
    applications_by_source: dict

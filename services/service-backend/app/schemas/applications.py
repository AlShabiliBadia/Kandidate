from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApplicationListItem(BaseModel):
    id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    current_stage_id: str
    applied_at: datetime
    match_score: Optional[int] = None
    recommendation: Optional[str] = None
    
    class Config:
        from_attributes = True


class ApplicationDetail(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    current_stage_id: str
    tracking_link_id: Optional[str]
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    candidate_phone: Optional[str]
    candidate_headline: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    applied_at: datetime
    
    class Config:
        from_attributes = True


class MoveApplicationRequest(BaseModel):
    stage_id: str


class VoteApplicationRequest(BaseModel):
    vote_value: int  # +1 or -1


class CommentApplicationRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    author_id: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import List
from datetime import datetime


class PipelineStageCreate(BaseModel):
    name: str
    order_index: int


class PipelineStageResponse(BaseModel):
    id: str
    name: str
    order_index: int
    
    class Config:
        from_attributes = True


class CreatePipelineRequest(BaseModel):
    name: str
    is_default: bool = False
    stages: List[PipelineStageCreate]


class PipelineResponse(BaseModel):
    id: str
    name: str
    is_default: bool
    created_at: datetime
    stages: List[PipelineStageResponse]
    
    class Config:
        from_attributes = True

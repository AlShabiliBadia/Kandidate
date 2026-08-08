from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import secrets

from ...core import (
    get_db, Job, JobQuestion, JobTrackingLink, Application, 
    User, JobStatus, JobType, WorkplaceType, QuestionType
)
from ...core.security import get_current_user, get_current_active_admin
from ...schemas.jobs import (
    CreateJobRequest, UpdateJobRequest, UpdateJobStatusRequest,
    UpdateJobQuestionsRequest, JobResponse, CreateTrackingLinkRequest,
    TrackingLinkResponse, JobStatsResponse
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return jobs


@router.post("", response_model=JobResponse)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Map employment_type string to JobType enum
    employment_type_map = {
        "full-time": JobType.FULL_TIME,
        "part-time": JobType.PART_TIME,
        "contract": JobType.CONTRACT,
        "internship": JobType.INTERNSHIP
    }
    
    job_type = employment_type_map.get(request.employment_type.lower(), JobType.FULL_TIME)
    
    # Map status string to JobStatus enum
    status_map = {
        "draft": JobStatus.DRAFT,
        "published": JobStatus.PUBLISHED,
        "closed": JobStatus.CLOSED
    }
    
    job_status = status_map.get(request.status.lower(), JobStatus.DRAFT) if request.status else JobStatus.DRAFT
    
    job = Job(
        pipeline_id=request.pipeline_id,
        title=request.title,
        description_html=request.description,
        department=request.department,
        job_type=job_type,
        workplace_type=WorkplaceType.REMOTE,  # Default to remote for now
        location=request.location,
        salary_min=request.salary_min,
        salary_max=request.salary_max,
        currency=request.currency,
        status=job_status
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    request: UpdateJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update only provided fields
    if request.title is not None:
        job.title = request.title
    if request.description_html is not None:
        job.description_html = request.description_html
    if request.department is not None:
        job.department = request.department
    if request.job_type is not None:
        job.job_type = JobType[request.job_type]
    if request.workplace_type is not None:
        job.workplace_type = WorkplaceType[request.workplace_type]
    if request.location is not None:
        job.location = request.location
    if request.salary_min is not None:
        job.salary_min = request.salary_min
    if request.salary_max is not None:
        job.salary_max = request.salary_max
    if request.currency is not None:
        job.currency = request.currency
    
    await db.commit()
    await db.refresh(job)
    
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: str,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Map status string to JobStatus enum
    status_map = {
        "draft": JobStatus.DRAFT,
        "published": JobStatus.PUBLISHED,
        "closed": JobStatus.CLOSED
    }
    
    job_status = status_map.get(status.lower())
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status}"
        )
    
    job.status = job_status
    
    await db.commit()
    await db.refresh(job)
    
    return job


@router.put("/{job_id}/questions", response_model=JobResponse)
async def update_job_questions(
    job_id: str,
    questions: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Delete existing questions
    existing_questions = (await db.execute(
        select(JobQuestion).where(JobQuestion.job_id == job_id)
    )).scalars().all()
    
    for q in existing_questions:
        await db.delete(q)
    
    # Map frontend question types to backend QuestionType enum
    type_map = {
        "text": QuestionType.SHORT_TEXT,
        "textarea": QuestionType.LONG_TEXT,
        "select": QuestionType.SELECT,
        "multiselect": QuestionType.SELECT,  # Use SELECT for now
        "yes_no": QuestionType.YES_NO,
        "file": QuestionType.FILE
    }
    
    # Create new questions
    for idx, question_data in enumerate(questions):
        question_type_str = question_data.get("question_type", "text").lower()
        question_type = type_map.get(question_type_str, QuestionType.SHORT_TEXT)
        
        question = JobQuestion(
            job_id=job_id,
            label=question_data.get("question_text", ""),
            type=question_type,
            is_required=question_data.get("is_required", False),
            options=question_data.get("options"),
            order_index=idx
        )
        db.add(question)
    
    await db.commit()
    await db.refresh(job)
    
    return job


@router.post("/{job_id}/tracking-links", response_model=TrackingLinkResponse)
async def create_tracking_link(
    job_id: str,
    request: CreateTrackingLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Generate unique slug
    slug = f"{job_id[:8]}-{request.source.lower()}-{secrets.token_urlsafe(8)}"
    
    tracking_link = JobTrackingLink(
        job_id=job_id,
        created_by=current_user.id,
        source=request.source,
        slug=slug,
        click_count=0
    )
    
    db.add(tracking_link)
    await db.commit()
    await db.refresh(tracking_link)
    
    return tracking_link


@router.get("/{job_id}/stats", response_model=JobStatsResponse)
async def get_job_stats(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Total applications
    total_result = await db.execute(
        select(func.count(Application.id)).where(Application.job_id == job_id)
    )
    total_applications = total_result.scalar() or 0
    
    # TODO: Implement applications_by_stage and applications_by_source
    # This requires joining with PipelineStage and JobTrackingLink
    
    return JobStatsResponse(
        job_id=job_id,
        total_applications=total_applications,
        applications_by_stage={},
        applications_by_source={}
    )

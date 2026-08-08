from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pathlib import Path
from uuid import uuid4
import json

from ...core import (
    get_db, Job, JobQuestion, User, Pipeline, PipelineStage,
    Application, ApplicationAnswer, Attachment, JobStatus, UserRole
)
from ...schemas.public import (
    PublicJobListItem, PublicJobDetail, SubmitApplicationRequest,
    ApplicationSubmittedResponse
)

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/jobs")
async def get_public_jobs(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    workplace_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job)
    
    if status:
        query = query.where(Job.status == JobStatus[status.upper()])
    else:
        query = query.where(Job.status == JobStatus.PUBLISHED)
    
    if department:
        query = query.where(Job.department == department)
    if job_type:
        query = query.where(Job.job_type == job_type)
    if workplace_type:
        query = query.where(Job.workplace_type == workplace_type)
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if employment_type:
        query = query.where(Job.job_type == employment_type)
    if search:
        query = query.where(
            (Job.title.ilike(f"%{search}%")) | 
            (Job.department.ilike(f"%{search}%"))
        )
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    jobs_data = []
    for job in jobs:
        # Get application count
        count_result = await db.execute(
            select(func.count(Application.id)).where(Application.job_id == job.id)
        )
        application_count = count_result.scalar() or 0
        
        jobs_data.append({
            "id": str(job.id),
            "title": job.title,
            "department": job.department,
            "location": job.location,
            "description": job.description_html,
            "requirements": job.description_html,
            "employment_type": job.job_type.value if job.job_type else None,
            "status": job.status.value if job.status else "draft",
            "application_count": application_count,
            "created_at": job.created_at.isoformat() if job.created_at else None
        })
    
    return {"jobs": jobs_data}


@router.get("/jobs/{job_id}")
async def get_public_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get custom questions
    questions_result = await db.execute(
        select(JobQuestion).where(JobQuestion.job_id == job_id).order_by(JobQuestion.order_index)
    )
    questions = questions_result.scalars().all()
    
    custom_questions = []
    for q in questions:
        custom_questions.append({
            "question_text": q.label,
            "question_type": q.type.value.lower() if q.type else "text",
            "is_required": q.is_required,
            "options": q.options
        })
    
    return {
        "id": str(job.id),
        "title": job.title,
        "description": job.description_html,
        "requirements": job.description_html,
        "department": job.department,
        "location": job.location,
        "employment_type": job.job_type.value if job.job_type else None,
        "status": job.status.value if job.status else "draft",
        "custom_questions": custom_questions,
        "created_at": job.created_at.isoformat() if job.created_at else None
    }


@router.post("/jobs/{job_id}/apply", response_model=ApplicationSubmittedResponse)
async def apply_to_job(
    job_id: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    headline: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    tracking_link_id: Optional[str] = Form(None),
    answers: str = Form("{}"),
    resume: UploadFile = File(...),
    cover_letter: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    from services.shared import ApplicationFileParseMessage, QUEUE_APPLICATION_INTAKE, settings
    from ...clients.rabbitmq_client import get_rabbitmq_connection, declare_queues, publish_message as publish_rmq
    
    answers_dict = json.loads(answers)
    
    job_result = await db.execute(
        select(Job).where(Job.id == job_id, Job.status == JobStatus.PUBLISHED)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not published"
        )
    
    user_result = await db.execute(
        select(User).where(User.email == email)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.CANDIDATE,
            is_guest=True,
            password_hash=None
        )
        db.add(user)
        await db.flush()
    
    pipeline_result = await db.execute(
        select(PipelineStage)
        .where(PipelineStage.pipeline_id == job.pipeline_id)
        .order_by(PipelineStage.order_index)
    )
    first_stage = pipeline_result.scalars().first()
    
    if not first_stage:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job pipeline not configured properly"
        )
    
    application = Application(
        job_id=job_id,
        candidate_id=user.id,
        current_stage_id=first_stage.id,
        tracking_link_id=tracking_link_id,
        candidate_first_name=first_name,
        candidate_last_name=last_name,
        candidate_email=email,
        candidate_phone=phone,
        candidate_headline=headline,
        linkedin_url=linkedin_url,
        github_url=github_url,
        portfolio_url=portfolio_url
    )
    
    db.add(application)
    await db.flush()
    
    for question_id, answer_value in answers_dict.items():
        answer = ApplicationAnswer(
            application_id=application.id,
            question_id=question_id,
            text_value=str(answer_value) if answer_value is not None else None
        )
        db.add(answer)
    
    upload_dir = Path(settings.upload_volume_path)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    resume_path = None
    if resume:
        resume_filename = f"{uuid4()}_{resume.filename}"
        resume_path = str(upload_dir / resume_filename)
        with open(resume_path, "wb") as f:
            f.write(await resume.read())
        
        resume_attachment = Attachment(
            application_id=application.id,
            file_type="resume",
            file_name=resume.filename,
            file_url=resume_path
        )
        db.add(resume_attachment)
    
    cover_letter_path = None
    if cover_letter:
        cover_letter_filename = f"{uuid4()}_{cover_letter.filename}"
        cover_letter_path = str(upload_dir / cover_letter_filename)
        with open(cover_letter_path, "wb") as f:
            f.write(await cover_letter.read())
        
        cover_letter_attachment = Attachment(
            application_id=application.id,
            file_type="cover_letter",
            file_name=cover_letter.filename,
            file_url=cover_letter_path
        )
        db.add(cover_letter_attachment)
    
    await db.commit()
    await db.refresh(application)
    
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    declare_queues(channel, [QUEUE_APPLICATION_INTAKE])
    
    message = ApplicationFileParseMessage(
        job_id=job_id,
        application_id=str(application.id),
        resume_path=resume_path,
        cover_letter_path=cover_letter_path
    )
    
    publish_rmq(channel, QUEUE_APPLICATION_INTAKE, message)
    connection.close()
    
    return ApplicationSubmittedResponse(
        application_id=str(application.id),
        message="Application submitted successfully. You will receive an email confirmation shortly.",
        email_sent=False
    )

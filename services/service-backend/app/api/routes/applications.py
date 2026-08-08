from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ...core import (
    get_db, Application, ApplicationComment, ApplicationActivity,
    User, PipelineStage
)
from ...core.security import get_current_user
from ...schemas.applications import (
    ApplicationListItem, ApplicationDetail, MoveApplicationRequest,
    VoteApplicationRequest, CommentApplicationRequest, CommentResponse
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[ApplicationListItem])
async def get_applications(
    job_id: Optional[str] = Query(None),
    stage_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Application)
    
    if job_id:
        query = query.where(Application.job_id == job_id)
    if stage_id:
        query = query.where(Application.current_stage_id == stage_id)
    
    result = await db.execute(query.order_by(Application.applied_at.desc()))
    applications = result.scalars().all()
    
    return applications


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.patch("/{application_id}/stage", response_model=ApplicationDetail)
async def move_application(
    application_id: str,
    request: MoveApplicationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify stage exists
    stage_result = await db.execute(
        select(PipelineStage).where(PipelineStage.id == request.stage_id)
    )
    stage = stage_result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Update stage
    old_stage_id = application.current_stage_id
    application.current_stage_id = request.stage_id
    
    # Log activity
    activity = ApplicationActivity(
        application_id=application_id,
        actor_id=current_user.id,
        action_type="stage_changed",
        details={"from_stage": str(old_stage_id), "to_stage": str(request.stage_id)}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(application)
    
    return application


@router.post("/{application_id}/vote")
async def vote_application(
    application_id: str,
    request: VoteApplicationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    activity = ApplicationActivity(
        application_id=application_id,
        actor_id=current_user.id,
        action_type="voted",
        details={"vote": request.vote_value}
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Vote recorded", "vote_value": request.vote_value}


@router.post("/{application_id}/comment", response_model=CommentResponse)
async def comment_application(
    application_id: str,
    request: CommentApplicationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    comment = ApplicationComment(
        application_id=application_id,
        author_id=current_user.id,
        content=request.content
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment


@router.post("/{application_id}/re-analyze")
async def reanalyze_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from services.shared import ApplicationFileParseMessage, QUEUE_APPLICATION_INTAKE
    from ...clients.rabbitmq_client import get_rabbitmq_connection, declare_queues, publish_message
    
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.attachments))
        .where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    resume_path = None
    cover_letter_path = None
    
    for attachment in application.attachments:
        if attachment.file_type == "resume":
            resume_path = attachment.file_url
        elif attachment.file_type == "cover_letter":
            cover_letter_path = attachment.file_url
    
    if not resume_path and not cover_letter_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files found to analyze"
        )
    
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    declare_queues(channel, [QUEUE_APPLICATION_INTAKE])
    
    message = ApplicationFileParseMessage(
        job_id=str(application.job_id),
        application_id=application_id,
        resume_path=resume_path,
        cover_letter_path=cover_letter_path
    )
    
    publish_message(channel, QUEUE_APPLICATION_INTAKE, message)
    connection.close()
    
    activity = ApplicationActivity(
        application_id=application_id,
        actor_id=current_user.id,
        action_type="re_analyzed",
        details={}
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Re-analysis triggered", "application_id": application_id}

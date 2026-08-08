from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from ...core import get_db, Pipeline, PipelineStage, User
from ...core.security import get_current_active_admin
from ...schemas.pipelines import CreatePipelineRequest, PipelineResponse, PipelineStageResponse

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=List[PipelineResponse])
async def get_pipelines(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.stages))
    )
    pipelines = result.scalars().all()
    
    return [
        PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            is_default=pipeline.is_default,
            created_at=pipeline.created_at,
            stages=[
                PipelineStageResponse(
                    id=str(stage.id),
                    name=stage.name,
                    order_index=stage.order_index
                )
                for stage in sorted(pipeline.stages, key=lambda s: s.order_index)
            ]
        )
        for pipeline in pipelines
    ]


@router.post("", response_model=PipelineResponse)
async def create_pipeline(
    request: CreatePipelineRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # If this is set as default, unset all others
    if request.is_default:
        result = await db.execute(select(Pipeline).where(Pipeline.is_default == True))
        existing_defaults = result.scalars().all()
        for p in existing_defaults:
            p.is_default = False
    
    # Create pipeline
    pipeline = Pipeline(
        name=request.name,
        is_default=request.is_default
    )
    db.add(pipeline)
    await db.flush()  # Get the pipeline ID
    
    # Create stages
    for stage_data in request.stages:
        stage = PipelineStage(
            pipeline_id=pipeline.id,
            name=stage_data.name,
            order_index=stage_data.order_index
        )
        db.add(stage)
    
    await db.commit()
    await db.refresh(pipeline)
    
    # Load stages
    result = await db.execute(
        select(Pipeline)
        .options(selectinload(Pipeline.stages))
        .where(Pipeline.id == pipeline.id)
    )
    pipeline = result.scalar_one()
    
    return PipelineResponse(
        id=str(pipeline.id),
        name=pipeline.name,
        is_default=pipeline.is_default,
        created_at=pipeline.created_at,
        stages=[
            PipelineStageResponse(
                id=str(stage.id),
                name=stage.name,
                order_index=stage.order_index
            )
            for stage in sorted(pipeline.stages, key=lambda s: s.order_index)
        ]
    )

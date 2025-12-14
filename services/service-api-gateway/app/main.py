from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from typing import List, Annotated
from pydantic import StringConstraints
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .handlers import file_handler
from .clients import rabbitmq_client
from .database import mongo_operations
from services.shared_utils import setup_logging
from services.config import JD_MIN_LENGTH, JD_MAX_LENGTH
from .database import get_db, Base, engine
from .database.models import CVAnalysis
from .services.job_sync_service import sync_job_to_postgres, get_job_with_analyses

logger = setup_logging("api-gateway")

app = FastAPI(
    title="Kandidate API Gateway",
    description="API Gateway for CV analysis and job matching",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


@app.get("/")
async def health_check():
    return {
        "service": "api-gateway",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/jobs/submit", 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit CVs for Analysis",
    description="Upload CV files with job description for AI-powered matching"
)
async def submit_job(
    jd_text: Annotated[str, StringConstraints(min_length=JD_MIN_LENGTH, max_length=JD_MAX_LENGTH)] = Form(),
    use_delay: bool = Form(True),
    files: List[UploadFile] = File()
):

    logger.info(f"Received job submission with {len(files)} file(s)")
    
    if not files:
        logger.warning("No files provided")
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    file_result = file_handler.process_files(files)
    
    if not file_result.saved_files:
        raise HTTPException(status_code=400, detail=file_result.error_detail)
    
    try:
        await mongo_operations.create_job(
            file_result.job_id,
            file_result.correlation_id,
            jd_text,
            len(file_result.saved_files)
        )
    except HTTPException:
        file_handler.cleanup_job_directory(file_result.job_dir)
        raise
    
    try:
        await rabbitmq_client.publish_job(
            file_result.job_id,
            file_result.correlation_id,
            jd_text,
            use_delay,
            file_result.saved_files
        )
    except HTTPException:
        file_handler.cleanup_job_directory(file_result.job_dir)
        try:
            await mongo_operations.delete_job(file_result.job_id)
            logger.info(f"Cleaned up job {file_result.job_id} from MongoDB after queue publish failure")
        except Exception as delete_error:
            logger.warning(f"Failed to delete job {file_result.job_id} from MongoDB during cleanup: {delete_error}")
        raise
    
    logger.info(
        f"Job {file_result.job_id} submitted successfully with "
        f"{len(file_result.saved_files)} valid file(s)"
    )
    if file_result.skipped_files:
        logger.warning(
            f"Job {file_result.job_id}: {len(file_result.skipped_files)} file(s) skipped"
        )
    
    return file_result.to_response()


@app.get("/jobs/{job_id}/status",
    summary="Get Job Status",
    description="Retrieve the current status and results of a submitted job"
)
async def get_job_status(job_id: str):
    job = await mongo_operations.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/jobs/{job_id}/add-cvs",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Add More CVs to Existing Job",
    description="Upload additional CV files to a job. If job doesn't exist in MongoDB, it will be recreated."
)
async def add_cvs_to_job(
    job_id: str,
    jd_text: Annotated[str, StringConstraints(min_length=JD_MIN_LENGTH, max_length=JD_MAX_LENGTH)] = Form(),
    use_delay: bool = Form(True),
    files: List[UploadFile] = File(),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Received request to add {len(files)} CV(s) to job {job_id}")
    
    if not files:
        logger.warning("No files provided")
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    existing_cv_count = 0
    correlation_id = None
    job_exists_in_mongo = False
    
    try:
        mongo_job = await mongo_operations.get_job(job_id)
        job_exists_in_mongo = True
        correlation_id = mongo_job.get("correlation_id")
        existing_cv_count = len(mongo_job.get("results", []))
        logger.info(f"Job {job_id} exists in MongoDB with {existing_cv_count} CVs")
    except HTTPException as e:
        if e.status_code == 404:
            logger.info(f"Job {job_id} not in MongoDB, will create/resume it")
            
            # Check PostgreSQL to get existing CV count for proper indexing
            postgres_job = await get_job_with_analyses(job_id, db)
            if postgres_job:
                existing_cv_count = len(postgres_job.get("analyses", []))
                correlation_id = postgres_job.get("correlation_id")
                logger.info(f"Found job {job_id} in PostgreSQL with {existing_cv_count} CVs")
        else:
            raise
    
    # Process new files
    file_result = file_handler.process_files(
        files, 
        existing_job_id=job_id,
        correlation_id=correlation_id,
        existing_cv_count=existing_cv_count
    )
    
    if not file_result.saved_files:
        raise HTTPException(status_code=400, detail=file_result.error_detail)
    
    # Publish to RabbitMQ FIRST
    try:
        await rabbitmq_client.publish_job(
            job_id,
            file_result.correlation_id,
            jd_text,
            use_delay,
            file_result.saved_files
        )
    except HTTPException:
        file_handler.cleanup_files(file_result.saved_files, file_result.job_dir)
        raise
    
    # Update or create job in MongoDB AFTER successful RabbitMQ publish
    try:
        if job_exists_in_mongo:
            # Update existing job
            await mongo_operations.add_files_to_job(job_id, len(file_result.saved_files))
            await mongo_operations.update_job_status(job_id, "pending")
            logger.info(f"Updated existing job {job_id} in MongoDB")
        else:
            # Create new job (resume)
            await mongo_operations.create_job(
                job_id,
                file_result.correlation_id,
                jd_text,
                len(file_result.saved_files)
            )
            logger.info(f"Created/resumed job {job_id} in MongoDB")
    except HTTPException:
        logger.error(f"Failed to update MongoDB after RabbitMQ publish for job {job_id}")
        raise
    
    logger.info(f"Added {len(file_result.saved_files)} CV(s) to job {job_id}")
    
    return {
        "job_id": job_id,
        "correlation_id": file_result.correlation_id,
        "status": "pending",
        "files_added": len(file_result.saved_files),
        "resumed": not job_exists_in_mongo,  # Flag to show if job was resumed
        "cv_details": [
            {
                "cv_id": file["cv_id"],
                "original_filename": file["original_filename"]
            }
            for file in file_result.saved_files
        ],
        "warnings": {
            "skipped_files": [f.get("filename") for f in file_result.skipped_files],
            "skipped_count": len(file_result.skipped_files),
        } if file_result.skipped_files else None
    }


@app.post("/jobs/{job_id}/sync",
    summary="Sync Job to PostgreSQL",
    description="Move completed job from MongoDB to PostgreSQL (only successful CVs)"
)
async def sync_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):

    logger.info(f"Received sync request for job {job_id}")
    
    mongo_job = await mongo_operations.get_job(job_id)

    correlation_id = mongo_job.get("correlation_id", "unknown")
    
    # Move data from MongoDB to PostgreSQL. 
    # Then delete the data from MongoDB.
    success = await sync_job_to_postgres(job_id, correlation_id, db)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync job {job_id} to PostgreSQL"
        )
    
    # Get Job full data for return.
    job_data = await get_job_with_analyses(job_id, db)
    
    return {
        "message": "Job synced successfully",
        "job": job_data
    }


@app.get("/jobs/{job_id}/results",
    summary="Get Job Results from PostgreSQL",
    description="Retrieve job results from PostgreSQL (only successful analyses)"
)
async def get_job_results(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    job_data = await get_job_with_analyses(job_id, db)
    
    if not job_data:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found in PostgreSQL. Try syncing first with POST /jobs/{job_id}/sync"
        )
    
    return job_data


@app.delete("/jobs/{job_id}/candidates/{cv_id}",
    summary="Delete Candidate Data (GDPR)",
    description="Delete a specific candidate's CV analysis from PostgreSQL. For privacy compliance."
)
async def delete_candidate(
    job_id: str,
    cv_id: str,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Received request to delete candidate {cv_id} from job {job_id}")
    
    # Delete from PostgreSQL
    result = await db.execute(
        select(CVAnalysis).where(
            CVAnalysis.job_id == job_id,
            CVAnalysis.cv_id == cv_id
        )
    )
    cv_analysis = result.scalar_one_or_none()
    
    if not cv_analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate {cv_id} not found in job {job_id}"
        )
    
    await db.delete(cv_analysis)
    await db.commit()
    
    logger.info(f"Deleted candidate {cv_id} from job {job_id}")
    
    return {
        "message": f"Candidate {cv_id} deleted successfully",
        "candidate_name": cv_analysis.candidate_name,
        "note": "Data permanently deleted for privacy compliance"
    }


import os
from typing import Optional
from pathlib import Path
import shutil
from datetime import datetime
import pymongo
import logging

from services.shared_models import AnalysisResult
from .mongodb import async_job_collection, sync_job_collection

logger = logging.getLogger("mongo-operations")


async def create_job(job_id: str, correlation_id: str, jd_text: str, file_count: int) -> dict:
    job_doc = {
        "_id": job_id,
        "correlation_id": correlation_id,
        "jd_text": jd_text,
        "status": "pending",
        "expected_files": file_count,
        "results": [],
        "errors": [],
        "created_at": datetime.utcnow().isoformat()
    }
    await async_job_collection.insert_one(job_doc)
    logger.info(f"[{correlation_id}] Created job {job_id} with {file_count} expected files")
    return job_doc


async def get_job(job_id: str) -> Optional[dict]:
    return await async_job_collection.find_one({"_id": job_id})


async def add_files_to_job(job_id: str, file_count: int) -> bool:
    result = await async_job_collection.update_one(
        {"_id": job_id},
        {"$inc": {"expected_files": file_count}}
    )
    
    if result.modified_count > 0:
        logger.info(f"Added {file_count} to expected_files for job {job_id}")
        return True
    else:
        logger.warning(f"Job {job_id} not found when trying to add files")
        return False


async def delete_job(job_id: str) -> bool:
    result = await async_job_collection.delete_one({"_id": job_id})
    
    if result.deleted_count > 0:
        logger.info(f"Deleted job {job_id} from MongoDB")
        return True
    else:
        logger.warning(f"Job {job_id} not found for deletion")
        return False


async def update_job_status(job_id: str, status: str) -> bool:
    result = await async_job_collection.update_one(
        {"_id": job_id},
        {"$set": {"status": status}}
    )
    
    if result.modified_count > 0:
        logger.info(f"Updated job {job_id} status to '{status}'")
        return True
    else:
        logger.warning(f"Job {job_id} not found when trying to update status")
        return False


def add_result_to_job_sync(
    job_id: str,
    cv_id: str,
    filename: str,
    status: str,
    data: Optional[AnalysisResult],
    error: Optional[str]
) -> None:
    if status == "success":
        updated_job = sync_job_collection.find_one_and_update(
            {"_id": job_id},
            {"$push": {"results": data.model_dump()}},
            return_document=pymongo.ReturnDocument.AFTER
        )
    elif status == "error":
        updated_job = sync_job_collection.find_one_and_update(
            {"_id": job_id},
            {"$push": {"errors": {"cv_id": cv_id, "filename": filename, "error": error}}},
            return_document=pymongo.ReturnDocument.AFTER
        )
    else:
        return
    
    if not updated_job:
        logger.warning(f"Job {job_id} not found when adding result")
        return
    
    result_count = len(updated_job.get("results", []))
    error_count = len(updated_job.get("errors", []))
    total_count = result_count + error_count
    expected_files = updated_job.get("expected_files", 0)
    
    if total_count >= expected_files:
        result = sync_job_collection.update_one(
            {"_id": job_id, "status": "pending"},
            {"$set": {"status": "complete"}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Job {job_id} completed: {result_count} results, {error_count} errors")
            cleanup_job_files(job_id)


def cleanup_job_files(job_id: str) -> None:
    try:
        upload_path = os.environ.get('UPLOAD_VOLUME_PATH', '/uploads')
        job_dir = Path(upload_path) / job_id
        
        if job_dir.exists() and job_dir.is_dir():
            shutil.rmtree(job_dir)
            logger.info(f"Cleaned up files for job {job_id}")
        else:
            logger.debug(f"No files to cleanup for job {job_id}")
    except Exception as e:
        logger.error(f"Failed to cleanup files for job {job_id}: {e}", exc_info=True)

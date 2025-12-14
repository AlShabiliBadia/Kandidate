from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import Job, CVAnalysis
from ..database import mongo_operations
from services.shared_utils import setup_logging

logger = setup_logging("job-sync-service")


async def sync_job_to_postgres(job_id: str, correlation_id: str, db: AsyncSession) -> bool:
    try:
        logger.info(f"[{correlation_id}] Starting sync for job {job_id}")
        
        mongo_job = await mongo_operations.get_job(job_id)
        
        if not mongo_job:
            logger.warning(f"[{correlation_id}] Job {job_id} not found in MongoDB")
            return False
        
        if mongo_job.get("status") != "complete":
            logger.warning(f"[{correlation_id}] Job {job_id} not complete (status: {mongo_job.get('status')})")
            return False
        
        result = await db.execute(select(Job).where(Job.id == job_id))
        existing_job = result.scalar_one_or_none()
        
        results = mongo_job.get("results", [])
        errors = mongo_job.get("errors", [])
        
        successful_results = results
        failed_count = len(errors)
        
        if existing_job: 
            logger.info(
                f"[{correlation_id}] Job {job_id} already exists in PostgreSQL, "
                f"adding {len(successful_results)} new CVs"
            )
            
            existing_cvs_result = await db.execute(
                select(CVAnalysis.cv_id).where(CVAnalysis.job_id == job_id)
            )
            existing_cv_ids = set(row[0] for row in existing_cvs_result.fetchall())
            
            new_cvs = [r for r in successful_results if r.get("cv_id") not in existing_cv_ids]
            
            if new_cvs:
                logger.info(f"[{correlation_id}] Adding {len(new_cvs)} new CVs to existing job")
                
                for result in new_cvs:
                    cv_analysis = CVAnalysis(
                        job_id=job_id,
                        cv_id=result.get("cv_id", "unknown"),
                        original_filename=result.get("original_filename", "unknown.pdf"),
                        candidate_name=result.get("candidate_name") or "Unknown Candidate",
                        match_score=result.get("match_score", 0),
                        summary_headline=result.get("summary_headline", ""),
                        conceptual_matches=result.get("conceptual_matches", []),
                        skill_gaps=result.get("skill_gaps", []),
                        experience_analysis=result.get("experience_analysis", ""),
                        recommendation=result.get("recommendation", "Review Needed"),
                        risk_assessment=result.get("risk_assessment", "Medium"),
                        email=result.get("email"),
                        phone=result.get("phone"),
                        linkedin_url=result.get("linkedin_url"),
                        github_url=result.get("github_url"),
                        portfolio_url=result.get("portfolio_url"),
                        analyzed_at=datetime.utcnow()
                    )
                    db.add(cv_analysis)
                
                existing_job.total_cvs += len(new_cvs)
                existing_job.successful_cvs += len(new_cvs)
                existing_job.completed_at = datetime.utcnow()
                
                await db.commit()
                logger.info(f"[{correlation_id}] Updated job {job_id} with {len(new_cvs)} new CVs")
            else:
                logger.info(f"[{correlation_id}] No new CVs to add, all already synced")
        
        else:
            logger.info(
                f"[{correlation_id}] Creating new job {job_id} in PostgreSQL: "
                f"{len(successful_results)} successful, {failed_count} failed (discarding failed)"
            )
            
            job = Job(
                id=job_id,
                jd_text=mongo_job.get("jd_text", ""),
                status="completed",
                total_cvs=mongo_job.get("expected_files", len(results)),
                successful_cvs=len(successful_results),
                failed_cvs=failed_count,
                created_at=datetime.fromisoformat(mongo_job["created_at"]) if "created_at" in mongo_job else datetime.utcnow(),
                completed_at=datetime.utcnow(),
                correlation_id=correlation_id
            )
            
            db.add(job)
            
            for result in successful_results:
                cv_analysis = CVAnalysis(
                    job_id=job_id,
                    cv_id=result.get("cv_id", "unknown"),
                    original_filename=result.get("original_filename", "unknown.pdf"),
                    candidate_name=result.get("candidate_name") or "Unknown Candidate",
                    match_score=result.get("match_score", 0),
                    summary_headline=result.get("summary_headline", ""),
                    conceptual_matches=result.get("conceptual_matches", []),
                    skill_gaps=result.get("skill_gaps", []),
                    experience_analysis=result.get("experience_analysis", ""),
                    recommendation=result.get("recommendation", "Review Needed"),
                    risk_assessment=result.get("risk_assessment", "Medium"),
                    email=result.get("email"),
                    phone=result.get("phone"),
                    linkedin_url=result.get("linkedin_url"),
                    github_url=result.get("github_url"),
                    portfolio_url=result.get("portfolio_url"),
                    analyzed_at=datetime.utcnow()
                )
                
                db.add(cv_analysis)
            
            await db.commit()
            
            logger.info(
                f"[{correlation_id}] Successfully synced job {job_id} to PostgreSQL "
                f"({len(successful_results)} CVs)"
            )
        
        try:
            await mongo_operations.delete_job(job_id)
            logger.info(f"[{correlation_id}] Deleted job {job_id} from MongoDB")
        except Exception as delete_error:
            logger.warning(
                f"[{correlation_id}] PostgreSQL sync successful but MongoDB deletion failed: {delete_error}"
            )
        
        return True
        
    except Exception as e:
        logger.error(f"[{correlation_id}] Failed to sync job {job_id}: {e}", exc_info=True)
        await db.rollback()
        return False


async def get_job_with_analyses(job_id: str, db: AsyncSession) -> Optional[dict]:
    try:
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        analyses_result = await db.execute(
            select(CVAnalysis)
            .where(CVAnalysis.job_id == job_id)
            .order_by(CVAnalysis.match_score.desc())
        )
        analyses = analyses_result.scalars().all()
        
        return {
            "job_id": job.id,
            "jd_text": job.jd_text,
            "status": job.status,
            "total_cvs": job.total_cvs,
            "successful_cvs": job.successful_cvs,
            "failed_cvs": job.failed_cvs,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "correlation_id": job.correlation_id,
            "analyses": [
                {
                    "cv_id": analysis.cv_id,
                    "original_filename": analysis.original_filename,
                    "candidate_name": analysis.candidate_name,
                    "match_score": analysis.match_score,
                    "summary_headline": analysis.summary_headline,
                    "conceptual_matches": analysis.conceptual_matches,
                    "skill_gaps": analysis.skill_gaps,
                    "experience_analysis": analysis.experience_analysis,
                    "recommendation": analysis.recommendation,
                    "risk_assessment": analysis.risk_assessment,
                    "analyzed_at": analysis.analyzed_at.isoformat()
                }
                for analysis in analyses
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get job {job_id} from PostgreSQL: {e}", exc_info=True)
        return None

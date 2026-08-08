from typing import List
from fastapi import HTTPException
from services.shared import (
    JobIntakeMessage,
    get_rabbitmq_connection,
    declare_queues,
    publish_message,
    setup_logging,
    QUEUE_APPLICATION_INTAKE
)

logger = setup_logging("rabbitmq-client")


async def publish_job(
    job_id: str,
    correlation_id: str,
    jd_text: str,
    use_delay: bool,
    file_paths: List[dict]
):
    logger.info(f"[{correlation_id}] Publishing job {job_id} to RabbitMQ")
    
    connection = None
    try:
        connection = get_rabbitmq_connection(logger=logger)
        channel = connection.channel()
        declare_queues(channel, [QUEUE_JOB_INTAKE], logger=logger)
        
        message = JobIntakeMessage(
            job_id=job_id,
            correlation_id=correlation_id,
            jd_text=jd_text,
            use_delay=use_delay,
            file_paths=file_paths,
            expected_file_count=len(file_paths)
        )
        
        publish_message(channel, QUEUE_JOB_INTAKE, message, logger=logger)
        
        logger.info(f"[{correlation_id}] Job {job_id} published to RabbitMQ")
        
    except Exception as e:
        logger.error(f"[{correlation_id}] Failed to publish to RabbitMQ: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"RabbitMQ is unreachable: {e}"
        )
    finally:
        if connection and connection.is_open:
            connection.close()
            logger.debug(f"[{correlation_id}] RabbitMQ connection closed")

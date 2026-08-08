from pika.channel import Channel

from services.shared import (
    JobResultMessage,
    publish_message,
    setup_logging,
    QUEUE_RESULTS_STORAGE
)

logger = setup_logging("file-parser-utils")


def publish_error_result(
    channel: Channel,
    job_id: str,
    correlation_id: str,
    cv_id: str,
    filename: str,
    error_message: str
) -> None:
    try:
        result_message = JobResultMessage(
            job_id=job_id,
            correlation_id=correlation_id,
            cv_id=cv_id,
            original_filename=filename,
            status="error",
            data=None,
            error=error_message
        )
        publish_message(channel, QUEUE_RESULTS_STORAGE, result_message, logger=logger)
        logger.warning(
            f"[{correlation_id}] Published error for {filename} (cv_id: {cv_id}) "
            f"in job {job_id}: {error_message[:100]}"
        )
    except Exception as e:
        logger.error(f"[{correlation_id}] Failed to publish error result: {e}", exc_info=True)

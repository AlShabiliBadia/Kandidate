from pydantic import ValidationError as PydanticValidationError
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from services.shared import (
    JobResultMessage,
    get_rabbitmq_connection,
    declare_queues,
    setup_logging,
    QUEUE_RESULTS_STORAGE
)
from ..database.mongo_operations import add_result_to_job_sync

logger = setup_logging("results-consumer")


def start_results_consumer():
    logger.info("RESULTS CONSUMER STARTING")
    
    connection = None
    try:
        connection = get_rabbitmq_connection(logger=logger)
        channel = connection.channel()
        
        declare_queues(channel, [QUEUE_RESULTS_STORAGE], logger=logger)
        
        channel.basic_qos(prefetch_count=1)
        
        def callback(
            ch: Channel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
        ) -> None:
            try:
                logger.info("Received result storage message")
                logger.debug(f"Message preview: {body[:150]}...")
                
                message = JobResultMessage.model_validate_json(body)
                logger.info(
                    f"[{message.correlation_id}] Validated result for job {message.job_id}, "
                    f"file: {message.original_filename}, status: {message.status}"
                )
                
                add_result_to_job_sync(
                    message.job_id,
                    message.cv_id,
                    message.original_filename,
                    message.status,
                    message.data,
                    message.error
                )
                
                logger.info(f"[{message.correlation_id}] Saved result to MongoDB for job {message.job_id}")
                
            except PydanticValidationError as e:
                logger.error(f"Message validation failed: {e}")
                logger.debug(f"Invalid message body: {body.decode('utf-8', errors='replace')}")
                
            except Exception as e:
                logger.error(f"Failed to store result: {e}", exc_info=True)
                
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug("Message acknowledged")
        
        channel.basic_consume(
            queue=QUEUE_RESULTS_STORAGE,
            on_message_callback=callback
        )
        
        logger.info(f"Listening for messages on '{QUEUE_RESULTS_STORAGE}'")
        logger.info("Results Consumer is ready")
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        if 'channel' in locals():
            channel.stop_consuming()
    except Exception as e:
        logger.critical(f"Fatal error in consumer: {e}", exc_info=True)
        raise
    finally:
        if connection and connection.is_open:
            connection.close()
            logger.info("RabbitMQ connection closed")


if __name__ == '__main__':
    start_results_consumer()

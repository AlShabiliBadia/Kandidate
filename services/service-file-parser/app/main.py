from services.shared import (
    get_rabbitmq_connection,
    declare_queues,
    setup_logging,
    QUEUE_APPLICATION_INTAKE,
    QUEUE_AI_ANALYSIS,
    QUEUE_RESULTS_STORAGE
)
from .processors import FileProcessor
from .handlers import MessageHandler

logger = setup_logging("file-parser")


def main_worker():
    logger.info("FILE PARSER SERVICE STARTING")
    
    connection = None
    try:
        # Connect to RabbitMQ
        connection = get_rabbitmq_connection(logger=logger)
        channel = connection.channel()
        
        # We declare ALL downstream queues here 
        # to ensure they exist before we try to publish to them. 
        # This prevents 404 errors if this service starts before the AI service.
        declare_queues(
            channel,
            [QUEUE_APPLICATION_INTAKE, QUEUE_AI_ANALYSIS, QUEUE_RESULTS_STORAGE],
            logger=logger
        )
        
        # Some PDFs take 10s to parse, others take 0.1s.
        # prefetch_count=1 ensures a worker never hoards messages it can't process immediately,
        # keeping the load balanced across all parser instances.
        channel.basic_qos(prefetch_count=1)
        
        # Initialize processor and handler
        processor = FileProcessor(channel)
        handler = MessageHandler(processor)
        
        # Start consuming messages
        channel.basic_consume(
            queue=QUEUE_APPLICATION_INTAKE,
            on_message_callback=handler.handle_job_intake
        )
        
        logger.info(f"Listening for messages on '{QUEUE_APPLICATION_INTAKE}'")
        logger.info("File Parser Worker is ready")
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        if 'channel' in locals():
            channel.stop_consuming()
            
    except Exception as e:
        logger.critical(f"Fatal error in worker: {e}", exc_info=True)
        raise
        
    finally:
        if connection and connection.is_open:
            connection.close()
            logger.info("RabbitMQ connection closed")


if __name__ == '__main__':
    main_worker()


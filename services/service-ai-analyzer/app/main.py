from services.shared import (
    get_rabbitmq_connection,
    declare_queues,
    setup_logging,
    settings,
    QUEUE_AI_ANALYSIS,
    QUEUE_RESULTS_STORAGE
)

from .analyzers import GeminiAnalyzer
from .processors import CVProcessor
from .handlers import MessageHandler
from .utils import load_system_prompt

logger = setup_logging("ai-analyzer")


def main_worker():    
    # We validate GEMINI_API_KEY immediately on startup. 
    # It is better to crash the container now than to process jobs and fail everytime.
    if not settings.gemini_api_key:
        logger.critical("GEMINI_API_KEY not set. Cannot start service.")
        logger.critical("Please set GEMINI_API_KEY environment variable and restart.")
        raise ValueError("Missing GEMINI_API_KEY environment variable")
    
    logger.info("Gemini API key validated")
    
    system_instruction = load_system_prompt()
    logger.info("System prompt loaded")
    
    connection = None
    try:
        # Initialize Gemini analyzer
        analyzer = GeminiAnalyzer(
            api_key=settings.gemini_api_key,
            system_instruction=system_instruction
        )
        
        connection = get_rabbitmq_connection(logger=logger)
        channel = connection.channel()
        
        declare_queues(
            channel,
            [QUEUE_AI_ANALYSIS, QUEUE_RESULTS_STORAGE],
            logger=logger
        )
        
        channel.basic_qos(prefetch_count=1)
        
        processor = CVProcessor(analyzer, channel)
        handler = MessageHandler(processor)
        
        channel.basic_consume(
            queue=QUEUE_AI_ANALYSIS,
            on_message_callback=handler.handle_batch_message
        )
        
        logger.info(f"Listening for messages on '{QUEUE_AI_ANALYSIS}'")
        logger.info("AI Analyzer Worker is ready")
        
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
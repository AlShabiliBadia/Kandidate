from pydantic import ValidationError as PydanticValidationError
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from services.shared import ApplicationFileParseMessage, setup_logging, ProcessingError
from ..processors import FileProcessor

logger = setup_logging("message-handler")


class MessageHandler:
    
    def __init__(self, processor: FileProcessor):
        self.processor = processor
    
    def handle_job_intake(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> None:
        try:
            logger.info("Received application file parse message")
            logger.debug(f"Message preview: {body[:200]}...")
            
            message = ApplicationFileParseMessage.model_validate_json(body)
            logger.info(f"Processing application {message.application_id} for job {message.job_id}")
            
            self.processor.process_application_files(message)
            
            logger.info(f"Completed processing application {message.application_id}")
            
        except PydanticValidationError as e:
            logger.error(f"Message validation failed: {e}")
            logger.debug(f"Invalid message body: {body.decode('utf-8', errors='replace')}")
            
        except ProcessingError as e:
            logger.error(f"Processing failed: {e.message}")
            
        except Exception as e:
            logger.error(f"Unexpected error in callback: {e}", exc_info=True)
            
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug("Message acknowledged")

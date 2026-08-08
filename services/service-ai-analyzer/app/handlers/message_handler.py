from pydantic import ValidationError as PydanticValidationError
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from services.shared import ApplicationAnalysisMessage, setup_logging
from ..processors import CVProcessor

logger = setup_logging("message-handler")


class MessageHandler:
    
    def __init__(self, processor: CVProcessor):
        self.processor = processor
    
    def handle_batch_message(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> None:
        try:
            logger.info("Received application analysis message")
            logger.debug(f"Message preview: {body[:200]}...")
            
            message = ApplicationAnalysisMessage.model_validate_json(body)
            logger.info(f"Processing application {message.application_id} for job {message.job_id}")
            
            self.processor.process_application(
                job_id=message.job_id,
                application_id=message.application_id,
                jd_text=message.jd_text,
                resume_text=message.resume_text,
                cover_letter_text=message.cover_letter_text
            )
            
            logger.info(f"Completed analysis for application {message.application_id}")
            
        except PydanticValidationError as e:
            logger.error(f"Message validation failed: {e}")
            logger.debug(f"Invalid message body: {body.decode('utf-8', errors='replace')}")
            
        except Exception as e:
            logger.error(f"Unexpected error in message handler: {e}", exc_info=True)
            
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug("Message acknowledged")

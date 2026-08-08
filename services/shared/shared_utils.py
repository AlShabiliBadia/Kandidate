import logging
import time
from typing import Optional
import pika
from pika.channel import Channel
from pika.connection import Connection
from pydantic import BaseModel

from .config import (
    settings,
    RABBITMQ_MAX_RETRIES,
    RABBITMQ_RETRY_INTERVAL,
    RABBITMQ_PREFETCH_COUNT,
    QUEUE_CONFIG
)


# Logging Configuration
def setup_logging(service_name: str, level: int = logging.INFO) -> logging.Logger:

    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    
    logger.handlers.clear()
    
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# RabbitMQ Connection Management
def get_rabbitmq_connection(
    host: Optional[str] = None,
    max_retries: int = RABBITMQ_MAX_RETRIES,
    logger: Optional[logging.Logger] = None
) -> Connection:
    host = host or settings.rabbitmq_host
    
    if logger:
        logger.info(f"Connecting to RabbitMQ at {host}")
    
    credentials = pika.PlainCredentials(
        settings.rabbitmq_user,
        settings.rabbitmq_pass
    )
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            
            if logger:
                logger.info(f"Connected to RabbitMQ on attempt {attempt}/{max_retries}")
            
            return connection
            
        except (pika.exceptions.AMQPConnectionError, ConnectionError) as e:
            last_error = e
            
            if logger:
                logger.warning(
                    f"Connection attempt {attempt}/{max_retries} failed: {e}"
                )
            
            if attempt < max_retries:
                if logger:
                    logger.info(f"Retrying in {RABBITMQ_RETRY_INTERVAL} seconds")
                time.sleep(RABBITMQ_RETRY_INTERVAL)
    
    error_msg = (
        f"Failed to connect to RabbitMQ at {host} "
        f"after {max_retries} attempts. Last error: {last_error}"
    )
    
    if logger:
        logger.error(error_msg)
    
    raise ServiceConnectionError(error_msg, "RabbitMQ")


def declare_queues(
    channel: Channel,
    queue_names: list[str],
    logger: Optional[logging.Logger] = None
) -> None:
    if logger:
        logger.info(f"Declaring {len(queue_names)} queues")
    
    for queue_name in queue_names:
        config = QUEUE_CONFIG.get(queue_name, {"durable": True})
        channel.queue_declare(queue=queue_name, **config)
        
        if logger:
            logger.debug(f"Queue declared: {queue_name}")
    
    if logger:
        logger.info("Queues declared")


# Message Publishing
def publish_message(
    channel: Channel,
    queue_name: str,
    message: BaseModel,
    durable: bool = True,
    logger: Optional[logging.Logger] = None
) -> None:
    try:
        body = message.model_dump_json()
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2 if durable else 1,
                content_type='application/json'
            )
        )
        
        if logger:
            logger.debug(f"Published message to {queue_name}: {body[:100]}...")
            
    except Exception as e:
        if logger:
            logger.error(f"Failed to publish message to {queue_name}: {e}", exc_info=True)
        raise




class ServiceError(Exception):
    
    def __init__(self, message: str, service: str, error_type: str = "Unknown"):
        self.message = message
        self.service = service
        self.error_type = error_type
        super().__init__(self.message)


class ValidationError(ServiceError):
    
    def __init__(self, message: str, service: str):
        super().__init__(message, service, "Validation")


class ProcessingError(ServiceError):
    def __init__(self, message: str, service: str):
        super().__init__(message, service, "Processing")


class ServiceConnectionError(ServiceError):
    def __init__(self, message: str, service: str):
        super().__init__(message, service, "Connection")

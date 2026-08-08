import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # RabbitMQ Configuration
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_user: str = "admin"
    rabbitmq_pass: str = "admin"
    rabbitmq_port: int = 5672
    
    # MongoDB Configuration
    mongo_url: str = "mongodb://mongodb:27017"
    mongo_db_name: str = "kandidate_db"
    
    # PostgreSQL Configuration
    postgres_user: str = "kandidate_user"
    postgres_password: str = "kandidate_pass_2024"
    postgres_db: str = "kandidate"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    # API Keys
    gemini_api_key: Optional[str] = None
    
    # Service URLs
    results_db_url: str = "http://service-results-db:80"
    
    # File Storage
    upload_volume_path: str = "/uploads"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Queue Names
QUEUE_APPLICATION_INTAKE = "application_intake_queue"
QUEUE_AI_ANALYSIS = "ai_analysis_queue"
QUEUE_RESULTS_STORAGE = "results_storage_queue"

# Queue Configuration
QUEUE_CONFIG = {
    QUEUE_APPLICATION_INTAKE: {"durable": True},
    QUEUE_AI_ANALYSIS: {"durable": True},
    QUEUE_RESULTS_STORAGE: {"durable": True},
}

# RabbitMQ Connection Settings
RABBITMQ_MAX_RETRIES = 5
RABBITMQ_RETRY_INTERVAL = 5  # seconds
RABBITMQ_PREFETCH_COUNT = 1  # How many messages a service is allowed to receive before replying with ack

# AI Service Settings
AI_RATE_LIMIT_DELAY = 5  # seconds between API calls when use_delay=True
GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"

# File Upload Limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = {".pdf", ".docx"}

# Job Description Limits
JD_MIN_LENGTH = 50
JD_MAX_LENGTH = 10000

# Create global settings instance
settings = Settings()

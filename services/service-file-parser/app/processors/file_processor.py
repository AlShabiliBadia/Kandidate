from pathlib import Path
from typing import Optional
from pika.channel import Channel

from services.shared import (
    ApplicationFileParseMessage,
    ApplicationAnalysisMessage,
    publish_message,
    setup_logging,
    QUEUE_AI_ANALYSIS,
    QUEUE_RESULTS_STORAGE
)
from ..parsers import extract_text_from_pdf, extract_text_from_docx
from ..utils import publish_error_result

logger = setup_logging("file-processor")


class FileProcessor:
    def __init__(self, channel: Channel):
        self.channel = channel
    
    def process_application_files(self, message: ApplicationFileParseMessage) -> None:
        logger.info(
            f"Processing application {message.application_id} for job {message.job_id}"
        )
        
        resume_text: Optional[str] = None
        cover_letter_text: Optional[str] = None
        
        if message.resume_path:
            resume_text = self._extract_file_text(message.resume_path, "resume")
        
        if message.cover_letter_path:
            cover_letter_text = self._extract_file_text(message.cover_letter_path, "cover_letter")
        
        if not resume_text and not cover_letter_text:
            logger.error(
                f"Failed to extract any text for application {message.application_id}"
            )
            return
        
        logger.info(
            f"Successfully extracted - Resume: {len(resume_text) if resume_text else 0} chars, "
            f"Cover Letter: {len(cover_letter_text) if cover_letter_text else 0} chars"
        )
        
        # TODO: Get JD text from database using job_id
        jd_text = "Job description placeholder"
        
        analysis_message = ApplicationAnalysisMessage(
            job_id=message.job_id,
            application_id=message.application_id,
            jd_text=jd_text,
            resume_text=resume_text,
            cover_letter_text=cover_letter_text
        )
        
        publish_message(self.channel, QUEUE_AI_ANALYSIS, analysis_message, logger=logger)
        logger.info(f"Published application {message.application_id} for AI analysis")
    
    def _extract_file_text(self, file_path_str: str, file_type: str) -> Optional[str]:
        try:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path_str}")
            
            suffix = file_path.suffix.lower()
            
            logger.debug(f"Extracting {file_type} from {file_path.name} ({suffix})")
            
            if suffix == '.pdf':
                text = extract_text_from_pdf(file_path)
            elif suffix == '.docx':
                text = extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
            
            logger.info(f"Extracted {len(text)} characters from {file_type}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting {file_type}: {e}", exc_info=True)
            return None

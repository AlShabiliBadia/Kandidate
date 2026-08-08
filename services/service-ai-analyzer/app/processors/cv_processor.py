import json
from typing import Optional
from pydantic import ValidationError as PydanticValidationError
from pika.channel import Channel

from services.shared import (
    AnalysisResult,
    ApplicationAnalysisResultMessage,
    publish_message,
    setup_logging,
    QUEUE_RESULTS_STORAGE
)
from ..analyzers import GeminiAnalyzer

logger = setup_logging("cv-processor")


class CVProcessor:
    
    def __init__(self, analyzer: GeminiAnalyzer, channel: Channel):
        self.analyzer = analyzer
        self.channel = channel
    
    def process_application(
        self,
        job_id: str,
        application_id: str,
        jd_text: str,
        resume_text: Optional[str],
        cover_letter_text: Optional[str]
    ) -> None:
        logger.info(f"Analyzing application {application_id} for job {job_id}")
        
        combined_text = ""
        if resume_text:
            combined_text += f"RESUME:\n{resume_text}\n\n"
        if cover_letter_text:
            combined_text += f"COVER LETTER:\n{cover_letter_text}"
        
        if not combined_text:
            logger.error(f"No text to analyze for application {application_id}")
            self._publish_result(application_id, success=False, error="No text content provided")
            return
        
        try:
            logger.debug(f"Sending to Gemini API (length: {len(combined_text)} chars)")
            result = self.analyzer.analyze_cv(combined_text, jd_text)
            
            self._publish_result(application_id, success=True, analysis_result=result)
            
            logger.info(
                f"Successfully analyzed application {application_id} "
                f"(score: {result.match_score}/100, recommendation: {result.recommendation})"
            )
            
        except (json.JSONDecodeError, PydanticValidationError) as e:
            logger.error(f"AI validation failed for application {application_id}: {str(e)[:200]}")
            self._publish_result(
                application_id,
                success=False,
                error=f"AI Validation Error: {str(e)[:200]}"
            )
            
        except Exception as e:
            logger.error(f"Gemini API error for application {application_id}: {e}", exc_info=True)
            self._publish_result(
                application_id,
                success=False,
                error=f"Gemini API Error: {str(e)}"
            )
    
    def _publish_result(
        self,
        application_id: str,
        success: bool,
        analysis_result: Optional[AnalysisResult] = None,
        error: Optional[str] = None
    ) -> None:
        try:
            result_message = ApplicationAnalysisResultMessage(
                application_id=application_id,
                success=success,
                analysis_result=analysis_result,
                error=error
            )
            
            publish_message(self.channel, QUEUE_RESULTS_STORAGE, result_message, logger=logger)
            
            status = "successful" if success else "failed"
            logger.debug(f"Published {status} result for application {application_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish result for application {application_id}: {e}", exc_info=True)
            logger.debug(f"[{correlation_id}] Published error result for {filename}")
                
        except Exception as e:
            logger.error(f"[{correlation_id}] Failed to publish result for {filename}: {e}", exc_info=True)

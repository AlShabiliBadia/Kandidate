import os
import logging
from pathlib import Path
from services.shared import AnalysisResult

logger = logging.getLogger(__name__)


def _get_default_prompt() -> str:
    schema = AnalysisResult.model_json_schema()
    properties = schema.get('properties', {})
    
    schema_fields = []
    for field_name, field_info in properties.items():
        field_type = field_info.get('type', 'any')
        description = field_info.get('description', '')
        schema_fields.append(f'"{field_name}": {field_type} - {description}')
    
    return f"""You are an expert Technical Recruiter and AI Analyzer for Kandidate.
Analyze CVs against Job Descriptions with fairness and precision.

OUTPUT FORMAT: Return ONLY a valid JSON object matching the AnalysisResult schema.
Focus on conceptual skill matches, not just keywords. Be unbiased and thorough.

Required fields: {', '.join(properties.keys())}

Be fair, unbiased, and focus on transferable skills and potential, not just exact keyword matches."""


def load_system_prompt() -> str:
    try:
        possible_paths = [
            os.environ.get('PROMPT_CONFIG_PATH'),
            Path(__file__).parent.parent.parent.parent / 'config' / 'prompt_system_instruction.txt',
            Path(__file__).parent / '../../config/prompt_system_instruction.txt',
        ]
        
        for config_path in possible_paths:
            if config_path and Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        logger.info(f"Loaded system prompt from: {config_path}")
                        return content
        
        logger.warning("prompt_system_instruction.txt not found. Using auto-generated default.")
        return _get_default_prompt()
        
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}. Using auto-generated default.")
        return _get_default_prompt()

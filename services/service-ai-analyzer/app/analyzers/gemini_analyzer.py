import instructor
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, SafetySettingDict, HarmCategory, HarmBlockThreshold

from services.shared import setup_logging, GEMINI_MODEL_NAME, AnalysisResult

logger = setup_logging("gemini-analyzer")


class GeminiAnalyzer:
    
    def __init__(self, api_key: str, system_instruction: str, model_name: str = GEMINI_MODEL_NAME):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.system_instruction = system_instruction
        genai.configure(api_key=api_key)  # type: ignore
        
        self.generation_config = GenerationConfig(
            response_mime_type="application/json",
            # We keep temperature low (0.1) because we want an 'Analyst'.
            # We need consistent, factual extraction, not creative variations.
            temperature=0.1
        )
        
        # We just shouldn't be blocking something like "Penetration testing".
        self.safety_settings = [
            SafetySettingDict(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),  # type: ignore
            SafetySettingDict(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),  # type: ignore
            SafetySettingDict(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),  # type: ignore
            SafetySettingDict(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),  # type: ignore
        ]
        
        # Create base Gemini model
        base_model = genai.GenerativeModel(  # type: ignore
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=self.system_instruction
        )
        
        # Instructor patches the Gemini client to support Pydantic models natively.
        # It handles the retry logic and validation loop if Gemini outputs malformed JSON.
        self.client = instructor.from_gemini(
            client=base_model,
            mode=instructor.Mode.GEMINI_JSON
        )
        
        logger.info(f"Gemini analyzer initialized with Instructor")
        logger.info(f"Model: {model_name}")
    
    def analyze_cv(self, cv_text: str, jd_text: str) -> AnalysisResult:

        prompt = f"""Here is the Job Description:

                    {jd_text}

                    ---

                    Here is the Candidate's CV:

                    {cv_text}

                    ---

                    Analyze this candidate against the job requirements and provide a comprehensive evaluation."""
                            
        try:
            result: AnalysisResult = self.client.chat.completions.create(
                # This ensures the AI output matches our Pydantic schema exactly,
                # or raises a validation error before we even see the data.
                response_model=AnalysisResult,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            logger.info(f"Analysis complete: {result.candidate_name}, Score: {result.match_score}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze CV: {e}")
            raise

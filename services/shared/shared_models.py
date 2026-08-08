from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Annotated

class ConceptualMatch(BaseModel):
    requested_skill: str = Field(description="The skill asked for in the JD")
    found_skill: str = Field(description="The equivalent skill found in the CV")
    reasoning: str = Field(description="Why these are equivalent")

class SkillGap(BaseModel):
    missing_skill: str = Field(description="A critical skill from the JD missing")
    learning_curve: Literal["Low", "Medium", "High"]

class AnalysisResult(BaseModel):
    cv_id: str = Field(default="", description="Unique identifier for this CV within the job")
    original_filename: str = Field(default="", description="Original filename uploaded by user")
    candidate_name: str = Field(default="Unknown Candidate", description="Candidate's name, inferred from text")
    match_score: Annotated[int, Field(ge=0, le=100, description="0-100 score based on conceptual fit")]
    summary_headline: str = Field(description="A 1-sentence punchy summary")
    conceptual_matches: List[ConceptualMatch] = Field(default_factory=list)
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    experience_analysis: str = Field(description="Analysis of years vs. impact")
    recommendation: Literal["Strong Hire", "Interview for Potential", "Backup", "Review Needed", "No Fit"]
    risk_assessment: Literal["Low", "Medium", "High"]
    email: Optional[str] = Field(default=None, description="Candidate's email address")
    phone: Optional[str] = Field(default=None, description="Candidate's phone number")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, description="Personal website/portfolio URL")
    
    model_config = {
        "extra": "forbid"
    }


class ApplicationFileParseMessage(BaseModel):
    job_id: str
    application_id: str
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None


class ApplicationAnalysisMessage(BaseModel):
    job_id: str
    application_id: str
    jd_text: str
    resume_text: Optional[str] = None
    cover_letter_text: Optional[str] = None


class ApplicationAnalysisResultMessage(BaseModel):
    application_id: str
    success: bool
    analysis_result: Optional[AnalysisResult] = None
    error: Optional[str] = None


class JobIntakeMessage(BaseModel):
    job_id: str
    correlation_id: str
    jd_text: str
    use_delay: bool
    file_paths: List[dict]
    expected_file_count: int

class BatchAnalysisMessage(BaseModel):
    job_id: str
    correlation_id: str
    jd_text: str
    use_delay: bool
    cvs: List[dict[str, str]]

class JobResultMessage(BaseModel):
    job_id: str
    correlation_id: str
    cv_id: str
    original_filename: str
    status: Literal["success", "error"]
    data: Optional[AnalysisResult] = None
    error: Optional[str] = None

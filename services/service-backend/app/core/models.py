import uuid
from datetime import datetime
from typing import List, Optional
import enum

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# --- Enums ---

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"
    REVIEWER = "REVIEWER"
    CANDIDATE = "CANDIDATE"

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"

class JobType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"

class WorkplaceType(str, enum.Enum):
    REMOTE = "REMOTE"
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"

class QuestionType(str, enum.Enum):
    SHORT_TEXT = "SHORT_TEXT"
    LONG_TEXT = "LONG_TEXT"
    YES_NO = "YES_NO"
    SELECT = "SELECT"
    FILE = "FILE"

class Recommendation(str, enum.Enum):
    STRONG_HIRE = "STRONG_HIRE"
    INTERVIEW = "INTERVIEW"
    BACKUP = "BACKUP"
    REVIEW_NEEDED = "REVIEW_NEEDED"
    NO_FIT = "NO_FIT"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# --- Base ---

class Base(DeclarativeBase):
    pass

# --- Models ---

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    company_website_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    brand_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Null for Shadow/Guest
    
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CANDIDATE)
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="candidate")
    activities: Mapped[List["ApplicationActivity"]] = relationship("ApplicationActivity", back_populates="actor")
    comments: Mapped[List["ApplicationComment"]] = relationship("ApplicationComment", back_populates="author")
    tracking_links: Mapped[List["JobTrackingLink"]] = relationship("JobTrackingLink", back_populates="creator")

class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stages: Mapped[List["PipelineStage"]] = relationship("PipelineStage", back_populates="pipeline", order_by="PipelineStage.order_index")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="pipeline")

class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="stages")
    current_applications: Mapped[List["Application"]] = relationship("Application", back_populates="current_stage")

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id"))
    
    title: Mapped[str] = mapped_column(String, index=True)
    description_html: Mapped[str] = mapped_column(Text)
    department: Mapped[Optional[str]] = mapped_column(String, index=True)
    
    job_type: Mapped[JobType] = mapped_column(Enum(JobType))
    workplace_type: Mapped[WorkplaceType] = mapped_column(Enum(WorkplaceType))
    location: Mapped[str] = mapped_column(String)
    
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String, default="USD")
    
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="jobs")
    questions: Mapped[List["JobQuestion"]] = relationship("JobQuestion", back_populates="job", order_by="JobQuestion.order_index")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="job")
    tracking_links: Mapped[List["JobTrackingLink"]] = relationship("JobTrackingLink", back_populates="job")

class JobQuestion(Base):
    __tablename__ = "job_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    
    label: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    options: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    job: Mapped["Job"] = relationship("Job", back_populates="questions")

class JobTrackingLink(Base):
    __tablename__ = "job_tracking_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    source: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)

    job: Mapped["Job"] = relationship("Job", back_populates="tracking_links")
    creator: Mapped["User"] = relationship("User", back_populates="tracking_links")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    current_stage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipeline_stages.id"))
    tracking_link_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("job_tracking_links.id"), nullable=True)

    # --- SNAPSHOT DATA ---
    candidate_first_name: Mapped[str] = mapped_column(String)
    candidate_last_name: Mapped[str] = mapped_column(String)
    candidate_email: Mapped[str] = mapped_column(String)
    candidate_phone: Mapped[Optional[str]] = mapped_column(String)
    candidate_headline: Mapped[Optional[str]] = mapped_column(String)
    
    linkedin_url: Mapped[Optional[str]] = mapped_column(String)
    github_url: Mapped[Optional[str]] = mapped_column(String)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String)

    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
    candidate: Mapped["User"] = relationship("User", back_populates="applications")
    current_stage: Mapped["PipelineStage"] = relationship("PipelineStage", back_populates="current_applications")
    
    answers: Mapped[List["ApplicationAnswer"]] = relationship("ApplicationAnswer", back_populates="application")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="application")
    ai_insight: Mapped["ApplicationAIInsight"] = relationship("ApplicationAIInsight", uselist=False, back_populates="application")
    activities: Mapped[List["ApplicationActivity"]] = relationship("ApplicationActivity", back_populates="application")
    comments: Mapped[List["ApplicationComment"]] = relationship("ApplicationComment", back_populates="application")

class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_questions.id"))
    
    text_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    boolean_value: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Matches ERD edge case fix

    application: Mapped["Application"] = relationship("Application", back_populates="answers")

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"))
    
    file_type: Mapped[str] = mapped_column(String)
    file_url: Mapped[str] = mapped_column(String)
    file_name: Mapped[str] = mapped_column(String)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="attachments")

class ApplicationAIInsight(Base):
    __tablename__ = "application_ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), unique=True)
    
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    recommendation: Mapped[Recommendation] = mapped_column(Enum(Recommendation))
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel))
    
    analysis_data: Mapped[dict] = mapped_column(JSONB)
    
    model_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="ai_insight")

class ApplicationActivity(Base):
    __tablename__ = "application_activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"))
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    action_type: Mapped[str] = mapped_column(String)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="activities")
    actor: Mapped["User"] = relationship("User", back_populates="activities")

class ApplicationComment(Base):
    __tablename__ = "application_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")


class LegacyJob(Base):
    __tablename__ = "jobs_legacy"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    total_cvs: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_cvs: Mapped[int] = mapped_column(Integer, default=0)
    failed_cvs: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    cv_analyses: Mapped[List["CVAnalysis"]] = relationship("CVAnalysis", back_populates="job", cascade="all, delete-orphan")


class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs_legacy.id", ondelete="CASCADE"), nullable=False)
    cv_id: Mapped[str] = mapped_column(String(36), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_headline: Mapped[str] = mapped_column(Text, nullable=False)
    conceptual_matches: Mapped[dict] = mapped_column(JSONB, nullable=False)
    skill_gaps: Mapped[dict] = mapped_column(JSONB, nullable=False)
    experience_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_assessment: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    job: Mapped["LegacyJob"] = relationship("LegacyJob", back_populates="cv_analyses")
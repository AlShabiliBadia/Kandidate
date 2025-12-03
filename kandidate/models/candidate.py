"""Domain models describing candidate documents and analytics results."""
from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from pydantic import BaseModel, Field


class CandidateDocument(BaseModel):
    """Represents a candidate submission ready for parsing and analysis."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the document")
    name: str = Field(description="Human friendly name for the document owner")
    text: str = Field(description="Plain text extracted from the submission")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary attributes captured during ingestion")


class CandidateAnalysis(BaseModel):
    """Structured representation of the AI-driven analysis outcome."""

    summary: str = Field(description="Short synopsis of the submission")
    keywords: List[str] = Field(default_factory=list, description="Detected high-signal keywords")
    score: float = Field(ge=0.0, le=1.0, description="Normalized fitness score between 0 and 1")
    warnings: List[str] = Field(default_factory=list, description="Quality or completeness warnings")


class CandidateResult(BaseModel):
    """Couples the original document with its computed analysis."""

    document: CandidateDocument
    analysis: CandidateAnalysis

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the result."""

        return self.model_dump()

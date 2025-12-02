"""FastAPI application exposing the pipeline over HTTP."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from kandidate.core import Pipeline
from kandidate.models import AppConfig, CandidateDocument, CandidateResult
from kandidate.utils.config_loader import load_config
from kandidate.utils.logging import configure_logging


class CandidatePayload(BaseModel):
    """Schema describing the API contract for candidate submissions."""

    name: str
    text: str
    metadata: dict[str, str] | None = None


def create_app(config: AppConfig | None = None) -> FastAPI:
    """Return a fully configured FastAPI instance."""

    app = FastAPI(title="Kandidate", version="0.1.0")
    config = config or load_config()
    configure_logging(config.logging)
    pipeline = Pipeline(config)

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return a quick health status."""

        return {"status": "ok"}

    @app.get("/candidates", response_model=list[CandidateResult])
    async def list_candidates() -> list[CandidateResult]:
        """Return every processed candidate."""

        return pipeline.repository.list_results()

    @app.post("/candidates", response_model=CandidateResult, status_code=201)
    async def create_candidate(payload: CandidatePayload) -> CandidateResult:
        """Ingest and analyze a candidate submission."""

        if not payload.text.strip():
            raise HTTPException(status_code=400, detail="Payload text must not be empty")
        document = CandidateDocument(name=payload.name, text=payload.text, metadata=payload.metadata or {})
        return pipeline.process_document(document)

    return app

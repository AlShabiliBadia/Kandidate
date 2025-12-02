from __future__ import annotations

from pathlib import Path

from kandidate.core import Pipeline
from kandidate.models import AppConfig, CandidateDocument, RepositoryConfig


def test_pipeline_process_document(tmp_path: Path) -> None:
    repository_path = tmp_path / "results.json"
    config = AppConfig(repository=RepositoryConfig(path=repository_path))
    pipeline = Pipeline(config)
    document = CandidateDocument(name="Aisha", text="Python FastAPI Docker Kubernetes experience")

    result = pipeline.process_document(document)

    assert result.analysis.keywords
    assert repository_path.exists()
    assert pipeline.repository.list_results()

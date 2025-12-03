from __future__ import annotations

from pathlib import Path

from kandidate.models import CandidateAnalysis, CandidateDocument, CandidateResult, RepositoryConfig
from kandidate.services import ResultRepository


def test_repository_persists_results(tmp_path: Path) -> None:
    repo_path = tmp_path / "results.json"
    repo = ResultRepository(RepositoryConfig(path=repo_path))
    document = CandidateDocument(name="Test", text="Python FastAPI developer")
    analysis = CandidateAnalysis(summary="Summary", keywords=["python"], score=0.9, warnings=[])
    result = CandidateResult(document=document, analysis=analysis)

    repo.save_result(result)
    stored = repo.list_results()

    assert len(stored) == 1
    assert stored[0].analysis.score == 0.9

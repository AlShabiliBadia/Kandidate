from __future__ import annotations

from kandidate.models import AnalyzerConfig, CandidateDocument
from kandidate.services import CandidateAnalyzer


def test_analyzer_scores_keywords() -> None:
    config = AnalyzerConfig(keywords=["python", "fastapi"], min_word_count=5)
    analyzer = CandidateAnalyzer(config)
    document = CandidateDocument(name="Test", text="Python developer with FastAPI expertise")
    analysis = analyzer.analyze(document)
    assert analysis.score >= 0.5
    assert analysis.keywords == ["python", "fastapi"]
    assert not analysis.warnings


def test_analyzer_warns_for_short_documents() -> None:
    config = AnalyzerConfig(keywords=["python"], min_word_count=100)
    analyzer = CandidateAnalyzer(config)
    document = CandidateDocument(name="Short", text="python")
    analysis = analyzer.analyze(document)
    assert analysis.warnings
    assert analysis.score <= 0.5

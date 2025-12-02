"""Heuristic analyzer offering deterministic scoring for submissions."""
from __future__ import annotations

import statistics
from typing import List

from kandidate.models import AnalyzerConfig, CandidateAnalysis, CandidateDocument
from kandidate.utils.logging import get_logger


class CandidateAnalyzer:
    """Extract lightweight, explainable insights from candidate documents."""

    def __init__(self, config: AnalyzerConfig, *, logger=None) -> None:
        """Initialize the analyzer.

        Args:
            config: Analyzer configuration containing scoring knobs.
            logger: Optional logger used for dependency injection in tests.
        """

        self.config = config
        self.logger = logger or get_logger(__name__)

    def analyze(self, document: CandidateDocument) -> CandidateAnalysis:
        """Generate a :class:`CandidateAnalysis` for a document.

        Args:
            document: Document to analyze.

        Returns:
            CandidateAnalysis: Structured summary, keyword hits, and score.
        """

        tokens = [token.lower() for token in document.text.split()]
        keyword_hits = [kw for kw in self.config.keywords if kw.lower() in tokens]
        coverage = len(keyword_hits) / max(len(self.config.keywords), 1)
        word_score = min(len(tokens) / max(self.config.min_word_count, 1), 1.0)
        score = self._normalize_score([coverage, word_score])

        warnings: List[str] = []
        if len(tokens) < self.config.min_word_count:
            warnings.append("Document is shorter than the recommended length.")
            score = max(score - 0.25, 0.0)
        if not keyword_hits:
            warnings.append("No target keywords detected; consider enriching the resume.")
            score = max(score - 0.1, 0.0)

        summary = document.text.strip().split("\n", maxsplit=1)[0][:200]
        return CandidateAnalysis(
            summary=summary or "No summary available",
            keywords=keyword_hits,
            score=score,
            warnings=warnings,
        )

    @staticmethod
    def _normalize_score(values: List[float]) -> float:
        """Combine multiple partial scores into a single bounded value.

        Args:
            values: Individual scoring contributions.

        Returns:
            float: Average score clamped to ``[0, 1]``.
        """

        if not values:
            return 0.0
        avg = statistics.mean(values)
        return max(0.0, min(round(avg, 3), 1.0))

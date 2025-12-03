"""Coordinated pipeline that parses, analyzes, and persists submissions."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from kandidate.models import AppConfig, CandidateDocument, CandidateResult
from kandidate.services import CandidateAnalyzer, DocumentParser, ResultRepository
from kandidate.utils.logging import get_logger


class Pipeline:
    """Represents the synchronous ingestion workflow for Kandidate."""

    def __init__(
        self,
        config: AppConfig,
        *,
        parser: DocumentParser | None = None,
        analyzer: CandidateAnalyzer | None = None,
        repository: ResultRepository | None = None,
    ) -> None:
        """Create a pipeline with dependency-injected components.

        Args:
            config: Fully merged application configuration.
            parser: Optional parser override.
            analyzer: Optional analyzer override.
            repository: Optional repository override.
        """

        self.config = config
        self.parser = parser or DocumentParser(config.parser)
        self.analyzer = analyzer or CandidateAnalyzer(config.analyzer)
        self.repository = repository or ResultRepository(config.repository)
        self.logger = get_logger(__name__)

    def process_paths(self, paths: Iterable[Path]) -> List[CandidateResult]:
        """Process an arbitrary collection of file paths.

        Args:
            paths: Iterable of filesystem paths.

        Returns:
            list[CandidateResult]: Persisted results.
        """

        results: List[CandidateResult] = []
        for path in paths:
            results.append(self.process_path(path))
        return results

    def process_directory(self, directory: Path) -> List[CandidateResult]:
        """Process all supported files contained in a directory.

        Args:
            directory: Directory to traverse.

        Returns:
            list[CandidateResult]: Persisted results.
        """

        documents = self.parser.parse_directory(directory)
        return self.process_documents(documents)

    def process_path(self, path: Path) -> CandidateResult:
        """Parse, analyze, and persist a single file.

        Args:
            path: Path to the candidate submission.

        Returns:
            CandidateResult: Persisted result object.
        """

        document = self.parser.parse_path(path)
        return self.process_document(document)

    def process_documents(self, documents: Sequence[CandidateDocument]) -> List[CandidateResult]:
        """Process a batch of already parsed documents.

        Args:
            documents: Pre-parsed submissions.

        Returns:
            list[CandidateResult]: Persisted results for each document.
        """

        results: List[CandidateResult] = []
        for document in documents:
            results.append(self.process_document(document))
        return results

    def process_document(self, document: CandidateDocument) -> CandidateResult:
        """Analyze a document and persist the resulting artifact.

        Args:
            document: Candidate submission ready for analysis.

        Returns:
            CandidateResult: Newly created result linking document and analysis.
        """

        analysis = self.analyzer.analyze(document)
        result = CandidateResult(document=document, analysis=analysis)
        saved = self.repository.save_result(result)
        self.logger.info("Processed candidate %s with score %.3f", document.name, analysis.score)
        return saved

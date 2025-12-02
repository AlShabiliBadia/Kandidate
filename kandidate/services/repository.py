"""Persistence layer for candidate results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from kandidate.models import CandidateResult, RepositoryConfig
from kandidate.utils.logging import get_logger


class ResultRepository:
    """Store results on the local filesystem in a JSON document."""

    def __init__(self, config: RepositoryConfig, *, logger=None) -> None:
        """Initialize the repository.

        Args:
            config: Repository configuration.
            logger: Optional injected logger instance for testing.
        """

        self.config = config
        self.path = Path(config.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger or get_logger(__name__)

    def save_result(self, result: CandidateResult) -> CandidateResult:
        """Persist a result and return it for chaining.

        Args:
            result: Processed candidate result.

        Returns:
            CandidateResult: The same instance that was persisted.
        """

        existing = self._load()
        existing.append(result.as_dict())
        self.path.write_text(json.dumps(existing, indent=2))
        self.logger.debug("Persisted result %s", result.document.id)
        return result

    def list_results(self) -> List[CandidateResult]:
        """Return every stored result.

        Returns:
            list[CandidateResult]: Materialized objects reconstructed from disk.
        """

        return [CandidateResult(**row) for row in self._load()]

    def _load(self) -> List[dict]:
        """Read the repository payload, returning an empty list when missing.

        Returns:
            list[dict]: Raw JSON payloads.
        """

        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text())
        except json.JSONDecodeError:
            self.logger.warning("Repository file %s is corrupt; recreating it", self.path)
            return []

"""Convert raw files or payloads into internal candidate documents."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence

from kandidate.models import CandidateDocument, ParserConfig
from kandidate.utils.logging import get_logger


class DocumentParser:
    """Simple parser supporting plaintext and JSON payloads."""

    def __init__(self, config: ParserConfig, *, logger=None) -> None:
        """Initialize the parser.

        Args:
            config: Parser configuration options.
            logger: Optional logger instance injected for testing.
        """

        self.config = config
        self.logger = logger or get_logger(__name__)

    def parse_path(self, path: Path) -> CandidateDocument:
        """Parse a document located on disk.

        Args:
            path: Location of the file being parsed.

        Returns:
            CandidateDocument: Structured representation of the parsed file.

        Raises:
            ValueError: If the file extension is unsupported or the payload is invalid.
        """

        if path.suffix.lower() not in self._normalized_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding=self.config.encoding))
            return self.parse_payload(payload)

        text = path.read_text(encoding=self.config.encoding)
        return CandidateDocument(name=path.stem, text=text, metadata={"source": str(path)})

    def parse_directory(self, directory: Path) -> List[CandidateDocument]:
        """Parse every supported file inside a directory.

        Args:
            directory: Directory containing submissions.

        Returns:
            list[CandidateDocument]: All successfully parsed documents.
        """

        documents: List[CandidateDocument] = []
        for path in directory.iterdir():
            if path.is_file() and path.suffix.lower() in self._normalized_extensions:
                documents.append(self.parse_path(path))
        return documents

    def parse_payload(self, payload: Mapping[str, Any]) -> CandidateDocument:
        """Validate dictionaries originating from API or JSON inputs.

        Args:
            payload: Arbitrary mapping describing the candidate submission.

        Returns:
            CandidateDocument: Parsed representation of the payload.

        Raises:
            ValueError: If the text field is blank.
        """

        name = str(payload.get("name") or payload.get("candidate") or "anonymous")
        text = str(payload.get("text") or payload.get("content") or "")
        metadata = dict(payload.get("metadata", {}))
        if not text.strip():
            raise ValueError("Payload is missing the `text` field.")
        return CandidateDocument(name=name, text=text, metadata=metadata)

    def parse_payloads(self, payloads: Sequence[Mapping[str, Any]]) -> List[CandidateDocument]:
        """Bulk-parse payloads, skipping entries that fail validation.

        Args:
            payloads: Iterable of candidate submission payloads.

        Returns:
            list[CandidateDocument]: Valid payloads transformed into domain objects.
        """

        documents: List[CandidateDocument] = []
        for payload in payloads:
            try:
                documents.append(self.parse_payload(payload))
            except ValueError as error:
                self.logger.warning("Skipping invalid payload: %s", error)
        return documents

    @property
    def _normalized_extensions(self) -> Iterable[str]:
        """Return lower-cased file extensions for quick membership tests.

        Returns:
            Iterable[str]: Normalized list of acceptable extensions.
        """

        return [ext.lower() for ext in self.config.supported_extensions]

"""Configuration dataclasses consumed across the application."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class LoggingConfig:
    """Configuration for the logging subsystem."""

    level: str = "INFO"
    json_format: bool = False


@dataclass(slots=True)
class ParserConfig:
    """File parsing behavior for candidate submissions."""

    supported_extensions: List[str] = field(
        default_factory=lambda: [".txt", ".md", ".json"],
    )
    encoding: str = "utf-8"
    chunk_size: int = 4096


@dataclass(slots=True)
class AnalyzerConfig:
    """Tunable heuristics for the light-weight analyzer."""

    keywords: List[str] = field(
        default_factory=lambda: ["python", "fastapi", "docker", "kubernetes", "gcp"],
    )
    min_word_count: int = 80


@dataclass(slots=True)
class RepositoryConfig:
    """Persistence settings for candidate results."""

    backend: str = "filesystem"
    path: Path = Path("data/results.json")


@dataclass(slots=True)
class APIConfig:
    """FastAPI runtime configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


@dataclass(slots=True)
class AppConfig:
    """Container object bundling every configuration namespace."""

    logging: LoggingConfig = field(default_factory=LoggingConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    repository: RepositoryConfig = field(default_factory=RepositoryConfig)
    api: APIConfig = field(default_factory=APIConfig)

    @property
    def repository_path(self) -> Path:
        """Expose a convenience accessor for repository path references."""

        return self.repository.path

"""Helpers responsible for loading richly-typed configuration objects."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

import yaml

from kandidate.models.config import (
    APIConfig,
    AnalyzerConfig,
    AppConfig,
    LoggingConfig,
    ParserConfig,
    RepositoryConfig,
)
from kandidate.utils.exceptions import KandidateError

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.yaml"
ENV_PREFIX = "KANDIDATE"


class AppConfigFactory:
    """Factory object to produce :class:`AppConfig` instances with overrides."""

    def __init__(self, default_path: Path | None = None) -> None:
        """Initialize the factory.

        Args:
            default_path: Optional configuration path overriding the default.
        """

        self.default_path = default_path or DEFAULT_CONFIG_PATH

    def build(self, config_path: Path | None = None, overrides: Mapping[str, Any] | None = None) -> AppConfig:
        """Load configuration from disk, env vars, and ad-hoc overrides.

        Args:
            config_path: Optional path to a YAML or JSON file.
            overrides: Mapping containing values that should win over all others.

        Returns:
            AppConfig: Resolved configuration object.
        """

        return load_config(config_path or self.default_path, overrides=overrides)


def load_config(path: Path | None = None, overrides: Mapping[str, Any] | None = None) -> AppConfig:
    """Load the project configuration by merging defaults, env vars, and overrides.

    Args:
        path: Path to the configuration document.
        overrides: Additional values taking precedence over disk and env vars.

    Returns:
        AppConfig: Fully merged configuration object.

    Raises:
        KandidateError: If the configuration file cannot be found or parsed.
    """

    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        raise KandidateError(f"Configuration file not found: {config_path}")

    raw_config = _load_file(config_path)
    raw_config = _merge_dicts(raw_config, _apply_env_overrides())
    if overrides:
        raw_config = _merge_dicts(raw_config, overrides)
    return _build_app_config(raw_config)


def _load_file(path: Path) -> Dict[str, Any]:
    """Load YAML or JSON configuration documents.

    Args:
        path: File path pointing to a YAML or JSON document.

    Returns:
        dict: Parsed representation of the configuration file.

    Raises:
        KandidateError: When encountering an unsupported extension.
    """

    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text()) or {}
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    raise KandidateError(f"Unsupported configuration format: {path.suffix}")


def _apply_env_overrides() -> Dict[str, Any]:
    """Translate ``KANDIDATE_*`` environment variables into nested overrides.

    Returns:
        dict: Environment driven overrides.
    """

    overrides: Dict[str, Any] = {}
    prefix = f"{ENV_PREFIX}_"
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        path_tokens = key[len(prefix) :].lower().split("__")
        _set_nested_value(overrides, path_tokens, _coerce_value(value))
    return overrides


def _set_nested_value(container: MutableMapping[str, Any], path: list[str], value: Any) -> None:
    """Assign a nested dictionary value using ``__`` separated keys.

    Args:
        container: Dictionary receiving the nested value.
        path: Sequence of nested keys.
        value: Value to assign at the leaf.
    """

    cursor: MutableMapping[str, Any] = container
    for token in path[:-1]:
        cursor = cursor.setdefault(token, {})  # type: ignore[assignment]
    cursor[path[-1]] = value


def _coerce_value(raw_value: str) -> Any:
    """Convert string inputs to ints, floats, or booleans when possible.

    Args:
        raw_value: The textual environment variable value.

    Returns:
        Any: Coerced value or the original string when conversion fails.
    """

    lowered = raw_value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(raw_value)
    except ValueError:
        pass
    try:
        return float(raw_value)
    except ValueError:
        pass
    return raw_value


def _merge_dicts(base: Mapping[str, Any], incoming: Mapping[str, Any]) -> Dict[str, Any]:
    """Deep merge dictionaries, preferring values from ``incoming``.

    Args:
        base: Base dictionary.
        incoming: Dictionary whose values should override ``base``.

    Returns:
        dict: Merged dictionary.
    """

    merged: Dict[str, Any] = dict(base)
    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], Mapping) and isinstance(value, Mapping):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _build_app_config(payload: Mapping[str, Any]) -> AppConfig:
    """Convert dictionaries into concrete dataclass instances.

    Args:
        payload: Arbitrary mappings of primitive values.

    Returns:
        AppConfig: Config object containing typed namespaces.
    """

    logging_cfg = LoggingConfig(**payload.get("logging", {}))
    parser_cfg = ParserConfig(**payload.get("parser", {}))
    analyzer_cfg = AnalyzerConfig(**payload.get("analyzer", {}))
    repository_payload = payload.get("repository", {})
    repository_cfg = RepositoryConfig(**_normalize_repository(repository_payload))
    api_cfg = APIConfig(**payload.get("api", {}))
    return AppConfig(
        logging=logging_cfg,
        parser=parser_cfg,
        analyzer=analyzer_cfg,
        repository=repository_cfg,
        api=api_cfg,
    )


def _normalize_repository(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Ensure repository paths are expanded and absolute.

    Args:
        payload: Repository configuration dictionary.

    Returns:
        dict: Normalized payload with expanded paths.
    """

    normalized = dict(payload)
    if "path" in normalized:
        normalized["path"] = Path(normalized["path"]).expanduser().resolve()
    return normalized

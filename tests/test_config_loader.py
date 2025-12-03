from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from kandidate.models import AppConfig
from kandidate.utils.config_loader import AppConfigFactory, load_config


def test_load_config_with_overrides(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
logging:
  level: WARNING
parser:
  encoding: utf-16
  chunk_size: 2048
repository:
  path: ./tmp/results.json
"""
    )
    monkeypatch.setenv("KANDIDATE_LOGGING__LEVEL", "DEBUG")
    merged = load_config(config_file, overrides={"parser": {"chunk_size": 1024}})
    assert merged.logging.level == "DEBUG"
    assert merged.parser.encoding == "utf-16"
    assert merged.parser.chunk_size == 1024
    assert merged.repository.path.exists() is False


def test_app_config_factory_uses_default(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("repository:\n  path: ./tmp/results.json\n")
    factory = AppConfigFactory(default_path=config_file)
    config = factory.build()
    assert isinstance(config, AppConfig)
    assert str(config.repository.path).endswith("results.json")

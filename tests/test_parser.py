from __future__ import annotations

import json
from pathlib import Path

import pytest

from kandidate.models import ParserConfig
from kandidate.services import DocumentParser


@pytest.fixture()
def parser() -> DocumentParser:
    return DocumentParser(ParserConfig())


def test_parse_path_text(tmp_path: Path, parser: DocumentParser) -> None:
    sample = tmp_path / "resume.txt"
    sample.write_text("Python FastAPI developer", encoding="utf-8")
    document = parser.parse_path(sample)
    assert document.name == "resume"
    assert "FastAPI" in document.text


def test_parse_path_json(tmp_path: Path, parser: DocumentParser) -> None:
    sample = tmp_path / "resume.json"
    sample.write_text(json.dumps({"name": "Jon", "text": "Experienced in Docker"}), encoding="utf-8")
    document = parser.parse_path(sample)
    assert document.name == "Jon"
    assert "Docker" in document.text


def test_parse_payload_validation(parser: DocumentParser) -> None:
    with pytest.raises(ValueError):
        parser.parse_payload({"name": "Test", "text": "  "})

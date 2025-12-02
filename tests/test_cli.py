from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from kandidate.cli import cli


def test_cli_run_command(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    repository_path = tmp_path / "results.json"
    config_path.write_text(f"repository:\n  path: {repository_path}\n")
    sample = tmp_path / "resume.txt"
    sample.write_text("Python FastAPI Docker", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["--config", str(config_path), "run", str(sample)])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["document"]["name"] == "resume"

"""Command-line entry points for the Kandidate toolkit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

import click

from kandidate.core import Pipeline
from kandidate.models import CandidateResult
from kandidate.utils.config_loader import AppConfigFactory
from kandidate.utils.logging import configure_logging

_config_factory = AppConfigFactory()


@click.group()
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--debug", is_flag=True, help="Enable verbose logging output")
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None, debug: bool) -> None:
    """Bootstrap configuration and share it with child commands."""

    overrides: dict[str, Any] = {}
    if debug:
        overrides = {"logging": {"level": "DEBUG"}}
    config = _config_factory.build(config_path=config_path, overrides=overrides)
    configure_logging(config.logging)
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def run(ctx: click.Context, input_path: Path) -> None:
    """Run the pipeline for ``input_path`` and print results as JSON."""

    config = ctx.obj["config"]
    pipeline = Pipeline(config)
    results: List[CandidateResult]
    if input_path.is_dir():
        results = pipeline.process_directory(input_path)
    elif input_path.suffix.lower() == ".json":
        payload = json.loads(input_path.read_text())
        documents = pipeline.parser.parse_payloads(payload if isinstance(payload, list) else [payload])
        results = pipeline.process_documents(documents)
    else:
        results = [pipeline.process_path(input_path)]
    click.echo(json.dumps([result.as_dict() for result in results], indent=2))


@cli.command(name="serve-api")
@click.option("--host", type=str)
@click.option("--port", type=int)
@click.pass_context
def serve_api(ctx: click.Context, host: str | None, port: int | None) -> None:
    """Launch the FastAPI server backed by the shared configuration."""

    from kandidate.services.api import create_app
    import uvicorn

    config = ctx.obj["config"]
    app = create_app(config)
    uvicorn.run(app, host=host or config.api.host, port=port or config.api.port, reload=config.api.reload)


def main() -> None:
    """Entrypoint used by ``python -m kandidate``."""

    cli()


if __name__ == "__main__":  # pragma: no cover
    main()

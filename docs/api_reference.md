# API Reference

## `kandidate.core`
- `Pipeline.process_path(path)` — parse, analyze, and persist a single file path, returning a `CandidateResult`.
- `Pipeline.process_directory(directory)` — bulk process every supported file inside the directory.
- `Pipeline.process_documents(documents)` — accept already parsed documents (from API or JSON) and return persisted results.

## `kandidate.services`
- `DocumentParser.parse_path(path)` — convert plaintext/JSON files into `CandidateDocument` objects.
- `DocumentParser.parse_payload(payload)` — validate dictionaries coming from API calls.
- `CandidateAnalyzer.analyze(document)` — calculate keyword coverage, length metrics, and quality warnings, producing `CandidateAnalysis`.
- `ResultRepository.save_result(result)` — append results to the configured repository backend.
- `create_app(config=None)` — build a FastAPI application that exposes `/health` and `/candidates` endpoints.

## `kandidate.utils`
- `load_config(path=None, overrides=None)` — merge YAML/JSON configuration with environment variables and produce an `AppConfig` instance.
- `configure_logging(config)` — configure the global logging backend, optionally emitting JSON logs.
- `get_logger(name)` — fetch a module-level logger that inherits global settings.

## CLI Commands
- `kandidate run <input_path>` — run the ingestion pipeline on files or JSON payloads and print structured JSON to STDOUT.
- `kandidate serve-api` — launch the FastAPI service (supports `--host`, `--port`, `--config`, `--debug`).

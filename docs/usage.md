# Usage Guide

## CLI

Process a directory or JSON payload:

```bash
kandidate run samples/
kandidate run payload.json --debug
```

## FastAPI

Start the API and submit a payload:

```bash
kandidate serve-api --host 0.0.0.0 --port 9000
```

```bash
curl -X POST http://localhost:9000/candidates \
  -H "Content-Type: application/json" \
  -d '{"name": "Amina", "text": "Experienced in Python and FastAPI"}'
```

Retrieve stored results:

```bash
curl http://localhost:9000/candidates
```

## Docker Compose

```bash
docker compose up --build
curl http://localhost:8000/health
```

## Configuration Overrides

All configuration values live in `config/default.yaml`. Override them with environment variables (`KANDIDATE_LOGGING__LEVEL=DEBUG`) or pass `--config` to the CLI.

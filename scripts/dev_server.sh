#!/usr/bin/env bash
set -euo pipefail
uvicorn kandidate.services.api:create_app --factory --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --reload

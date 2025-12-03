#!/usr/bin/env bash
set -euo pipefail
black kandidate tests
isort kandidate tests

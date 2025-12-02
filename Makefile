.PHONY: install format lint test coverage dev docker-build docker-run

install:
	pip install -e .[dev]
	pre-commit install

format:
	./scripts/format.sh

lint:
	black --check kandidate tests
	isort --check-only kandidate tests
	flake8 kandidate tests
	mypy kandidate

test:
	pytest

coverage:
	pytest --cov=kandidate --cov-report=xml

dev:
	uvicorn kandidate.services.api:create_app --factory --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t kandidate:latest .

docker-run:
	docker compose up --build

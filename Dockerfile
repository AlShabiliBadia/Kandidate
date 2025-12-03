FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md LICENSE /app/
RUN pip install --upgrade pip && pip install -e .

COPY . /app

CMD ["uvicorn", "kandidate.services.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

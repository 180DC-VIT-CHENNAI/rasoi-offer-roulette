FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .
COPY data ./data
COPY Makefile ./
COPY ui ./ui

CMD ["python", "-m", "rasoi.cli", "submit", "--data", "data/public", "--out", "submission/"]

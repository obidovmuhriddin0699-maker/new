# Development image for the FastAPI backend and Celery worker.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY backend/pyproject.toml ./
RUN mkdir app && touch app/__init__.py \
    && pip install ".[dev]" \
    && rm -rf app

COPY backend/ ./

# /var/lib/muxriddin/media: uploaded post media (MEDIA_ROOT), kept outside the source
# bind mount on a named volume so the non-root user can write to it.
RUN useradd --create-home --uid 1000 appuser && mkdir -p /app/data /var/lib/muxriddin/media \
    && chown -R appuser /app /var/lib/muxriddin
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

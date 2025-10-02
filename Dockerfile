# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# No system deps needed; using manylinux wheels and psycopg2-binary

# Install Python deps first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project (excluding what's in .dockerignore)
COPY . /app

# Create non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
RUN chmod +x /app/entrypoint.sh
USER appuser

EXPOSE 8000

# Entrypoint handles migrations and static files
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "practice_journal.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]



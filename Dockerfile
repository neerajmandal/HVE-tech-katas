# syntax=docker/dockerfile:1.7

# --- Stage 1: Build Tailwind CSS ---
FROM node:22-bullseye-slim AS frontend
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY tailwind.config.js ./
COPY static/ ./static/
COPY templates/ ./templates/
COPY apps/ ./apps/

RUN npx @tailwindcss/cli \
    -i ./static/input.css \
    -o ./static/output.css \
    --config ./tailwind.config.js \
    --minify

# --- Stage 2: Python application ---
FROM python:3.12-slim-bookworm AS backend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System dependencies (Postgres client libs for psycopg2-binary runtime + build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpq-dev \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure project virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies (locked, no dev deps)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application source
COPY . .

# Bring in the built Tailwind CSS from the frontend stage
COPY --from=frontend /app/static/output.css ./static/output.css

# Collect static files for WhiteNoise / Django to serve
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000

# Render injects $PORT. Run migrations then start Gunicorn.
CMD ["sh", "-c", "uv run python manage.py migrate --noinput && uv run gunicorn StingrayHealthPortal.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60 --access-logfile - --error-logfile -"]

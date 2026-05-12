# Use Node.js for building TailwindCSS
FROM node:22-bullseye-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY tailwind.config.js ./
COPY static/input.css static/
COPY templates/ ./templates/
COPY apps/ ./apps/
RUN npx @tailwindcss/cli -i ./static/input.css -o ./static/output.css --config ./tailwind.config.js --minify

# Use Python for the main application
FROM python:3.12-slim-bookworm AS backend
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy dependency files and install with uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Copy built CSS from frontend stage
COPY --from=frontend /app/static/output.css ./static/output.css

# Pre-compress assets (django-compressor offline mode) then collect static files
ENV DEBUG=False
RUN python manage.py compress --force \
    && python manage.py collectstatic --noinput

# Make runtime script executable
RUN chmod +x start.sh

EXPOSE 8000
CMD ["./start.sh"]

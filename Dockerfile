# RetailPulse - Production Container Image
FROM python:3.11-slim-bookworm

# System dependencies for MySQL connector and cloud SDK utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source and configurations
COPY src/ ./src/
COPY config/ ./config/
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy data (including embedded SQLite demo database), scripts, SQL, dbt, and dashboard
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY sql/ ./sql/
COPY database/ ./database/
COPY dbt/ ./dbt/
COPY dashboard/ ./dashboard/

# Default port for web services
ENV PORT=8000
ENV USE_SQLITE="true"
EXPOSE 8000

# Default entrypoint runs the FastAPI REST API (can be overridden by Docker CLI or Render)
CMD ["sh", "-c", "uvicorn retailpulse.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


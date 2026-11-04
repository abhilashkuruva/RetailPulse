# RetailPulse - Production Container Image
FROM python:3.11-slim-bullseye

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

# Copy executable scripts, SQL definitions, dbt project, and dashboard
COPY scripts/ ./scripts/
COPY sql/ ./sql/
COPY database/ ./database/
COPY dbt/ ./dbt/
COPY dashboard/ ./dashboard/

# Default entrypoint runs the pipeline orchestrator
ENTRYPOINT ["python", "scripts/run_pipeline.py"]
CMD ["--mode", "full"]


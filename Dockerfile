FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY openenv_core_submission/server/requirements.txt ./requirements_server.txt
COPY requirements_local.txt ./requirements_local.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_server.txt && \
    pip install --no-cache-dir -r requirements_local.txt

# Copy application code
COPY openenv_core_submission/ ./openenv_core_submission/
COPY openenv/ ./openenv/
COPY dashboard/ ./dashboard/
COPY entrypoint.sh ./entrypoint.sh
COPY README.md ./README.md

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TASK_DIFFICULTY=medium

# Expose port 8000 for OpenEnv API and Dashboard
EXPOSE 8000

# Health check - check if Dashboard/API is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the dashboard app which now includes OpenEnv API endpoints
# This makes it compatible with both the validator (port 8000) and the interactive dashboard
CMD python -m uvicorn dashboard.app:app --host 0.0.0.0 --port 8000

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get-update && apt-get install -y --no-install-recommends \
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
COPY README.md ./README.md

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TASK_DIFFICULTY=medium

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/', timeout=5).status_code == 200 or exit(1)" || exit 1

# Start both servers: OpenEnv on 8000, Dashboard on 3000
CMD sh -c 'python -m uvicorn openenv_core_submission.server.app:app --host 0.0.0.0 --port 8000 &' && \
    sleep 2 && \
    python -m uvicorn dashboard.app:app --host 0.0.0.0 --port 3000

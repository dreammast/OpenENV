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

# Expose ports
EXPOSE 3000 8000

# Health check - check if Dashboard is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Run the entrypoint script which starts both servers
ENTRYPOINT ["./entrypoint.sh"]

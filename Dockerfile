FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY openenv_core_submission/ ./openenv_core_submission/
COPY openenv/ ./openenv/
COPY dashboard/ ./dashboard/

# Set environment variables
ENV TASK_DIFFICULTY=easy
ENV DASHBOARD_PORT=3000
ENV PORT=8000

# Expose ports
EXPOSE 8000 3000

# Run the application
CMD ["sh", "-c", "python -m openenv_core_submission.server.app & python dashboard/app.py"]

#!/bin/bash
# Docker entrypoint script to start both OpenEnv server and Dashboard

echo "🚀 Starting OpenEnv servers..."

# Start OpenEnv API server on port 8000 in background
echo "📡 Starting OpenEnv API server on port 8000..."
python -m uvicorn openenv_core_submission.server.app:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Give the API server time to start
sleep 3

# Start Dashboard on port 3000 in foreground
echo "🎨 Starting Dashboard on port 3000..."
python -m uvicorn dashboard.app:app --host 0.0.0.0 --port 3000

# Keep the script running
wait $SERVER_PID

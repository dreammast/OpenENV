"""
📊 OpenEnv Dashboard Server
Serves both the monitoring dashboard and OpenEnv API endpoints.
Runs on port 8000 (for validator compatibility).
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import requests as req

# Import OpenEnv core components
from openenv.core.env_server.http_server import HTTPEnvServer
from openenv_core_submission.models import EducationAction, EducationObservation
from openenv_core_submission.server.easy_env import EasyQuizTutorEnvironment
from openenv_core_submission.server.medium_env import MediumEssayCoachEnvironment
from openenv_core_submission.server.hard_env import HardDropoutRiskEnvironment

# FastAPI app
app = FastAPI(
    title="OpenEnv Education Platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc"
)

# ─ OpenEnv Server Setup ────────────────────────────────────────────────────

# Determine which environment to load based on env var
task_type = os.environ.get("TASK_DIFFICULTY", "medium").lower()

TASK_MAP = {
    "easy": EasyQuizTutorEnvironment,
    "medium": MediumEssayCoachEnvironment,
    "hard": HardDropoutRiskEnvironment
}

env_class = TASK_MAP.get(task_type, MediumEssayCoachEnvironment)

# Create HTTPEnvServer and register routes
server = HTTPEnvServer(
    env_class,
    EducationAction,
    EducationObservation,
    max_concurrent_envs=10,
)

# Register OpenEnv API routes (for validator & direct API access)
server.register_routes(app)

# ─ Dashboard Routes ────────────────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard HTML"""
    html_path = DASHBOARD_DIR / "index.html"
    try:
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>404 - Dashboard HTML Not Found</h1><p>Missing: index.html</p>",
            status_code=404
        )

# ─ Dashboard API Proxy Routes ──────────────────────────────────────────────

# For backward compatibility with dashboard UI proxying
EASY_URL = os.getenv("EASY_ENV_URL", "http://localhost:8000")
MEDIUM_URL = os.getenv("MEDIUM_ENV_URL", "http://localhost:8000")
HARD_URL = os.getenv("HARD_ENV_URL", "http://localhost:8000")

ENV_URLS = {"easy": EASY_URL, "medium": MEDIUM_URL, "hard": HARD_URL}


@app.api_route("/api/{env}/{path:path}", methods=["GET", "POST"])
async def proxy(env: str, path: str, request: Request):
    """Proxy dashboard requests to environment servers (backward compat)"""
    base_url = ENV_URLS.get(env)
    if not base_url:
        return JSONResponse(content={"error": f"Unknown env: {env}"}, status_code=404)
    try:
        body = await request.body()
        url = f"{base_url}/{path}"
        if request.method == "POST":
            r = req.post(url, data=body, headers={"Content-Type": "application/json"}, timeout=10)


# ─ Health Check ────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OpenEnv", "task": task_type}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", "8000"))  # Default to 8000 for validator
    print("🎨 OpenEnv Dashboard: http://localhost:{}".format(port))
    print("📚 API Docs: http://localhost:{}/docs".format(port))
    print("📡 Task: {} environment".format(task_type))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

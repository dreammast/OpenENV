"""
📊 OpenEnv Dashboard Server
Serves both the monitoring dashboard and OpenEnv API endpoints.
Runs on port 3000.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import requests as req

# Import OpenEnv server components
from openenv_core_submission.server.app import server as openenv_server
from openenv_core_submission.models import EducationAction, EducationObservation

app = FastAPI(
    title="OpenEnv Education Platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc"
)

# ─ OpenEnv API Routes (direct endpoints for validator) ──────────────────────
# Register OpenEnv routes directly to support validator checks
openenv_server.register_routes(app)

# ─ Dashboard Integration ──────────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent

EASY_URL = os.getenv("EASY_ENV_URL", "http://localhost:8000")
MEDIUM_URL = os.getenv("MEDIUM_ENV_URL", "http://localhost:8000")
HARD_URL = os.getenv("HARD_URL", "http://localhost:8000")

ENV_URLS = {"easy": EASY_URL, "medium": MEDIUM_URL, "hard": HARD_URL}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard HTML"""
    html_path = DASHBOARD_DIR / "index.html"
    try:
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard Not Found</h1>", status_code=404)


# ─ Dashboard API Proxy Routes ──────────────────────────────────────────────

@app.api_route("/api/{env}/{path:path}", methods=["GET", "POST"])
async def proxy(env: str, path: str, request: Request):
    """Proxy dashboard requests to local environment servers"""
    base_url = ENV_URLS.get(env)
    if not base_url:
        return JSONResponse(content={"error": f"Unknown env: {env}"}, status_code=404)
    try:
        body = await request.body()
        url = f"{base_url}/{path}"
        if request.method == "POST":
            r = req.post(url, data=body, headers={"Content-Type": "application/json"}, timeout=10)
        else:
            r = req.get(url, timeout=10)
        return JSONResponse(content=r.json(), status_code=r.status_code)
    except req.ConnectionError:
        return JSONResponse(
            content={"error": f"{env.title()} env server not running on {base_url}"},
            status_code=503,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OpenEnv Dashboard"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", "3000"))
    print("🎨 Dashboard: http://localhost:{}".format(port))
    print("📚 API Docs: http://localhost:{}/docs".format(port))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

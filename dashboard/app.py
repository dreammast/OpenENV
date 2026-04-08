"""
📊 OpenEnv Dashboard Server
Serves the monitoring dashboard and proxies requests to env servers.
Runs on port 3000.
"""

import os
import requests as req
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="OpenEnv Dashboard", version="1.0.0")

EASY_URL = os.getenv("EASY_ENV_URL", "http://localhost:8000")
MEDIUM_URL = os.getenv("MEDIUM_ENV_URL", "http://localhost:8000")
HARD_URL = os.getenv("HARD_ENV_URL", "http://localhost:8000")

DASHBOARD_DIR = Path(__file__).parent

ENV_URLS = {"easy": EASY_URL, "medium": MEDIUM_URL, "hard": HARD_URL}


# ── Generic proxy ─────────────────────────────────────────────────────────────

@app.api_route("/api/{env}/{path:path}", methods=["GET", "POST"])
async def proxy(env: str, path: str, request: Request):
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


# ── Serve dashboard HTML ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_path = DASHBOARD_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", "5500"))
    print("📊 Dashboard: http://localhost:{}".format(port))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

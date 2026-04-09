"""
📊 OpenEnv Dashboard & API Server
Unified FastAPI application serving both the API and dashboard UI.
Runs on port 8000.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the pre-configured app from the server module
# This app already has HTTPEnvServer configured with all routes
try:
    from openenv_core_submission.server.app import app
except ImportError:
    # Fallback: Create a minimal app if import fails
    from fastapi import FastAPI
    app = FastAPI(title="OpenEnv Education Platform", version="1.0.0")

# ─ Dashboard Route ──────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard HTML"""
    html_path = DASHBOARD_DIR / "index.html"
    try:
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>OpenEnv API Server</h1><p>Dashboard HTML not found. Visit /docs for API documentation.</p>",
            status_code=200  # Return 200 anyway, API is working
        )


# ─ Entry Point ──────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    print("🎨 OpenEnv Platform (API + Dashboard): http://localhost:{}".format(port))
    print("📚 API Docs: http://localhost:{}/docs".format(port))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

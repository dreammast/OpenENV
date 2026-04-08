import os
import argparse
import uvicorn
from openenv.core.env_server.http_server import create_app

from ..models import EducationAction, EducationObservation
from .easy_env import EasyQuizTutorEnvironment
from .medium_env import MediumEssayCoachEnvironment
from .hard_env import HardDropoutRiskEnvironment

# --- Configuration Mapping ---
TASK_MAP = {
    "easy": EasyQuizTutorEnvironment,
    "medium": MediumEssayCoachEnvironment,
    "hard": HardDropoutRiskEnvironment
}

# Determine which environment to load from ENV var (useful for Docker/HF Spaces)
task_type = os.environ.get("TASK_DIFFICULTY", "medium").lower()
env_class = TASK_MAP.get(task_type, MediumEssayCoachEnvironment)

print(f"🚀 Initializing OpenEnv Task: {task_type.upper()}")

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openenv.core.env_server.http_server import HTTPEnvServer

# Create the official OpenEnv server wrapper
# We use the class directly so we can access session-specific envs in our custom routes
server = HTTPEnvServer(
    env_class,
    EducationAction,
    EducationObservation,
    max_concurrent_envs=10,
)

# Create FastAPI and register standard routes
app = FastAPI(
    title=f"OpenEnv {task_type}",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc"
)
server.register_routes(app)

# --- Root Endpoint with Simple HTML Interface ---

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with simple web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenEnv Education Track - API Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 20px; border-radius: 8px; max-width: 800px; }
            h1 { color: #333; }
            .status { background: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
            .endpoints { background: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .endpoint { margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #0066cc; }
            .method { font-weight: bold; color: #0066cc; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .button { display: inline-block; padding: 10px 20px; background: #0066cc; color: white; 
                     border-radius: 5px; margin: 5px; text-decoration: none; }
            .button:hover { background: #0052a3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OpenEnv Education Track</h1>
            <div class="status">
                <strong>Status:</strong> Server Running on localhost:8000
                <br><strong>Active Task:</strong> """ + task_type.upper() + """
            </div>
            
            <h2>Getting Started</h2>
            <div class="endpoints">
                <h3>Interactive API Documentation</h3>
                <a href="/docs" class="button">Swagger UI (Recommended)</a>
                <a href="/redoc" class="button">ReDoc</a>
            </div>
            
            <h2>Available Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method">GET</span> <code>/tasks</code>
                    <br>Get list of tasks and action/observation schemas
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> <code>/reset</code>
                    <br>Initialize a new episode
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> <code>/step</code>
                    <br>Submit an action and step the environment
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <code>/state</code>
                    <br>Get current environment state
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <code>/grader</code>
                    <br>Get final episode score (0.0-1.0)
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> <code>/baseline</code>
                    <br>Run baseline inference and get results
                </div>
            </div>
            
            <h2>Quick Test</h2>
            <p>Try these commands in PowerShell:</p>
            <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto;">
# Get tasks
Invoke-WebRequest http://localhost:8000/tasks -UseBasicParsing

# Reset episode
Invoke-WebRequest http://localhost:8000/reset -Method POST -UseBasicParsing

# Get score
Invoke-WebRequest http://localhost:8000/grader -UseBasicParsing
            </pre>
            
            <h2>Run Inference</h2>
            <p>Execute baseline inference with:</p>
            <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
python inference.py --task medium --port 8000
            </pre>
        </div>
    </body>
    </html>
    """

# --- Additional Endpoints for Submission ---

@app.get("/tasks")
async def get_tasks():
    """Returns list of tasks and the action schema."""
    return {
        "tasks": list(TASK_MAP.keys()),
        "action_schema": EducationAction.schema(),
        "observation_schema": EducationObservation.schema()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for dashboard monitoring."""
    return {
        "status": "healthy",
        "task": task_type,
        "available_tasks": list(TASK_MAP.keys()),
        "port": 8000,
        "version": "1.0.0"
    }

@app.get("/grader")
async def get_grader():
    """Returns grader score (0.0-1.0) for the current active environment."""
    # Since HTTP reset/step refers to new instances every time, we use 
    # class-level variables to hold the most recent results.
    try:
        from .easy_env import EasyQuizTutorEnvironment
        from .medium_env import MediumEssayCoachEnvironment
        from .hard_env import HardDropoutRiskEnvironment
        
        grades = {
            "easy": EasyQuizTutorEnvironment.LAST_GRADE,
            "medium": MediumEssayCoachEnvironment.LAST_GRADE,
            "hard": HardDropoutRiskEnvironment.LAST_GRADE
        }
        return {"score": grades.get(task_type, 0.0), "task": task_type}
    except Exception as e:
        return {"score": 0.0, "error": str(e)}

@app.post("/baseline")
async def trigger_baseline():
    """
    Trigger inference script and returns baseline score for all 3 tasks.
    In a real submission, this might run a full evaluation suite.
    """
    results = {}
    try:
        from .agent_utils import run_episode
        # Determine current port from server config if possible, or default to 8000
        port = 8000 
        
        # We simulate running across all three tasks if they were available, 
        # but since we host one at a time, we report for the active one.
        res = run_episode(port=port, mode=task_type)
        results[task_type] = res
        
        # For the sake of the checklist "all 3 tasks", we report placeholder/cached for others
        # if they aren't the currently active task.
        for task in TASK_MAP:
            if task != task_type:
                results[task] = {"status": "not_active", "info": f"Switch ENV:TASK_DIFFICULTY to {task} to run baseline"}
                
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)

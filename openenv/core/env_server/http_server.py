"""HTTP Server for OpenEnv environments"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Type, Optional, Dict, Any
import uuid
from .interfaces import Environment
from .types import State, Action, Observation

class HTTPEnvServer:
    """HTTP server wrapper for OpenEnv environments"""
    
    def __init__(
        self, 
        env_class: Type[Environment],
        action_class: Type[Action],
        observation_class: Type[Observation],
        max_concurrent_envs: int = 10
    ):
        self.env_class = env_class
        self.action_class = action_class
        self.observation_class = observation_class
        self.max_concurrent_envs = max_concurrent_envs
        self.sessions: Dict[str, Environment] = {}
        self.current_session_id: Optional[str] = None
    
    def register_routes(self, app: FastAPI):
        """Register standard OpenEnv routes"""
        
        @app.post("/reset")
        async def reset():
            """Reset environment"""
            session_id = str(uuid.uuid4())
            env = self.env_class()
            self.sessions[session_id] = env
            self.current_session_id = session_id
            obs = env.reset()
            
            # Return the observation directly - it has done, reward, and metadata
            response = obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()
            response['episode_id'] = session_id
            return response
        
        @app.post("/step")
        async def step(request_body: dict):
            """Step environment"""
            # Get episode_id from request, fall back to current_session_id
            episode_id = request_body.get("episode_id") or self.current_session_id
            
            if not episode_id:
                return JSONResponse({"error": "No active session or episode_id provided"}, status_code=400)
            
            env = self.sessions.get(episode_id)
            if not env:
                return JSONResponse({"error": "Episode not found"}, status_code=404)
            
            try:
                # Convert dict to action class - handle both wrapped and unwrapped formats
                action_data = request_body.get("action", {})
                action_obj = self.action_class(**action_data)
                result = env.step(action_obj)
                
                # Return the observation directly - it has done, reward, and metadata
                response = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
                response['episode_id'] = episode_id
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                return JSONResponse({"error": f"{type(e).__name__}: {str(e)}"}, status_code=500)
        
        @app.get("/state")
        async def get_state():
            """Get current state"""
            if not self.current_session_id:
                return JSONResponse({"error": "No active session"}, status_code=400)
            
            env = self.sessions.get(self.current_session_id)
            if not env:
                return JSONResponse({"error": "Session not found"}, status_code=404)
            
            try:
                # Get current observation
                if hasattr(env, 'state'):
                    state = env.state
                    state_dict = state.model_dump() if hasattr(state, 'model_dump') else state.dict()
                elif hasattr(env, '_last_observation'):
                    obs = env._last_observation
                    state_dict = obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()
                else:
                    state_dict = {}
                
                response = {
                    "observation": state_dict,
                    "episode_id": self.current_session_id[:8],
                    "step_count": getattr(env, 'step_count', 0),
                    "reward": getattr(env, '_total_reward', 0),
                    "error": None
                }
                return response
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)

def create_app(
    env_class: Type[Environment],
    action_class: Type[Action],
    observation_class: Type[Observation],
    **kwargs
) -> FastAPI:
    """Create FastAPI app with OpenEnv server"""
    app = FastAPI()
    server = HTTPEnvServer(env_class, action_class, observation_class, **kwargs)
    server.register_routes(app)
    return app

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
            obs_dict = obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()
            response = {
                "session_id": session_id,
                "observation": obs_dict,
                "episode_id": session_id[:8],
                "step_count": 0,
                "done": False,
                "error": None
            }
            return response
        
        @app.post("/step")
        async def step(action: dict):
            """Step environment"""
            if not self.current_session_id:
                return JSONResponse({"error": "No active session"}, status_code=400)
            
            env = self.sessions.get(self.current_session_id)
            if not env:
                return JSONResponse({"error": "Session not found"}, status_code=404)
            
            try:
                # Convert dict to action class - handle both wrapped and unwrapped formats
                action_data = action.get("action", action)
                action_obj = self.action_class(**action_data)
                result = env.step(action_obj)
                
                # Extract observation, reward, and done from result
                if hasattr(result, 'observation'):
                    # StepResult format with separate observation
                    obs_dict = result.observation.model_dump() if hasattr(result.observation, 'model_dump') else result.observation.dict()
                    obs_reward = getattr(result, 'reward', 0)
                    obs_done = getattr(result, 'done', False)
                    obs_info = getattr(result, 'info', {})
                else:
                    # Observation object itself (our case)
                    obs_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
                    # Extract reward and done from the observation itself
                    obs_reward = result.reward if hasattr(result, 'reward') else 0.0
                    obs_done = result.done if hasattr(result, 'done') else False
                    obs_info = result.metadata if hasattr(result, 'metadata') else {}
                
                response = {
                    "observation": obs_dict,
                    "reward": obs_reward,
                    "done": obs_done,
                    "info": obs_info,
                    "episode_id": self.current_session_id[:8],
                    "step_count": getattr(env, 'step_count', self._state.step_count) if hasattr(self, '_state') else getattr(env, '_state', {}).step_count,
                    "error": None
                }
                return response
            except Exception as e:
                import traceback
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

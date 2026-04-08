"""Core types for OpenEnv environments"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import uuid

class State(BaseModel):
    """Environment state"""
    episode_id: str = None
    step_count: int = 0
    
    def __init__(self, **data):
        if 'episode_id' not in data:
            data['episode_id'] = str(uuid.uuid4())
        super().__init__(**data)

class Action(BaseModel):
    """Base action class"""
    pass

class Observation(BaseModel):
    """Base observation class"""
    reward: float = 0.0
    done: bool = False
    metadata: Optional[Dict[str, Any]] = {}

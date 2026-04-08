"""OpenEnv Client Types"""
from pydantic import BaseModel
from typing import Optional, Dict, Any

class StepResult(BaseModel):
    """Result of a step"""
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Optional[Dict[str, Any]] = {}

"""OpenEnv Environment Client"""
from __future__ import annotations
from typing import Dict, Any, Optional, TypeVar, Generic
from .client_types import StepResult

T_Action = TypeVar('T_Action')
T_Observation = TypeVar('T_Observation')
T_State = TypeVar('T_State')

class EnvClient(Generic[T_Action, T_Observation, T_State]):
    """Client for connecting to OpenEnv environments"""
    
    def __init__(self, url: str = "http://localhost:8000"):
        self.url = url
    
    def reset(self) -> T_Observation:
        """Reset environment"""
        pass
    
    def step(self, action: T_Action) -> StepResult:
        """Step environment"""
        pass

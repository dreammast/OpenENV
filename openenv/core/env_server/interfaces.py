"""Environment interface"""
from abc import ABC, abstractmethod
from typing import Any
from .types import State, Action, Observation

class Environment(ABC):
    """Base environment interface"""
    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    
    @property
    @abstractmethod
    def state(self) -> State:
        """Return current state"""
        pass
    
    @abstractmethod
    def reset(self) -> Observation:
        """Reset environment"""
        pass
    
    @abstractmethod
    def step(self, action: Action) -> Observation:
        """Take one step"""
        pass

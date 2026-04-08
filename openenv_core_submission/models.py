# Copyright (c) Meta Platforms, Inc. and affiliates.
from openenv.core.env_server.types import Action, Observation
from pydantic import Field, BaseModel
from typing import Dict, List, Optional

# --- Shared Models ---

class StudentProfile(BaseModel):
    topic_scores: Optional[Dict[str, float]] = None
    last_difficulty: Optional[Dict[str, int]] = None
    quality_scores: Optional[Dict[str, float]] = None
    overall_grade: Optional[str] = None
    weakest_area: Optional[str] = None
    risk_factors: Optional[Dict[str, float]] = None
    dropout_risk: Optional[float] = None
    gpa: Optional[float] = None
    attendance_rate: Optional[int] = None
    engagement_score: Optional[int] = None

# --- Action Models ---

class EducationAction(Action):
    # Easy Task (Quiz)
    topic: Optional[str] = Field(None, description="Topic for the quiz")
    difficulty: Optional[int] = Field(None, description="Difficulty level (1-4)")
    question_text: Optional[str] = Field(None, description="The actual question text")

    # Medium Task (Essay)
    feedback_type: Optional[str] = Field(None, description="Type of feedback provided")
    focus_area: Optional[str] = Field(None, description="Focus area for revision")
    specificity: Optional[int] = Field(None, description="Specificity level (1-3)")

    # Hard Task (Dropout)
    intervention_type: Optional[str] = Field(None, description="Type of intervention")
    intensity: Optional[int] = Field(None, description="Intensity of intervention (1-3)")
    rationale: Optional[str] = Field(None, description="Reason for the intervention")

# --- Observation Models ---

class EducationObservation(Observation):
    student_profile: StudentProfile = Field(..., description="Current student state or profile")
    question_history: Optional[List[dict]] = None
    feedback_history: Optional[List[str]] = None
    turns_remaining: Optional[int] = None
    revisions_remaining: Optional[int] = None
    week: Optional[int] = None
    resource_cost: Optional[float] = None
    intervention_effective: Optional[bool] = None
    
    # Standard OpenEnv fields (inherited from Observation)
    # reward: float
    # done: bool

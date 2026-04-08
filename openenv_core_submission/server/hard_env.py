import random
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from ..models import EducationAction, EducationObservation, StudentProfile

INTERVENTION_TARGETS = {
    "academic_tutoring": "academic_struggle",
    "financial_aid_review": "financial_stress",
    "mental_health_referral": "mental_health",
    "peer_mentorship": "social_isolation",
    "study_group": "academic_struggle",
    "career_guidance": "mental_health",
    "family_outreach": "social_isolation",
    "flexible_schedule": "attendance_decline",
}
INTENSITY_COSTS = {1: 0.05, 2: 0.15, 3: 0.30}
RISK_FACTORS = ["academic_struggle", "financial_stress", "social_isolation", "mental_health", "attendance_decline"]

class HardDropoutRiskEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.semester_weeks = 7
        self._init_session()

    def _init_session(self):
        self.root_cause = random.choice(RISK_FACTORS)
        self.risk_factors = {}
        for factor in RISK_FACTORS:
            if factor == self.root_cause:
                self.risk_factors[factor] = round(random.uniform(0.60, 0.90), 2)
            else:
                self.risk_factors[factor] = round(random.uniform(0.10, 0.50), 2)
        
        self.gpa = round(random.uniform(1.5, 3.0), 2)
        self.attendance_rate = random.randint(40, 75)
        self.engagement_score = random.randint(20, 55)
        self.outcome = "active"
        self.total_resource_cost = 0.0
        self.support_received = []
        self.intervention_effective = False
        self.dropout_risk = self._compute_risk()

    def _compute_risk(self) -> float:
        avg = sum(self.risk_factors.values()) / len(self.risk_factors)
        return round(min(0.99, max(0.05, avg + random.uniform(-0.05, 0.05))), 2)

    def reset(self) -> EducationObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._init_session()
        return self._make_observation(reward=0.0, done=False)

    def step(self, action: EducationAction) -> EducationObservation:
        self._state.step_count += 1
        
        itype = action.intervention_type or "academic_tutoring"
        intensity = max(1, min(3, action.intensity or 2))
        cost = INTENSITY_COSTS.get(intensity, 0.15)
        self.total_resource_cost += cost
        self.support_received.append(itype)

        target_factor = INTERVENTION_TARGETS.get(itype, "academic_struggle")
        current_severity = self.risk_factors.get(target_factor, 0.3)
        is_root = (target_factor == self.root_cause)
        self.intervention_effective = is_root

        reduction = intensity * (random.uniform(0.06, 0.14) if is_root else random.uniform(0.01, 0.04))
        self.risk_factors[target_factor] = round(max(0.02, current_severity - reduction), 3)

        for factor in RISK_FACTORS:
            if factor != target_factor:
                self.risk_factors[factor] = round(min(0.99, max(0.02, self.risk_factors[factor] + random.uniform(-0.02, 0.04))), 3)

        old_dropout = self.dropout_risk
        self.dropout_risk = self._compute_risk()

        if self.risk_factors.get("academic_struggle", 0.5) < 0.3:
            self.gpa = round(min(4.0, self.gpa + random.uniform(0.05, 0.15)), 2)
        if self.risk_factors.get("attendance_decline", 0.5) < 0.3:
            self.attendance_rate = min(100, self.attendance_rate + random.randint(2, 8))
        self.engagement_score = min(100, max(0, self.engagement_score + random.randint(-3, 7)))

        if random.random() < self.dropout_risk * 0.08:
            self.outcome = "dropped_out"

        if self._state.step_count >= self.semester_weeks:
            if self.outcome == "active":
                self.outcome = "persisted" if self.dropout_risk < 0.5 else "dropped_out"

        reward = (old_dropout - self.dropout_risk) * 2.0 - cost * 0.5
        if self.intervention_effective: reward += 0.15
        if self.outcome == "persisted": reward += 1.0
        elif self.outcome == "dropped_out": reward -= 0.5

        done = self.outcome != "active" or self._state.step_count >= self.semester_weeks
        return self._make_observation(reward=round(reward, 4), done=done)

    def _make_observation(self, reward: float, done: bool) -> EducationObservation:
        profile = StudentProfile(
            risk_factors=dict(self.risk_factors),
            dropout_risk=self.dropout_risk,
            gpa=self.gpa,
            attendance_rate=self.attendance_rate,
            engagement_score=self.engagement_score
        )
        return EducationObservation(
            student_profile=profile,
            week=self._state.step_count,
            resource_cost=self.total_resource_cost,
            intervention_effective=self.intervention_effective,
            reward=reward,
            done=done,
            metadata={"step": self._state.step_count, "outcome": self.outcome}
        )

    @property
    def state(self) -> State:
        return self._state

    LAST_GRADE = 0.0

    def grade(self) -> float:
        """Returns the final episode score (0.0-1.0) based on student outcome and risk reduction."""
        if self.outcome == "persisted":
            score = 1.0
        elif self.outcome == "dropped_out":
            score = 0.0
        else:
            # If still active (episode not finished)
            score = round(float(1.0 - self.dropout_risk), 3)
        
        HardDropoutRiskEnvironment.LAST_GRADE = score
        return score

import random
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from ..models import EducationAction, EducationObservation, StudentProfile

QUALITY_DIMENSIONS = ["structure", "grammar", "content", "creativity", "coherence"]
FEEDBACK_TARGETS = {
    "structural_reorganize": ["structure"],
    "grammar_correction": ["grammar"],
    "content_deepening": ["content"],
    "creative_suggestion": ["creativity"],
    "coherence_linking": ["coherence"],
    "thesis_strengthening": ["structure", "content"],
    "evidence_addition": ["content", "coherence"],
    "style_refinement": ["creativity", "grammar"],
}

class MediumEssayCoachEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.max_revisions = 5
        self._init_session()

    def _init_session(self):
        self.quality = {dim: round(random.uniform(0.15, 0.45), 3) for dim in QUALITY_DIMENSIONS}
        self.weak_spot = random.choice(QUALITY_DIMENSIONS)
        self.quality[self.weak_spot] = round(random.uniform(0.05, 0.20), 3)
        self.receptivity = random.uniform(0.5, 0.9)
        self.self_correction = random.uniform(0.02, 0.08)
        self.stubbornness = random.choice(QUALITY_DIMENSIONS)
        self.feedback_history = []
        self.initial_quality = dict(self.quality)

    def _get_grade(self):
        avg = sum(self.quality.values()) / len(QUALITY_DIMENSIONS)
        if avg >= 0.8: return "A"
        if avg >= 0.65: return "B"
        if avg >= 0.5: return "C"
        if avg >= 0.35: return "D"
        return "F"

    def reset(self) -> EducationObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._init_session()
        return self._make_observation(reward=0.0, done=False)

    def step(self, action: EducationAction) -> EducationObservation:
        self._state.step_count += 1
        
        ftype = action.feedback_type or "grammar_correction"
        specificity = action.specificity or 2
        
        targets = FEEDBACK_TARGETS.get(ftype, ["grammar"])
        old_avg = sum(self.quality.values()) / len(QUALITY_DIMENSIONS)
        self.feedback_history.append(ftype)

        for dim in QUALITY_DIMENSIONS:
            if dim in targets:
                base_gain = self.receptivity * specificity * 0.06
                if dim == self.weak_spot: base_gain *= 1.5
                repeat_count = self.feedback_history.count(ftype)
                diminish = max(0.3, 1.0 - repeat_count * 0.15)
                base_gain *= diminish
                if dim == self.stubbornness: base_gain *= 0.4
                gain = base_gain + random.uniform(-0.02, 0.03)
                self.quality[dim] = min(1.0, round(self.quality[dim] + gain, 4))
            else:
                drift = self.self_correction + random.uniform(-0.01, 0.02)
                self.quality[dim] = min(1.0, max(0.01, round(self.quality[dim] + drift, 4)))

        new_avg = sum(self.quality.values()) / len(QUALITY_DIMENSIONS)
        reward = (new_avg - old_avg) * 5.0
        
        # Penalties/Bonuses
        weakest_dim = min(self.quality, key=self.quality.get)
        if any(d in targets for d in [weakest_dim, self.weak_spot]): reward += 0.15
        if specificity == 1: reward -= 0.05
        if len(set(self.feedback_history)) >= 3: reward += 0.05

        done = self._state.step_count >= self.max_revisions
        if done:
            if new_avg > 0.7: reward += 0.5
            elif new_avg > 0.5: reward += 0.2
            if min(self.quality.values()) > 0.4: reward += 0.3

        return self._make_observation(reward=round(reward, 4), done=done)

    def _make_observation(self, reward: float, done: bool) -> EducationObservation:
        profile = StudentProfile(
            quality_scores=dict(self.quality),
            overall_grade=self._get_grade(),
            weakest_area=min(self.quality, key=self.quality.get)
        )
        return EducationObservation(
            student_profile=profile,
            feedback_history=list(self.feedback_history[-4:]),
            revisions_remaining=self.max_revisions - self._state.step_count,
            reward=reward,
            done=done,
            metadata={"step": self._state.step_count}
        )

    @property
    def state(self) -> State:
        return self._state

    LAST_GRADE = 0.0

    def grade(self) -> float:
        """Returns the final episode score (0.0-1.0) based on average essay quality."""
        if not self.quality:
            return MediumEssayCoachEnvironment.LAST_GRADE
        avg_quality = sum(self.quality.values()) / len(QUALITY_DIMENSIONS)
        score = round(float(avg_quality), 3)
        MediumEssayCoachEnvironment.LAST_GRADE = score
        return score

import random
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from ..models import EducationAction, EducationObservation, StudentProfile

TOPICS = ["fractions", "algebra", "geometry", "statistics"]

class EasyQuizTutorEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.max_turns = 8
        self._init_session()

    def _init_session(self):
        self.topic_scores = {t: round(random.uniform(0.05, 0.40), 2) for t in TOPICS}
        self.last_difficulty = {t: 1 for t in TOPICS}
        self.question_history = []
        self.learning_rate = random.uniform(0.08, 0.20)
        self.base_accuracy = random.uniform(0.35, 0.65)

    def reset(self) -> EducationObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._init_session()
        return self._make_observation(reward=0.0, done=False)

    def step(self, action: EducationAction) -> EducationObservation:
        self._state.step_count += 1
        
        topic = action.topic if action.topic in TOPICS else random.choice(TOPICS)
        difficulty = max(1, min(4, action.difficulty or 2))

        # Simulate answer
        mastery = self.topic_scores.get(topic, 0.2)
        difficulty_penalty = (difficulty - 1) * 0.15
        p_correct = min(0.95, max(0.05, self.base_accuracy + mastery - difficulty_penalty))
        correct = random.random() < p_correct

        # Compute reward
        reward = 0.0
        mastery_level = max(1, min(4, int(mastery * 4) + 1))
        if correct:
            reward += 0.3
            if difficulty in (mastery_level, mastery_level + 1): reward += 0.2
            elif difficulty < mastery_level: reward -= 0.1
        else:
            if difficulty > mastery_level + 1: reward -= 0.2
            else: reward += 0.05
        
        recent_topics = [h["topic"] for h in self.question_history[-2:]]
        if topic not in recent_topics: reward += 0.1

        # Update mastery
        if correct:
            gain = self.learning_rate * (0.5 + difficulty * 0.15)
            self.topic_scores[topic] = min(1.0, round(self.topic_scores[topic] + gain, 3))
        else:
            loss = 0.02 * difficulty
            self.topic_scores[topic] = max(0.0, round(self.topic_scores[topic] - loss, 3))
        self.last_difficulty[topic] = difficulty

        self.question_history.append({
            "topic": topic,
            "difficulty": difficulty,
            "correct": correct,
            "turn": self._state.step_count,
        })

        done = self._state.step_count >= self.max_turns
        if done:
            avg_mastery = sum(self.topic_scores.values()) / len(TOPICS)
            reward += round(avg_mastery * 0.5, 3)

        return self._make_observation(reward=round(reward, 3), done=done)

    def _make_observation(self, reward: float, done: bool) -> EducationObservation:
        profile = StudentProfile(
            topic_scores=dict(self.topic_scores),
            last_difficulty=dict(self.last_difficulty)
        )
        return EducationObservation(
            student_profile=profile,
            question_history=list(self.question_history[-5:]),
            turns_remaining=self.max_turns - self._state.step_count,
            reward=reward,
            done=done,
            metadata={"step": self._state.step_count}
        )

    @property
    def state(self) -> State:
        return self._state

    LAST_GRADE = 0.0

    def grade(self) -> float:
        """Returns the final episode score (0.0-1.0) based on average topic mastery."""
        if not self.topic_scores:
             return EasyQuizTutorEnvironment.LAST_GRADE
        avg_mastery = sum(self.topic_scores.values()) / len(TOPICS)
        score = round(float(avg_mastery), 3)
        EasyQuizTutorEnvironment.LAST_GRADE = score
        return score

from __future__ import annotations
from typing import List
from rzero.challenger import Challenger, EpisodeFeedback
from rzero.types import Task
import uuid, random

class RewriteChallengerTrainable(Challenger):
    """Toy example: learns a bias that shifts difficulty up/down based on reward."""
    def __init__(self) -> None:
        self.bias = 0.0  # learned offset in [-0.2, 0.2]
        self._pool = [
            "The quick brown fox jumps over the lazy dog.",
            "Hello, world!",
            "R-zero keeps accuracy in the Goldilocks zone.",
        ]

    def propose_batch(self, n: int, *, difficulty: float) -> List[Task]:
        d = min(0.95, max(0.05, difficulty + self.bias))
        tasks: List[Task] = []
        for _ in range(n):
            txt = random.choice(self._pool)
            prompt = f"Rewrite (difficulty={d:.2f}): {txt}"
            tasks.append(Task(id=str(uuid.uuid4()), domain="rewrite", prompt=prompt, difficulty=d))
        return tasks

    def update(self, feedback: EpisodeFeedback) -> None:
        # simple bandit-style hill climbing on bias using the reward signal
        r = float(feedback.get("reward", 0.0))
        step = 0.02 if r >= 0.8 else (-0.02 if r <= 0.2 else 0.0)
        self.bias = max(-0.2, min(0.2, self.bias + step))

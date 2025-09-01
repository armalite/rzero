from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .types import Sample
from .challenger import Challenger
from .solver import Solver
from .verifier import Verifier
from .curriculum import Curriculum

@dataclass
class Trainer:
    challenger: Challenger
    solver: Solver
    verifier: Verifier
    curriculum: Curriculum = field(default_factory=Curriculum)
    difficulty: float = 0.5

    def run_episode(self, batch_size: int) -> tuple[list[Sample], float]:
        tasks = self.challenger.propose_batch(batch_size, difficulty=self.difficulty)
        samples: list[Sample] = []
        correct = 0
        for t in tasks:
            sol = self.solver.solve(t)
            ver = self.verifier.verify(t, sol)
            samples.append(Sample(task=t, solution=sol, verification=ver))
            if ver.passed:
                correct += 1
        accuracy = correct / max(1, len(tasks))
        self.difficulty = self.curriculum.adjust(self.difficulty, accuracy)
        return samples, accuracy

    def run(self, episodes: int, batch_size: int) -> list[Sample]:
        log: list[Sample] = []
        for _ in range(episodes):
            ep_samples, accuracy = self.run_episode(batch_size)
            log.extend(ep_samples)

            # --- Solver update: per-sample reward is verification.score
            try:
                self.solver.update(ep_samples)  # trainable solvers learn here
            except AttributeError:
                pass

            # --- Challenger reward: highest when accuracy near target band mid-point
            target_mid = (self.curriculum.target_low + self.curriculum.target_high) / 2.0
            # Simple shaped reward in [0, 1]: 1 at target_mid, tapering off to 0 at band edges or beyond
            width = max(1e-6, (self.curriculum.target_high - self.curriculum.target_low) / 2.0)
            chall_reward = max(0.0, 1.0 - abs(accuracy - target_mid) / width)

            try:
                self.challenger.update({
                    "difficulty": self.difficulty,
                    "accuracy": accuracy,
                    "reward": chall_reward,
                })  # trainable challengers learn here
            except AttributeError:
                pass
        return log


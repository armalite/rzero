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
            ep_samples, _ = self.run_episode(batch_size)
            log.extend(ep_samples)
        return log
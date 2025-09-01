from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Curriculum:
    target_low: float = 0.6
    target_high: float = 0.8
    step: float = 0.05
    min_diff: float = 0.05
    max_diff: float = 0.95

    def adjust(self, difficulty: float, accuracy: float) -> float:
        if accuracy > self.target_high:
            difficulty = min(self.max_diff, difficulty + self.step)
        elif accuracy < self.target_low:
            difficulty = max(self.min_diff, difficulty - self.step)
        return round(difficulty, 3)
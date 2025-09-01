from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from .types import Task, Solution, Sample

class Solver(ABC):
    """Attempts to solve a Task. May optionally learn via update(samples)."""

    name: str = "solver"

    @abstractmethod
    def solve(self, task: Task) -> Solution: ...

    # Optional training hook (no-op by default)
    def update(self, samples: List[Sample]) -> None:  # called between episodes
        pass

    # Optional persistence hooks
    def save(self, path: str) -> None:  # pragma: no cover
        pass

    def load(self, path: str) -> None:  # pragma: no cover
        pass

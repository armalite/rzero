from __future__ import annotations

from abc import ABC, abstractmethod

from .types import Task, Solution

class Solver(ABC):
    """Attempts to solve a Task."""

    name: str = "solver"

    @abstractmethod
    def solve(self, task: Task) -> Solution: ...
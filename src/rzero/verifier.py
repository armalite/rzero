from __future__ import annotations

from abc import ABC, abstractmethod

from .types import Task, Solution, Verification

class Verifier(ABC):
    """Verifies a (task, solution) pair and returns a Verification."""

    @abstractmethod
    def verify(self, task: Task, solution: Solution) -> Verification: ...
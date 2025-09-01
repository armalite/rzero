from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TypedDict
from .types import Task

class EpisodeFeedback(TypedDict, total=False):
    difficulty: float
    accuracy: float
    reward: float  # challenger reward

class Challenger(ABC):
    """Produces tasks for a given domain and difficulty, and may learn from feedback."""
    @abstractmethod
    def propose_batch(self, n: int, *, difficulty: float) -> List[Task]: ...
    # Optional training hook
    def update(self, feedback: EpisodeFeedback) -> None:  # no-op by default
        pass

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .types import Task

class Challenger(ABC):
    """Produces tasks for a given domain and difficulty."""

    @abstractmethod
    def propose_batch(self, n: int, *, difficulty: float) -> List[Task]: ...
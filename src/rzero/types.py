from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str
    domain: str
    prompt: str
    difficulty: float = Field(ge=0.0, le=1.0, default=0.5)
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Solution(BaseModel):
    task_id: str
    solver: str = "heuristic"
    content: str
    latency_ms: Optional[float] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class Verification(BaseModel):
    task_id: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)

class Sample(BaseModel):
    task: Task
    solution: Solution
    verification: Verification
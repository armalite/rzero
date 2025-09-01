from __future__ import annotations

import os
from typing import Any, Dict

from rzero.solver import Solver
from rzero.types import Task, Solution

# This uses the official "openai" SDK v1 style.
# Users must: pip install rzero[llm] and set OPENAI_API_KEY
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


SYSTEM = (
    "You are a helpful coding assistant. "
    "Return ONLY valid Python code implementing the requested function. "
    "No markdown, no explanations."
)

class CodeIOLLMSolver(Solver):
    """LLM-backed solver for the Code-IO domain."""
    name = "codeio-llm"

    def __init__(self, model: str = "gpt-5-mini", temperature: float = 0.0) -> None:
        if OpenAI is None:
            raise RuntimeError(
                "openai package not installed. Install with: pip install rzero[llm]"
            )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY in your environment.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def solve(self, task: Task) -> Solution:
        spec = task.meta.get("spec") or {}
        name = spec.get("name", "")
        prompt = (
            f"{task.prompt}\n\n"
            f"Function name must be exactly: {name}\n"
            "Return only the code (no comments or prose)."
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            )
            code = resp.choices[0].message.content or ""
            return Solution(task_id=task.id, solver=self.name, content=code.strip())
        except Exception as e:  # pragma: no cover
            return Solution(task_id=task.id, solver=self.name, content="# ERROR", meta={"error": str(e)})

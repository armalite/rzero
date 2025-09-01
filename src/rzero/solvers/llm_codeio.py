from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, Optional

from rzero.solver import Solver
from rzero.types import Task, Solution

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


SYSTEM = (
    "You are a helpful coding assistant. "
    "Return ONLY valid Python code implementing the requested function. "
    "No markdown, no explanations."
)

CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _supports_free_temperature(model: str) -> bool:
    # Heuristic: some GPT-5* endpoints require the default temp only.
    # We treat 'gpt-5' family as 'fixed temp' unless overridden later.
    return not model.lower().startswith("gpt-5")


def _extract_code(text: str) -> str:
    if not text:
        return ""
    m = CODE_FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()


class CodeIOLLMSolver(Solver):
    """LLM-backed solver for the Code-IO domain."""
    name = "codeio-llm"

    def __init__(self, model: str = "gpt-5-mini", temperature: Optional[float] = None) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed. Install with: pip install rzero[llm]")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY in your environment.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

        # If model doesn't support custom temperature, ignore whatever was passed.
        if _supports_free_temperature(model):
            self.temperature: Optional[float] = temperature if temperature is not None else 0.0
        else:
            self.temperature = None  # omit from API call

    def solve(self, task: Task) -> Solution:
        spec = task.meta.get("spec") or {}
        name = spec.get("name", "")
        prompt = (
            f"{task.prompt}\n\n"
            f"Function name must be exactly: {name}\n"
            "Return only the code (no comments or prose)."
        )

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            }
            if self.temperature is not None:
                kwargs["temperature"] = self.temperature  # only include when supported

            t0 = time.perf_counter()
            resp = self.client.chat.completions.create(**kwargs)
            dt_ms = int((time.perf_counter() - t0) * 1000)

            raw = resp.choices[0].message.content or ""
            code = _extract_code(raw)

            return Solution(
                task_id=task.id,
                solver=self.name,
                content=code,
                latency_ms=dt_ms,
                meta={"raw": raw[:5000]},  # keep a trimmed copy for debugging
            )
        except Exception as e:  # pragma: no cover
            return Solution(
                task_id=task.id,
                solver=self.name,
                content="# ERROR",
                latency_ms=None,
                meta={"error": str(e)},
            )

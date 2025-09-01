from __future__ import annotations
from typing import List, Dict
from rzero.solver import Solver
from rzero.types import Task, Solution, Sample

class CodeIOTrainable(Solver):
    """Minimal trainable example for code-io: cache best-passing code per spec name."""

    name = "codeio-trainable"

    def __init__(self) -> None:
        self.memory: Dict[str, str] = {}

    def solve(self, task: Task) -> Solution:
        spec = (task.meta or {}).get("spec", {})
        name = spec.get("name", "func")
        code = self.memory.get(
            name,
            f"def {name}(*args, **kwargs):\n    raise NotImplementedError\n",
        )
        return Solution(task_id=task.id, solver=self.name, content=code)

    def update(self, samples: List[Sample]) -> None:
        # Learn from successes: remember code that passed all tests
        for s in samples:
            if s.task.domain != "code-io":
                continue
            spec = (s.task.meta or {}).get("spec", {})
            name = spec.get("name")
            if name and s.verification.passed:
                self.memory[name] = s.solution.content

    def save(self, path: str) -> None:
        import json
        import pathlib
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.memory, indent=2), encoding="utf-8")

    def load(self, path: str) -> None:
        import json
        import pathlib
        p = pathlib.Path(path)
        if p.exists():
            self.memory = json.loads(p.read_text(encoding="utf-8"))

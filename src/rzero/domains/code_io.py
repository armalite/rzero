from __future__ import annotations

import random
import string
from typing import Any, Callable, Dict, List

from ..types import Task, Solution, Verification
from ..challenger import Challenger
from ..solver import Solver
from ..verifier import Verifier

# --- Code-IO domain: generate tiny function specs with tests, solve heuristically, verify by execution.

_SPEC_BANK = [
    {
        "name": "add",
        "prompt": "Write a function add(a, b) that returns a + b.",
        "tests": [((1, 2), 3), ((-5, 5), 0), ((10, -3), 7)]
    },
    {
        "name": "reverse_string",
        "prompt": "Write a function reverse_string(s) that returns the reversed string.",
        "tests": [(("abc",), "cba"), (("",), ""), (("racecar",), "racecar")]
    },
    {
        "name": "factorial",
        "prompt": "Write a function factorial(n) that returns n! for n>=0 (with factorial(0)==1).",
        "tests": [((0,), 1), ((3,), 6), ((5,), 120)]
    },
]

def _rand_id(prefix: str) -> str:
    return prefix + "-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

class CodeIOChallenger(Challenger):
    def propose_batch(self, n: int, *, difficulty: float) -> List[Task]:
        tasks: List[Task] = []
        for _ in range(n):
            spec = random.choice(_SPEC_BANK)
            prompt = spec["prompt"]
            task = Task(id=_rand_id("code"), domain="code-io", prompt=prompt, difficulty=difficulty, meta={"spec": spec})
            tasks.append(task)
        return tasks

class CodeIOSolver(Solver):
    name = "codeio-heuristic"
    def solve(self, task: Task) -> Solution:
        spec = task.meta.get("spec") or {}
        name = spec.get("name", "")
        if name == "add":
            code = "def add(a, b):\n    return a + b\n"
        elif name == "reverse_string":
            code = "def reverse_string(s):\n    return s[::-1]\n"
        elif name == "factorial":
            code = (
                "def factorial(n):\n"
                "    if n < 0:\n        raise ValueError('n must be >= 0')\n"
                "    out = 1\n"
                "    for i in range(2, n+1):\n        out *= i\n"
                "    return out\n"
            )
        else:
            code = "# TODO: unknown spec\n"
        return Solution(task_id=task.id, solver=self.name, content=code)

class CodeIOVerifier(Verifier):
    def verify(self, task: Task, solution: Solution) -> Verification:
        spec = task.meta.get("spec") or {}
        name = spec.get("name", "")
        tests = spec.get("tests", [])
        # Execute in a restricted namespace
        global_ns: Dict[str, Any] = {"__builtins__": {"range": range, "len": len, "ValueError": ValueError}}
        local_ns: Dict[str, Any] = {}
        try:
            exec(solution.content, global_ns, local_ns)
        except Exception as e:
            return Verification(task_id=task.id, passed=False, score=0.0, feedback=f"exec error: {e}")

        fn = local_ns.get(name)
        if not callable(fn):
            return Verification(task_id=task.id, passed=False, score=0.0, feedback="function not defined")

        passed = 0
        for args, expected in tests:
            try:
                out = fn(*args)
                if out == expected:
                    passed += 1
            except Exception:
                # counts as failure
                pass
        score = passed / max(1, len(tests))
        return Verification(task_id=task.id, passed=score == 1.0, score=score, feedback="")
from __future__ import annotations

import ast
import operator as op
import random
import string
from dataclasses import dataclass
from typing import Any, List

from ..types import Task, Solution, Verification
from ..challenger import Challenger
from ..solver import Solver
from ..verifier import Verifier

# Safe eval for arithmetic expressions
_ALLOWED = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def _safe_eval(expr: str) -> float:
    node = ast.parse(expr, mode="eval")

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Num):  # type: ignore[attr-defined]
            return float(n.n)  # type: ignore[attr-defined]
        if isinstance(n, ast.BinOp):
            if type(n.op) not in _ALLOWED:
                raise ValueError("op not allowed")
            return _ALLOWED[type(n.op)](_eval(n.left), _eval(n.right))  # type: ignore[index]
        if isinstance(n, ast.UnaryOp):
            if type(n.op) not in _ALLOWED:
                raise ValueError("uop not allowed")
            return _ALLOWED[type(n.op)](_eval(n.operand))  # type: ignore[index]
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        raise ValueError("bad node")
    return _eval(node)

class ArithmeticChallenger(Challenger):
    def propose_batch(self, n: int, *, difficulty: float) -> List[Task]:
        tasks: List[Task] = []
        # difficulty influences number range and operators
        max_n = int(10 + 90 * difficulty)  # 10..100
        ops = ['+', '-'] + (['*'] if difficulty >= 0.3 else []) + (['/'] if difficulty >= 0.6 else [])
        for i in range(n):
            a, b = random.randint(1, max_n), random.randint(1, max_n)
            c = random.randint(1, max_n) if difficulty >= 0.6 else None
            op1 = random.choice(ops)
            expr = f"{a} {op1} {b}"
            if c is not None:
                op2 = random.choice(ops)
                expr = f"{expr} {op2} {c}"
            task_id = "arith-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            tasks.append(Task(id=task_id, domain="arithmetic", prompt=expr, difficulty=difficulty))
        return tasks

class ArithmeticSolver(Solver):
    name = "arith-heuristic"
    def solve(self, task: Task) -> Solution:
        try:
            value = _safe_eval(task.prompt)
            if value.is_integer():
                ans = str(int(value))
            else:
                ans = f"{value:.6f}"
            return Solution(task_id=task.id, solver=self.name, content=ans)
        except Exception as e:
            return Solution(task_id=task.id, solver=self.name, content="ERROR", meta={"error": str(e)})

class ArithmeticVerifier(Verifier):
    def verify(self, task: Task, solution: Solution) -> Verification:
        try:
            truth = _safe_eval(task.prompt)
        except Exception as e:
            return Verification(task_id=task.id, passed=False, score=0.0, feedback=f"bad task: {e}")
        try:
            pred = float(solution.content)
        except Exception:
            return Verification(task_id=task.id, passed=False, score=0.0, feedback="non-numeric")
        passed = abs(pred - truth) < 1e-6
        return Verification(task_id=task.id, passed=passed, score=1.0 if passed else 0.0, feedback="")
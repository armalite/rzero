# rzero
⚡ A reference implementation of **R-Zero** (Aug 2025) - the self-evolving training loop where Challengers and Solvers co-adapt, with pluggable components, curriculum control, and dataset logging.

⚠️ Early Development - APIs may change.

It provides:
 - A neat CLI (`rzero run`, `rzero dataset`) for quick experiments
 - A Python API for plugging in your own **Solvers, Challengers, and Verifiers**
 - Built-in support for **co-evolution**: `Solver.update(samples)` and `Challenger.update(feedback)` are called automatically
 - Automatic difficulty control ("curriculum") to keep performance in the learning zone
 - Structured datasets (`.jsonl`) of every run for analysis or offline training

Out of the box you get two demo domains:
 - arithmetic → generate math expressions, solve with a safe evaluator, verify correctness.
 - code-io → generate small Python functions, solve with heuristics or an LLM, verify by executing unit tests.

##  What is R-Zero?

R-Zero is a brand-new framework (published on arXiv in August 2025) for **self-evolving reasoning models**.  
The core idea: instantiate two models - a Challenger and a Solver - that co-evolve by challenging each other and learning continuously **without any human-curated tasks or labels** [R-Zero: Self-Evolving Reasoning LLM from Zero Data](https://arxiv.org/abs/2508.05004).

This package is not just a demo. It’s designed so you can plug in trainable Solvers and Challengers and run a co-evolutionary R-Zero loop, as introduced in the 2025 paper.

 ## 🚀 Quickstart
Clone the repo and set up a local environment:
```bash
make dev    # create .venv, install in editable mode with dev deps

# run arithmetic for 3 episodes, batch size 10
rzero run --domain arithmetic --episodes 3 --batch-size 10

# run code-io with heuristic solver
rzero run --domain code-io --episodes 2 --batch-size 5

# inspect dataset stats (defaults to ./data/rzero_samples.jsonl)
rzero dataset -p ./data/rzero_samples.jsonl

```

## Optional: LLM Solver
Install with extras:
```bash
pip install rzero[llm]
export OPENAI_API_KEY=sk-...
rzero run --domain code-io --solver llm --model gpt-5-mini --episodes 1 --batch-size 5
```
This uses GPT-5-mini as the solver. Every attempt is unit-tested, scored, and logged.

---
## 🧩 Core Concepts
 - Task → a challenge prompt with metadata + difficulty.
 - Solution → the solver’s attempt.
 - Verification → pass/fail and score, plus feedback.
 - Sample → (Task, Solution, Verification) — one datapoint.
 - Curriculum → nudges difficulty to keep accuracy in a target band.
 - Trainer → orchestrates episodes and logs datasets.

 ---

## 🔄 R-Zero Training (Co-Evolution)

The R-Zero paper (Aug 2025) describes a *co-evolutionary loop*:
- The **Solver** learns from verification scores on each task.
- The **Challenger** learns to propose tasks near the Solver’s “edge of ability.”
- The **Curriculum** keeps difficulty in the Goldilocks zone.
- Every step is logged to JSONL for later analysis or fine-tuning.

In this package:
- `Solver.update(samples)` lets your model train after each episode.
- `Challenger.update(feedback)` lets your task generator adapt using episode-level rewards.
- `Trainer` automatically calls these hooks for you.

So if you implement both hooks, you get a fully-fledged **R-Zero training loop** without extra scaffolding.

 ---
## 🛠 Using rzero in your own code
The CLI is for quick runs. The real power comes from plugging in your own Solver.

### Minimal Example
Implementing your own solver:
```python
from rzero.loop import Trainer
from rzero.curriculum import Curriculum
from rzero.domains.code_io import CodeIOChallenger, CodeIOVerifier
from rzero.solver import Solver
from rzero.types import Task, Solution, Sample

class MySolver(Solver):
    name = "my-solver"

    def solve(self, task: Task) -> Solution:
        # Call your model (LLM, HuggingFace, PyTorch, etc.)
        pred = f"answer for: {task.prompt}"
        return Solution(task_id=task.id, solver=self.name, content=pred)

    def update(self, samples: list[Sample]) -> None:
        # Train your model here using verified samples
        good = [s for s in samples if s.verification.passed]
        for s in good:
            # ... training step ...
            pass

trainer = Trainer(
    challenger=CodeIOChallenger(),
    solver=MySolver(),
    verifier=CodeIOVerifier(),
    curriculum=Curriculum(),
    difficulty=0.5,
)

samples = trainer.run(episodes=3, batch_size=10)  # calls update() after each episode

```
This lets you reuse the loop, curriculum, and dataset logging with any model, not just the demos.


---

## 📦 Offline Training (Replay)
You can also train your solver offline from a saved dataset:
```python
from rzero.storage import read_jsonl
from rzero.types import Sample, Task, Solution, Verification
from my_solver import MySolver

rows = read_jsonl("./data/codeio_llm.jsonl")
samples = [
    Sample(
        task=Task(**r["task"]),
        solution=Solution(**r["solution"]),
        verification=Verification(**r["verification"]),
    )
    for r in rows
]

solver = MySolver()
solver.update(samples)      # train from prior data
solver.save("./data/state.json")

```
This is handy if you generate data with the LLM solver, then want to replay it into your own model.

## Extending Challengers and Verifiers

Besides plugging in your own Solver, you can also bring your own **Challenger** (task generator) and **Verifier** (scoring function).

A Challenger must implement:
```python
from rzero.challenger import Challenger
from rzero.types import Task

class MyChallenger(Challenger):
    def propose_batch(self, difficulty: float, batch_size: int) -> list[Task]:
        ...
```

A Verifier must implement:
```python
from rzero.verifier import Verifier
from rzero.types import Task, Solution, Verification

class MyVerifier(Verifier):
    def verify(self, task: Task, solution: Solution) -> Verification:
        ...

```

You can then wire them into the Trainer:
```python
trainer = Trainer(
    challenger=MyChallenger(),
    solver=MySolver(),
    verifier=MyVerifier(),
    curriculum=Curriculum(),
    difficulty=0.5,
)
samples = trainer.run(episodes=3, batch_size=10)
```

## 🔒 Safety
The code-io verifier executes returned Python functions in a restricted namespace.
Even so: only run trusted tasks/solutions in a safe environment. Treat all generated code as potentially unsafe.

## 📜 License
MIT Licensed.

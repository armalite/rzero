# rzero

Reusable training loop built around *challenger → solver → verifier* with curriculum control and a neat CLI.

Includes two example domains:
- **arithmetic**: generate math expressions, solve with a safe evaluator, verify correctness.
- **code-io**: generate small Python functions, solve with heuristic templates, verify by executing tests.

## Quickstart

Clone the repo and set up a local environment:

```bash
make dev    # create .venv, install in editable mode with dev deps

# run arithmetic for 3 episodes, batch-size 10
rzero run --domain arithmetic --episodes 3 --batch-size 10

# run code-io
rzero run --domain code-io --episodes 2 --batch-size 5

# inspect dataset stats (defaults to ./data/rzero_samples.jsonl)
rzero dataset -p ./data/rzero_samples.jsonl
```

## Concepts

 - Task → a challenge prompt with metadata and difficulty.
 - Solution → the solver's attempt.
 - Verification → pass/fail and score, plus feedback.
 - Sample → (Task, Solution, Verification).
 - Curriculum → nudges difficulty to keep accuracy near a target band.

## Using rzero in your own code

Besides the CLI, you can import rzero into Python and plug in your own solver:
```python
from rzero.loop import Trainer
from rzero.curriculum import Curriculum
from rzero.domains.code_io import CodeIOChallenger, CodeIOVerifier
from rzero.solver import Solver
from rzero.types import Task, Solution

class MySolver(Solver):
    def solve(self, task: Task) -> Solution:
        # call your own model here (LLM, HuggingFace, custom logic…)
        return Solution(task_id=task.id, solver="my-solver", content="...")

trainer = Trainer(
    challenger=CodeIOChallenger(),
    solver=MySolver(),
    verifier=CodeIOVerifier(),
    curriculum=Curriculum(),
    difficulty=0.5,
)

samples = trainer.run(episodes=2, batch_size=8)

```
This lets you reuse the R-zero loop, curriculum, and dataset logging with any model, not just the demo solvers.

## Safety
The `code-io` verifier executes code in a restricted namespace - still, only run trusted tasks/solutions in secure environments.

MIT Licensed
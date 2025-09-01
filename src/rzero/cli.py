from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import click

from .loop import Trainer
from .curriculum import Curriculum
from .storage import write_jsonl
from .domains.arithmetic import ArithmeticChallenger, ArithmeticSolver, ArithmeticVerifier
from .domains.code_io import CodeIOChallenger, CodeIOSolver, CodeIOVerifier

DATA_DIR = Path("./data").expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

@click.group()
def main() -> None:
    """rzero CLI: run training loops and manage datasets."""

@main.command()
@click.option("--domain", type=click.Choice(["arithmetic", "code-io"]), default="arithmetic")
@click.option("--solver", type=click.Choice(["heuristic", "llm"]), default="heuristic", show_default=True)
@click.option("--episodes", type=int, default=2, show_default=True)
@click.option("--batch-size", type=int, default=8, show_default=True)
@click.option(
    "--dataset",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DATA_DIR / "rzero_samples.jsonl",
    show_default=True,
    help="JSONL output path for samples (defaults to ./data/rzero_samples.jsonl).",
)
@click.option("--seed-difficulty", type=float, default=0.5, show_default=True, help="Initial difficulty [0..1].")
@click.option("--model", default="gpt-5-mini", show_default=True, help="LLM model name (only used when --solver=llm).")
@click.option(
    "--temperature",
    type=float,
    default=None,
    show_default=True,
    help="LLM temperature; some models (e.g. gpt-5-*) only allow their default and will ignore this.",
)
def run(domain: str, solver: str, episodes: int, batch_size: int, dataset: Path, seed_difficulty: float, model: str, temperature: float) -> None:
    """Run the training loop for a domain."""
    # Domain wiring
    if domain == "arithmetic":
        from .domains.arithmetic import ArithmeticChallenger, ArithmeticSolver, ArithmeticVerifier
        challenger = ArithmeticChallenger()
        verifier = ArithmeticVerifier()
        if solver == "llm":
            click.echo("LLM solver is not supported for arithmetic; using heuristic.", err=True)
        from .domains.arithmetic import ArithmeticSolver as DefaultSolver
        solver_impl = DefaultSolver()
    else:
        from .domains.code_io import CodeIOChallenger, CodeIOSolver, CodeIOVerifier
        challenger = CodeIOChallenger()
        verifier = CodeIOVerifier()
        if solver == "llm":
            try:
                from .solvers.llm_codeio import CodeIOLLMSolver
                solver_impl = CodeIOLLMSolver(model=model, temperature=temperature)
            except Exception as e:
                raise click.ClickException(str(e))
        else:
            solver_impl = CodeIOSolver()

    trainer = Trainer(
        challenger=challenger,
        solver=solver_impl,
        verifier=verifier,
        curriculum=Curriculum(),
        difficulty=seed_difficulty,
    )

    samples = trainer.run(episodes=episodes, batch_size=batch_size)
    click.echo(f"Collected {len(samples)} samples. Final difficulty ~ {trainer.difficulty:.2f}.")
    path = write_jsonl(samples, dataset)
    click.echo(f"Wrote samples to {path}")

@main.command("dataset")
@click.option("-p", "--path", type=click.Path(dir_okay=False, exists=True, path_type=Path), required=True)
def dataset_cmd(path: Path) -> None:
    """Quickly show dataset stats."""
    import statistics as st
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    n = len(rows)
    scores = [r["verification"]["score"] for r in rows]
    acc = sum(1 for s in scores if s >= 1.0) / max(1, n)
    click.echo(f"Samples: {n}")
    if scores:
        click.echo(f"Accuracy: {acc:.3f}, mean score: {st.mean(scores):.3f}")

@main.command()
@click.option("-p", "--path", type=click.Path(dir_okay=False, exists=True, path_type=Path), required=True)
@click.option("--save", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional path to save solver state after replay.")
def replay(path: Path, save: Path | None) -> None:
    """Replay a dataset (JSONL of Samples) to update a trainable solver."""
    from .domains.code_io import CodeIOChallenger, CodeIOVerifier
    from .solvers.trainable_template import CodeIOTrainable
    from .storage import read_jsonl
    from .types import Sample, Task, Solution, Verification

    # Build samples back from JSON (schema-aware)
    rows = read_jsonl(path)
    samples = [
        Sample(
            task=Task(**row["task"]),
            solution=Solution(**row["solution"]),
            verification=Verification(**row["verification"]),
        )
        for row in rows
    ]

    solver = CodeIOTrainable()
    solver.update(samples)
    click.echo(f"Replayed {len(samples)} samples into {solver.name}.")

    if save:
        solver.save(str(save))
        click.echo(f"Saved solver state to {save}")

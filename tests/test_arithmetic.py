from rzero.loop import Trainer
from rzero.curriculum import Curriculum
from rzero.domains.arithmetic import ArithmeticChallenger, ArithmeticSolver, ArithmeticVerifier

def test_arithmetic_smoke():
    trainer = Trainer(
        challenger=ArithmeticChallenger(),
        solver=ArithmeticSolver(),
        verifier=ArithmeticVerifier(),
        curriculum=Curriculum(),
        difficulty=0.4,
    )
    samples = trainer.run(episodes=1, batch_size=5)
    assert len(samples) == 5
    # all should verify fine with heuristic solver
    assert sum(1 for s in samples if s.verification.passed) == 5
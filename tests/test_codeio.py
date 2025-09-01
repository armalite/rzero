from rzero.loop import Trainer
from rzero.curriculum import Curriculum
from rzero.domains.code_io import CodeIOChallenger, CodeIOSolver, CodeIOVerifier

def test_codeio_smoke():
    trainer = Trainer(
        challenger=CodeIOChallenger(),
        solver=CodeIOSolver(),
        verifier=CodeIOVerifier(),
        curriculum=Curriculum(),
        difficulty=0.5,
    )
    samples = trainer.run(episodes=1, batch_size=6)
    assert len(samples) == 6
    assert sum(1 for s in samples if s.verification.passed) >= 4  # some randomness allowed
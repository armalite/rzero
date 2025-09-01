from __future__ import annotations

# placeholder for an LLM client wrapper.
# Can implement OpenAI / Azure / etc. here later 
class LLM:
    def __init__(self, **kwargs): ...
    def complete(self, prompt: str) -> str:
        raise NotImplementedError("LLM not wired; this project runs fully without it.")
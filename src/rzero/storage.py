from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Any

from .types import Sample

def write_jsonl(samples: Iterable[Sample], path: str | Path) -> Path:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s.model_dump(mode="json"), ensure_ascii=False) + "\n")
    return p

def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path).expanduser()
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows
from pathlib import Path
from typing import Optional


def get_ready_made_dir(default_path: Path, *potentials: Optional[Path]):
    for p in potentials:
        if p and p.exists() and p.is_dir():
            return p
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path

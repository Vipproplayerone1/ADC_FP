from functools import lru_cache

from app.config import get_settings


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    path = get_settings().prompts_dir / f"{name}.txt"
    return path.read_text(encoding="utf-8")

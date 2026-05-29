import re
from pathlib import Path


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._\-]+")


def safe_filename(name: str) -> str:
    """Strip path components and dangerous characters from an uploaded filename."""
    base = Path(name).name
    cleaned = _SAFE_NAME_RE.sub("_", base).strip("._")
    return cleaned or "uploaded.pdf"


def save_bytes(content: bytes, dest_dir: Path, filename: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / safe_filename(filename)
    path.write_bytes(content)
    return path

"""Safe file operations within the workdir."""
from pathlib import Path
from typing import Optional

class FileTool:
    def __init__(self, workdir: Path):
        self.workdir = workdir.resolve()

    def _resolve(self, path: str) -> Path:
        p = (self.workdir / path).resolve()
        if not p.is_relative_to(self.workdir):
            raise ValueError(f"Path {path} is outside workdir")
        return p

    def read(self, path: str) -> str:
        p = self._resolve(path)
        return p.read_text()

    def write(self, path: str, content: str) -> dict:
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return {"status": "written", "path": str(p)}

    def exists(self, path: str) -> bool:
        p = self._resolve(path)
        return p.exists()

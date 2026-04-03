"""Git operations for the workdir (assumes git repo)."""
import subprocess
from pathlib import Path
from typing import Optional

class GitTool:
    def __init__(self, workdir: Path):
        self.workdir = workdir

    def _run(self, *args, capture_output: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git"] + list(args),
            cwd=self.workdir,
            capture_output=capture_output,
            text=True,
            timeout=30,
        )

    def init(self) -> dict:
        self._run("init")
        self._run("config", "user.email", "xander-operator@example.com")
        self._run("config", "user.name", "Xander Operator")
        return {"status": "initialized"}

    def add(self, path: str = ".") -> dict:
        res = self._run("add", path)
        return {"status": "added", "stdout": res.stdout}

    def commit(self, message: str, allow_empty: bool = False) -> dict:
        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")
        res = self._run(*args)
        if res.returncode == 0:
            return {"status": "committed", "sha": res.stdout.strip()}
        else:
            return {"status": "error", "error": res.stderr}

    def diff(self, path: Optional[str] = None) -> str:
        args = ["diff"]
        if path:
            args.append(path)
        res = self._run(*args)
        return res.stdout

    def reset_hard(self, commit: str = "HEAD") -> dict:
        res = self._run("reset", "--hard", commit)
        return {"status": "reset", "returncode": res.returncode}

    def status(self) -> dict:
        res = self._run("status", "--porcelain")
        return {"status": res.stdout}

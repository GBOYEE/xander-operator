import pytest
from pathlib import Path

@pytest.fixture
def temp_workspace(tmp_path: Path):
    return tmp_path / "workspace"

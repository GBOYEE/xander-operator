import pytest
from pathlib import Path
from xander_operator.tools.file_tool import FileTool
from xander_operator.tools.git_tool import GitTool

def test_file_tool_write_and_read(tmp_path: Path):
    ft = FileTool(workdir=tmp_path)
    ft.write("test.txt", "content")
    assert ft.read("test.txt") == "content"
    assert ft.exists("test.txt")

def test_file_tool_outside_workdir_raises(tmp_path: Path):
    ft = FileTool(workdir=tmp_path)
    with pytest.raises(ValueError):
        ft.write("../outside.txt", "hax0r")

def test_git_tool_init_and_commit(tmp_path: Path):
    gt = GitTool(workdir=tmp_path)
    gt.init()
    ft = FileTool(workdir=tmp_path)
    ft.write("file.txt", "data")
    gt.add(".")
    res = gt.commit("test commit")
    assert res["status"] == "committed"
    assert res.get("sha")

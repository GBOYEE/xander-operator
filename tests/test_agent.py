import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from xander_operator.agent import CodingAgent
from xander_operator.config import Settings

def test_agent_creates_file(temp_workspace: Path):
    # Mock LLM to return a simple file creation plan
    mock_response = json.dumps([{"file": "hello.txt", "content": "Hello, world!"}])
    with patch.object(CodingAgent, "_call_llm", return_value=mock_response):
        agent = CodingAgent(workdir=temp_workspace)
        result = agent.execute("create hello.txt with 'Hello, world!'")
        assert result["status"] == "success"
        assert "hello.txt" in result["files_written"]
        assert (temp_workspace / "hello.txt").read_text() == "Hello, world!"
        # Check git commit happened
        assert result.get("commit", {}).get("status") == "committed"

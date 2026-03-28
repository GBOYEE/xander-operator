"""Tests for LLM client and caching."""
import pytest  # noqa: F401
from unittest.mock import MagicMock, patch
from xander_operator.llm import generate_response, clear_cache

def test_generate_response_mocked(mocker):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello world"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    mocker.patch("xander_operator.llm.get_llm_client", return_value=mock_client)
    # Ensure cache is not used (or we clear)
    # First call
    result = generate_response("Say hi", model="gpt-4", use_cache=True)
    assert result == "Hello world"
    mock_client.chat.completions.create.assert_called_once()

    # Second call with same prompt should hit cache if library uses caching; but we patched client; second call would return from cache without calling client again.
    mock_client.chat.completions.create.reset_mock()
    result2 = generate_response("Say hi", model="gpt-4", use_cache=True)
    assert result2 == "Hello world"
    # Depending on implementation, the client call should not happen again because cache hit.
    mock_client.chat.completions.create.assert_not_called()

def test_generate_response_no_client_when_missing(mocker):
    mocker.patch("xander_operator.llm.LLM_AVAILABLE", False)
    result = generate_response("test")
    assert result is None

def test_clear_cache_function(tmp_path):
    # Override cache db path via env? For simplicity, test that clear_cache runs without error.
    # It just deletes from CACHE_DB which is a file. We can call it.
    # But we need to ensure DB exists? Can't guarantee.
    # We'll just call and ensure no exception.
    try:
        clear_cache()
    except Exception as e:
        pytest.fail(f"clear_cache raised: {e}")

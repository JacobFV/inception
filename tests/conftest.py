import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Return a Path object pointing to the test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def sample_chat_response():
    """Return a sample chat response dictionary."""
    return {
        "chat": {
            "id": "test-chat-id",
            "title": "Test Chat",
            "models": ["lambda.mercury-coder-small"],
            "params": {},
            "history": {
                "messages": {},
                "current_id": "test-message-id"
            },
            "messages": [],
            "tags": [],
            "timestamp": 1742265411000
        }
    }

@pytest.fixture
def sample_chat_completion_chunk():
    """Return a sample chat completion chunk dictionary."""
    return {
        "id": "test-completion-id",
        "object": "chat.completion.chunk",
        "created": 1742265411,
        "model": "mercury-coder-small",
        "choices": [{
            "index": 0,
            "delta": {"content": "Hello"},
            "finish_reason": None,
            "content_filter_results": {
                "hate": {"filtered": False},
                "self_harm": {"filtered": False},
                "sexual": {"filtered": False},
                "violence": {"filtered": False},
                "jailbreak": {"filtered": False, "detected": False},
                "profanity": {"filtered": False, "detected": False}
            }
        }],
        "system_fingerprint": "",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    } 
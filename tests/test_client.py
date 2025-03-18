import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import httpx
from sseclient import SSEClient

from inception_api.client import (
    InceptionAI,
    Message,
    Chat,
    ChatHistory,
    ChatCompletionChunk,
    CompletionChoice,
    ContentFilterResults,
    ContentFilterResult,
    Usage
)

@pytest.fixture
def mock_client():
    with patch("inception_api.client.httpx.Client") as mock:
        yield mock

@pytest.fixture
def client(mock_client):
    return InceptionAI("test-api-key")

def test_client_initialization():
    client = InceptionAI("test-api-key")
    assert client.api_key == "test-api-key"
    assert client.base_url == "https://chat.inceptionlabs.ai"
    assert client.headers == {
        "Authorization": "Bearer test-api-key",
        "Content-Type": "application/json",
    }

def test_create_chat(client, mock_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "chat": {
            "id": "test-chat-id",
            "title": "New Chat",
            "models": ["lambda.mercury-coder-small"],
            "params": {},
            "history": {
                "messages": {},
                "current_id": "test-message-id"
            },
            "messages": [],
            "tags": [],
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
    }
    mock_client.return_value.post.return_value = mock_response

    chat = client.create_chat("Hello!")
    assert isinstance(chat, Chat)
    assert chat.id == "test-chat-id"

def test_list_chats(client, mock_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "chats": [
            {
                "id": "chat-1",
                "title": "Chat 1"
            },
            {
                "id": "chat-2",
                "title": "Chat 2"
            }
        ]
    }
    mock_client.return_value.get.return_value = mock_response

    chats = client.list_chats()
    assert len(chats["chats"]) == 2
    assert chats["chats"][0]["id"] == "chat-1"

def test_delete_chat(client, mock_client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_client.return_value.delete.return_value = mock_response

    client.delete_chat("test-chat-id")
    mock_client.return_value.delete.assert_called_once()

def test_chat_completion(client, mock_client):
    # Create mock SSE events
    events = [
        type('Event', (), {'data': json.dumps({
            "id": "test-completion-id",
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
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
        })}),
        type('Event', (), {'data': '[DONE]'})
    ]

    # Mock SSEClient
    mock_sse = Mock(spec=SSEClient)
    mock_sse.events.return_value = events

    with patch('inception_api.client.SSEClient', return_value=mock_sse):
        messages = [Message(role="user", content="Hello")]
        chunks = list(client.chat_completion(messages))
        
        assert len(chunks) == 1
        chunk = chunks[0]
        assert isinstance(chunk, ChatCompletionChunk)
        assert chunk.choices[0].delta["content"] == "Hello"

def test_message_model():
    message = Message(role="user", content="test message")
    assert message.role == "user"
    assert message.content == "test message"
    assert message.models == []

def test_chat_history_model():
    message = Message(role="user", content="test")
    history = ChatHistory(messages={message.id: message}, current_id=message.id)
    assert len(history.messages) == 1
    assert history.current_id == message.id

def test_chat_model():
    message = Message(role="user", content="test")
    history = ChatHistory(messages={message.id: message}, current_id=message.id)
    chat = Chat(
        models=["lambda.mercury-coder-small"],
        history=history,
        messages=[message]
    )
    assert len(chat.messages) == 1
    assert chat.models == ["lambda.mercury-coder-small"]

def test_error_handling(client, mock_client):
    mock_client.return_value.post.side_effect = httpx.HTTPError("API Error")
    
    with pytest.raises(httpx.HTTPError):
        client.create_chat("Hello!") 
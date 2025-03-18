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
    Usage,
    SignInResponse,
    Permissions,
    WorkspacePermissions,
    ChatPermissions
)

@pytest.fixture
def mock_client():
    with patch("inception_api.client.httpx.Client") as mock:
        yield mock

@pytest.fixture
def sample_headers():
    return {
        "authorization": "Bearer test-token",
        "content-type": "application/json",
        "cookie": "test-cookie",
        "user-agent": "test-agent"
    }

@pytest.fixture
def client(mock_client, sample_headers):
    return InceptionAI(headers=sample_headers)

def test_client_initialization(sample_headers):
    client = InceptionAI(headers=sample_headers)
    assert client.base_url == "https://chat.inceptionlabs.ai"
    assert client.headers == sample_headers
    assert "content-type" in client.headers

def test_client_from_web_auth():
    with patch("inception_api.client.sync_playwright") as mock_playwright:
        # Mock browser context and page
        mock_context = Mock()
        mock_page = Mock()
        mock_response = Mock()
        
        # Setup response headers
        mock_response.request.headers = {
            "authorization": "Bearer test-token",
            "user-agent": "test-agent"
        }
        
        # Setup cookie data
        mock_context.cookies.return_value = [
            {"name": "test_cookie", "value": "test_value"}
        ]
        
        mock_page.goto.return_value = mock_response
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_context.return_value = mock_context

        client = InceptionAI.from_web_auth()
        
        assert "authorization" in client.headers
        assert "cookie" in client.headers
        assert "content-type" in client.headers

def test_client_from_credentials():
    with patch("inception_api.client.httpx.Client") as mock_client:
        # Mock successful signin response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "test-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "profile_image_url": "https://example.com/image.jpg",
            "token": "test-token",
            "token_type": "Bearer",
            "expires_at": "2024-12-31T23:59:59Z",
            "permissions": {
                "workspace": {
                    "models": True,
                    "knowledge": True,
                    "prompts": True,
                    "tools": True
                },
                "chat": {
                    "file_upload": True,
                    "delete": True,
                    "edit": True,
                    "temporary": True
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.post.return_value = mock_response

        client = InceptionAI.from_credentials("test@example.com", "password")
        
        assert "authorization" in client.headers
        assert client.headers["authorization"] == "Bearer test-token"
        assert "content-type" in client.headers

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
    mock_response.json.return_value = [
        {
            "id": "chat-1",
            "title": "Chat 1"
        },
        {
            "id": "chat-2",
            "title": "Chat 2"
        }
    ]
    mock_client.return_value.get.return_value = mock_response

    chats = client.list_chats()
    assert len(chats) == 2
    assert chats[0]["id"] == "chat-1"

def test_delete_chat(client, mock_client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_client.return_value.delete.return_value = mock_response

    client.delete_chat("test-chat-id")
    mock_client.return_value.delete.assert_called_once()

def test_chat_completion(client, mock_client):
    # Create mock response with proper byte encoding
    mock_response = Mock()
    mock_response.iter_lines.return_value = [
        b'data: ' + json.dumps({
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
        }).encode('utf-8'),
        b'data: [DONE]'
    ]
    mock_client.return_value.post.return_value = mock_response

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

def test_maximum_context_size(client, mock_client):
    """Test that the client handles maximum context size appropriately"""
    long_message = "test " * 25000
    
    mock_response = Mock()
    mock_response.iter_lines.return_value = [
        b'data: ' + json.dumps({
            "id": "1",
            "object": "chat.completion.chunk",
            "created": 1,
            "model": "mercury-coder-small",
            "choices": [{
                "index": 0,
                "delta": {"content": "Error"},
                "finish_reason": "length",
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
                "prompt_tokens": 25000,
                "completion_tokens": 1,
                "total_tokens": 25001
            }
        }).encode('utf-8')
    ]
    mock_client.return_value.post.return_value = mock_response

    messages = [Message(role="user", content=long_message)]
    chunks = list(client.chat_completion(messages))
    
    assert chunks[0].choices[0].finish_reason == "length"
    assert chunks[0].usage.prompt_tokens >= 25000

def test_streaming_performance(client, mock_client):
    """Test streaming performance over long sequences"""
    import time
    
    num_chunks = 100
    chunk_content = "test " * 10
    
    mock_response = Mock()
    mock_response.iter_lines.return_value = [
        b'data: ' + json.dumps({
            "id": "1",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "mercury-coder-small",
            "choices": [{
                "index": 0,
                "delta": {"content": chunk_content},
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
                "prompt_tokens": 10,
                "completion_tokens": i+1,
                "total_tokens": i+11
            }
        }).encode('utf-8')
        for i in range(num_chunks)
    ] + [b'data: [DONE]']
    
    mock_client.return_value.post.return_value = mock_response

    start_time = time.time()
    chunks = list(client.chat_completion([Message(role="user", content="Test streaming")]))
    end_time = time.time()
    
    total_tokens = sum(len(chunk.choices[0].delta.get("content", "").split()) for chunk in chunks)
    duration = end_time - start_time
    tokens_per_second = total_tokens / duration if duration > 0 else 0
    
    assert len(chunks) == num_chunks
    assert tokens_per_second > 0
    assert all(chunk.choices[0].delta.get("content") == chunk_content for chunk in chunks)

def test_streaming_backpressure(client, mock_client):
    """Test that streaming handles backpressure appropriately"""
    import time
    
    def slow_consumer_iter_lines():
        for i in range(10):
            time.sleep(0.1)
            yield b'data: ' + json.dumps({
                "id": "1",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mercury-coder-small",
                "choices": [{
                    "index": 0,
                    "delta": {"content": f"chunk{i}"},
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
                    "prompt_tokens": 10,
                    "completion_tokens": i+1,
                    "total_tokens": i+11
                }
            }).encode('utf-8')
        yield b'data: [DONE]'
    
    mock_response = Mock()
    mock_response.iter_lines.return_value = slow_consumer_iter_lines()
    mock_client.return_value.post.return_value = mock_response

    start_time = time.time()
    chunks = list(client.chat_completion([Message(role="user", content="Test backpressure")]))
    duration = time.time() - start_time
    
    assert len(chunks) == 10
    assert duration >= 1.0  # Should take at least 1 second due to the sleeps
    assert all(chunk.choices[0].delta.get("content").startswith("chunk") for chunk in chunks)

def test_error_handling_unauthorized(client, mock_client):
    """Test handling of unauthorized access"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=Mock(),
        response=mock_response
    )
    mock_client.return_value.get.side_effect = mock_response.raise_for_status.side_effect

    with pytest.raises(Exception) as exc_info:
        client.list_chats()
    assert "Authentication failed" in str(exc_info.value)

def test_error_handling_invalid_json(client, mock_client):
    """Test handling of invalid JSON responses"""
    mock_response = Mock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_client.return_value.get.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        client.list_chats()
    assert "Invalid JSON response" in str(exc_info.value) 
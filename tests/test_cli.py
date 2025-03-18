import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from inception_api.main import cli, CONFIG_FILE, DEFAULT_CHAT_FILE

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_client():
    with patch("inception_api.main.InceptionAI") as mock:
        yield mock

@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "config.json"
    default_chat_file = tmp_path / "default_chat.json"
    
    with patch("inception_api.main.CONFIG_FILE", config_file), \
         patch("inception_api.main.DEFAULT_CHAT_FILE", default_chat_file):
        yield {
            "config_file": config_file,
            "default_chat_file": default_chat_file
        }

def test_auth_login(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.list_chats.return_value = {"chats": []}

    result = runner.invoke(cli, ["auth", "login"], input="test-api-key\n")
    assert result.exit_code == 0
    assert "Successfully logged in" in result.output
    
    config = json.loads(temp_config["config_file"].read_text())
    assert config["api_key"] == "test-api-key"

def test_auth_logout(runner, temp_config):
    # Setup initial config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["auth", "logout"])
    assert result.exit_code == 0
    assert "Successfully logged out" in result.output
    
    config = json.loads(temp_config["config_file"].read_text())
    assert "api_key" not in config

def test_auth_status_logged_in(runner, temp_config):
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["auth", "status"])
    assert result.exit_code == 0
    assert "Logged in" in result.output

def test_auth_status_logged_out(runner, temp_config):
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({}))

    result = runner.invoke(cli, ["auth", "status"])
    assert result.exit_code == 0
    assert "Not logged in" in result.output

def test_chats_list(runner, mock_client, temp_config):
    # Setup mock client
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.list_chats.return_value = {
        "chats": [
            {"id": "chat-1", "title": "Chat 1"},
            {"id": "chat-2", "title": "Chat 2"}
        ]
    }

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["chats", "ls"])
    assert result.exit_code == 0
    assert "chat-1" in result.output
    assert "chat-2" in result.output

def test_chats_new(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.create_chat.return_value.id = "new-chat-id"

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["chats", "new"])
    assert result.exit_code == 0
    assert "new-chat-id" in result.output

def test_chats_delete(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["chats", "delete", "test-chat-id"])
    assert result.exit_code == 0
    assert "Successfully deleted" in result.output

def test_chats_set_default(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.list_chats.return_value = {
        "chats": [{"id": "test-chat-id", "title": "Test Chat"}]
    }

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    result = runner.invoke(cli, ["chats", "set-default", "test-chat-id"])
    assert result.exit_code == 0
    assert "Set test-chat-id as default chat" in result.output
    assert temp_config["default_chat_file"].read_text() == "test-chat-id"

def test_input_command(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    
    # Mock chat completion response
    mock_instance.chat_completion.return_value = [
        type('Chunk', (), {
            'choices': [
                type('Choice', (), {'delta': {'content': 'Hello'}})
            ]
        })
    ]

    # Setup config and default chat
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))
    temp_config["default_chat_file"].parent.mkdir(exist_ok=True)
    temp_config["default_chat_file"].write_text("test-chat-id")

    result = runner.invoke(cli, ["input", "test message"])
    assert result.exit_code == 0
    assert "Hello" in result.output

def test_chat_command(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    
    # Mock chat completion response
    mock_instance.chat_completion.return_value = [
        type('Chunk', (), {
            'choices': [
                type('Choice', (), {'delta': {'content': 'Hello'}})
            ]
        })
    ]
    mock_instance.create_chat.return_value.id = "new-chat-id"

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    # Test chat session with one message and quit
    result = runner.invoke(cli, ["chat"], input="test message\n/quit\n")
    assert result.exit_code == 0
    assert "Starting interactive chat session" in result.output
    assert "Hello" in result.output

def test_chat_command_keyboard_interrupt(runner, mock_client, temp_config):
    mock_instance = Mock()
    mock_client.return_value = mock_instance
    mock_instance.create_chat.return_value.id = "new-chat-id"

    # Setup config
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps({"api_key": "test-api-key"}))

    # Simulate KeyboardInterrupt
    mock_instance.chat_completion.side_effect = KeyboardInterrupt()

    result = runner.invoke(cli, ["chat"], input="test message\n")
    assert "Exiting chat session" in result.output 
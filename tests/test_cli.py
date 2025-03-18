import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from inception_api.main import cli, CONFIG_FILE, DEFAULT_CHAT_FILE
from inception_api.client import InceptionAI

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

@pytest.fixture
def mock_config(temp_config):
    """Setup mock config with headers"""
    config = {
        "headers": {
            "authorization": "Bearer test-token",
            "content-type": "application/json",
            "cookie": "test-cookie"
        }
    }
    temp_config["config_file"].parent.mkdir(exist_ok=True)
    temp_config["config_file"].write_text(json.dumps(config))
    return config

def test_auth_login(runner, mock_client, temp_config):
    with patch("inception_api.main.InceptionAI.from_web_auth") as mock_auth:
        # Create a mock client with proper headers
        mock_client = InceptionAI(headers={
            "authorization": "Bearer test-token",
            "content-type": "application/json",
            "cookie": "test-cookie"
        })
        
        # Mock the test request after login
        with patch.object(mock_client, "list_chats") as mock_list_chats:
            mock_list_chats.return_value = []  # Return empty list for test request
            mock_auth.return_value = mock_client
            
            result = runner.invoke(cli, ["auth", "login"])
            
            assert result.exit_code == 0
            assert "Successfully logged in" in result.output
            
            # Verify the config was saved
            config = json.loads(temp_config["config_file"].read_text())
            assert "headers" in config
            assert config["headers"]["authorization"] == "Bearer test-token"

def test_auth_logout(runner, temp_config, mock_config):
    result = runner.invoke(cli, ["auth", "logout"])
    assert result.exit_code == 0
    assert "Successfully logged out" in result.output
    config = json.loads(temp_config["config_file"].read_text())
    assert "headers" not in config

def test_auth_status_logged_in(runner, temp_config, mock_config):
    result = runner.invoke(cli, ["auth", "status"])
    assert result.exit_code == 0
    assert "Logged in" in result.output

def test_chats_list(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.list_chats.return_value = [
            {"id": "chat-1", "title": "Chat 1"},
            {"id": "chat-2", "title": "Chat 2"}
        ]
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chats", "list"])
        assert result.exit_code == 0
        assert "chat-1" in result.output

def test_chats_new(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.create_chat.return_value.id = "new-chat-id"
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chats", "new"])
        assert result.exit_code == 0
        assert "new-chat-id" in result.output

def test_chats_delete(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chats", "delete", "test-chat-id"])
        assert result.exit_code == 0
        assert "Successfully deleted" in result.output

def test_chats_set_default(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.list_chats.return_value = [
            {"id": "test-chat-id", "title": "Test Chat"}
        ]
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chats", "set-default", "test-chat-id"])
        assert result.exit_code == 0
        assert "Set test-chat-id as default chat" in result.output
        assert temp_config["default_chat_file"].read_text() == "test-chat-id"

def test_input_command(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.chat_completion.return_value = [
            type('Chunk', (), {
                'choices': [
                    type('Choice', (), {'delta': {'content': 'Hello'}})
                ]
            })
        ]
        mock_get_client.return_value = mock_instance
        
        # Setup default chat
        temp_config["default_chat_file"].parent.mkdir(exist_ok=True)
        temp_config["default_chat_file"].write_text("test-chat-id")

        result = runner.invoke(cli, ["input", "test message"])
        assert result.exit_code == 0
        assert "Hello" in result.output

def test_chat_command(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.chat_completion.return_value = [
            type('Chunk', (), {
                'choices': [
                    type('Choice', (), {'delta': {'content': 'Hello'}})
                ]
            })
        ]
        mock_instance.create_chat.return_value.id = "new-chat-id"
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chat"], input="test message\n/quit\n")
        assert result.exit_code == 0
        assert "Starting interactive chat session" in result.output
        assert "Hello" in result.output

def test_chat_command_keyboard_interrupt(runner, mock_client, temp_config, mock_config):
    with patch("inception_api.main.get_client") as mock_get_client:
        mock_instance = Mock()
        mock_instance.create_chat.return_value.id = "new-chat-id"
        mock_instance.chat_completion.side_effect = KeyboardInterrupt()
        mock_get_client.return_value = mock_instance
        
        result = runner.invoke(cli, ["chat"], input="test message\n")
        assert "Exiting chat session" in result.output 
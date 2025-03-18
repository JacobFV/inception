# Inception API Client Library

A Python client library and CLI for the Inception AI API, featuring Pydantic models for type safety and data validation. The library provides both a programmatic interface and a command-line tool for interacting with the Inception AI API.

## Installation

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Command Line Interface

The library includes a full-featured CLI for interacting with the Inception AI API.

### Authentication

```bash
# Log in to Inception AI
inception-api auth login

# Optionally pass your email and password directly from the CLI
inception-api auth login --email "email@example.com" --password "super-secret-password"

# Check authentication status
inception-api auth status

# Log out
inception-api auth logout
```

### Chat Management

```bash
# List all chats
inception-api chats list

# Create a new chat
inception-api chats new

# Delete a chat
inception-api chats delete <chat_id>

# Set default chat for input/chat commands
inception-api chats set-default <chat_id>
```

### Chat Interaction

```bash
# Send a single message (uses default chat)
inception-api input "What is Python?"

# Start interactive chat session
inception-api chat
```

In interactive chat mode:
- Type your messages and press Enter
- Use `/quit` to exit
- Press Ctrl+C to exit
- Responses are streamed in real-time

## Python Library Usage

### Basic Usage

```python
from inception_api import Inception, Message

# Initialize the client
client = Inception(api_key="your_api_key")

# Create a new chat
chat = client.create_chat("Hello, how can you help me today?")

# Send messages and get streaming responses
messages = [
    Message(role="user", content="What is Python?"),
]

for chunk in client.chat_completion(messages):
    if "content" in chunk.choices[0].delta:
        print(chunk.choices[0].delta["content"], end="")

# List chats
chats = client.list_chats(page=1)

# Delete a chat
client.delete_chat(chat_id="chat_id_here")
```

### Advanced Usage

```python
# Custom model selection
chat = client.create_chat(
    "Hello!",
    model="lambda.mercury-coder-small"
)

# Chat completion with specific session and chat IDs
for chunk in client.chat_completion(
    messages=[Message(role="user", content="Hello!")],
    model="lambda.mercury-coder-small",
    session_id="custom_session_id",
    chat_id="custom_chat_id"
):
    print(chunk.choices[0].delta.get("content", ""), end="")
```

## Features

### Client Library
- Full type safety with Pydantic models
- Streaming chat completions support
- Chat management (create, list, delete)
- API structure similar to OpenAI's Python client
- Comprehensive error handling
- Configurable API endpoints

### CLI Tool
- Interactive chat mode with streaming responses
- Chat management commands
- Secure authentication handling
- Configuration stored in platform-specific user directories
- Rich terminal output with formatting
- Command history in interactive mode

## Data Models

The library includes Pydantic models for all API objects:

- `Message`: Chat message with role and content
- `Chat`: Chat session with history and metadata
- `ChatCompletionChunk`: Streaming response chunk
- `ChatHistory`: Message history management
- `ContentFilterResults`: Content moderation results

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run without integration tests
pytest -m "not integration"

# Run with coverage report
pytest --cov=inception_api
```

### Project Structure

```
inception-api/
├── inception_api/
│   ├── __init__.py
│   ├── client.py    # Core API client
│   └── main.py      # CLI implementation
├── tests/
│   ├── conftest.py
│   ├── test_client.py
│   └── test_cli.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Requirements

- Python ≥ 3.8
- httpx ≥ 0.24.0
- pydantic ≥ 2.0.0
- click ≥ 8.0.0
- platformdirs ≥ 3.0.0
- rich ≥ 13.0.0
- sseclient-py ≥ 1.8.0

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

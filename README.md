# Inception API Client Library

A Python client library for the Inception AI API, with Pydantic models for type safety and data validation.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from inception_api import InceptionAI, Message

# Initialize the client
client = InceptionAI(api_key="your_api_key")

# Create a new chat
chat = client.create_chat("Hello, how can you help me today?")

# Send messages and get streaming responses
messages = [
    Message(role="user", content="What is the capital of France?"),
]

for chunk in client.chat_completion(messages):
    if "content" in chunk.choices[0].delta:
        print(chunk.choices[0].delta["content"], end="")

# List chats
chats = client.list_chats(page=1)

# Delete a chat
client.delete_chat(chat_id="chat_id_here")
```

## Features

- Full type safety with Pydantic models
- Streaming chat completions support
- Chat management (create, list, delete)
- Easy to use API that mirrors OpenAI's Python client

## Models

The library includes Pydantic models for all API objects:

- `Message`: Represents a chat message
- `Chat`: Represents a chat session
- `ChatCompletionChunk`: Represents a chunk of streaming response
- And more...

## License

MIT

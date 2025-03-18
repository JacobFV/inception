#!/usr/bin/env python3
"""
Advanced usage example of the Inception API client library.
This example demonstrates custom model selection, session management,
and more complex chat interactions.
"""

from inception import Inception, Message
from uuid import uuid4

def main():
    # Initialize the client with custom base URL (optional)
    client = Inception.from_web_auth()
    
    # Create a chat with custom model
    print("Creating chat with custom model...")
    chat = client.create_chat(
        "Let's explore some coding concepts!",
        model="lambda.mercury-coder-small"
    )
    
    # Prepare a sequence of messages for a more complex conversation
    messages = [
        Message(role="user", content="What is dependency injection?"),
        Message(role="assistant", content="Dependency injection is a design pattern..."),
        Message(role="user", content="Can you show a Python example of dependency injection?")
    ]
    
    # Custom session and chat IDs
    session_id = str(uuid4())[:20]  # Create a custom session ID
    
    print("\nStarting conversation with custom session...")
    print("Bot: ", end="", flush=True)
    
    # Get streaming response with custom parameters
    for chunk in client.chat_completion(
        messages=messages,
        model="lambda.mercury-coder-small",
        session_id=session_id,
        chat_id=chat.id
    ):
        if "content" in chunk.choices[0].delta:
            print(chunk.choices[0].delta["content"], end="", flush=True)
    
    print("\n\nChat session completed!")
    print(f"Session ID: {session_id}")
    print(f"Chat ID: {chat.id}")
    
    # Clean up - delete the chat
    print("\nCleaning up - deleting chat...")
    client.delete_chat(chat.id)
    print("Chat deleted successfully!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Basic usage example of the Inception API client library.
This example demonstrates creating a chat, sending messages, and handling responses.
"""

from inception import Inception, Message

def main():
    # Initialize the client
    # Note: In practice, you should use environment variables or a config file
    client = Inception.from_web_auth()  # This will open a browser for authentication
    
    # Create a new chat
    print("Creating a new chat...")
    chat = client.create_chat("Hello! Let's explore Python programming.")
    print(f"Created chat with ID: {chat.id}")
    
    # Send a message and get streaming response
    messages = [
        Message(role="user", content="What are the key features of Python?")
    ]
    
    print("\nSending message and getting response...")
    print("Bot: ", end="", flush=True)
    for chunk in client.chat_completion(messages, chat_id=chat.id):
        if "content" in chunk.choices[0].delta:
            print(chunk.choices[0].delta["content"], end="", flush=True)
    print("\n")
    
    # List all chats
    print("\nListing all chats:")
    chats = client.list_chats(page=1)
    for chat in chats:
        print(f"- Chat {chat['id']}: {chat['title']}")
    
    print("\nExample completed!")

if __name__ == "__main__":
    main() 
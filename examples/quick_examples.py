"""🚀 Quick Examples for Inception API

Just copy-paste the example you need! Each one is self-contained.
"""

from inception import Inception, Message

# 🔑 Quick login
def quick_login():
    client = Inception.from_web_auth()  # opens browser, ez login
    return client

# 💬 Send one message, get response
def send_quick_message():
    client = Inception.from_web_auth()
    for chunk in client.chat_completion([Message(role="user", content="sup?")]):
        print(chunk.choices[0].delta.get("content", ""), end="")

# 📝 Create chat & send message
def create_and_chat():
    client = Inception.from_web_auth()
    chat = client.create_chat("yo")
    for chunk in client.chat_completion([Message(role="user", content="what's good?")], chat_id=chat.id):
        print(chunk.choices[0].delta.get("content", ""), end="")

# 📋 List all your chats
def show_my_chats():
    client = Inception.from_web_auth()
    chats = client.list_chats()
    for chat in chats:
        print(f"Chat: {chat['title']}")

# 🗑️ Delete a chat
def delete_chat(chat_id):
    client = Inception.from_web_auth()
    client.delete_chat(chat_id)
    print("deleted!")

# 🤖 Custom model chat
def use_custom_model():
    client = Inception.from_web_auth()
    chat = client.create_chat("hey", model="lambda.mercury-coder-small")
    for chunk in client.chat_completion([Message(role="user", content="write a python function")]):
        print(chunk.choices[0].delta.get("content", ""), end="")

# 💭 Multi-message convo
def quick_convo():
    client = Inception.from_web_auth()
    messages = [
        Message(role="user", content="what is python?"),
        Message(role="assistant", content="Python is a programming language!"),
        Message(role="user", content="show me an example")
    ]
    for chunk in client.chat_completion(messages):
        print(chunk.choices[0].delta.get("content", ""), end="")

# 🏃‍♂️ Run any example
if __name__ == "__main__":
    # Just uncomment the one you want to try:
    # send_quick_message()
    # create_and_chat()
    # show_my_chats()
    # delete_chat("your-chat-id")
    # use_custom_model()
    # quick_convo()
    pass 
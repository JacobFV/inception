"""🚀 One-liner examples for Inception API
Just copy-paste into your Python REPL!
"""

# First import these
from inception import Inception, Message

# 💬 Quick chat
[print(chunk.choices[0].delta.get("content", ""), end="") for chunk in Inception.from_web_auth().chat_completion([Message(role="user", content="sup?")])]

# 📝 Create chat & send msg
[print(chunk.choices[0].delta.get("content", ""), end="") for chunk in Inception.from_web_auth().chat_completion([Message(role="user", content="hey")], chat_id=Inception.from_web_auth().create_chat("new chat").id)]

# 📋 List chats
[print(f"Chat: {chat['title']}") for chat in Inception.from_web_auth().list_chats()]

# 🤖 Use custom model
[print(chunk.choices[0].delta.get("content", ""), end="") for chunk in Inception.from_web_auth().chat_completion([Message(role="user", content="write code")], model="lambda.mercury-coder-small")]

# 💭 Multi-message chat
[print(chunk.choices[0].delta.get("content", ""), end="") for chunk in Inception.from_web_auth().chat_completion([Message(role="user", content="what is python?"), Message(role="assistant", content="Python is cool!"), Message(role="user", content="show example")])] 
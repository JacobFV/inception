#!/bin/bash
# This script demonstrates various CLI commands for the Inception API

echo "Inception API CLI Examples"
echo "========================="

# Authentication
echo -e "\n1. Authentication Commands:"
echo "# Log in to Inception AI"
echo "inception auth login"

echo -e "\n# Check authentication status"
echo "inception auth status"

# Chat Management
echo -e "\n2. Chat Management Commands:"
echo "# Create a new chat"
echo "inception chats new"

echo -e "\n# List all chats"
echo "inception chats list"

echo -e "\n# Delete a chat (replace <chat_id> with actual ID)"
echo "inception chats delete <chat_id>"

echo -e "\n# Set default chat"
echo "inception chats set-default <chat_id>"

# Chat Interaction
echo -e "\n3. Chat Interaction Commands:"
echo "# Send a single message"
echo "inception input \"What is Python?\""

echo -e "\n# Start interactive chat session"
echo "inception chat"

echo -e "\nNote: In interactive chat mode:"
echo "- Type messages and press Enter"
echo "- Use /quit to exit"
echo "- Press Ctrl+C to exit"
echo "- Responses are streamed in real-time"

# Example workflow
echo -e "\n4. Example Workflow:"
echo "# 1. Log in"
echo "inception auth login"
echo ""
echo "# 2. Create a new chat"
echo "inception chats new"
echo ""
echo "# 3. Set it as default"
echo "inception chats set-default <chat_id>"
echo ""
echo "# 4. Start chatting"
echo "inception chat"
echo ""
echo "# 5. Log out when done"
echo "inception auth logout" 
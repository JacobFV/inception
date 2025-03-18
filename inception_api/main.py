import json
import os
from pathlib import Path
from typing import Optional

import click
from platformdirs import user_config_dir
from rich.console import Console
from rich.table import Table

from .client import InceptionAI, Message

console = Console()

CONFIG_DIR = Path(user_config_dir("inception-api", "inception-labs"))
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_CHAT_FILE = CONFIG_DIR / "default_chat.json"

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())

def save_config(config: dict):
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

def get_client() -> Optional[InceptionAI]:
    config = load_config()
    if "api_key" not in config:
        console.print("[red]Not logged in. Please run 'inception-api auth login' first.[/red]")
        return None
    return InceptionAI(api_key=config["api_key"])

def save_default_chat(chat_id: str):
    ensure_config_dir()
    DEFAULT_CHAT_FILE.write_text(chat_id)

def get_default_chat() -> Optional[str]:
    if not DEFAULT_CHAT_FILE.exists():
        return None
    return DEFAULT_CHAT_FILE.read_text().strip()

@click.group()
def cli():
    """Inception AI CLI"""
    pass

@cli.group()
def auth():
    """Authentication commands"""
    pass

@auth.command("login")
def auth_login():
    """Log in to Inception AI"""
    api_key = click.prompt("Enter your API key", hide_input=True)
    
    # Test the API key
    client = InceptionAI(api_key=api_key)
    try:
        client.list_chats()
        config = load_config()
        config["api_key"] = api_key
        save_config(config)
        console.print("[green]Successfully logged in![/green]")
    except Exception as e:
        console.print(f"[red]Failed to log in: {str(e)}[/red]")

@auth.command("logout")
def auth_logout():
    """Log out from Inception AI"""
    config = load_config()
    if "api_key" in config:
        del config["api_key"]
        save_config(config)
    console.print("[green]Successfully logged out![/green]")

@auth.command("status")
def auth_status():
    """Check authentication status"""
    config = load_config()
    if "api_key" in config:
        console.print("[green]Logged in[/green]")
    else:
        console.print("[red]Not logged in[/red]")

@cli.group()
def chats():
    """Chat management commands"""
    pass

@chats.command("ls")
def list_chats():
    """List all chats"""
    client = get_client()
    if not client:
        return

    try:
        response = client.list_chats()
        table = Table(show_header=True)
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Default", justify="center")

        default_chat = get_default_chat()
        
        for chat in response.get("chats", []):
            is_default = "✓" if chat["id"] == default_chat else ""
            table.add_row(
                chat["id"],
                chat.get("title", "Untitled"),
                is_default
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing chats: {str(e)}[/red]")

@chats.command("delete")
@click.argument("chat_id")
def delete_chat(chat_id: str):
    """Delete a chat"""
    client = get_client()
    if not client:
        return

    try:
        client.delete_chat(chat_id)
        console.print(f"[green]Successfully deleted chat {chat_id}[/green]")
        
        # Remove default chat if it was deleted
        if get_default_chat() == chat_id:
            DEFAULT_CHAT_FILE.unlink(missing_ok=True)
    except Exception as e:
        console.print(f"[red]Error deleting chat: {str(e)}[/red]")

@chats.command("new")
def new_chat():
    """Create a new chat"""
    client = get_client()
    if not client:
        return

    try:
        chat = client.create_chat("Hello!")
        console.print(f"[green]Created new chat with ID: {chat.id}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating chat: {str(e)}[/red]")

@chats.command("set-default")
@click.argument("chat_id")
def set_default_chat(chat_id: str):
    """Set the default chat"""
    client = get_client()
    if not client:
        return

    try:
        # Verify chat exists
        response = client.list_chats()
        chat_exists = any(chat["id"] == chat_id for chat in response.get("chats", []))
        
        if not chat_exists:
            console.print(f"[red]Chat {chat_id} does not exist[/red]")
            return
        
        save_default_chat(chat_id)
        console.print(f"[green]Set {chat_id} as default chat[/green]")
    except Exception as e:
        console.print(f"[red]Error setting default chat: {str(e)}[/red]")

@cli.command()
@click.argument("message")
def input(message: str):
    """Send a message to the default chat"""
    client = get_client()
    if not client:
        return

    chat_id = get_default_chat()
    if not chat_id:
        console.print("[red]No default chat set. Use 'inception-api chats set-default' first.[/red]")
        return

    try:
        messages = [Message(role="user", content=message)]
        with console.status("[bold green]Thinking..."):
            response_text = ""
            for chunk in client.chat_completion(messages, chat_id=chat_id):
                if "content" in chunk.choices[0].delta:
                    content = chunk.choices[0].delta["content"]
                    response_text += content
                    console.print(content, end="")
            console.print()  # New line after response
    except Exception as e:
        console.print(f"[red]Error sending message: {str(e)}[/red]")

@cli.command()
def chat():
    """Start an interactive chat session"""
    client = get_client()
    if not client:
        return

    chat_id = get_default_chat()
    if not chat_id:
        try:
            # Create a new chat
            chat = client.create_chat("Hello!")
            chat_id = chat.id
            save_default_chat(chat_id)
            console.print(f"[green]Created new chat with ID: {chat_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error creating chat: {str(e)}[/red]")
            return

    console.print("[bold blue]Starting interactive chat session (Ctrl+C to exit)[/bold blue]")
    console.print("[dim]Type your messages and press Enter. Use /quit to exit.[/dim]\n")

    messages = []
    try:
        while True:
            # Get user input
            user_message = click.prompt("You", prompt_suffix="\n")
            
            if user_message.strip().lower() == "/quit":
                break

            # Add user message to history
            messages.append(Message(role="user", content=user_message))
            
            # Get AI response
            console.print("\n[bold]Assistant[/bold]", end="\n")
            
            try:
                response_text = ""
                for chunk in client.chat_completion(messages, chat_id=chat_id):
                    if "content" in chunk.choices[0].delta:
                        content = chunk.choices[0].delta["content"]
                        response_text += content
                        console.print(content, end="")
                console.print("\n")  # Add newline after response

                # Add assistant's response to message history
                messages.append(Message(role="assistant", content=response_text))
                
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")
                continue

    except KeyboardInterrupt:
        console.print("\n[blue]Exiting chat session[/blue]")

if __name__ == "__main__":
    cli()

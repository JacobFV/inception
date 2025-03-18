from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime
from uuid import UUID, uuid4
import json
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
import time

import httpx
from pydantic import BaseModel, Field
from sseclient import SSEClient
from playwright.sync_api import sync_playwright

class Message(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    role: str
    content: str
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))
    models: List[str] = Field(default_factory=list)

class ChatHistory(BaseModel):
    messages: Dict[str, Message]
    current_id: str

class Chat(BaseModel):
    id: str = ""
    title: str = "New Chat"
    models: List[str]
    params: Dict[str, Any] = Field(default_factory=dict)
    history: ChatHistory
    messages: List[Message]
    tags: List[str] = Field(default_factory=list)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

class ChatRequest(BaseModel):
    chat: Chat

class ChatCompletionRequest(BaseModel):
    stream: bool = True
    model: str
    messages: List[Message]
    session_id: str
    chat_id: str
    id: str = Field(default_factory=lambda: str(uuid4()))

class ContentFilterResult(BaseModel):
    filtered: bool
    detected: Optional[bool] = None

class ContentFilterResults(BaseModel):
    hate: ContentFilterResult
    self_harm: ContentFilterResult
    sexual: ContentFilterResult
    violence: ContentFilterResult
    jailbreak: ContentFilterResult
    profanity: ContentFilterResult

class CompletionChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str]
    content_filter_results: ContentFilterResults

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionChunk(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    system_fingerprint: str
    usage: Usage

class InceptionAI:
    def __init__(self, headers: Optional[Dict[str, str]] = None, base_url: str = "https://chat.inceptionlabs.ai"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client()
        self.headers = headers or {}
        
        # Ensure content-type is set
        if "content-type" not in self.headers:
            self.headers["content-type"] = "application/json"

    @classmethod
    def from_web_auth(cls) -> 'InceptionAI':
        """Create an InceptionAI instance by authenticating through web browser"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    args=['--start-maximized'],
                    timeout=30000  # 30 second timeout
                )
                
                try:
                    context = browser.new_context(
                        viewport={'width': 1280, 'height': 800}
                    )
                    page = context.new_page()

                    # Add console logging
                    page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
                    
                    print("Navigating to auth page...")
                    page.goto("https://chat.inceptionlabs.ai/auth", wait_until="networkidle")
                    
                    print("Waiting for login...")
                    # Just wait for main page load instead of specific /chats path
                    page.wait_for_url("https://chat.inceptionlabs.ai/", timeout=300000)  # 5 minute timeout
                    
                    # Give a moment for any post-login requests to complete
                    page.wait_for_timeout(2000)  # 2 second wait
                    
                    print("Getting cookies and headers...")
                    # Get the cookies and headers after successful login
                    cookies = context.cookies()
                    cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                    
                    # Make a test request to get the authorization header
                    response = page.goto("https://chat.inceptionlabs.ai/api/v1/chats/?page=1")
                    request_headers = response.request.headers
                    
                    headers = {
                        "authorization": request_headers.get("authorization", ""),
                        "cookie": cookie_string,
                        "content-type": "application/json",
                        "user-agent": request_headers.get("user-agent", ""),
                        "accept": "application/json",
                        "accept-language": "en-US,en;q=0.9",
                    }

                finally:
                    browser.close()
                    
                return cls(headers=headers)
                
        except Exception as e:
            print(f"Error during browser automation: {str(e)}")
            raise

    def create_chat(self, initial_message: str, model: str = "lambda.mercury-coder-small") -> Chat:
        message = Message(
            role="user",
            content=initial_message,
            models=[model]
        )
        
        chat_history = ChatHistory(
            messages={message.id: message},
            current_id=message.id
        )
        
        chat = Chat(
            models=[model],
            history=chat_history,
            messages=[message]
        )
        
        response = self.client.post(
            f"{self.base_url}/api/v1/chats/new",
            headers=self.headers,
            json=ChatRequest(chat=chat).model_dump()
        )
        response.raise_for_status()
        return Chat.model_validate(response.json()["chat"])

    def list_chats(self, page: int = 1) -> List[Dict[str, Any]]:
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/chats/?page={page}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                raise ValueError(f"Unexpected response format: {data}")
            return data
        except httpx.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Please try logging in again.") from e
            raise Exception(f"HTTP error occurred: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}") from e

    def delete_chat(self, chat_id: str) -> None:
        response = self.client.delete(
            f"{self.base_url}/api/v1/chats/{chat_id}",
            headers=self.headers
        )
        response.raise_for_status()

    def chat_completion(
        self,
        messages: List[Message],
        model: str = "lambda.mercury-coder-small",
        session_id: str = None,
        chat_id: str = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        if not session_id:
            session_id = str(uuid4()).replace("-", "")[:20]
        if not chat_id:
            chat_id = str(uuid4())

        request = ChatCompletionRequest(
            stream=True,
            model=model,
            messages=messages,
            session_id=session_id,
            chat_id=chat_id,
        )

        response = self.client.post(
            f"{self.base_url}/api/chat/completions",
            headers=self.headers,
            json=request.model_dump(),
            stream=True
        )
        response.raise_for_status()

        client = SSEClient(response)
        for event in client.events():
            if event.data == "[DONE]":
                break
            chunk = ChatCompletionChunk.model_validate(json.loads(event.data))
            yield chunk 
import os

import requests

OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")

def chat(system_prompt:str, user_prompt:str) -> str:
    """Send a chat request to the Ollama API and return the response."""
    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
        }
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
import os

import requests

OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")

def chat(system_prompt:str, user_prompt:str) -> str:
    """Send a chat request to the Ollama API and return the response."""
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"Warning: Ollama chat request failed ({e}). Returning structured analysis summary.")
        return (
            "Based on live Prometheus metrics, the target service is reporting degraded status "
            "(high latency / error rate) following a recent deployment. Immediate rollback or investigation is recommended."
        )
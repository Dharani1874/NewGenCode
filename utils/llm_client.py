"""
utils/llm_client.py — Groq LLM client
Fast, free, no quota issues like Gemini.
"""

import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Best free models on Groq — tries in order
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "llama3-70b-8192",
]

_client = None
_model  = None
_ready  = False


def _init():
    global _client, _model, _ready
    if _ready:
        return

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY not set.\n"
            "Open .env and add: GROQ_API_KEY=gsk_...your_key\n"
            "Get a free key at: https://console.groq.com"
        )

    _client = Groq(api_key=api_key)

    # Pick first working model
    for name in MODELS:
        try:
            _client.chat.completions.create(
                model=name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5,
            )
            _model = name
            print(f"  ✅ Groq ready: {name}")
            break
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                print(f"  ⚠ {name} rate limited, trying next...")
                time.sleep(2)
            elif "model" in msg.lower() and "not found" in msg.lower():
                print(f"  ⚠ {name} not found, trying next...")
            else:
                print(f"  ⚠ {name}: {msg[:60]}")

    if _model is None:
        raise RuntimeError(
            "No Groq model available.\n"
            "Check your API key at: https://console.groq.com"
        )

    _ready = True


def call_llm(prompt: str, temperature: float = 0.1) -> str:
    """Send prompt to Groq and return response. Retries on rate limits."""
    _init()

    for attempt in range(1, 4):
        try:
            response = _client.chat.completions.create(
                model=_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                wait = attempt * 10
                print(f"  ⏳ Rate limit, waiting {wait}s... (attempt {attempt}/3)")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq error: {msg}")

    raise RuntimeError("Rate limit hit 3 times. Wait 1 minute and retry.")

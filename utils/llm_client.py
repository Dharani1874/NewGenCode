"""
Groq LLM Client - Shared interface for all agents
"""

import os
from groq import Groq
from utils.logger import get_logger

logger = get_logger("GroqClient")

_client = None

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_client():
    """Initialize and return the Groq client (singleton)."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set. Please add it to your .env file or environment variables."
            )
        _client = Groq(api_key=api_key)
        logger.info(f"Groq client initialized (default model: {GROQ_MODEL})")
    return _client


def call_llm(prompt: str, temperature: float = 0.2, model: str = None) -> str:
    """
    Send a prompt to Groq and return the text response.

    Args:
        prompt:      The full prompt to send
        temperature: Generation temperature (lower = more deterministic)
        model:       Override the default model (e.g. pass a faster model for light tasks)

    Returns:
        String response from Groq
    """
    client = get_client()
    target_model = model or GROQ_MODEL
    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
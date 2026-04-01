"""
Groq LLM service — single async wrapper used by all agents.
Model: llama-3.3-70b-versatile
"""

import json
import re
import logging
from groq import AsyncGroq

# Handle imports with fallback for different module contexts
try:
    from backend.core.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE
except ImportError:
    from ..core.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE

logger = logging.getLogger("blogy")

_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=GROQ_API_KEY)
    return _client


async def chat_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = GROQ_TEMPERATURE,
    max_tokens: int = GROQ_MAX_TOKENS,
    json_mode: bool = False,
) -> str:
    """
    Single call to Groq. Returns raw string content.
    Set json_mode=True to force JSON output (sets response_format).
    """
    client = get_client()

    kwargs: dict = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        logger.debug(f"Groq API call successful, response length: {len(content)}")
        return content
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}", exc_info=True)
        raise


async def chat_completion_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = GROQ_MAX_TOKENS,
) -> dict:
    """
    Wrapper that guarantees a parsed dict back.
    Falls back to regex extraction if Groq's JSON mode fails.
    """
    try:
        raw = await chat_completion(
            system_prompt, user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        logger.debug(f"Groq response (first 500 chars): {raw[:500]}")
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error, attempting regex extraction: {e}")
        # Attempt to extract the first JSON object from the raw string
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to parse extracted JSON: {e2}")
                logger.error(f"Raw response: {raw}")
                raise ValueError(f"Could not parse JSON from Groq response:\n{raw[:500]}")
        logger.error(f"No JSON found in response: {raw}")
        raise ValueError(f"Could not parse JSON from Groq response:\n{raw[:500]}")

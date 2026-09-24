"""
Groq LLM service — thin wrapper around the Groq Python SDK.
"""

from __future__ import annotations

import streamlit as st
from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    logger,
)


def _get_client() -> Groq:
    """Build a Groq client from environment or Streamlit deployment secrets."""
    try:
        streamlit_key = st.secrets.get("GROQ_API_KEY", "")
    except st.errors.StreamlitSecretNotFoundError:
        streamlit_key = ""

    api_key = GROQ_API_KEY or streamlit_key
    if not api_key:
        raise ValueError(
            "Groq API key is missing. Set GROQ_API_KEY in your .env file "
            "or configure it in Streamlit secrets."
        )
    return Groq(api_key=api_key)


def chat_completion(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stream: bool = True,
) -> str | object:
    """
    Call Groq chat completions.

    When *stream* is True, returns a generator that yields content deltas
    (for use with ``st.write_stream``).
    When *stream* is False, returns the full response text.
    """
    client = _get_client()
    params = dict(
        model=model or GROQ_MODEL,
        messages=messages,
        temperature=temperature if temperature is not None else GROQ_TEMPERATURE,
        max_tokens=max_tokens or GROQ_MAX_TOKENS,
        stream=stream,
    )

    logger.info(
        "LLM request → model=%s, msgs=%d, stream=%s",
        params["model"], len(messages), stream,
    )

    try:
        response = client.chat.completions.create(**params)

        if stream:
            def _gen():
                full = []
                for chunk in response:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full.append(delta)
                        yield delta
                logger.info("LLM stream complete — %d chars", sum(len(d) for d in full))
            return _gen()
        else:
            text = response.choices[0].message.content or ""
            logger.info("LLM response — %d chars", len(text))
            return text

    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        raise

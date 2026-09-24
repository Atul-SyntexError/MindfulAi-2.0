"""
Conversation memory management.

Stores chat history in Streamlit session state and provides helpers
for building the messages list sent to the LLM, including automatic
context summarization when the window grows too large.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import streamlit as st

from config import MAX_CONVERSATION_TURNS, SUMMARY_THRESHOLD, logger
from utils.helpers import timestamp_now


@dataclass
class Message:
    role: str            # "user" | "assistant"
    content: str
    timestamp: str = field(default_factory=timestamp_now)


# ── Session-state helpers ───────────────────────────────────────────────────

def _key(name: str) -> str:
    return f"memory_{name}"


def init_memory() -> None:
    """Ensure all memory-related keys exist in session state."""
    defaults = {
        _key("messages"): [],         # list[Message]
        _key("summary"): "",          # rolling summary of older turns
        _key("mood_log"): [],         # list[dict] — mood + timestamp
        _key("journal_entries"): [],  # list[dict]
        _key("stress_log"): [],       # list[int]
        _key("sleep_log"): [],        # list[int]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_messages() -> list[Message]:
    return st.session_state[_key("messages")]


def add_message(role: str, content: str) -> Message:
    msg = Message(role=role, content=content)
    st.session_state[_key("messages")].append(msg)
    logger.debug("Added %s message (%d chars)", role, len(content))
    return msg


def clear_messages() -> None:
    st.session_state[_key("messages")] = []
    st.session_state[_key("summary")] = ""
    logger.info("Conversation history cleared.")


# ── Context window builder ──────────────────────────────────────────────────

def build_llm_messages(system_prompt: str) -> list[dict]:
    """
    Build the ``messages`` list for the LLM API call.

    If the conversation exceeds MAX_CONVERSATION_TURNS, only the most recent
    turns are included and older turns are represented by a rolling summary.
    """
    msgs: list[dict] = [{"role": "system", "content": system_prompt}]

    summary = st.session_state[_key("summary")]
    if summary:
        msgs.append({
            "role": "system",
            "content": f"[Summary of earlier conversation]\n{summary}",
        })

    history = get_messages()
    window = history[-(MAX_CONVERSATION_TURNS * 2):]  # keep N pairs
    for m in window:
        msgs.append({"role": m.role, "content": m.content})

    return msgs


def needs_summary() -> bool:
    """Return True when the conversation is long enough to warrant summarization."""
    return len(get_messages()) > SUMMARY_THRESHOLD * 2


def set_summary(summary: str) -> None:
    st.session_state[_key("summary")] = summary
    # trim the stored messages to recent window only
    history = get_messages()
    keep = MAX_CONVERSATION_TURNS * 2
    if len(history) > keep:
        st.session_state[_key("messages")] = history[-keep:]
    logger.info("Conversation summarized; older messages trimmed.")


# ── Mood / Journal / Wellness logs ──────────────────────────────────────────

def log_mood(mood: str) -> None:
    st.session_state[_key("mood_log")].append({
        "mood": mood,
        "ts": datetime.now().isoformat(),
    })


def get_mood_log() -> list[dict]:
    return st.session_state[_key("mood_log")]


def get_mood_labels() -> list[str]:
    return [entry["mood"] for entry in get_mood_log()]


def log_journal(entry: str) -> None:
    st.session_state[_key("journal_entries")].append({
        "entry": entry,
        "ts": datetime.now().isoformat(),
    })


def get_journal_entries() -> list[dict]:
    return st.session_state[_key("journal_entries")]


def log_stress(level: int) -> None:
    st.session_state[_key("stress_log")].append(level)


def get_stress_log() -> list[int]:
    return st.session_state[_key("stress_log")]


def log_sleep(hours: int) -> None:
    st.session_state[_key("sleep_log")].append(hours)


def get_sleep_log() -> list[int]:
    return st.session_state[_key("sleep_log")]

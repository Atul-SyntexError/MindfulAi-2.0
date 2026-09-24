"""
Chat UI component — renders conversation history and handles user input.
"""

from __future__ import annotations

import hashlib

import streamlit as st

from config import APP_SUBTITLE, APP_TITLE
from services.memory import get_messages
from services.speech import (
    NoSpeechDetected,
    SpeechServiceUnavailable,
    transcribe_audio,
)


# ── Header ──────────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the main page header."""
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header-topline">
                <span class="app-header-mark">✦</span>
                <span class="app-header-kicker">PRIVATE WELLBEING SPACE</span>
            </div>
            <h1 class="app-header-title">{APP_TITLE}</h1>
            <p class="app-header-subtitle">{APP_SUBTITLE}</p>
            <div class="app-header-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Welcome card ────────────────────────────────────────────────────────────

def render_welcome() -> None:
    """Show a welcome card when the conversation is empty."""
    st.markdown(
        """
        <div class="welcome-card">
            <p class="welcome-eyebrow">A quieter place to check in</p>
            <h3 class="welcome-title">Start wherever you are.</h3>
            <p class="welcome-text">
                Share what is present for you today. MindfulAI can help you slow down,
                notice patterns, and find one manageable next step.
            </p>
            <div class="feature-grid">
                <div class="feature-chip"><span>01</span> Mood tracking</div>
                <div class="feature-chip"><span>02</span> Guided journaling</div>
                <div class="feature-chip"><span>03</span> CBT techniques</div>
                <div class="feature-chip"><span>04</span> Wellness insights</div>
            </div>
            <p class="welcome-hint">
                Begin with a mood check-in, or simply write what is on your mind.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Message history ─────────────────────────────────────────────────────────

def render_messages() -> None:
    """Render the full chat history with styled bubbles."""
    messages = get_messages()

    if not messages:
        render_welcome()
        return

    for msg in messages:
        with st.chat_message(msg.role, avatar="🙂" if msg.role == "user" else "🧠"):
            st.markdown(msg.content)
            st.caption(msg.timestamp)


# ── Chat input ──────────────────────────────────────────────────────────────

def render_chat_input() -> str | None:
    """Render the chat input and return the user's text (or None)."""
    return st.chat_input(
        placeholder="Tell me what's on your mind…",
    )


# ── Voice input ─────────────────────────────────────────────────────────────

def render_voice_input(language_code: str) -> str | None:
    """
    Render the microphone input and, on a new recording, transcribe it.

    Returns the transcribed text exactly once per new recording (so it can
    be fed into the SAME processing pipeline as typed input) — returns None
    on every other rerun, including reruns of an already-processed recording.
    """
    st.session_state.setdefault("voice_status", "idle")
    st.session_state.setdefault("last_voice_hash", None)

    col_mic, col_status = st.columns([1, 3], vertical_alignment="center")

    with col_mic:
        audio = st.audio_input("🎙 Speak", label_visibility="visible")

    if audio is None:
        # Nothing recorded yet (or the widget was reset) — nothing to do.
        with col_status:
            if st.session_state["voice_status"] == "captured":
                st.caption("✓ Voice captured")
            elif st.session_state["voice_status"] == "no_speech":
                st.caption("Couldn't understand the audio. Please try again.")
            elif st.session_state["voice_status"] == "service_error":
                st.caption("Voice service unavailable. Please try again or type instead.")
        return None

    audio_bytes = audio.getvalue()
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if audio_hash == st.session_state["last_voice_hash"]:
        # Same recording as last run — already processed, don't resend.
        with col_status:
            if st.session_state["voice_status"] == "captured":
                st.caption("✓ Voice captured")
            elif st.session_state["voice_status"] == "no_speech":
                st.caption("Couldn't understand the audio. Please try again.")
            elif st.session_state["voice_status"] == "service_error":
                st.caption("Voice service unavailable. Please try again or type instead.")
        return None

    st.session_state["last_voice_hash"] = audio_hash

    with col_status:
        with st.spinner("● Listening…"):
            try:
                text = transcribe_audio(audio_bytes, language=language_code)
            except NoSpeechDetected:
                st.session_state["voice_status"] = "no_speech"
                st.caption("Couldn't understand the audio. Please try again.")
                return None
            except SpeechServiceUnavailable:
                st.session_state["voice_status"] = "service_error"
                st.caption("Voice service unavailable. Please try again or type instead.")
                return None
            except Exception:  # noqa: BLE001 — never crash the app on a bad recording
                st.session_state["voice_status"] = "service_error"
                st.caption("Something went wrong processing the audio. Please try again.")
                return None

        st.session_state["voice_status"] = "captured"
        st.caption(f"✓ Voice captured: “{text}”")

    return text

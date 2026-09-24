"""
MindfulAI — AI-Powered Mental Wellbeing Companion
Main Streamlit application entry point.

Run:  streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="MindfulAI — Mental Wellbeing Companion",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**MindfulAI v1.0** — An AI-powered mental wellbeing companion "
            "built with Streamlit & Groq.  \n"
            "⚠️ This is NOT a substitute for professional mental health care."
        ),
    },
)

# ── Load custom CSS ─────────────────────────────────────────────────────────
_css_path = Path(__file__).parent / "assets" / "style.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── App imports (after page config) ─────────────────────────────────────────
from config import GROQ_API_KEY, logger  # noqa: E402
from components.chat import (  # noqa: E402
    render_chat_input,
    render_header,
    render_messages,
    render_voice_input,
)
from components.sidebar import render_sidebar  # noqa: E402
from prompts.templates import SUMMARY_PROMPT, build_system_prompt  # noqa: E402
from services.llm import chat_completion  # noqa: E402
from services.memory import (  # noqa: E402
    add_message,
    build_llm_messages,
    get_messages,
    get_mood_labels,
    init_memory,
    needs_summary,
    set_summary,
)
from utils.safety import crisis_response_card, detect_crisis  # noqa: E402


def main() -> None:
    """Application main loop."""

    # ── Initialise session state ────────────────────────────────────────
    init_memory()

    # ── Sidebar (returns current check-in data) ─────────────────────────
    checkin = render_sidebar()

    # ── Guard: API key must be present ──────────────────────────────────
    try:
        streamlit_key = st.secrets.get("GROQ_API_KEY", "")
    except st.errors.StreamlitSecretNotFoundError:
        streamlit_key = ""

    has_key = bool(GROQ_API_KEY or streamlit_key)
    if not has_key:
        render_header()
        st.warning(
            "🔐 **MindfulAI is not connected yet.** Add `GROQ_API_KEY` to your `.env` file "
            "or Streamlit secrets, then restart the app. Get a key at "
            "[console.groq.com](https://console.groq.com).",
            icon="⚠️",
        )
        st.stop()

    # ── Main chat area ──────────────────────────────────────────────────
    render_header()
    render_messages()

    # ── Handle user input (typed OR voice — same downstream pipeline) ────
    voice_text = render_voice_input(checkin.get("voice_lang", "en-IN"))
    typed_text = render_chat_input()

    # Typed input takes precedence if both somehow arrive in the same run;
    # in practice only one will be non-None on any given rerun.
    user_text = typed_text or voice_text

    if user_text:
        source = "voice" if (voice_text and not typed_text) else "typed"
        logger.info("User input received via %s (%d chars)", source, len(user_text))

        # Display user message
        with st.chat_message("user", avatar="🙂"):
            st.markdown(user_text)

        add_message("user", user_text)

        # ── Safety check ────────────────────────────────────────────
        if detect_crisis(user_text):
            crisis_md = crisis_response_card()
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(crisis_md)
            add_message("assistant", crisis_md)
            st.rerun()
            return

        # ── Build system prompt with personalisation ────────────────
        system_prompt = build_system_prompt(
            mood=checkin.get("mood"),
            stress=checkin.get("stress"),
            sleep=checkin.get("sleep"),
            journal=checkin.get("journal"),
            mood_history=get_mood_labels(),
        )

        messages = build_llm_messages(system_prompt)

        # ── Stream the assistant response ───────────────────────────
        with st.chat_message("assistant", avatar="🧠"):
            try:
                stream = chat_completion(messages, stream=True)
                full_response = st.write_stream(stream)
            except ValueError as exc:
                st.error(f"⚙️ Configuration error: {exc}")
                logger.error("Config error: %s", exc)
                return
            except Exception as exc:
                st.error(
                    "😔 Something went wrong while generating a response. "
                    "Please check your API key and try again."
                )
                logger.error("LLM error: %s", exc)
                return

        add_message("assistant", full_response)

        # ── Summarise if conversation is getting long ───────────────
        if needs_summary():
            _run_summary(system_prompt)

        st.rerun()

    # ── Footer disclaimer ───────────────────────────────────────────────
    st.markdown(
        '<div class="disclaimer-bar">'
        "⚠️ MindfulAI is an AI companion, <strong>not</strong> a licensed therapist. "
        "If you're in crisis, please contact a professional or call your local helpline."
        "</div>",
        unsafe_allow_html=True,
    )


# ── Helpers ─────────────────────────────────────────────────────────────────

def _run_summary(system_prompt: str) -> None:
    """Summarise older conversation turns to keep the context window lean."""
    try:
        history = get_messages()
        convo_text = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in history[:-10]
        )
        summary_prompt = SUMMARY_PROMPT.format(conversation=convo_text)
        summary = chat_completion(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": summary_prompt},
            ],
            stream=False,
            max_tokens=400,
        )
        set_summary(summary)
        logger.info("Conversation summarised successfully.")
    except Exception as exc:
        logger.warning("Summary generation failed: %s", exc)


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()

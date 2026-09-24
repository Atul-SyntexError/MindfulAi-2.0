"""
Configuration management for the Mental Wellbeing Agent.
Loads environment variables and provides application-wide settings.
"""

from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

# ── Load .env ───────────────────────────────────────────────────────────────
load_dotenv()

# ── API ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

# ── App metadata ────────────────────────────────────────────────────────────
APP_TITLE = "MindfulAI"
APP_SUBTITLE = "Your Personal Mental Wellbeing Companion"
APP_VERSION = "1.0.0"

# ── Memory ──────────────────────────────────────────────────────────────────
MAX_CONVERSATION_TURNS: int = 40  # pairs kept in context window
SUMMARY_THRESHOLD: int = 20       # summarise after this many pairs

# ── Safety ──────────────────────────────────────────────────────────────────
# NOTE: voice input is transcribed into plain text (English or Hindi) before
# it ever reaches detect_crisis(), so the keyword list below MUST cover both
# languages — otherwise a Hindi crisis disclosure spoken aloud would silently
# bypass the safety layer that catches the same disclosure typed in English.
_CRISIS_KEYWORDS_EN: list[str] = [
    "kill myself", "end my life", "want to die", "suicide",
    "self-harm", "hurt myself", "no reason to live", "better off dead",
    "can't go on", "ending it all", "don't want to be alive",
    "cut myself", "overdose", "jump off", "hang myself",
]

# Hindi (Devanagari) — as produced by the hi-IN speech-recognition model —
# plus common Romanized ("Hinglish") equivalents, since a user may also type
# Hinglish or the en-IN model may transliterate Hindi speech phonetically.
_CRISIS_KEYWORDS_HI: list[str] = [
    # Devanagari
    "आत्महत्या", "खुदकुशी", "खुद को नुकसान", "खुद को चोट",
    "मरना चाहता हूं", "मरना चाहती हूं", "मर जाना चाहता", "मर जाना चाहती",
    "जीना नहीं चाहता", "जीना नहीं चाहती", "जीने का मन नहीं",
    "जान देना चाहता", "जान देना चाहती", "अपनी जान लेना",
    "जिंदगी खत्म", "जीवन समाप्त", "मौत चाहता", "मौत चाहती",
    # Romanized / Hinglish
    "aatmahatya", "khudkushi", "khud ko nuksan", "khud ko chot",
    "marna chahta hoon", "marna chahti hoon",
    "jeena nahi chahta", "jeena nahi chahti",
    "jaan dena chahta", "jaan dena chahti", "zindagi khatam", "jindagi khatam",
]

CRISIS_KEYWORDS: list[str] = _CRISIS_KEYWORDS_EN + _CRISIS_KEYWORDS_HI

CRISIS_RESOURCES = {
    "🇺🇸 USA": "988 Suicide & Crisis Lifeline — call or text **988**",
    "🇮🇳 India": "iCall — **9152987821** · Vandrevala Foundation — **1860-2662-345**",
    "🇬🇧 UK": "Samaritans — **116 123**",
    "🌍 International": "befrienders.org/need-to-talk",
}

# ── Mood options ────────────────────────────────────────────────────────────
MOOD_OPTIONS: dict[str, str] = {
    "😊 Happy": "happy",
    "😌 Calm": "calm",
    "😟 Anxious": "anxious",
    "😢 Sad": "sad",
    "😠 Angry": "angry",
    "😩 Stressed": "stressed",
    "😴 Exhausted": "exhausted",
    "🤔 Confused": "confused",
}

MOOD_COLORS: dict[str, str] = {
    "happy": "#4ade80",
    "calm": "#60a5fa",
    "anxious": "#fbbf24",
    "sad": "#818cf8",
    "angry": "#f87171",
    "stressed": "#fb923c",
    "exhausted": "#94a3b8",
    "confused": "#c084fc",
}

STRESS_LEVELS = ["1 — Very Low", "2", "3", "4", "5 — Moderate", "6", "7", "8", "9", "10 — Extreme"]
SLEEP_HOURS = [f"{h} hrs" for h in range(0, 13)]

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("mindfulai")

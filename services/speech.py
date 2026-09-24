"""
Speech recognition service — converts browser-recorded audio (from
``st.audio_input``) into text, supporting English and Hindi.

Design notes
────────────
• Uses the SpeechRecognition library's free Google Web Speech API backend
  (no API key required, matches the project's "no unnecessary dependency /
  no API key needed for a preview feature" constraint).
• The microphone itself is handled entirely by Streamlit's native
  ``st.audio_input`` widget (recording happens in the user's browser), so no
  desktop-only microphone package (e.g. PyAudio) is required — this works
  the same after deployment (Streamlit Cloud, Render, etc.) as it does
  locally.
• "Auto Detect" is a best-effort heuristic: the free Google Web Speech API
  has no official language-auto-detect mode, so we run recognition against
  both English and Hindi language models. We prefer a Hindi result that
  actually contains Devanagari script (a reliable signal, since the English
  model can't produce it) and fall back to whichever result reported higher
  confidence otherwise. Confidence alone is NOT trustworthy with this free
  backend — it is frequently 0.0 or absent — so this is explicitly a
  heuristic, not a guaranteed detector.
"""

from __future__ import annotations

import io
import re

import speech_recognition as sr

from config import logger

# Devanagari Unicode block. The en-IN model cannot produce these characters,
# so their presence in an hi-IN result is a much more reliable signal than
# the free API's confidence score (see note in transcribe_audio below).
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# ── Public language options ─────────────────────────────────────────────────
# Keys are what the UI shows the user; values are Google Web Speech API
# BCP-47 language codes.
VOICE_LANGUAGE_OPTIONS: dict[str, str] = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Auto Detect": "auto",
}

_AUTO_CANDIDATES = ["en-IN", "hi-IN"]


class SpeechRecognitionError(Exception):
    """Base class for speech-recognition failures."""


class NoSpeechDetected(SpeechRecognitionError):
    """Raised when the audio contains no recognizable speech."""


class SpeechServiceUnavailable(SpeechRecognitionError):
    """Raised when the recognition service can't be reached (network/API)."""


def _load_audio(audio_bytes: bytes) -> sr.AudioData:
    """Load raw WAV bytes (as produced by ``st.audio_input``) into an AudioData object."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            return recognizer.record(source)
    except (ValueError, EOFError, OSError) as exc:
        # Corrupted, empty, or otherwise unreadable audio (should be rare —
        # st.audio_input always produces valid WAV — but we never want a
        # raw parsing exception to bubble up to the UI).
        raise NoSpeechDetected(f"Unreadable audio: {exc}") from exc


def _recognize_one(audio_data: sr.AudioData, language: str) -> tuple[str, float]:
    """
    Try recognizing *audio_data* in a single *language*.

    Returns (transcript, confidence). transcript is "" if nothing was
    recognized. Raises SpeechServiceUnavailable on network/API failure.
    """
    recognizer = sr.Recognizer()
    try:
        result = recognizer.recognize_google(audio_data, language=language, show_all=True)
    except sr.RequestError as exc:
        raise SpeechServiceUnavailable(str(exc)) from exc

    if not result or not result.get("alternative"):
        return "", 0.0

    best = result["alternative"][0]
    transcript = (best.get("transcript") or "").strip()
    confidence = float(best.get("confidence", 0.0) or 0.0)
    return transcript, confidence


def transcribe_audio(audio_bytes: bytes, language: str = "en-IN") -> str:
    """
    Transcribe recorded audio to text.

    *language* is a Google Web Speech API code ("en-IN", "hi-IN") or the
    literal string "auto" for best-effort auto-detect across English/Hindi.

    Raises:
        NoSpeechDetected: audio was processed but no speech was recognized.
        SpeechServiceUnavailable: the recognition backend could not be reached.
    """
    if not audio_bytes:
        raise NoSpeechDetected("Empty audio.")

    audio_data = _load_audio(audio_bytes)

    if language == "auto":
        # Run recognition against every candidate language and keep every
        # non-empty result — we can't rely on `language=="auto"` picking a
        # winner from confidence scores alone (see note below).
        results: list[tuple[str, str, float]] = []
        last_error: SpeechServiceUnavailable | None = None
        for candidate in _AUTO_CANDIDATES:
            try:
                text, conf = _recognize_one(audio_data, candidate)
            except SpeechServiceUnavailable as exc:
                last_error = exc
                continue
            if text:
                results.append((candidate, text, conf))

        if not results:
            if last_error is not None:
                raise last_error
            raise NoSpeechDetected("No speech detected in either language.")

        # NOTE — Auto Detect is explicitly best-effort: the free Google Web
        # Speech API has no official language-ID mode, and in practice its
        # `confidence` field is frequently 0.0 or missing for both
        # candidates, which makes confidence alone an unreliable tie-breaker
        # (it would silently default to whichever language was tried first).
        # Devanagari characters can only come from the hi-IN model, so if a
        # hi-IN attempt produced any, that's a stronger real-world signal of
        # a correct match than the reported confidence — use it when present,
        # and fall back to confidence otherwise.
        devanagari_hits = [
            r for r in results if r[0] == "hi-IN" and _DEVANAGARI_RE.search(r[1])
        ]
        candidate, best_text, best_conf = (
            devanagari_hits[0] if devanagari_hits else max(results, key=lambda r: r[2])
        )
        logger.info(
            "Voice (auto-detect → %s) transcribed — %d chars", candidate, len(best_text)
        )
        return best_text

    text, _conf = _recognize_one(audio_data, language)
    if not text:
        raise NoSpeechDetected("No speech detected.")
    logger.info("Voice (%s) transcribed — %d chars", language, len(text))
    return text

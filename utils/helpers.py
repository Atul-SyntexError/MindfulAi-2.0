"""
General helper utilities — timestamps, formatters, validators.
"""

from __future__ import annotations

from datetime import datetime


def timestamp_now() -> str:
    """Return a human-readable timestamp for the current moment."""
    return datetime.now().strftime("%I:%M %p")

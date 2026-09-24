"""
Safety layer — detects crisis language and provides immediate resources.
"""

from __future__ import annotations

import re
from config import CRISIS_KEYWORDS, CRISIS_RESOURCES, logger


def _build_pattern() -> re.Pattern:
    """Compile a single regex from all crisis keywords (case-insensitive)."""
    escaped = [re.escape(kw) for kw in CRISIS_KEYWORDS]
    return re.compile("|".join(escaped), re.IGNORECASE)


_CRISIS_RE = _build_pattern()


def detect_crisis(text: str) -> bool:
    """Return True if the text contains any crisis keyword."""
    match = bool(_CRISIS_RE.search(text))
    if match:
        logger.warning("Crisis language detected in user input.")
    return match


def crisis_response_card() -> str:
    """Return a Markdown card with crisis hotline information."""
    lines = [
        "## 🚨 You Are Not Alone",
        "",
        "It sounds like you may be going through an incredibly difficult time. "
        "**Your feelings are valid**, and there are people who want to help.",
        "",
        "**Please reach out to a crisis service now:**",
        "",
    ]
    for region, info in CRISIS_RESOURCES.items():
        lines.append(f"- {region}: {info}")
    lines += [
        "",
        "---",
        "",
        "💛 *I'm an AI and not a substitute for professional help. "
        "A trained counselor can give you the real support you deserve.*",
    ]
    return "\n".join(lines)

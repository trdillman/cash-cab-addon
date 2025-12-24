from __future__ import annotations

import re

_FIRST_DIGIT_RE = re.compile(r"\d")


def address_only(text: str) -> str:
    """Best-effort remove venue/building names from the front of an address.

    Examples:
    - "Starbucks, 123 Main St, Toronto" -> "123 Main St, Toronto"
    - "Starbucks - 123 Main St, Toronto" -> "123 Main St, Toronto"
    - "123 Main St, Toronto" -> unchanged
    """
    raw = (text or "").strip()
    if not raw:
        return ""

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return raw

    # If a leading segment contains a digit but also includes a name prefix
    # (e.g. "Starbucks - 123 Main St"), strip up to the first digit.
    m0 = _FIRST_DIGIT_RE.search(parts[0])
    if m0 and m0.start() > 0:
        stripped = parts[0][m0.start() :].lstrip(" -–—,")
        if stripped:
            parts[0] = stripped

    # If there's a comma-separated venue name first, drop everything before the
    # first segment that looks like an address (has a digit).
    start_idx = 0
    for idx, part in enumerate(parts):
        if _FIRST_DIGIT_RE.search(part):
            start_idx = idx
            break

    return ", ".join(parts[start_idx:]).strip() or raw


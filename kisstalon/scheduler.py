"""Schedule parsing and due-checking."""

from __future__ import annotations

import re
from datetime import datetime, timedelta


def _parse_interval(schedule: str) -> timedelta | None:
    """Parse 'every Xh', 'every Xm', 'daily', 'nightly' into a timedelta."""
    s = schedule.strip().lower()

    if s == "daily":
        return timedelta(hours=24)
    if s == "nightly":
        return timedelta(hours=24)

    m = re.match(r"every\s+(\d+)\s*([hm])", s)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        if unit == "h":
            return timedelta(hours=val)
        if unit == "m":
            return timedelta(minutes=val)

    return None


def is_due(schedule: str, last_run: datetime | None) -> bool:
    """Check whether a talon with the given schedule and last_run is due now."""
    now = datetime.now()
    interval = _parse_interval(schedule)

    if interval is None:
        return False  # unknown schedule format, skip

    if last_run is None:
        return True  # never run before

    # For 'nightly', only run between 1am-5am
    if schedule.strip().lower() == "nightly":
        if not (1 <= now.hour <= 5):
            return False

    return (now - last_run) >= interval

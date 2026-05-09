"""Pure date helpers used by the renderer."""
from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Iterator


def iter_months(start: date, end: date) -> Iterator[tuple[int, int]]:
    """Yield `(year, month)` for every month between `start` and `end` inclusive."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def days_in_month(year: int, month: int) -> list[date]:
    """Return every date in the given month."""
    last = monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, last + 1)]

"""Pymdownx Blocks calendar extension.

Renders TOML-driven calendar blocks of the form::

    /// calendar
    start = 2026-01-01
    end = 2026-03-31
    view = "month"
    weekends = "dim"
    holidays = [2026-01-06, 2026-02-14]

    [[ranges]]
    from = 2026-01-10
    to = 2026-01-15
    class = "vacation"
    ///
"""
from __future__ import annotations

from .block import CalendarBlock
from .errors import CalendarError
from .extension import CalendarExtension, makeExtension
from .i18n import DEFAULT_LOCALE, Locale, available_locales, get_locale, register_locale
from .models import CalendarConfig, DateRange, DayAnnotation
from .parser import parse_calendar
from .renderer import render_calendar

__all__ = [
    "CalendarBlock",
    "CalendarConfig",
    "CalendarError",
    "CalendarExtension",
    "DEFAULT_LOCALE",
    "DateRange",
    "DayAnnotation",
    "Locale",
    "available_locales",
    "get_locale",
    "makeExtension",
    "parse_calendar",
    "register_locale",
    "render_calendar",
]

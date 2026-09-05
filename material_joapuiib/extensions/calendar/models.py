"""Internal models for the calendar extension."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .i18n import DEFAULT_LOCALE, Locale

VALID_WEEKENDS: tuple[str, ...] = ("show", "hide", "plain")
VALID_SIZES: tuple[str, ...] = ("sm", "md", "lg", "xl", "xxl")
VALID_RANGE_EXCLUDE: tuple[str, ...] = ("weekends", "holidays")


@dataclass(frozen=True)
class DateRange:
    """Inclusive date range with an associated CSS class, optional tooltip and label."""

    start: date
    end: date
    css_class: str
    tooltip: str = ""
    label: str = ""
    exclude: frozenset[str] = field(default_factory=frozenset)

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


@dataclass(frozen=True)
class DayAnnotation:
    """Single-day annotation: optional CSS class, tooltip and label."""

    day: date
    css_class: str = ""
    tooltip: str = ""
    label: str = ""
    override: bool = False


@dataclass(frozen=True)
class CalendarConfig:
    """Validated, immutable configuration for a calendar block."""

    start: date
    end: date
    weekends: str = "show"
    size: str = "lg"
    holidays: frozenset[date] = field(default_factory=frozenset)
    holidays_plain: bool = False
    holiday_tooltip: str = ""
    ranges: tuple[DateRange, ...] = ()
    days: tuple[DayAnnotation, ...] = ()
    locale: Locale = DEFAULT_LOCALE

    def is_weekend(self, day: date) -> bool:
        return day.weekday() >= 5

    def is_visible(self, day: date) -> bool:
        return not (self.weekends == "hide" and self.is_weekend(day))

    def in_window(self, day: date) -> bool:
        return self.start <= day <= self.end

    def _ranges_apply(self, day: date) -> bool:
        """Whether `[[ranges]]` classes/tooltips apply to `day`, calendar-wide."""
        if self.weekends == "plain" and self.is_weekend(day):
            return False
        if self.holidays_plain and day in self.holidays:
            return False
        return True

    def _range_applies(self, r: DateRange, day: date) -> bool:
        """Whether a specific range's class/tooltip/label applies to `day`."""
        if not r.contains(day):
            return False
        if not self._ranges_apply(day):
            return False
        if "weekends" in r.exclude and self.is_weekend(day):
            return False
        if "holidays" in r.exclude and day in self.holidays:
            return False
        return True

    def _day_annotations(self, day: date) -> list[DayAnnotation]:
        return [a for a in self.days if a.day == day]

    @staticmethod
    def _is_overridden(day_annotations: list[DayAnnotation]) -> bool:
        return any(a.override for a in day_annotations)

    def classes_for(self, day: date) -> list[str]:
        """Compute the conditional CSS classes for a given day.

        A `[[days]]` entry with `override = true` drops the weekend/holiday/
        range classes that would otherwise apply to `day`, replacing them
        with the day annotations' own classes.
        """
        day_annotations = self._day_annotations(day)
        override = self._is_overridden(day_annotations)

        classes: list[str] = []
        if not override:
            if self.weekends in ("show", "plain") and self.is_weekend(day):
                classes.append("weekend")
            if day in self.holidays:
                classes.append("holiday")
            for r in self.ranges:
                if self._range_applies(r, day):
                    classes.append(r.css_class)
        for a in day_annotations:
            if a.css_class:
                classes.append(a.css_class)
        return classes

    def labels_for(self, day: date) -> list[tuple[str, str]]:
        """Collect in-cell labels for `day` as `(source_class, text)` pairs.

        Holiday days don't carry their own label (`[holiday].tooltip` covers
        the popover). Range labels are suppressed whenever the parent range's
        class is suppressed (same rule as range classes), and dropped
        entirely on an overridden day.
        """
        day_annotations = self._day_annotations(day)
        override = self._is_overridden(day_annotations)

        out: list[tuple[str, str]] = []
        if not override:
            for r in self.ranges:
                if self._range_applies(r, day) and r.label:
                    out.append((r.css_class, r.label))
        for a in day_annotations:
            if a.label:
                out.append((a.css_class, a.label))
        return out

    def tooltips_for(self, day: date) -> list[tuple[str, str]]:
        """Collect tooltip entries for `day` as `(source_class, markdown_text)` pairs.

        `source_class` is the CSS class that visually identifies the source
        (e.g. ``"holiday"``, the range's `class`, or the day annotation's
        `class`). Used by the renderer to colour the bullet in front of each
        line. May be an empty string when no class was provided.

        Holiday and range tooltips are dropped entirely on an overridden day
        (same rule as range classes/labels).
        """
        day_annotations = self._day_annotations(day)
        override = self._is_overridden(day_annotations)

        out: list[tuple[str, str]] = []
        if not override:
            if day in self.holidays and self.holiday_tooltip:
                out.append(("holiday", self.holiday_tooltip))
            for r in self.ranges:
                if self._range_applies(r, day) and r.tooltip:
                    out.append((r.css_class, r.tooltip))
        for a in day_annotations:
            if a.tooltip:
                out.append((a.css_class, a.tooltip))
        return out

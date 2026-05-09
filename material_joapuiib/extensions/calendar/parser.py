"""TOML configuration parser for the calendar extension."""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

from .errors import CalendarError
from .i18n import DEFAULT_LOCALE, Locale, get_locale
from .models import CalendarConfig, DateRange, DayAnnotation, VALID_WEEKENDS


_INCLUDE_RE = re.compile(r'^[ \t]*!include[ \t]+"([^"\n]+)"[ \t]*$', re.MULTILINE)
_MAX_INCLUDE_DEPTH = 16


def parse_calendar(
    text: str,
    *,
    default_locale: str | Locale | None = None,
    base_path: str | Path | None = None,
) -> CalendarConfig:
    """Parse the TOML body of a calendar block into a `CalendarConfig`.

    Parameters
    ----------
    text:
        Raw TOML body of the block.
    default_locale:
        Locale to use when the block does not specify its own. Accepts a
        locale code, a `Locale` instance, or ``None`` for English.
    base_path:
        Source file the body came from. Used to resolve `!include "..."`
        directives relative to that file. When ``None``, includes resolve
        relative to the current working directory.
    """
    expanded = _expand_includes(text, _coerce_base_path(base_path))
    try:
        data = tomllib.loads(expanded)
    except tomllib.TOMLDecodeError as e:
        raise CalendarError(_format_toml_error(e)) from e
    return _build_config(data, _coerce_default_locale(default_locale))


def _coerce_base_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return Path(value)


def _expand_includes(
    text: str,
    base_path: Path | None,
    *,
    visited: frozenset[str] = frozenset(),
    depth: int = 0,
) -> str:
    """Replace `!include "path"` lines with the referenced file contents."""
    if depth >= _MAX_INCLUDE_DEPTH:
        raise CalendarError(
            f"!include exceeded max recursion depth ({_MAX_INCLUDE_DEPTH})"
        )

    base_dir = base_path.parent if base_path is not None else Path.cwd()

    def replace(match: re.Match[str]) -> str:
        rel = match.group(1)
        target = (base_dir / rel).resolve()
        target_str = str(target)
        if target_str in visited:
            raise CalendarError(f"!include cycle detected: {rel!r}")
        if not target.is_file():
            raise CalendarError(
                f"!include cannot read {rel!r} (resolved to {target})"
            )
        try:
            content = target.read_text(encoding="utf-8")
        except OSError as e:
            raise CalendarError(f"!include failed for {rel!r}: {e}") from e
        return _expand_includes(
            content,
            target,
            visited=visited | {target_str},
            depth=depth + 1,
        )

    return _INCLUDE_RE.sub(replace, text)


_TOML_LOCATION_RE = re.compile(r"\(at line (\d+),\s*column (\d+)\)")


def _format_toml_error(err: "tomllib.TOMLDecodeError") -> str:
    """Format `tomllib`'s decode error with an explicit line/column callout."""
    message = str(err)
    match = _TOML_LOCATION_RE.search(message)
    if match:
        line, col = match.group(1), match.group(2)
        cleaned = _TOML_LOCATION_RE.sub("", message).strip().rstrip(":").strip()
        return f"invalid TOML at line {line}, column {col}: {cleaned}"
    return f"invalid TOML: {message}"


def _coerce_default_locale(value: str | Locale | None) -> Locale:
    if value is None:
        return DEFAULT_LOCALE
    if isinstance(value, Locale):
        return value
    resolved = get_locale(value)
    if resolved is None:
        raise CalendarError(f"unknown default locale {value!r}")
    return resolved


def _is_pure_date(value: Any) -> bool:
    return isinstance(value, date) and not isinstance(value, datetime)


def _build_config(data: Mapping[str, Any], default_locale: Locale) -> CalendarConfig:
    start = _require_date(data, "start")
    end = _require_date(data, "end")
    if end < start:
        raise CalendarError(f"'end' ({end}) must be on or after 'start' ({start})")

    weekends = _enum(data, "weekends", VALID_WEEKENDS, default="show")

    holidays, holidays_plain, holiday_tooltip = _parse_holiday_section(
        data.get("holiday", {})
    )

    return CalendarConfig(
        start=start,
        end=end,
        weekends=weekends,
        holidays=holidays,
        holidays_plain=holidays_plain,
        holiday_tooltip=holiday_tooltip,
        ranges=_parse_ranges(data.get("ranges", [])),
        days=_parse_days(data.get("days", [])),
        locale=_resolve_locale(data, default_locale),
    )


def _parse_holiday_section(value: Any) -> tuple[frozenset[date], bool, str]:
    """Parse the `[holiday]` table into (dates, plain, tooltip)."""
    if not isinstance(value, dict):
        raise CalendarError("'holiday' must be a table")

    extra = set(value) - {"dates", "plain", "tooltip"}
    if extra:
        raise CalendarError(f"'holiday' has unknown fields: {sorted(extra)}")

    dates = _parse_holidays(value.get("dates", []))

    plain = value.get("plain", False)
    if not isinstance(plain, bool):
        raise CalendarError("'holiday.plain' must be a boolean")

    tooltip = value.get("tooltip", "")
    if not isinstance(tooltip, str):
        raise CalendarError("'holiday.tooltip' must be a string")

    return dates, plain, tooltip.strip()


def _resolve_locale(data: Mapping[str, Any], default_locale: Locale) -> Locale:
    """Resolve the effective locale for the calendar.

    Resolution order: inline overrides > `locale` field > extension default.
    """
    base = default_locale
    if "locale" in data:
        code = data["locale"]
        if not isinstance(code, str) or not code.strip():
            raise CalendarError("'locale' must be a non-empty string")
        resolved = get_locale(code)
        if resolved is None:
            raise CalendarError(
                f"unsupported locale {code!r}. "
                "Provide bundled code, install babel, or override "
                "'month_names'/'weekday_labels' explicitly."
            )
        base = resolved

    months_override = data.get("month_names")
    weekdays_override = data.get("weekday_labels")
    if months_override is None and weekdays_override is None:
        return base

    months = _validate_string_list(months_override, "month_names", 12, base.month_names)
    weekdays = _validate_string_list(weekdays_override, "weekday_labels", 7, base.weekday_labels)
    return Locale(code=base.code, month_names=months, weekday_labels=weekdays)


def _validate_string_list(
    value: Any,
    field_name: str,
    expected_length: int,
    fallback: tuple[str, ...],
) -> tuple[str, ...]:
    if value is None:
        return fallback
    if not isinstance(value, list) or len(value) != expected_length:
        raise CalendarError(
            f"'{field_name}' must be a list of {expected_length} strings"
        )
    if not all(isinstance(v, str) and v for v in value):
        raise CalendarError(f"'{field_name}' entries must be non-empty strings")
    return tuple(value)


def _require_date(data: Mapping[str, Any], key: str) -> date:
    if key not in data:
        raise CalendarError(f"missing required field '{key}'")
    value = data[key]
    if not _is_pure_date(value):
        raise CalendarError(
            f"field '{key}' must be a TOML local-date (YYYY-MM-DD), got {type(value).__name__}"
        )
    return value


def _enum(data: Mapping[str, Any], key: str, choices: tuple[str, ...], default: str) -> str:
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, str) or value not in choices:
        raise CalendarError(f"'{key}' must be one of {list(choices)}, got {value!r}")
    return value


def _parse_holidays(value: Any) -> frozenset[date]:
    if not isinstance(value, list):
        raise CalendarError("'holiday.dates' must be a list of dates or [from, to] ranges")
    holidays: set[date] = set()
    for i, item in enumerate(value):
        if _is_pure_date(item):
            holidays.add(item)
        elif isinstance(item, list):
            holidays.update(_expand_holiday_range(i, item))
        else:
            raise CalendarError(
                f"holiday.dates[{i}] must be a TOML local-date or [from, to] pair, "
                f"got {type(item).__name__}"
            )
    return frozenset(holidays)


def _expand_holiday_range(idx: int, pair: list[Any]) -> list[date]:
    """Expand a `[from, to]` pair into the inclusive list of dates."""
    if len(pair) != 2:
        raise CalendarError(
            f"holiday.dates[{idx}] range must have exactly 2 elements [from, to], "
            f"got {len(pair)}"
        )
    start, end = pair
    if not _is_pure_date(start) or not _is_pure_date(end):
        raise CalendarError(
            f"holiday.dates[{idx}] range elements must be TOML local-dates"
        )
    if end < start:
        raise CalendarError(
            f"holiday.dates[{idx}] end ({end}) must be on or after start ({start})"
        )

    span = (end - start).days
    return [start + timedelta(days=offset) for offset in range(span + 1)]


def _parse_days(value: Any) -> tuple[DayAnnotation, ...]:
    if not isinstance(value, list):
        raise CalendarError("'days' must be an array of tables")
    out: list[DayAnnotation] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CalendarError(f"days[{i}] must be a table")
        out.append(_parse_day(i, item))
    return tuple(out)


def _parse_day(idx: int, item: Mapping[str, Any]) -> DayAnnotation:
    if "date" not in item:
        raise CalendarError(f"days[{idx}] missing field 'date'")
    day = item["date"]
    if not _is_pure_date(day):
        raise CalendarError(f"days[{idx}] 'date' must be a TOML local-date")

    css_class = item.get("class", "")
    if not isinstance(css_class, str):
        raise CalendarError(f"days[{idx}] 'class' must be a string")

    tooltip = item.get("tooltip", "")
    if not isinstance(tooltip, str):
        raise CalendarError(f"days[{idx}] 'tooltip' must be a string")

    label = item.get("label", "")
    if not isinstance(label, str):
        raise CalendarError(f"days[{idx}] 'label' must be a string")

    extra = set(item) - {"date", "class", "tooltip", "label"}
    if extra:
        raise CalendarError(
            f"days[{idx}] unknown fields: {sorted(extra)}"
        )

    return DayAnnotation(
        day=day,
        css_class=css_class.strip(),
        tooltip=tooltip.strip(),
        label=label.strip(),
    )


def _parse_ranges(value: Any) -> tuple[DateRange, ...]:
    if not isinstance(value, list):
        raise CalendarError("'ranges' must be an array of tables")
    out: list[DateRange] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CalendarError(f"ranges[{i}] must be a table")
        out.append(_parse_range(i, item))
    return tuple(out)


def _parse_range(idx: int, item: Mapping[str, Any]) -> DateRange:
    for required in ("from", "to", "class"):
        if required not in item:
            raise CalendarError(f"ranges[{idx}] missing field '{required}'")

    extra = set(item) - {"from", "to", "class", "tooltip", "label"}
    if extra:
        raise CalendarError(f"ranges[{idx}] unknown fields: {sorted(extra)}")

    r_start = item["from"]
    r_end = item["to"]
    css_class = item["class"]
    tooltip = item.get("tooltip", "")
    label = item.get("label", "")

    if not _is_pure_date(r_start) or not _is_pure_date(r_end):
        raise CalendarError(f"ranges[{idx}] 'from' and 'to' must be TOML local-dates")
    if r_end < r_start:
        raise CalendarError(
            f"ranges[{idx}] 'to' ({r_end}) must be on or after 'from' ({r_start})"
        )
    if not isinstance(css_class, str) or not css_class.strip():
        raise CalendarError(f"ranges[{idx}] 'class' must be a non-empty string")
    if not isinstance(tooltip, str):
        raise CalendarError(f"ranges[{idx}] 'tooltip' must be a string")
    if not isinstance(label, str):
        raise CalendarError(f"ranges[{idx}] 'label' must be a string")

    return DateRange(
        start=r_start,
        end=r_end,
        css_class=css_class.strip(),
        tooltip=tooltip.strip(),
        label=label.strip(),
    )

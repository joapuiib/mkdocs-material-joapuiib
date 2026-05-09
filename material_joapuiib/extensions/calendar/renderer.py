"""HTML rendering for the calendar extension."""
from __future__ import annotations

import xml.etree.ElementTree as etree
from datetime import date
from typing import Callable, Optional

from .dates import days_in_month, iter_months
from .models import CalendarConfig


# Callable signature: takes a list of `(source_class, markdown_text)` tuples
# and returns a stash placeholder (or pre-escaped HTML) that goes inside
# `<div class="md-calendar-tooltip__inner">`. Block.py threads a real
# renderer that runs each text through Python-Markdown, wraps each in a
# `<li class="md-calendar-tooltip-item {source_class}">`, and stashes the
# joined HTML via the parent markdown's htmlStash.
TooltipRenderer = Callable[[list[tuple[str, str]]], str]


def render_calendar(
    root: etree.Element,
    config: CalendarConfig,
    *,
    tooltip_renderer: Optional[TooltipRenderer] = None,
    id_prefix: str = "md-cal-tip",
    id_start: int = 0,
) -> int:
    """Decorate `root` and append the rendered calendar tree as children.

    When `tooltip_renderer` is provided, day cells with tooltips emit a
    `data-cal-tip` attribute pointing at a `<div class="md-tooltip2">` node
    appended inside `root`. Otherwise tooltips fall back to the plain `title`
    attribute (text only).

    Returns the next available id index after this calendar so callers can
    keep tooltip IDs unique across multiple calendars on the same page.
    """
    root.set("class", " ".join(_root_classes(config)))
    root.set("data-start", config.start.isoformat())
    root.set("data-end", config.end.isoformat())
    root.set("lang", config.locale.code)

    state = _RenderState(
        tooltip_renderer=tooltip_renderer,
        id_prefix=id_prefix,
        next_id=id_start,
    )

    for year, month in iter_months(config.start, config.end):
        _render_month(root, config, year, month, state)

    for tip_id, payload in state.tooltips:
        _emit_tooltip_node(root, tip_id, payload)

    return state.next_id


# ---------------------------------------------------------------------------
# Render-time state
# ---------------------------------------------------------------------------

class _RenderState:
    """Mutable bag of state for one render pass."""

    def __init__(
        self,
        *,
        tooltip_renderer: Optional[TooltipRenderer],
        id_prefix: str,
        next_id: int,
    ) -> None:
        self.tooltip_renderer = tooltip_renderer
        self.id_prefix = id_prefix
        self.next_id = next_id
        self.tooltips: list[tuple[str, str]] = []

    def register_tooltip(self, tooltips: list[tuple[str, str]]) -> str:
        tip_id = f"{self.id_prefix}-{self.next_id}"
        self.next_id += 1
        if self.tooltip_renderer is not None:
            payload = self.tooltip_renderer(tooltips)
        else:
            # Fallback used only by tests / direct API calls that skip the
            # block layer; concatenates the markdown sources verbatim.
            payload = " · ".join(text for _, text in tooltips)
        self.tooltips.append((tip_id, payload))
        return tip_id


# ---------------------------------------------------------------------------
# CSS / class helpers
# ---------------------------------------------------------------------------

def _root_classes(config: CalendarConfig) -> list[str]:
    classes = ["md-calendar"]
    if config.weekends == "hide":
        classes.append("md-calendar-no-weekends")
    return classes


def _visible_weekdays(config: CalendarConfig) -> list[int]:
    return list(range(5)) if config.weekends == "hide" else list(range(7))


def _day_classes(config: CalendarConfig, day: date) -> list[str]:
    classes = ["md-calendar-day"]
    if not config.in_window(day):
        classes.append("md-calendar-day-outside")
    if day == date.today():
        classes.append("today")
    classes.extend(config.classes_for(day))
    return classes


# ---------------------------------------------------------------------------
# Cell helpers
# ---------------------------------------------------------------------------

def _emit_weekday_header(grid: etree.Element, config: CalendarConfig) -> None:
    for w in _visible_weekdays(config):
        cell = etree.SubElement(grid, "div", {"class": "md-calendar-weekday"})
        cell.text = config.locale.weekday_label(w)


def _emit_day(
    grid: etree.Element,
    config: CalendarConfig,
    day: date,
    state: _RenderState,
) -> None:
    attrib = {
        "class": " ".join(_day_classes(config, day)),
        "data-date": day.isoformat(),
    }
    tooltips = config.tooltips_for(day)
    if tooltips:
        tip_id = state.register_tooltip(tooltips)
        attrib["data-cal-tip"] = tip_id
        attrib["tabindex"] = "0"
        # Screen-reader contract: announce the popover body when the cell
        # gets focus. Pairs with role="tooltip" on the popover itself.
        attrib["aria-describedby"] = tip_id
    cell = etree.SubElement(grid, "div", attrib)
    num = etree.SubElement(cell, "span", {"class": "md-calendar-day-number"})
    num.text = str(day.day)

    for source_class, text in config.labels_for(day):
        label_classes = ["md-calendar-day-label"]
        if source_class:
            label_classes.append(source_class)
        label = etree.SubElement(
            cell, "span", {"class": " ".join(label_classes)}
        )
        label.text = text


def _emit_empty(grid: etree.Element) -> None:
    etree.SubElement(grid, "div", {"class": "md-calendar-day md-calendar-day-empty"})


def _emit_tooltip_node(
    parent: etree.Element,
    tip_id: str,
    payload: str,
) -> None:
    """Append a hidden tooltip body. Styled by `calendar.css`, mounted by JS."""
    tip = etree.SubElement(
        parent,
        "div",
        {
            "class": "md-calendar-tooltip",
            "id": tip_id,
            "role": "tooltip",
            "hidden": "hidden",
        },
    )
    inner = etree.SubElement(
        tip, "div", {"class": "md-calendar-tooltip__inner md-typeset"}
    )
    # `payload` is a Python-Markdown htmlStash placeholder produced by the
    # block (or plain joined text when no renderer is wired). Either way we
    # drop it straight into `inner.text`; the markdown postprocessor will
    # replace placeholders in the final HTML pass.
    inner.text = payload


# ---------------------------------------------------------------------------
# Section renderer
# ---------------------------------------------------------------------------

def _render_month(
    parent: etree.Element,
    config: CalendarConfig,
    year: int,
    month: int,
    state: _RenderState,
) -> None:
    section = etree.SubElement(parent, "section", {"class": "md-calendar-month-block"})
    header = etree.SubElement(section, "header", {"class": "md-calendar-month-title"})
    header.text = f"{config.locale.month_name(month)} {year}"

    grid = etree.SubElement(section, "div", {"class": "md-calendar-grid"})
    _emit_weekday_header(grid, config)

    visible = [d for d in days_in_month(year, month) if config.is_visible(d)]
    if not visible:
        return

    last_col = 4 if config.weekends == "hide" else 6
    for _ in range(visible[0].weekday()):
        _emit_empty(grid)
    for day in visible:
        _emit_day(grid, config, day, state)
    for _ in range(last_col - visible[-1].weekday()):
        _emit_empty(grid)

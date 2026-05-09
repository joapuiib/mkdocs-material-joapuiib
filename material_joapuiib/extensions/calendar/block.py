"""Pymdownx Block implementation for calendars."""
from __future__ import annotations

import re
import xml.etree.ElementTree as etree

import markdown
from pymdownx.blocks.block import Block

from .errors import CalendarError
from .parser import parse_calendar
from .renderer import render_calendar


_SINGLE_PARAGRAPH_RE = re.compile(r"^<p>(.*)</p>$", re.S)


# Markdown extensions used to render tooltip strings. Kept minimal so tooltip
# bodies render bold/italic/links/code without pulling block-level features
# that don't make sense inside a popover.
_TOOLTIP_MD_EXTENSIONS: tuple[str, ...] = ("extra", "smarty")


def _detect_page_locale(md: markdown.Markdown) -> str | None:
    """Return the locale code MkDocs has attached to the current page.

    The mkdocs-static-i18n plugin (and Material's i18n integration) sets
    ``page.file.locale`` to the rendered language. We probe that path
    defensively so the extension still works outside MkDocs.
    """
    page = getattr(md, "page", None)
    file_obj = getattr(page, "file", None) if page is not None else None
    locale = getattr(file_obj, "locale", None) if file_obj else None
    return locale or None


class CalendarBlock(Block):
    """`/// calendar` block backed by a TOML body."""

    NAME = "calendar"
    ARGUMENT = False
    OPTIONS: dict = {}

    def on_init(self) -> None:
        # No per-block setup. The tooltip Markdown instance lives in the
        # shared `tracker` so every calendar on the same page reuses it.
        return None

    def _tooltip_md(self) -> markdown.Markdown:
        """Return the shared tooltip Markdown converter for this document."""
        md = self.tracker.get("tooltip_md")
        if md is None:
            md = markdown.Markdown(extensions=list(_TOOLTIP_MD_EXTENSIONS))
            self.tracker["tooltip_md"] = md
        return md

    def on_markdown(self) -> str:
        # Body is TOML, never Markdown — keep it untouched.
        return "raw"

    def on_create(self, parent: etree.Element) -> etree.Element:
        # Placeholder; rebuilt in `on_end` once the TOML body is available.
        return etree.SubElement(parent, "div", {"class": "md-calendar-pending"})

    def on_end(self, block: etree.Element) -> None:
        body = block.text or ""
        block.clear()
        block.text = None
        block.attrib.clear()

        default_locale = self._resolve_default_locale()
        base_path = self._resolve_base_path()

        try:
            config = parse_calendar(
                str(body),
                default_locale=default_locale,
                base_path=base_path,
            )
        except CalendarError as err:
            self._render_error(block, str(err))
            return

        self.tracker.setdefault("counter", 0)
        next_id = render_calendar(
            block,
            config,
            tooltip_renderer=self._render_tooltip,
            id_start=self.tracker["counter"],
        )
        self.tracker["counter"] = next_id

    def _render_tooltip(self, items: list[tuple[str, str]]) -> str:
        """Render tooltip entries as colour-bulleted lines.

        Each `(source_class, markdown_text)` becomes one `<div>` whose CSS
        class drives the bullet colour. We deliberately avoid `<ul>/<li>` so
        Material's `md-typeset` list styling doesn't stack a second bullet on
        top of ours. The joined HTML is stashed on the parent markdown so it
        survives serialization untouched.
        """
        parts = ['<div class="md-calendar-tooltip-items">']
        for source_class, text in items:
            md = self._tooltip_md()
            html = md.convert(text)
            md.reset()
            html = self._unwrap_single_paragraph(html.strip())

            classes = ["md-calendar-tooltip-item"]
            if source_class:
                classes.append(source_class)
            parts.append(f'<div class="{" ".join(classes)}">{html}</div>')
        parts.append("</div>")
        return self.md.htmlStash.store("".join(parts))

    def _resolve_default_locale(self) -> str | None:
        """Return the configured default locale, expanding ``"auto"``.

        ``auto`` falls back to the locale that the MkDocs i18n plugin attaches
        to the current page (``md.page.file.locale``). Without that signal we
        return ``None`` so the parser uses its built-in default.
        """
        configured = self.config.get("locale") if self.config else None
        if configured != "auto":
            return configured
        return _detect_page_locale(self.md)

    def _resolve_base_path(self) -> str | None:
        """Source path used to resolve `!include` directives, or ``None``."""
        page = getattr(self.md, "page", None)
        file_obj = getattr(page, "file", None) if page is not None else None
        return getattr(file_obj, "abs_src_path", None) if file_obj else None

    @staticmethod
    def _unwrap_single_paragraph(html: str) -> str:
        """Drop the wrapping `<p>…</p>` when the body is a single paragraph.

        Keeps tooltip lines visually flat inside their `<li>` while preserving
        multi-paragraph bodies as-is.
        """
        match = _SINGLE_PARAGRAPH_RE.match(html)
        if match and "<p>" not in match.group(1):
            return match.group(1)
        return html

    @staticmethod
    def _render_error(block: etree.Element, message: str) -> None:
        block.set("class", "md-calendar md-calendar-error")
        msg = etree.SubElement(block, "p", {"class": "md-calendar-error-message"})
        msg.text = f"Calendar error: {message}"

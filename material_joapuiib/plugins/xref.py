"""Cross-references to numbered captions (figures, tables...).

Syntax: ``[@id]`` or ``[@path/to/page.md#id]``. The link text is the label of
the caption, as rendered by ``pymdownx.blocks.caption`` (e.g. "Figura 2").

Resolution works on the rendered HTML, so the numbers always match the ones
shown in the captions:

- ``on_page_content``: collects the captioned figures of the page and resolves
  the references to targets of the same page.
- ``on_post_build``: every page is rendered, so the references to targets of
  other pages are resolved by patching the generated files.
"""

from __future__ import annotations

import logging
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path

import lxml.html
from mkdocs.plugins import BasePlugin
from mkdocs.utils import get_relative_url

log = logging.getLogger("mkdocs.plugins.xref")

REF_RE = re.compile(r"\[@([^\s\[\]<>&\"']+)\]")

# Text inside these elements is never rewritten. Other tags are copied as is.
SKIP_OR_TAG_RE = re.compile(
    r"<(code|pre|script|style|a|kbd|textarea)\b[^>]*>.*?</\1\s*>"
    r"|<!--.*?-->"
    r"|<[^>]+>",
    re.IGNORECASE | re.DOTALL,
)

PENDING_RE = re.compile(
    r'<a class="xref" data-xref-pending="([^"]*)">[^<]*</a>'
)

LABEL_TRAILING = " .: "


@dataclass(frozen=True)
class Target:
    src_uri: str
    url: str
    id: str
    label: str


def extract_targets(html: str, src_uri: str, url: str) -> list[Target]:
    """Return the numbered captioned figures found in a rendered page."""
    if "caption-prefix" not in html:
        return []

    root = lxml.html.fragment_fromstring(html, create_parent="div")
    targets = []
    for figure in root.xpath("//figure[@id]"):
        prefix = figure.xpath(
            "./figcaption//span[contains(concat(' ', @class, ' '), ' caption-prefix ')]"
        )
        if not prefix:
            continue
        label = prefix[0].text_content().strip(LABEL_TRAILING)
        if label:
            targets.append(Target(src_uri, url, figure.get("id"), label))
    return targets


def split_ref(ref: str) -> tuple[str | None, str]:
    """Split ``path#id`` into ``(path, id)``; ``id`` into ``(None, id)``."""
    if "#" in ref:
        path, _, id = ref.rpartition("#")
        return (path or None), id
    return None, ref


def render_link(href: str, id: str, label: str) -> str:
    return f'<a class="xref" href="{href}" data-xref="{id}">{label}</a>'


def rewrite_refs(html: str, replace) -> str:
    """Apply ``replace(match) -> str`` to every ref in text content."""
    if "[@" not in html:
        return html

    out = []
    pos = 0
    for m in SKIP_OR_TAG_RE.finditer(html):
        out.append(REF_RE.sub(replace, html[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(REF_RE.sub(replace, html[pos:]))
    return "".join(out)


class XrefPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        # (src_uri, id) -> Target. Kept across builds so `serve --dirty` works.
        self.targets: dict[tuple[str, str], Target] = {}
        # src_uri -> dest_uri of pages that contain unresolved references
        self.pending: dict[str, tuple[str, str]] = {}

    def on_pre_build(self, config):
        self.pending = {}

    def on_page_content(self, html, page, config, files):
        src_uri = page.file.src_uri

        self.targets = {
            k: t for k, t in self.targets.items() if t.src_uri != src_uri
        }
        local = {}
        for target in extract_targets(html, src_uri, page.url):
            key = (src_uri, target.id)
            if key in self.targets:
                log.warning(f"{src_uri}: duplicated caption id '{target.id}'")
            self.targets[key] = target
            local[target.id] = target

        has_pending = False

        def replace(match: re.Match) -> str:
            nonlocal has_pending
            ref = match.group(1)
            path, id = split_ref(ref)
            if path is None and id in local:
                return render_link(f"#{id}", id, local[id].label)
            has_pending = True
            return f'<a class="xref" data-xref-pending="{ref}">{match.group(0)}</a>'

        html = rewrite_refs(html, replace)
        if has_pending:
            self.pending[src_uri] = (page.file.dest_uri, page.url)
        return html

    def on_post_build(self, config):
        for src_uri, (dest_uri, url) in self.pending.items():
            path = Path(config.site_dir) / dest_uri
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            patched = PENDING_RE.sub(
                lambda m: self._resolve(m.group(1), src_uri, url), text
            )
            if patched != text:
                path.write_text(patched, encoding="utf-8")

    def _resolve(self, ref: str, src_uri: str, url: str) -> str:
        path, id = split_ref(ref)
        fallback = f"[@{ref}]"

        if path is not None:
            base = posixpath.dirname(src_uri)
            candidates = [
                posixpath.normpath(posixpath.join(base, path)),
                posixpath.normpath(path.lstrip("/")),
            ]
            found = [
                self.targets[(c, id)] for c in candidates if (c, id) in self.targets
            ]
        else:
            found = [t for (_, i), t in self.targets.items() if i == id]

        if not found:
            log.warning(f"{src_uri}: unknown reference '{fallback}'")
            return fallback
        if len(found) > 1:
            log.warning(
                f"{src_uri}: ambiguous reference '{fallback}', "
                f"use [@path/to/page.md#{id}] (found in "
                f"{', '.join(t.src_uri for t in found)})"
            )
            return fallback

        target = found[0]
        href = get_relative_url(target.url, url) if target.src_uri != src_uri else ""
        return render_link(f"{href}#{id}", id, target.label)

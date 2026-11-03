"""Locate ``/// access`` sections in rendered page HTML."""
from __future__ import annotations

import html
import json
import re
from typing import Callable

START_RE = re.compile(
    r'<div class="access-section" data-access-section="([^"]*)">')
DIV_RE = re.compile(r"<div\b|</div>")
HEADING_ID_RE = re.compile(r'<h[1-6]\b[^>]*\bid="([^"]+)"')


def split_list(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def parse_options(raw: str) -> dict:
    """Section options from the attribute, with list values split."""
    options = json.loads(html.unescape(raw))
    for key in ("allow", "deny", "bypass", "password", "bypass_password"):
        if key in options:
            options[key] = split_list(options[key])
    return options


def heading_ids(fragment: str) -> set[str]:
    return set(HEADING_ID_RE.findall(fragment))


def transform(content: str, replace: Callable[[str, dict], str]) -> str:
    """Replace every access section by ``replace(inner_html, options)``.

    Nested sections are replaced first, so ``inner_html`` never contains one.
    """
    out = []
    pos = 0
    while True:
        match = START_RE.search(content, pos)
        if not match:
            out.append(content[pos:])
            break
        depth = 1
        scan = match.end()
        while depth:
            tag = DIV_RE.search(content, scan)
            if tag is None:
                raise ValueError("unbalanced <div> in access section")
            depth += 1 if tag.group(0) == "<div" else -1
            scan = tag.end()
        inner = content[match.end():tag.start()]
        out.append(content[pos:match.start()])
        out.append(replace(transform(inner, replace), parse_options(match.group(1))))
        pos = tag.end()
    return "".join(out)

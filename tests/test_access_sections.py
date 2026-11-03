import pytest
from zoneinfo import ZoneInfo

from material_joapuiib.plugins.access import sections
from material_joapuiib.plugins.access.rules import (
    AccessConfigError, Directory, resolve_section,
)

TZ = ZoneInfo("UTC")


def wrap(inner, opts='{&quot;password&quot;: &quot;x&quot;}'):
    return f'<div class="access-section" data-access-section="{opts}">{inner}</div>'


def test_replaces_section_and_keeps_rest():
    html = "<p>a</p>" + wrap("<p>secret</p>") + "<p>b</p>"
    out = sections.transform(html, lambda inner, o: f"[{inner}|{o}]")
    assert out == "<p>a</p>[<p>secret</p>|{'password': ['x']}]<p>b</p>"


def test_nested_divs_inside_section():
    html = wrap("<div><div>deep</div></div><p>x</p>") + "<div>after</div>"
    out = sections.transform(html, lambda inner, o: "S")
    assert out == "S<div>after</div>"


def test_nested_sections_inner_first():
    inner = wrap("<p>in</p>", "{&quot;password&quot;: &quot;i&quot;}")
    html = wrap("<p>out</p>" + inner)
    seen = []

    def repl(content, opts):
        seen.append(content)
        return f"<{opts['password'][0]}>"

    out = sections.transform(html, repl)
    assert out == "<x>"
    assert seen == ["<p>in</p>", "<p>out</p><i>"]


def test_unbalanced_is_error():
    with pytest.raises(ValueError):
        sections.transform('<div class="access-section" data-access-section="{}"><div>', lambda *_: "")


def test_options_split_lists():
    opts = sections.parse_options("{&quot;allow&quot;: &quot;a, b&quot;, &quot;end&quot;: &quot;2030-01-01&quot;}")
    assert opts == {"allow": ["a", "b"], "end": "2030-01-01"}


def test_heading_ids():
    assert sections.heading_ids('<h2 id="a">A</h2><h3 class="x" id="b">B</h3><p id="c">') == {"a", "b"}


def directory():
    return Directory.build({"bob": {"password": "p"}}, {})


def test_resolve_section_ok():
    a = resolve_section(directory(), {"allow": ["bob"], "password": ["x"]}, TZ, "w")
    assert a.protected and a.users == {"bob": False} and a.passwords == ["x"]


def test_resolve_section_empty_is_error():
    with pytest.raises(AccessConfigError, match="without options"):
        resolve_section(directory(), {}, TZ, "w")


def test_resolve_section_rejects_page_only_keys():
    with pytest.raises(AccessConfigError, match="unknown"):
        resolve_section(directory(), {"password": ["x"], "nav": "hide"}, TZ, "w")

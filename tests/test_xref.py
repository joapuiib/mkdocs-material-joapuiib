"""Tests for the xref plugin."""
from __future__ import annotations

import logging

from material_joapuiib.plugins.xref import (
    XrefPlugin,
    extract_targets,
    rewrite_refs,
    REF_RE,
    split_ref,
)

FIG = """
<figure id="figure-a"><p><img src="a.png"></p>
<figcaption><p><span class="caption-prefix">Figura 2.</span> Text</p></figcaption></figure>
<figure id="no-number"><figcaption><p>Plain</p></figcaption></figure>
<figure><figcaption><p><span class="caption-prefix">Figura 3.</span> No id</p></figcaption></figure>
"""


def test_extract_targets_only_numbered_with_id():
    targets = extract_targets(FIG, "a.md", "a/")
    assert [(t.id, t.label) for t in targets] == [("figure-a", "Figura 2")]


def test_split_ref():
    assert split_ref("x") == (None, "x")
    assert split_ref("../p.md#x") == ("../p.md", "x")


def test_rewrite_skips_code_and_tags():
    html = '<p>[@a] <code>[@a]</code> <a href="x">[@a]</a> <img alt="[@a]"></p><pre><code>[@a]</code></pre>'
    out = rewrite_refs(html, lambda m: "X")
    assert out == '<p>X <code>[@a]</code> <a href="x">[@a]</a> <img alt="[@a]"></p><pre><code>[@a]</code></pre>'


def test_ref_regex_ignores_normal_brackets():
    assert REF_RE.search("[text](url) [^1] [ @a]") is None
    assert REF_RE.search("[@figure-a]").group(1) == "figure-a"


class FakeFile:
    def __init__(self, src, dest):
        self.src_uri, self.dest_uri = src, dest


class FakePage:
    def __init__(self, src, url):
        self.file = FakeFile(src, url + "index.html")
        self.url = url


def test_same_page_and_cross_page(tmp_path):
    plugin = XrefPlugin()
    plugin.on_pre_build(None)
    page_a = FakePage("a.md", "a/")
    page_b = FakePage("sub/b.md", "sub/b/")

    html_a = plugin.on_page_content("<p>[@figure-a] [@nope]</p>" + FIG, page_a, None, None)
    assert '<a class="xref" href="#figure-a" data-xref="figure-a">Figura 2</a>' in html_a
    assert 'data-xref-pending="nope"' in html_a

    html_b = plugin.on_page_content(
        "<p>[@figure-a] [@../a.md#figure-a]</p>", page_b, None, None
    )
    assert html_b.count("data-xref-pending") == 2

    class Cfg:
        site_dir = str(tmp_path)

    for page, html in ((page_a, html_a), (page_b, html_b)):
        p = tmp_path / page.file.dest_uri
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding="utf-8")

    plugin.on_post_build(Cfg())

    out_b = (tmp_path / "sub/b/index.html").read_text()
    assert out_b.count('href="../../a/#figure-a"') == 2
    assert "Figura 2</a>" in out_b

    out_a = (tmp_path / "a/index.html").read_text()
    assert "[@nope]" in out_a and "data-xref-pending" not in out_a


def test_ambiguous_warns(tmp_path, caplog):
    plugin = XrefPlugin()
    plugin.on_pre_build(None)
    for src, url in (("a.md", "a/"), ("b.md", "b/")):
        plugin.on_page_content(FIG, FakePage(src, url), None, None)
    page_c = FakePage("c.md", "c/")
    html = plugin.on_page_content("<p>[@figure-a]</p>", page_c, None, None)
    p = tmp_path / "c/index.html"
    p.parent.mkdir(parents=True)
    p.write_text(html)

    class Cfg:
        site_dir = str(tmp_path)

    with caplog.at_level(logging.WARNING, logger="mkdocs.plugins.xref"):
        plugin.on_post_build(Cfg())
    assert "ambiguous" in caplog.text

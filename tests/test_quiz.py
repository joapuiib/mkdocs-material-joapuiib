"""Tests for the ``/// quiz`` pymdownx Blocks extension."""
from __future__ import annotations

from textwrap import dedent

import markdown


def render(src: str, **ext_config) -> str:
    md = markdown.Markdown(
        extensions=["material_joapuiib.extensions.quiz", "pymdownx.tasklist"],
        extension_configs={"material_joapuiib.extensions.quiz": ext_config},
    )
    return md.convert(dedent(src))


BASIC = """
/// quiz | Which port does **PostgreSQL** use?
- [ ] 8069
- [x] `5432`
- [ ] 3306

It is the default port.
///
"""


def test_question_rendered_with_inline_markdown():
    html = render(BASIC)
    assert '<div class="quiz-question">Which port does <strong>PostgreSQL</strong> use?</div>' in html


def test_options_marked_and_markers_removed():
    html = render(BASIC)
    assert '<ul class="quiz-options">' in html
    assert '<li class="quiz-option">8069</li>' in html
    assert '<li class="quiz-option" data-quiz-correct=""><code>5432</code></li>' in html
    assert "[x]" not in html and "[ ]" not in html
    # tasklist must not turn the options into checkboxes
    assert "checkbox" not in html


def test_explanation_wrapped():
    html = render(BASIC)
    assert '<div class="quiz-explanation">\n<p>It is the default port.</p>\n</div>' in html


def test_without_explanation():
    html = render("""
    /// quiz | Q
    - [x] a
    - [ ] b
    ///
    """)
    assert "quiz-explanation" not in html


def test_loose_list():
    html = render("""
    /// quiz | Q
    - [ ] a

    - [X] b
    ///
    """)
    assert '<li class="quiz-option" data-quiz-correct="">\n<p>b</p>' in html
    assert "[X]" not in html


def test_multiple_correct():
    html = render("""
    /// quiz | Q
    - [x] a
    - [ ] b
    - [x] c
    ///
    """)
    assert html.count("data-quiz-correct") == 2


def test_without_question():
    html = render("""
    /// quiz
    - [x] a
    ///
    """)
    assert "quiz-question" not in html
    assert 'class="quiz-option"' in html


def test_shuffle_default_off():
    assert "data-quiz-shuffle" not in render(BASIC)


def test_shuffle_extension_config():
    assert "data-quiz-shuffle" in render(BASIC, shuffle=True)


def test_shuffle_block_option_overrides_config():
    on = render("""
    /// quiz | Q
        shuffle: true

    - [x] a
    ///
    """)
    off = render("""
    /// quiz | Q
        shuffle: false

    - [x] a
    ///
    """, shuffle=True)
    assert "data-quiz-shuffle" in on
    assert "data-quiz-shuffle" not in off

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
    assert '<li class="quiz-option">\n<div class="quiz-option-body">8069</div>\n</li>' in html
    assert '<li class="quiz-option" data-quiz-correct="">\n<div class="quiz-option-body"><code>5432</code></div>\n</li>' in html
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
    assert '<li class="quiz-option" data-quiz-correct="">\n<div class="quiz-option-body">\n<p>b</p>' in html
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


def test_tilde_prefix_shuffles():
    html = render("""
    /// quiz | ~ Which one?
    - [x] A
    - [ ] B
    ///
    """)
    assert "data-quiz-shuffle" in html
    assert '<div class="quiz-question">Which one?</div>' in html


def test_tilde_prefix_respects_explicit_option():
    html = render("""
    /// quiz | ~ Which one?
        shuffle: false

    - [x] A
    - [ ] B
    ///
    """)
    assert "data-quiz-shuffle" not in html


def test_solutions_only_in_the_page_when_previewing():
    from material_joapuiib.extensions import quiz as quiz_mod

    src = "/// exam | T\n    id: t\n\n//// quiz-test | Q?\n- [x] a\n- [ ] b\n////\n///\n"
    try:
        quiz_mod.PREVIEW_SOLUTIONS = False
        assert "data-quiz-solution" not in render(src)
        quiz_mod.PREVIEW_SOLUTIONS = True
        assert 'data-quiz-solution' in render(src)
    finally:
        quiz_mod.PREVIEW_SOLUTIONS = False


def test_authoring_mistakes_are_warned(caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="mkdocs.material_joapuiib.quiz")
    render("/// quiz | No answer\n- [ ] a\n- [ ] b\n///\n")
    render("/// quiz-match | Pairs\n- Portugal\n- Italy -> Rome\n///\n")
    render("/// quiz-order | One\n- Only\n///\n")
    messages = " ".join(r.getMessage() for r in caplog.records)
    assert "cap opció està marcada" in messages
    assert "«Portugal» no té `->`" in messages
    assert "calen almenys dos elements" in messages


def test_well_formed_questions_do_not_warn(caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="mkdocs.material_joapuiib.quiz")
    render("/// quiz | Ok\n- [ ] a\n- [x] b\n///\n")
    render("/// quiz-text | Ok\n- a\n///\n")
    assert not caplog.records

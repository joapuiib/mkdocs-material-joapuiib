"""``/// quiz`` block: interactive multiple-choice question.

The argument is the question. The body is a Markdown list whose items start
with ``[ ]`` (wrong) or ``[x]`` (correct). Anything after the list is the
explanation, shown only once the question is answered correctly::

    /// quiz | Which port does PostgreSQL listen on by default?
    - [ ] 8069
    - [x] 5432
    - [ ] 3306

    `5432` is the default PostgreSQL port.
    ///

Block options:

- ``shuffle``: shuffle the options in the browser. Defaults to the extension
  ``shuffle`` setting (``false``).

The theme ships the styles (``stylesheets/quiz.css``) and the behaviour
(``javascript/quiz.js``).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as etree

from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_ternary

_MARKER_RE = re.compile(r"^\s*\[([ xX])\]\s+")


def _first_text_holder(li: etree.Element) -> etree.Element:
    """Return the element holding the item's leading text.

    Tight lists keep the text in ``<li>``; loose lists wrap it in ``<p>``.
    """
    if not (li.text or "").strip() and len(li) and li[0].tag == "p":
        return li[0]
    return li


class QuizBlock(Block):
    NAME = "quiz"
    ARGUMENT = None
    OPTIONS = {"shuffle": [None, type_ternary]}

    def on_create(self, parent: etree.Element) -> etree.Element:
        quiz = etree.SubElement(parent, "div", {"class": "quiz"})
        shuffle = self.options["shuffle"]
        if shuffle is None:
            shuffle = self.config.get("shuffle", False)
        if shuffle:
            quiz.set("data-quiz-shuffle", "")
        if self.argument:
            question = etree.SubElement(quiz, "div", {"class": "quiz-question"})
            question.text = self.argument
        return quiz

    def on_end(self, block: etree.Element) -> None:
        options = next((child for child in block if child.tag == "ul"), None)
        if options is None:
            return

        options.set("class", "quiz-options")
        for li in options.findall("li"):
            li.set("class", "quiz-option")
            holder = _first_text_holder(li)
            match = _MARKER_RE.match(holder.text or "")
            if not match:
                continue
            holder.text = holder.text[match.end():]
            if match.group(1) in "xX":
                li.set("data-quiz-correct", "")

        rest = [
            child for child in block
            if child is not options and child.get("class") != "quiz-question"
        ]
        if rest:
            explanation = etree.SubElement(block, "div", {"class": "quiz-explanation"})
            for child in rest:
                block.remove(child)
                explanation.append(child)


class QuizExtension(BlocksExtension):
    def __init__(self, *args, **kwargs):
        self.config = {
            "shuffle": [False, "Shuffle the options of every quiz by default."],
        }
        super().__init__(*args, **kwargs)

    def extendMarkdownBlocks(self, md, block_mgr):  # noqa: N802 (markdown API)
        block_mgr.register(QuizBlock, self.getConfigs())


def makeExtension(*args, **kwargs):  # noqa: N802 (markdown API)
    return QuizExtension(*args, **kwargs)

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
  ``shuffle`` setting (``false``). A leading ``~`` in the question
  (``/// quiz | ~ Question``) is a shorthand for ``shuffle: true``.

Outside an exam, ``quiz-text`` checks the answer on Enter. ``quiz-match``, ``quiz-order``, ``quiz-essay`` and ``points`` are ignored by the
browser script: they are only meaningful inside an ``/// exam`` block (see below).

``/// exam`` block: wraps several ``/// quiz`` blocks into an exam that students
solve in the browser. The correct answers are **removed from the generated
HTML**; the explanations too. The student exports an encrypted file with the
answers (RSA-OAEP + AES-GCM, with the teacher's public key) and uploads it to
the LMS. ``python -m material_joapuiib.examtool grade`` decrypts and grades
the answers using the Markdown source, which is never published.

Question blocks (``quiz-test`` is ``quiz`` with a name that fits an exam):

- ``/// quiz-test``: list of ``[ ]`` / ``[x]`` options. Several ``[x]`` make
  it multiple choice.
- ``/// quiz-text``: short answer. Each list item is an accepted answer.
- ``/// quiz-match``: each list item is ``left -> right``.
- ``/// quiz-order``: list items in the correct order (shown shuffled).
- ``/// quiz-essay``: free text, graded by hand.

``demo: true`` on an ``/// exam`` only shows the questions (no name field,
no export button): useful for documentation examples.

The theme ships the styles (``stylesheets/quiz.css``) and the behaviour
(``javascript/quiz.js``).
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import random
import re
import xml.etree.ElementTree as etree

import markdown
from markdown.treeprocessors import Treeprocessor
from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import (
    Block,
    type_boolean,
    type_number,
    type_string,
    type_ternary,
)

log = logging.getLogger("mkdocs.material_joapuiib.quiz")  # a warning fails `--strict` builds

# Solutions of the exams converted so far, by exam id. Read by the grader
# (``material_joapuiib.examtool``); never written to the generated site.
SOLUTIONS: dict[str, dict] = {}

# Development preview: when true, every question of an exam also carries its solution in a
# ``data-quiz-solution`` attribute so the author can see it. Only the ``access`` plugin turns it on,
# and only for ``serve``: a production build must never contain the solutions.
PREVIEW_SOLUTIONS = False


def _inline_html(text: str) -> str:
    """Render the inline Markdown of a solution (code, emphasis...) without the wrapping paragraph."""
    html = markdown.markdown(text)
    return re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S)


def _preview(quiz: etree.Element, data: dict) -> None:
    """Keep the solution in the page, as HTML for the texts (development preview only)."""
    if not PREVIEW_SOLUTIONS:
        return
    for key in ("accepted", "order"):
        if key in data:
            data[key] = [_inline_html(t) for t in data[key]]
    if "pairs" in data:
        data["pairs"] = [[_inline_html(t) for t in pair] for pair in data["pairs"]]
    quiz.set("data-quiz-solution", json.dumps(data, ensure_ascii=False))

_MARKER_RE = re.compile(r"^\s*\[([ xX])\](?:\s+|$)")


def _first_text_holder(li: etree.Element) -> etree.Element:
    """Return the element holding the item's leading text.

    Tight lists keep the text in ``<li>``; loose lists wrap it in ``<p>``.
    """
    if not (li.text or "").strip() and len(li) and li[0].tag == "p":
        return li[0]
    return li


def _check_authoring(quiz: etree.Element, options: etree.Element | None, question: str) -> None:
    """Warn about questions that cannot be answered or graded as written."""
    qtype = quiz.get("data-quiz-type", "choice")
    where = f"quiz '{question or '(sense enunciat)'}'"
    items = options.findall("li") if options is not None else []
    if qtype == "choice":
        if len(items) < 2:
            log.warning("%s: cal almenys dues opcions.", where)
        elif not any("data-quiz-correct" in li.attrib for li in items):
            log.warning("%s: cap opció està marcada com a correcta (`[x]`).", where)
    elif qtype == "text" and not items:
        log.warning("%s: no té cap resposta acceptada.", where)
    elif qtype == "match":
        bad = [_raw(li) for li in items if "->" not in _raw(li)]
        for raw in bad:
            log.warning("%s: l'element «%s» no té `->` i s'ignora.", where, raw)
        if len(items) - len(bad) < 2:
            log.warning("%s: calen almenys dues parelles `esquerra -> dreta`.", where)
    elif qtype == "order" and len(items) < 2:
        log.warning("%s: calen almenys dos elements.", where)


class QuizBlock(Block):
    NAME = "quiz"
    TYPE = "choice"
    ARGUMENT = None
    OPTIONS = {
        "shuffle": [None, type_ternary],
        "points": [1, type_number],
        "lang": ["", type_string],
        "table": [False, type_boolean],
        "columns": ["", type_string],
        "pinned": ["", type_string],
    }

    def on_create(self, parent: etree.Element) -> etree.Element:
        quiz = etree.SubElement(parent, "div", {"class": "quiz"})
        shuffle = self.options["shuffle"]
        argument = self.argument
        if argument and argument.startswith("~"):
            # `/// quiz | ~ Question` is a shorthand for `shuffle: true`.
            argument = argument[1:].lstrip()
            if shuffle is None:
                shuffle = True
        if shuffle is None:
            shuffle = self.config.get("shuffle", False)
        if shuffle:
            quiz.set("data-quiz-shuffle", "")
        if self.TYPE != "choice":
            quiz.set("data-quiz-type", self.TYPE)
        if self.options["lang"]:
            quiz.set("data-quiz-lang", self.options["lang"])
        if self.options["table"]:
            # `quiz-essay` only: the answer is an editable table, saved as a Markdown table.
            quiz.set("data-quiz-table", "")
            if self.options["columns"]:
                quiz.set("data-quiz-columns", self.options["columns"])
            if self.options["pinned"]:
                # A last column that cannot be renamed or removed.
                quiz.set("data-quiz-pinned", self.options["pinned"])
        quiz.set("data-quiz-points", str(self.options["points"]))
        if argument:
            question = etree.SubElement(quiz, "div", {"class": "quiz-question"})
            question.text = argument
        return quiz

    def on_end(self, block: etree.Element) -> None:
        options = next((child for child in block if child.tag == "ul"), None)

        if options is not None:
            if block.get("data-quiz-type", "choice") == "choice":
                options.set("class", "quiz-options")
                for li in options.findall("li"):
                    li.set("class", "quiz-option")
                    holder = _first_text_holder(li)
                    match = _MARKER_RE.match(holder.text or "")
                    if match:
                        holder.text = holder.text[match.end():]
                        if match.group(1) in "xX":
                            li.set("data-quiz-correct", "")
                    # One flex item for the whole content, so inline markup
                    # (code, emphasis) does not become separate columns.
                    body = etree.Element("div", {"class": "quiz-option-body"})
                    body.text, li.text = li.text, None
                    for child in list(li):
                        li.remove(child)
                        body.append(child)
                    li.append(body)
            else:
                options.set("class", "quiz-items")
        question = next((c for c in block if c.get("class") == "quiz-question"), None)
        _check_authoring(block, options, (question.text or "") if question is not None else "")

        content = [c for c in block if c.get("class") != "quiz-question"]
        if options is None:
            # No list (e.g. an essay): everything is part of the statement.
            before, after = ([] if block.get("data-quiz-type", "choice") == "choice" else content), []
        else:
            position = content.index(options)
            before, after = content[:position], content[position + 1:]

        if before:
            stem = etree.Element("div", {"class": "quiz-stem"})
            for child in before:
                block.remove(child)
                stem.append(child)
            question = next((c for c in block if c.get("class") == "quiz-question"), None)
            block.insert(list(block).index(question) + 1 if question is not None else 0, stem)
        if after:
            explanation = etree.SubElement(block, "div", {"class": "quiz-explanation"})
            for child in after:
                block.remove(child)
                explanation.append(child)


class QuizTestBlock(QuizBlock):
    NAME = "quiz-test"


class QuizTextBlock(QuizBlock):
    NAME = "quiz-text"
    TYPE = "text"


class QuizMatchBlock(QuizBlock):
    NAME = "quiz-match"
    TYPE = "match"


class QuizOrderBlock(QuizBlock):
    NAME = "quiz-order"
    TYPE = "order"


class QuizEssayBlock(QuizBlock):
    NAME = "quiz-essay"
    TYPE = "essay"


# ---------------------------------------------------------------- exam

def _raw(li: etree.Element) -> str:
    """Raw Markdown text of a list item (inline patterns are not applied yet)."""
    return (_first_text_holder(li).text or "").strip()


def _token(qid: str, text: str) -> str:
    """Opaque identifier of an option, so the HTML does not reveal the solution."""
    return hashlib.sha1(f"{qid}:{text}".encode()).hexdigest()[:8]


def _shuffled(items: list, seed: str, avoid_identity: bool = True) -> list:
    rng = random.Random(seed)
    out = list(items)
    for _ in range(20):
        rng.shuffle(out)
        if not avoid_identity or len(out) < 2 or out != items:
            break
    return out


def _clean_key(key: str) -> str:
    """Return a PEM or base64 public key as a single-line base64 SPKI string.

    ``key`` may also be the path of a file (relative to the working directory)
    that contains the public key.
    """
    if key and "\n" not in key and len(key) < 1024 and os.path.isfile(key):
        with open(key, encoding="utf-8") as f:
            key = f.read()
    cleaned = "".join(
        line.strip() for line in key.strip().splitlines() if not line.startswith("-----")
    )
    if cleaned:
        try:
            base64.b64decode(cleaned, validate=True)
        except ValueError as err:
            raise ValueError(
                f"exam public_key is not a valid base64/PEM key nor an existing file: {key[:60]!r}"
            ) from err
    return cleaned


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "exam"


def _penalty(quiz: etree.Element, points: float, divisor: int) -> None:
    """Publish what a wrong answer subtracts, as a percentage of the question's points."""
    if divisor > 0:
        quiz.set("data-quiz-penalty-pct", f"{round(100 / divisor, 1):g}")


def _secure_quiz(quiz: etree.Element, qid: str) -> dict:
    """Strip the solution from a quiz and return it as a dict for the grader."""
    qtype = quiz.get("data-quiz-type", "choice")
    points = float(quiz.attrib.get("data-quiz-points", 1))
    quiz.set("data-quiz-points", f"{points:g}")  # the page shows the score of each question
    question = next((c for c in quiz if c.get("class") == "quiz-question"), None)
    solution = {"points": points, "question": (question.text if question is not None else "")}
    quiz.set("data-quiz-id", qid)

    for child in list(quiz):
        if child.get("class") == "quiz-explanation":
            quiz.remove(child)
    items_list = next((c for c in quiz if c.tag == "ul"), None)
    items = items_list.findall("li") if items_list is not None else []

    if qtype == "choice":
        correct = []
        for i, li in enumerate(items):
            if "data-quiz-correct" in li.attrib:
                correct.append(i)
                del li.attrib["data-quiz-correct"]
            li.set("data-i", str(i))
        quiz.set("data-quiz-type", "multiple" if len(correct) > 1 else "single")
        solution.update(type="choice", correct=correct, n=len(items))
        # Single answer: -p/(n-1). Several answers: the grader subtracts p/k for each wrong option
        # marked; it is not published, because it would reveal how many answers are correct (k).
        if len(correct) <= 1:
            _penalty(quiz, points, len(items) - 1)
        _preview(quiz, {"type": "choice", "correct": correct})
        return solution

    raws = [_raw(li) for li in items]
    if items_list is not None:
        quiz.remove(items_list)

    if qtype == "text":
        etree.SubElement(quiz, "input", {
            "class": "exam-text", "type": "text",
            "autocomplete": "off", "spellcheck": "false",
        })
        solution.update(type="text", accepted=raws)
        _preview(quiz, {"type": "text", "accepted": raws})
    elif qtype == "essay":
        etree.SubElement(quiz, "textarea", {"class": "exam-essay", "rows": "8"}).text = ""
        solution.update(type="essay")
    elif qtype == "match":
        pairs = [tuple(part.strip() for part in raw.split("->", 1)) for raw in raws]
        pairs = [p for p in pairs if len(p) == 2]
        rows = etree.SubElement(quiz, "div", {"class": "exam-match"})
        for left, _right in pairs:
            row = etree.SubElement(rows, "div", {"class": "exam-match-row"})
            etree.SubElement(row, "span", {"class": "exam-match-left"}).text = left
        rights = etree.SubElement(quiz, "ul", {"class": "exam-match-rights", "hidden": ""})
        for right in _shuffled([p[1] for p in pairs], qid, avoid_identity=False):
            etree.SubElement(rights, "li", {"data-token": _token(qid, right)}).text = right
        solution.update(type="match", answers=[_token(qid, p[1]) for p in pairs])
        _penalty(quiz, points, len(pairs))  # each error cancels one correct pair
        _preview(quiz, {"type": "match", "pairs": [list(p) for p in pairs]})
    elif qtype == "order":
        order = etree.SubElement(quiz, "ul", {"class": "exam-order"})
        for raw in _shuffled(raws, qid):
            etree.SubElement(order, "li", {"data-token": _token(qid, raw)}).text = raw
        solution.update(type="order", order=[_token(qid, raw) for raw in raws])
        _penalty(quiz, points, len(raws))  # each error cancels one correct item
        _preview(quiz, {"type": "order", "order": raws})
    return solution


class ExamBlock(Block):
    NAME = "exam"
    ARGUMENT = None
    OPTIONS = {
        "id": ["", type_string],
        "key": ["", type_string],
        "demo": [False, type_boolean],
        "lockdown": [False, type_boolean],
        "unlock": ["", type_string],
    }

    def on_create(self, parent: etree.Element) -> etree.Element:
        # `no-copy` makes Material skip the "copy to clipboard" button of the code blocks.
        exam = etree.SubElement(parent, "div", {"class": "exam no-copy"})
        self._id = self.options["id"] or _slug(self.argument or "exam")
        exam.set("data-exam-id", self._id)
        key = _clean_key(self.options["key"] or self.config.get("public_key", ""))
        if key:
            exam.set("data-exam-key", key)
        if self.options["demo"]:
            exam.set("data-exam-demo", "")
        if self.options["lockdown"]:
            exam.set("data-exam-lockdown", "")
            if self.options["unlock"]:
                # Only a salted hash reaches the page; the browser compares it with the typed password.
                digest = hashlib.sha256(f"{self._id}:{self.options['unlock']}".encode()).hexdigest()
                exam.set("data-exam-unlock", digest)
        if self.argument:
            title = etree.SubElement(exam, "div", {"class": "exam-title"})
            title.text = self.argument
        return exam


class ExamTreeprocessor(Treeprocessor):
    """Remove the solutions from every ``/// exam`` once all its blocks are built.

    It runs after the blocks have been parsed (so every ``/// quiz`` is complete)
    and before the inline patterns (so list items still hold the raw Markdown).
    """

    def run(self, root: etree.Element) -> None:
        for exam in [el for el in root.iter("div") if "exam" in (el.get("class") or "").split()]:
            if exam.get("data-exam-done") is not None:
                continue
            exam.set("data-exam-done", "")
            solutions = {}
            quizzes = [el for el in exam.iter("div") if el.get("class") == "quiz"]
            for n, quiz in enumerate(quizzes, 1):
                question = next((c for c in quiz if c.get("class") == "quiz-question"), None)
                if question is not None:
                    text = question.text or ""
                else:  # no argument: use the raw text of the statement
                    text = "".join(t for el in quiz.iter() if el.get("class") != "quiz-options"
                                   for t in (el.text,) if t)
                qid = f"q{n}-{hashlib.sha1(text.encode()).hexdigest()[:6]}"
                solutions[qid] = _secure_quiz(quiz, qid)
            SOLUTIONS[exam.get("data-exam-id")] = solutions

        # Outside an exam, match and order are practice questions: the page checks them.
        in_exam = {id(q) for exam in root.iter("div") if "exam" in (exam.get("class") or "").split()
                   for q in exam.iter("div")}
        for n, quiz in enumerate(el for el in root.iter("div") if el.get("class") == "quiz"):
            qtype = quiz.get("data-quiz-type")
            if id(quiz) in in_exam or qtype not in ("match", "order"):
                continue
            explanation = next((c for c in quiz if c.get("class") == "quiz-explanation"), None)
            solution = _secure_quiz(quiz, f"practice{n}")
            if explanation is not None:  # `_secure_quiz` drops it; a practice question shows it once solved
                quiz.append(explanation)
            quiz.set("data-quiz-answer", json.dumps(solution["answers"] if qtype == "match" else solution["order"]))


class QuizExtension(BlocksExtension):
    def __init__(self, *args, **kwargs):
        self.config = {
            "shuffle": [False, "Shuffle the options of every quiz by default."],
            "public_key": ["", "Public key (SPKI base64 or PEM) used to encrypt the exam answers."],
        }
        super().__init__(*args, **kwargs)

    def extendMarkdownBlocks(self, md, block_mgr):  # noqa: N802 (markdown API)
        for block in (QuizBlock, QuizTestBlock, QuizTextBlock, QuizMatchBlock,
                      QuizOrderBlock, QuizEssayBlock):
            block_mgr.register(block, self.getConfigs())
        block_mgr.register(ExamBlock, self.getConfigs())
        md.treeprocessors.register(ExamTreeprocessor(md), "exam", 25)


def makeExtension(*args, **kwargs):  # noqa: N802 (markdown API)
    return QuizExtension(*args, **kwargs)

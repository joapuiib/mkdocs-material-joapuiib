"""Tests for the ``/// exam`` block and the grading tool."""
from __future__ import annotations

import base64
import json
from textwrap import dedent

import markdown
import pytest
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from material_joapuiib import examtool
from material_joapuiib.extensions import quiz

EXAM = """
/// exam | Test
    id: demo

//// quiz-test | Port?
- [ ] 8069
- [x] 5432

Explanation
////

//// quiz-test | Several?
- [x] A
- [x] B
- [ ] C
////

//// quiz-text | Extension?
    points: 2

- `.class`
- class
////

//// quiz-match | Match
- A -> one
- B -> two
////

//// quiz-order | Order
- first
- second
- third
////

//// quiz-essay | Essay
////
///
"""


def render(src=EXAM, **config):
    quiz.SOLUTIONS.clear()
    md = markdown.Markdown(
        extensions=["material_joapuiib.extensions.quiz"],
        extension_configs={"material_joapuiib.extensions.quiz": config},
    )
    return md.convert(dedent(src))


def test_no_solution_in_html():
    html = render()
    assert "data-quiz-correct" not in html
    assert "quiz-explanation" not in html and "Explanation" not in html
    assert 'data-quiz-type="single"' in html and 'data-quiz-type="multiple"' in html
    assert "`.class`" not in html and ".class" not in html
    assert '<textarea class="exam-essay"' in html


def test_copy_button_disabled():
    assert 'class="exam no-copy"' in render()


def test_public_key_cleaned():
    html = render(public_key="-----BEGIN PUBLIC KEY-----\nAAAA\nBBBB\n-----END PUBLIC KEY-----")
    assert 'data-exam-key="AAAABBBB"' in html


def test_public_key_from_file(tmp_path):
    key = tmp_path / "exam.pub"
    key.write_text("-----BEGIN PUBLIC KEY-----\nAAAA\nBBBB\n-----END PUBLIC KEY-----\n")
    assert 'data-exam-key="AAAABBBB"' in render(public_key=str(key))


def test_invalid_public_key_fails_the_build():
    import pytest
    with pytest.raises(ValueError):
        render(public_key="keys/does-not-exist.pub")


def test_essay_language_option():
    html = render("""
    /// exam | T

    //// quiz-essay | Write it
        lang: java
    ////
    ///
    """)
    assert 'data-quiz-lang="java"' in html


def test_solutions_collected():
    render()
    sol = quiz.SOLUTIONS["demo"]
    kinds = [s["type"] for s in sol.values()]
    assert kinds == ["choice", "choice", "text", "match", "order", "essay"]
    first, second, third = list(sol.values())[:3]
    assert first["correct"] == [1] and second["correct"] == [0, 1]
    assert third["points"] == 2 and third["accepted"] == ["`.class`", "class"]


def test_order_not_in_solution_order():
    html = render()
    first, second, third = (html.index(w) for w in ("first<", "second<", "third<"))
    assert not (first < second < third)


def test_scoring():
    render()
    q = quiz.SOLUTIONS["demo"]
    ids = list(q)
    assert examtool.score(q[ids[0]], [1]) == 1.0
    assert examtool.score(q[ids[0]], [0]) == -1.0  # two options: a wrong one subtracts 1/(2-1)
    assert examtool.score(q[ids[1]], [0, 1]) == 1.0
    assert examtool.score(q[ids[1]], [0]) == 0.5
    assert examtool.score(q[ids[1]], [0, 2]) == 0.0
    assert examtool.score(q[ids[2]], " Class ") == 1.0
    assert examtool.score(q[ids[2]], None) == 0.0
    assert examtool.score(q[ids[3]], q[ids[3]]["answers"]) == 1.0
    assert examtool.score(q[ids[4]], q[ids[4]]["order"]) == 1.0
    assert examtool.score(q[ids[5]], "text") is None


def test_wrong_answers_subtract():
    single = {"type": "choice", "correct": [0], "n": 4, "points": 1}
    assert examtool.score(single, [1]) == pytest.approx(-1 / 3)
    assert examtool.score(single, None) == 0.0
    match = {"type": "match", "answers": ["a", "b", "c", "d"], "points": 1}
    assert examtool.score(match, ["a", "b", "x", "y"]) == 0.0  # 2 right - 2 wrong
    assert examtool.score(match, ["a", "b", "c", "x"]) == 0.5  # 3 right - 1 wrong
    assert examtool.score(match, ["a", "", "", ""]) == 0.25  # blanks are not errors
    order = {"type": "order", "order": ["a", "b", "c"], "points": 1}
    assert examtool.score(order, ["a", "c", "b"]) == 0.0  # 1 right - 2 wrong
    assert examtool.score(order, ["a", "b", "c"]) == 1.0


def test_total_is_never_negative():
    solutions = {"q1": {"type": "choice", "correct": [0], "n": 2, "points": 1}}
    graded = examtool.grade_submission(solutions, {"answers": {"q1": [1]}})
    assert graded["scores"]["q1"] == -1.0
    assert graded["total"] == 0.0


def test_decrypt_roundtrip(tmp_path):
    private = RSA.generate(2048)
    payload = {"v": 1, "exam": "demo", "name": "Ada", "answers": {"q1": [1]}}
    aes_key, iv = get_random_bytes(32), get_random_bytes(12)
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(json.dumps(payload).encode())
    blob = {
        "key": base64.b64encode(PKCS1_OAEP.new(private.publickey(), hashAlgo=SHA256).encrypt(aes_key)).decode(),
        "iv": base64.b64encode(iv).decode(),
        "data": base64.b64encode(ct + tag).decode(),
    }
    assert examtool.decrypt(blob, private) == payload


def test_lockdown_exposes_only_a_salted_hash_of_the_unlock_password():
    import hashlib

    html = render("""
/// exam | Test
    id: demo
    lockdown: true
    unlock: secret

//// quiz-text | Q?
- a
////
///
""")
    assert "data-exam-lockdown" in html
    assert f'data-exam-unlock="{hashlib.sha256(b"demo:secret").hexdigest()}"' in html
    assert "secret" not in html

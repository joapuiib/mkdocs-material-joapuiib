"""Command line tool for ``/// exam`` blocks.

Generate a key pair (keep the private key out of the repository)::

    python -m material_joapuiib.examtool keygen --private examen.key

The command prints the public key; set it as ``public_key`` in the
``material_joapuiib.extensions.quiz`` extension configuration.

Grade the answers downloaded from the LMS (a folder or a ``.zip``)::

    python -m material_joapuiib.examtool grade \\
        --private examen.key --source docs/examens/examen.md \\
        --submissions entregues.zip --csv notes.csv --essays redaccions/
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import sys
import zipfile
from pathlib import Path

import markdown
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from material_joapuiib.extensions import quiz

EXT = "material_joapuiib.extensions.quiz"


# ------------------------------------------------------------------ keys

def keygen(private: Path, bits: int = 3072) -> str:
    key = RSA.generate(bits)
    private.write_bytes(key.export_key("PEM"))
    private.chmod(0o600)
    return base64.b64encode(key.publickey().export_key("DER")).decode()


# ------------------------------------------------------------------ decrypt

def decrypt(blob: dict, private: RSA.RsaKey) -> dict:
    cipher = PKCS1_OAEP.new(private, hashAlgo=SHA256)
    aes_key = cipher.decrypt(base64.b64decode(blob["key"]))
    data = base64.b64decode(blob["data"])
    aes = AES.new(aes_key, AES.MODE_GCM, nonce=base64.b64decode(blob["iv"]))
    return json.loads(aes.decrypt_and_verify(data[:-16], data[-16:]))


def read_submissions(path: Path):
    """Yield ``(name, text)`` for every file in a folder or a zip file."""
    if path.is_dir():
        for file in sorted(p for p in path.rglob("*") if p.is_file()):
            yield file.name, file.read_text(encoding="utf-8", errors="replace")
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    yield info.filename, zf.read(info).decode("utf-8", errors="replace")
    else:
        yield path.name, path.read_text(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ grading

def load_solutions(source: Path) -> dict:
    quiz.SOLUTIONS.clear()
    markdown.Markdown(extensions=[EXT]).convert(source.read_text(encoding="utf-8"))
    return dict(quiz.SOLUTIONS)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).replace("`", "")).strip().lower()


def score(solution: dict, answer) -> float | None:
    """Fraction of the question solved, or ``None`` if graded by hand.

    Wrong answers subtract, as the exam page announces:

    * single choice: a wrong option subtracts ``1/(n-1)`` of the question (``n`` options), so it
      can be negative; an unanswered question is 0;
    * multiple choice, match and order: each wrong answer cancels one correct one, and the
      question never goes below 0.
    """
    kind = solution["type"]
    if kind == "essay":
        return None
    if answer is None:
        return 0.0
    if kind == "choice":
        correct, chosen = set(solution["correct"]), set(answer)
        if len(correct) == 1:
            if chosen == correct:
                return 1.0
            n = solution.get("n", 0)
            return -1 / (n - 1) if chosen and n > 1 else 0.0
        return max(0.0, (len(chosen & correct) - len(chosen - correct)) / len(correct))
    if kind == "text":
        return 1.0 if _norm(answer) in {_norm(a) for a in solution["accepted"]} else 0.0
    if kind in ("match", "order"):
        expected = solution["answers" if kind == "match" else "order"]
        given = list(answer)[: len(expected)]
        right = sum(1 for e, a in zip(expected, given) if e == a)
        wrong = sum(1 for e, a in zip(expected, given) if a and e != a)
        return max(0.0, (right - wrong) / len(expected))
    return 0.0


def find_answer(answers: dict, qid: str):
    """Answer of ``qid``. Falls back to the question number (``q7-...``) when the
    question text changed after the page was published, so the hash differs."""
    if qid in answers:
        return answers[qid]
    prefix = qid.split("-", 1)[0] + "-"
    matches = [v for k, v in answers.items() if k.startswith(prefix)]
    return matches[0] if len(matches) == 1 else None


def grade_submission(solutions: dict, payload: dict) -> dict:
    result = {"scores": {}, "manual": [], "total": 0.0, "max": 0.0}
    for qid, sol in solutions.items():
        s = score(sol, find_answer(payload["answers"], qid))
        if s is None:
            result["manual"].append(qid)
            continue
        points = sol["points"]
        result["scores"][qid] = round(s * points, 3)
        result["total"] += s * points
        result["max"] += points
    result["total"] = max(0.0, result["total"])  # the grade is never negative
    return result


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_") or "alumne"


def write_essays(directory: Path, solutions: dict, payload: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    lines = [f"# {payload['name']}", ""]
    for qid in (q for q, s in solutions.items() if s["type"] == "essay"):
        title = solutions[qid]["question"] or qid
        lines += [f"## {title}", "", "```", str(find_answer(payload["answers"], qid) or ""), "```", ""]
    (directory / f"{_slug(payload['name'])}.md").write_text("\n".join(lines), encoding="utf-8")


def cmd_grade(args) -> int:
    private = RSA.import_key(Path(args.private).read_bytes())
    solutions_by_exam = load_solutions(Path(args.source))
    if not solutions_by_exam:
        print("No s'ha trobat cap bloc /// exam en el fitxer.", file=sys.stderr)
        return 1
    exam_id = args.exam or next(iter(solutions_by_exam))
    solutions = solutions_by_exam[exam_id]
    qids = list(solutions)

    rows, errors = [], 0
    for name, text in read_submissions(Path(args.submissions)):
        try:
            payload = decrypt(json.loads(text), private)
        except (ValueError, KeyError, json.JSONDecodeError):
            print(f"[ignorat] {name}: no és una entrega xifrada vàlida", file=sys.stderr)
            errors += 1
            continue
        if payload.get("exam") != exam_id:
            print(f"[ignorat] {name}: examen «{payload.get('exam')}» ≠ «{exam_id}»", file=sys.stderr)
            errors += 1
            continue
        res = grade_submission(solutions, payload)
        rows.append({"student": payload["name"], "file": name, "start": payload.get("start", ""),
                     "date": payload.get("end") or payload.get("date", ""),
                     "incidents": sum(1 for e in payload.get("events", []) if e.get("type") not in ("consent", "unlock")),
                     "events": [e for e in payload.get("events", []) if e.get("type") not in ("consent", "unlock")], **res})
        if args.essays:
            write_essays(Path(args.essays), solutions, payload)

    rows.sort(key=lambda r: r["student"].lower())
    for r in rows:
        print(f"{r['student']:<40} {r['total']:6.2f} / {r['max']:.2f}   (redaccions per corregir: {len(r['manual'])}, incidències: {r['incidents']})")
        for e in r["events"]:
            print(f"    · {e.get('t', '')}  {e.get('type', '')}" + (f": {e['note']}" if e.get("note") else ""))
    print(f"\n{len(rows)} entregues corregides, {errors} ignorades.")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["student", "file", "start", "date", "total", "max", "manual", "incidents", *qids])
            for r in rows:
                w.writerow([r["student"], r["file"], r["start"], r["date"], round(r["total"], 3), r["max"],
                            len(r["manual"]), r["incidents"], *[r["scores"].get(q, "manual") for q in qids]])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="examtool", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    kg = sub.add_parser("keygen", help="genera la parella de claus")
    kg.add_argument("--private", required=True, help="fitxer on es guarda la clau privada (PEM)")

    gr = sub.add_parser("grade", help="desxifra i corregeix les entregues")
    gr.add_argument("--private", required=True, help="clau privada (PEM)")
    gr.add_argument("--source", required=True, help="fitxer Markdown de l'examen")
    gr.add_argument("--submissions", required=True, help="carpeta o .zip amb les entregues")
    gr.add_argument("--exam", help="identificador de l'examen (per defecte, el primer)")
    gr.add_argument("--csv", help="fitxer CSV d'eixida")
    gr.add_argument("--essays", help="carpeta on es guarden les respostes de redacció")

    args = parser.parse_args(argv)
    if args.command == "keygen":
        print(keygen(Path(args.private)))
        return 0
    return cmd_grade(args)


if __name__ == "__main__":
    sys.exit(main())

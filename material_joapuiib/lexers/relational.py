"""Pygments lexer for the textual notation of the relational model.

Notation:

- ``ENTITAT``: entity (table) name, written in uppercase.
- ``#atribut``: attribute that is part of the primary key.
- ``atribut(ENTITAT:#atribut)``: foreign key and the attribute it references.
- ``#atribut(ENTITAT:#atribut)``: foreign key that is also part of the primary key.
- ``-- text``: comment.

Example::

    CICLE_FORMATIU (
        #id_cicle,
        nom,
        id_familia(FAMILIA_PROFESSIONAL:#id_familia)
    )

Tokens (scoped CSS lives in ``stylesheets/highlight.css``):

- ``Name.Class`` (``nc``): entity.
- ``Name.Constant`` (``no``): primary key attribute.
- ``Name.Attribute`` (``na``): foreign key attribute.
- ``Name.Variable`` (``nv``): attribute that is both primary and foreign key.
- ``Name`` (``n``): any other attribute.
"""
import re

from pygments.lexer import RegexLexer
from pygments.token import Comment, Name, Punctuation, Text, Whitespace

__all__ = ["RelationalLexer"]

_WORD = r"[^\W\d]\w*"
# A foreign key is an attribute followed by a reference such as "(ENTITAT:#atribut)".
_REFERENCE = r"(?=\s*\(\s*[^\W\d]\w*\s*:)"


def _word(lexer, match):
    """Uppercase words are entities; the rest are plain attributes or text."""
    word = match.group(0)
    yield match.start(), Name.Class if word.isupper() else Name, word


class RelationalLexer(RegexLexer):
    """Lexer for the relational model notation used in the course notes."""

    name = "Relational model"
    aliases = ["relational", "relacional", "rel"]
    filenames = []
    mimetypes = []
    flags = re.MULTILINE | re.UNICODE

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"--.*?$", Comment.Single),
            (r"#" + _WORD + _REFERENCE, Name.Variable, "reference"),
            (_WORD + _REFERENCE, Name.Attribute, "reference"),
            (r"#" + _WORD, Name.Constant),
            (_WORD, _word),
            (r"[(),;]", Punctuation),
            (r".", Text),
        ],
        "reference": [
            (r"\s+", Whitespace),
            (r"\(", Punctuation),
            (r":", Punctuation),
            (r"#" + _WORD, Name.Constant),
            (_WORD, Name.Class),
            (r"\)", Punctuation, "#pop"),
            # Malformed reference: give control back to the root state.
            (r"", Text, "#pop"),
        ],
    }

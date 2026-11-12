"""Tests for the relational model Pygments lexer."""
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment, Name, Punctuation

from material_joapuiib.lexers import RelationalLexer


def tokens(src):
    return [(t, v) for t, v in RelationalLexer().get_tokens(src) if v.strip()]


def test_registered_by_alias():
    assert isinstance(get_lexer_by_name("relational"), RelationalLexer)


def test_entity_and_primary_key():
    assert tokens("COTXE(#matricula, marca)") == [
        (Name.Class, "COTXE"),
        (Punctuation, "("),
        (Name.Constant, "#matricula"),
        (Punctuation, ","),
        (Name, "marca"),
        (Punctuation, ")"),
    ]


def test_foreign_key():
    assert tokens("propietari(PERSONA:#dni)") == [
        (Name.Attribute, "propietari"),
        (Punctuation, "("),
        (Name.Class, "PERSONA"),
        (Punctuation, ":"),
        (Name.Constant, "#dni"),
        (Punctuation, ")"),
    ]


def test_primary_and_foreign_key():
    result = tokens("#id_cicle(CICLE:#id_cicle)")
    assert result[0] == (Name.Variable, "#id_cicle")
    assert (Name.Class, "CICLE") in result


def test_unicode_identifiers():
    assert tokens("CANÇO(#id_canço, títol)")[:3] == [
        (Name.Class, "CANÇO"),
        (Punctuation, "("),
        (Name.Constant, "#id_canço"),
    ]


def test_comment():
    assert (Comment.Single, "-- comentari") in tokens("nom -- comentari")


def test_entity_with_whitespace_before_parenthesis():
    result = tokens("ESTUDIANT (\n    #nia,\n    nom\n)")
    assert result[0] == (Name.Class, "ESTUDIANT")
    assert (Name.Constant, "#nia") in result

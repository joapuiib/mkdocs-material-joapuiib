"""Tests for the snippets extension with sed-like filters."""
import markdown
import pytest

from material_joapuiib.extensions.snippets import (
    SnippetFilterError,
    apply_sed,
    makeExtension,
)


ABBR = """\
Intro line
--8<-- [start:abbr]
*[HTML]: Hyper Text Markup Language
*[CSS]: Cascading Style Sheets
--8<-- [end:abbr]
"""


@pytest.fixture
def base(tmp_path):
    (tmp_path / "abbr.md").write_text(ABBR, encoding="utf-8")
    (tmp_path / "plain.md").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    (tmp_path / "details.md").write_text("details content\n", encoding="utf-8")
    (tmp_path / "outer.md").write_text('details here\n--8<-- "details.md"\ndetails again\n', encoding="utf-8")
    (tmp_path / "block.md").write_text("details\n-8<-\ndetails.md\n-8<-\ndetails\n", encoding="utf-8")
    (tmp_path / "nested.md").write_text('--8<-- "plain.md | sed s/a/A/g"\n', encoding="utf-8")
    return tmp_path


def preprocess(src, base, **kwargs):
    md = markdown.Markdown(extensions=[makeExtension(base_path=[str(base)], **kwargs)])
    return md.preprocessors["snippet"].run(src.split("\n"))


class TestApplySed:
    def test_first_occurrence_only(self):
        assert apply_sed("s/a/X/", ["banana"]) == ["bXnana"]

    def test_global(self):
        assert apply_sed("s/a/X/g", ["banana"]) == ["bXnXnX"]

    def test_nth(self):
        assert apply_sed("s/a/X/2", ["banana"]) == ["banXna"]

    def test_nth_global(self):
        assert apply_sed("s/a/X/2g", ["banana"]) == ["banXnX"]

    def test_ignore_case(self):
        assert apply_sed("s/A/x/gi", ["aA"]) == ["xx"]

    def test_ampersand_and_groups(self):
        assert apply_sed(r"s/\[(\w+)\]/<&|\1>/", ["*[HTML]: x"]) == ["*<[HTML]|HTML>: x"]

    def test_escaped_ampersand(self):
        assert apply_sed(r"s/a/\&/", ["a"]) == ["&"]

    def test_custom_delimiter(self):
        assert apply_sed("s|/|-|g", ["a/b/c"]) == ["a-b-c"]

    def test_escaped_delimiter(self):
        assert apply_sed(r"s/\//-/g", ["a/b"]) == ["a-b"]

    def test_escaped_pipe_delimiter_is_literal(self):
        assert apply_sed(r"s|a\|b|X|g", ["a|b ab"]) == ["X ab"]

    def test_multiple_commands(self):
        assert apply_sed("s/a/b/; s/b/c/", ["a"]) == ["c"]

    def test_delete_with_address(self):
        assert apply_sed("/^#/d", ["# x", "y"]) == ["y"]

    def test_negated_address(self):
        assert apply_sed("/keep/!d", ["keep me", "drop"]) == ["keep me"]

    def test_address_restricts_substitution(self):
        assert apply_sed("/^\\*/s/^\\*/- /", ["*[A]: a", "*b"]) == ["- [A]: a", "- b"]
        assert apply_sed("/x/s/a/b/", ["ax", "a"]) == ["bx", "a"]

    def test_newline_in_replacement_splits_lines(self):
        assert apply_sed(r"s/,/\n/g", ["a,b"]) == ["a", "b"]

    def test_blank_lines_preserved(self):
        assert apply_sed("s/a/b/", ["a", ""]) == ["b", ""]

    @pytest.mark.parametrize("script", [
        "",
        "s/a/b",
        "s/a/b/z",
        "x",
        "s/^*/x/",  # POSIX BRE: invalid in Python regex
        "s//x/",
        "/a/",
    ])
    def test_invalid_scripts(self, script):
        with pytest.raises(SnippetFilterError):
            apply_sed(script, ["a"])

    def test_invalid_group_reference(self):
        with pytest.raises(SnippetFilterError):
            apply_sed(r"s/a/\1/", ["a"])


class TestSnippets:
    def test_plain_snippet_unchanged(self, base):
        assert preprocess('--8<-- "plain.md"', base) == ["alpha", "beta", "gamma", ""]

    def test_plain_section_unchanged(self, base):
        result = preprocess('--8<-- "abbr.md:abbr"', base)
        assert result == ["*[HTML]: Hyper Text Markup Language", "*[CSS]: Cascading Style Sheets"]

    def test_whole_file_filter(self, base):
        assert preprocess('--8<-- "plain.md | sed s/a/A/g"', base) == ["AlphA", "betA", "gAmmA", ""]

    def test_whole_file_strips_section_markers(self, base):
        result = preprocess(r'--8<-- "abbr.md | sed s/^\*/* /"', base)
        assert result == [
            "Intro line",
            "* [HTML]: Hyper Text Markup Language",
            "* [CSS]: Cascading Style Sheets",
            "",
        ]

    def test_section_filter(self, base):
        result = preprocess(r'--8<-- "abbr.md:abbr | sed s/^\*\[(\w+)\]: /- **\1**: /"', base)
        assert result == ["- **HTML**: Hyper Text Markup Language", "- **CSS**: Cascading Style Sheets"]

    def test_no_space_around_pipe(self, base):
        assert preprocess('--8<-- "plain.md|sed /beta/d"', base) == ["alpha", "gamma", ""]

    def test_pipe_delimiter_inside_script(self, base):
        assert preprocess('--8<-- "plain.md | sed s|a|A|"', base) == ["Alpha", "betA", "gAmma", ""]

    def test_single_quotes_allow_double_quotes_in_script(self, base):
        assert preprocess("""--8<-- 'plain.md | sed s/beta/"b"/'""", base) == ["alpha", '"b"', "gamma", ""]

    def test_nested_snippet_filter(self, base):
        assert preprocess('--8<-- "nested.md"', base) == ["AlphA", "betA", "gAmmA", "", ""]

    def test_block_syntax(self, base):
        result = preprocess('-8<-\nplain.md | sed /^b/d\n-8<-', base)
        assert result == ["alpha", "gamma", ""]

    def test_same_file_different_filters(self, base):
        result = preprocess('--8<-- "plain.md | sed /alpha/!d"\n--8<-- "plain.md | sed /beta/!d"', base)
        assert result == ["alpha", "beta"]

    def test_indentation_kept(self, base):
        assert preprocess('    --8<-- "plain.md | sed /^b/!d"', base) == ["    beta"]

    def test_invalid_script_raises(self, base):
        with pytest.raises(SnippetFilterError):
            preprocess('--8<-- "plain.md | sed s/a/b"', base)

    def test_line_range_filter(self, base):
        assert preprocess('--8<-- "plain.md:1:2 | sed s/a/A/g"', base) == ["AlphA", "betA"]

    def test_multiple_line_ranges_filter(self, base):
        assert preprocess('--8<-- "plain.md:1:1,3:3 | sed s/^/- /"', base) == ["- alpha", "- gamma"]

    def test_line_range_strips_markers(self, base):
        result = preprocess(r'--8<-- "abbr.md:2:5 | sed s/^\*/* /"', base)
        assert result == ["* [HTML]: Hyper Text Markup Language", "* [CSS]: Cascading Style Sheets"]

    def test_missing_file_ignored(self, base):
        assert preprocess('--8<-- "missing.md | sed s/a/b/"', base) == []

    def test_full_conversion(self, base):
        md = markdown.Markdown(extensions=[makeExtension(base_path=[str(base)])])
        html = md.convert(r'--8<-- "abbr.md:abbr | sed s/^\*\[(\w+)\]: /- **\1**: /"')
        assert "<li><strong>HTML</strong>: Hyper Text Markup Language</li>" in html


def upper(lines, args):
    return [line.upper() for line in lines]


def prefix(lines, args):
    return [args + line if line else line for line in lines]


class TestCustomFilters:
    def test_custom_filter(self, base):
        result = preprocess('--8<-- "plain.md | upper"', base, filters={"upper": upper})
        assert result == ["ALPHA", "BETA", "GAMMA", ""]

    def test_custom_filter_receives_raw_args(self, base):
        result = preprocess('--8<-- "plain.md | prefix  [x] s/a|b/ "', base, filters={"prefix": prefix})
        assert result == ["[x] s/a|b/alpha", "[x] s/a|b/beta", "[x] s/a|b/gamma", ""]

    def test_custom_filter_on_section(self, base):
        result = preprocess('--8<-- "abbr.md:abbr | upper"', base, filters={"upper": upper})
        assert result == ["*[HTML]: HYPER TEXT MARKUP LANGUAGE", "*[CSS]: CASCADING STYLE SHEETS"]

    def test_builtin_sed_still_available(self, base):
        result = preprocess('--8<-- "plain.md | sed /^b/d"', base, filters={"upper": upper})
        assert result == ["alpha", "gamma", ""]

    def test_override_builtin(self, base):
        result = preprocess('--8<-- "plain.md | sed whatever"', base, filters={"sed": upper})
        assert result == ["ALPHA", "BETA", "GAMMA", ""]

    def test_unknown_filter(self, base):
        with pytest.raises(SnippetFilterError, match="Unknown snippet filter 'nope'"):
            preprocess('--8<-- "plain.md | nope"', base)

    def test_missing_filter_name(self, base):
        with pytest.raises(SnippetFilterError):
            preprocess('--8<-- "plain.md | s/a/b/"', base)

    def test_not_callable(self, base):
        with pytest.raises(SnippetFilterError, match="not callable"):
            preprocess('--8<-- "plain.md"', base, filters={"bad": "x"})

    def test_bad_return_value(self, base):
        with pytest.raises(SnippetFilterError, match="list of strings"):
            preprocess('--8<-- "plain.md | bad"', base, filters={"bad": lambda lines, args: "x"})


class TestFilterChain:
    def test_two_filters(self, base):
        result = preprocess('--8<-- "plain.md | sed /^b/d | upper"', base, filters={"upper": upper})
        assert result == ["ALPHA", "GAMMA", ""]

    def test_order_matters(self, base):
        filters = {"upper": upper}
        result = preprocess('--8<-- "plain.md | upper | sed s/A/x/"', base, filters=filters)
        assert result == ["xLPHA", "BETx", "GxMMA", ""]
        result = preprocess('--8<-- "plain.md | sed s/A/x/ | upper"', base, filters=filters)
        assert result == ["ALPHA", "BETA", "GAMMA", ""]

    def test_three_filters_on_section(self, base):
        result = preprocess(
            r'--8<-- "abbr.md:abbr | sed /CSS/d | sed s/^\*\[(\w+)\]: /- **\1**: / | prefix >"',
            base, filters={"prefix": prefix},
        )
        assert result == [">- **HTML**: Hyper Text Markup Language"]

    def test_pipe_without_spaces_is_an_argument(self, base):
        result = preprocess('--8<-- "plain.md | sed s|a|A|g | sed s/l|m/_/g"', base)
        assert result == ["A_phA", "betA", "gA__A", ""]

    def test_regex_alternation(self, base):
        assert preprocess('--8<-- "plain.md | sed /alpha|gamma/d"', base) == ["beta", ""]

    def test_bracketed_pipe_with_spaces(self, base):
        (base / "pipes.md").write_text("a | b\n", encoding="utf-8")
        assert preprocess('--8<-- "pipes.md | sed s/ [|] /-/"', base) == ["a-b", ""]

    def test_same_file_different_chains(self, base):
        result = preprocess(
            '--8<-- "plain.md | sed /alpha/!d | upper"\n--8<-- "plain.md | sed /alpha/!d"',
            base, filters={"upper": upper},
        )
        assert result == ["ALPHA", "alpha"]

    def test_nested_chain(self, base):
        (base / "outer.md").write_text('--8<-- "plain.md | sed /^b/d | upper"\n', encoding="utf-8")
        assert preprocess('--8<-- "outer.md"', base, filters={"upper": upper}) == ["ALPHA", "GAMMA", "", ""]

    @pytest.mark.parametrize("spec", ["sed s/a/b/ |", "sed s/a/b/ |  | sed s/b/c/", "| sed s/a/b/"])
    def test_empty_filter_in_chain(self, base, spec):
        with pytest.raises(SnippetFilterError):
            preprocess(f'--8<-- "plain.md | {spec}"', base)

    def test_unknown_filter_in_chain(self, base):
        with pytest.raises(SnippetFilterError, match="'nope'"):
            preprocess('--8<-- "plain.md | sed s/a/b/ | nope"', base)

    def test_bad_return_in_chain(self, base):
        with pytest.raises(SnippetFilterError, match="'bad'"):
            preprocess('--8<-- "plain.md | sed s/a/b/ | bad"', base, filters={"bad": lambda lines, args: None})


class TestSyntaxMask:
    def test_nested_snippet_notation_untouched(self, base):
        result = preprocess('--8<-- "outer.md | sed s/details/summary/g"', base)
        assert result == ["summary here", "details content", "", "summary again", ""]

    def test_block_notation_untouched(self, base):
        result = preprocess('--8<-- "block.md | sed s/details/summary/g"', base)
        assert result == ["summary", "details content", "", "summary", ""]

    def test_delete_cannot_remove_notation(self, base):
        result = preprocess('--8<-- "outer.md | sed /details/d"', base)
        assert result == ["details content", "", ""]

    def test_runs_filtered_separately(self, base):
        calls = []

        def spy(lines, args):
            calls.append(list(lines))
            return lines

        preprocess('--8<-- "outer.md | spy"', base, filters={"spy": spy})
        assert calls == [["details here"], ["details again", ""]]

    def test_escaped_notation_is_content(self, base):
        (base / "esc.md").write_text(';--8<-- "details.md"\n', encoding="utf-8")
        result = preprocess('--8<-- "esc.md | sed s/details/summary/"', base)
        assert result == ['--8<-- "summary.md"', ""]

    def test_section_markers_untouched(self, base):
        result = preprocess(r'--8<-- "abbr.md | sed s/start/begin/"', base)
        assert result[0] == "Intro line"


def test_requires_extension_points(monkeypatch, base):
    from pymdownx.snippets import SnippetPreprocessor
    monkeypatch.delattr(SnippetPreprocessor, "process_snippet_lines")
    with pytest.raises(RuntimeError, match="process_snippet_lines"):
        markdown.Markdown(extensions=[makeExtension(base_path=[str(base)])])

"""Tests for the heading_numbers extension."""
import markdown
import pytest
from material_joapuiib.extensions.heading_numbers import (
    makeExtension,
    slugify_without_numbers,
)


def convert(src, **kwargs):
    md = markdown.Markdown(extensions=[makeExtension(**kwargs)])
    return md.convert(src)


class TestBasicNumbering:
    def test_h1(self):
        result = convert("# Heading")
        assert '<span class="heading-number">1. </span>' in result

    def test_h2(self):
        # h1 counter=0, h2 counter=1 → "0.1."
        result = convert("## Heading")
        assert '<span class="heading-number">0.1. </span>' in result

    def test_sequential_h1(self):
        result = convert("# A\n# B\n# C")
        assert ">1. </span>" in result
        assert ">2. </span>" in result
        assert ">3. </span>" in result

    def test_nested_h2_under_h1(self):
        result = convert("# A\n## B\n## C")
        assert ">1. </span>" in result
        assert ">1.1. </span>" in result
        assert ">1.2. </span>" in result

    def test_deep_nesting(self):
        result = convert("# A\n## B\n### C")
        assert ">1. </span>" in result
        assert ">1.1. </span>" in result
        assert ">1.1.1. </span>" in result

    def test_counter_reset_on_new_h1(self):
        result = convert("# A\n## B\n# C\n## D")
        assert ">1.1. </span>" in result
        assert ">2.1. </span>" in result

    def test_skipped_level_uses_zero(self):
        result = convert("# A\n### C")
        assert ">1.0.1. </span>" in result


class TestStartLevel:
    def test_start_level_2_skips_h1(self):
        result = convert("# Title\n## Section", start_level=2)
        assert "<h1>Title</h1>" in result
        assert '<span class="heading-number">1. </span>' in result

    def test_start_level_2_h1_resets_counter(self):
        result = convert("# A\n## B\n# C\n## D", start_level=2)
        lines = result.splitlines()
        # Both h2 sections should start at 1.
        assert result.count(">1. </span>") == 2

    def test_start_level_3(self):
        result = convert("## Section\n### Sub", start_level=3)
        assert "<h2>Section</h2>" in result
        assert ">1. </span>" in result

    def test_h2_resets_h3_counter(self):
        result = convert("## A\n### B\n## C\n### D", start_level=3)
        assert result.count(">1. </span>") == 2


class TestSpanStructure:
    def test_span_class(self):
        result = convert("# Heading")
        assert 'class="heading-number"' in result

    def test_text_preserved(self):
        result = convert("# My Heading")
        assert "My Heading" in result

    def test_heading_with_code(self):
        result = convert("# `code` heading")
        assert '<span class="heading-number">1. </span>' in result
        assert "<code>code</code>" in result


class TestSlugifyWithoutNumbers:
    def test_strips_single_number(self):
        assert slugify_without_numbers("1. Title", "-") == "title"

    def test_strips_nested_number(self):
        assert slugify_without_numbers("1.1. Background", "-") == "background"

    def test_strips_deep_number(self):
        assert slugify_without_numbers("2.1.1. Data collection", "-") == "data-collection"

    def test_no_number_prefix(self):
        assert slugify_without_numbers("Plain Title", "-") == "plain-title"

    def test_number_in_middle_preserved(self):
        assert slugify_without_numbers("Step 1. Do this", "-") == "step-1-do-this"

---
title: Heading Numbers
icon: material/format-list-numbered
---
# Heading Numbers

`heading_numbers` is a Python-Markdown extension that prepends section numbers
to headings in the generated HTML. Numbers follow the format `1.`, `1.1.`, `1.1.1.`, etc.

## Setup

Add the extension to `markdown_extensions` in `mkdocs.yml`:

```yaml
markdown_extensions:
  - material_joapuiib.extensions.heading_numbers
  - toc:
      slugify: !!python/name:material_joapuiib.extensions.heading_numbers.slugify_without_numbers
```

Configuring toc's `slugify` is optional but recommended — it strips numbers from
heading anchors so links remain stable if numbering changes.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `start_level` | `int` | `1` | First heading level to number. `1` = h1, `2` = h2, etc. |

### Example: start at h2

```yaml
markdown_extensions:
  - material_joapuiib.extensions.heading_numbers:
      start_level: 2
  - toc:
      slugify: !!python/name:material_joapuiib.extensions.heading_numbers.slugify_without_numbers
```

With `start_level: 2`, h1 headings are left unnumbered and h2 headings start at `1.`.

## Numbering format

| Heading | Number |
|---------|--------|
| `# H1` | `1.` |
| `## H2` | `1.1.` |
| `### H3` | `1.1.1.` |

Counters reset when a parent heading is encountered. For example:

```markdown
# Introduction         → 1. Introduction
## Background          → 1.1. Background
## Motivation          → 1.2. Motivation
# Methods              → 2. Methods
## Data collection     → 2.1. Data collection
### Instruments        → 2.1.1. Instruments
## Analysis            → 2.2. Analysis
```

## HTML output

Each number is wrapped in a `<span class="heading-number">` element, which allows
CSS targeting:

```html
<h2 id="background">
  <span class="heading-number">1.1. </span>Background
</h2>
```

## TOC integration

Numbers appear in the table of contents entries. When `slugify_without_numbers`
is configured, the anchor (`id`) on the heading is generated from the heading
text without the number prefix, so `## Background` gets `id="background"` regardless
of its numbering.

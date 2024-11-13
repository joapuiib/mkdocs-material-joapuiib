---
title: Icons
icon: material/book-open-variant
---
## Custom icons

### IntelliJ

| Icon | Markdown |
|------|----------|
| :intellij-breakpoint: | `:intellij-breakpoint:` |
| :intellij-debug: | `:intellij-debug:` |
| :intellij-resume: | `:intellij-resume:` |
| :intellij-run: | `:intellij-run:` |
| :intellij-step-into: | `:intellij-step-into:` |
| :intellij-step-out: | `:intellij-step-out:` |
| :intellij-step-over: | `:intellij-step-over:` |
| :intellij-stop: | `:intellij-stop:` |


## Built-in icons
A complete list can be found at https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/#search

## Page icons
In the frontmatter:
```md
---
icon: material/book-open-variant
---
```

## Section icons
Section icons are set as a prefix to the section title in the table of contents.
This also works for external links.

```yaml title=".pages"
nav:
    - ...
    - ":material/pencil-outline: Icon section": icons
```

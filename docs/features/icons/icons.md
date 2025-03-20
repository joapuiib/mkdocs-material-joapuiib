---
title: Icons
icon: material/book-open-variant
---
## Custom icons

| Icon | Markdown |
|------|----------|
| :simple-softcatala: | `:simple-softcatala:` |

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
| :intellij-maven: | `:intellij-maven:` |
| :intellij-maven-load: | `:intellij-maven-load:` |

__Sources__:

- [intellij-community](https://github.com/JetBrains/intellij-community/tree/master/platform/icons/src)
- [maven](https://github.com/JetBrains/intellij-community/tree/master/plugins/maven/src/main/resources/images)


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

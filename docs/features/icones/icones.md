---
title: Icones
icon: material/book-open-variant
---

# Icones

> Referència: [:octicons-link-external-16: Icons, Emojis &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/icons-emojis.html)

## Icones personalitzades

| Icona | Markdown |
|-------|----------|
| :artificial-intelligence: | `:artificial-intelligence:` |
| :artificial-intelligence-outline: | `:artificial-intelligence-outline:` |

```md
:speedometer:{.difficulty .basic title="Basic"}
:speedometer:{.difficulty .initial title="Inicial"}
:speedometer:{.difficulty .intermediate title="Intermediate"}
:speedometer:{.difficulty .advanced title="Advanced"}
:speedometer:{.difficulty .expert title="Expert"}
:speedometer:{.difficulty .extreme title="Extreme"}
```
/// html | div.result
:speedometer:{.difficulty .basic title="Basic"}
:speedometer:{.difficulty .initial title="Inicial"}
:speedometer:{.difficulty .intermediate title="Intermediate"}
:speedometer:{.difficulty .advanced title="Advanced"}
:speedometer:{.difficulty .expert title="Expert"}
:speedometer:{.difficulty .extreme title="Extreme"}
///

### IntelliJ

| Icona | Markdown |
|-------|----------|
| :intellij-class: | `:intellij-class:` |
| :intellij-class-abstract: | `:intellij-class-abstract:` |
| :intellij-class-junit-test: | `:intellij-class-junit-test:` |
| :intellij-enum: | `:intellij-enum:` |
| :intellij-exception: | `:intellij-exception:` |
| :intellij-interface: | `:intellij-interface:` |
| :intellij-record: | `:intellij-record:` |
| :intellij-exclude-folder: | `:intellij-exclude-folder:` |
| :intellij-src-folder: | `:intellij-src-folder:` |
| :intellij-resources-folder: | `:intellij-resources-folder:` |
| :intellij-test-folder: | `:intellij-test-folder:` |
| :intellij-test-resources-folder: | `:intellij-test-resources-folder:` |
| :intellij-package: | `:intellij-package:` |
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

__Fonts__:

- [intellij-community](https://github.com/JetBrains/intellij-community/tree/master/platform/icons/src)
- [maven](https://github.com/JetBrains/intellij-community/tree/master/plugins/maven/src/main/resources/images)

## Icones integrades

Llistat complet a [:octicons-link-external-16: Search &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/icons-emojis.html#search).

## Icones de pàgina

Al front matter:

```md
---
icon: material/book-open-variant
---
```

## Icones de secció

Les icones de secció es configuren com a prefix del títol al fitxer `.nav.yml`. També funcionen per a enllaços externs. Veure [Section icons](../../plugins/sectionicons.md).

```yaml title=".nav.yml"
nav:
    - "*"
    - ":material/pencil-outline: Secció amb icona": icons
```

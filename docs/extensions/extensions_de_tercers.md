---
title: Extensions de tercers
icon: material/package-variant
---

# Extensions de tercers

Llistat d'extensions de Markdown de tercers incloses i configurades en aquest tema. Les extensions s'apliquen automàticament; només cal instal·lar el tema.

> Referència: [:octicons-link-external-16: Python-Markdown extensions &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/setup/extensions/python-markdown.html)

## Python-Markdown integrades

Extensions distribuïdes amb [Python-Markdown](https://python-markdown.github.io/extensions/).

| Extensió | Descripció | Documentació |
|----------|------------|--------------|
| `abbr` | Abreviatures amb tooltip. | [:octicons-link-external-16: Abbreviations](https://python-markdown.github.io/extensions/abbreviations/) |
| `admonition` | Blocs destacats per a notes i avisos. | [:octicons-link-external-16: Admonition](https://python-markdown.github.io/extensions/admonition/) |
| `attr_list` | Atributs HTML als elements Markdown amb `{ }`. | [:octicons-link-external-16: Attribute Lists](https://python-markdown.github.io/extensions/attr_list/) |
| `def_list` | Llistes de definicions. | [:octicons-link-external-16: Definition Lists](https://python-markdown.github.io/extensions/definition_lists/) |
| `footnotes` | Notes a peu de pàgina amb `[^1]`. | [:octicons-link-external-16: Footnotes](https://python-markdown.github.io/extensions/footnotes/) |
| `md_in_html` | Processament de Markdown dins d'elements HTML amb `markdown`. | [:octicons-link-external-16: Markdown in HTML](https://python-markdown.github.io/extensions/md_in_html/) |
| `sane_lists` | Comportament millorat de les llistes. | [:octicons-link-external-16: Sane Lists](https://python-markdown.github.io/extensions/sane_lists/) |
| `toc` | Generació de l'índex de continguts. | [:octicons-link-external-16: Table of Contents](https://python-markdown.github.io/extensions/toc/) |

## PyMdown Extensions

Conjunt d'extensions de [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/).

| Extensió | Descripció | Documentació |
|----------|------------|--------------|
| `pymdownx.arithmatex` | Renderitzat de fórmules matemàtiques amb KaTeX/MathJax. Veure [Matemàtiques](../features/matematiques.md). | [:octicons-link-external-16: Arithmatex](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/) |
| `pymdownx.blocks.html` | Blocs `/// html | div.X` amb processament de Markdown. | [:octicons-link-external-16: HTML Blocks](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/html/) |
| `pymdownx.blocks.caption` | Subtítols configurables per a figures, taules i imatges. Veure [Subtítols](../features/subtitols.md). | [:octicons-link-external-16: Caption Blocks](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/caption/) |
| `pymdownx.details` | Admonicions plegables (`???`). | [:octicons-link-external-16: Details](https://facelessuser.github.io/pymdown-extensions/extensions/details/) |
| `pymdownx.emoji` | Suport d'emojis i icones SVG. Veure [Emoji](emoji.md). | [:octicons-link-external-16: Emoji](https://facelessuser.github.io/pymdown-extensions/extensions/emoji/) |
| `pymdownx.fancylists` | Llistes amb lletres i numerals romans. Veure [Llistes](../features/llistes.md). | [:octicons-link-external-16: Fancy Lists](https://facelessuser.github.io/pymdown-extensions/extensions/fancylists/) |
| `pymdownx.highlight` | Ressaltat de sintaxi amb Pygments. Veure [Blocs de codi](../features/blocs_de_codi.md). | [:octicons-link-external-16: Highlight](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/) |
| `pymdownx.inlinehilite` | Ressaltat de sintaxi inline. | [:octicons-link-external-16: InlineHilite](https://facelessuser.github.io/pymdown-extensions/extensions/inlinehilite/) |
| `pymdownx.keys` | Tecles del teclat amb `++ctrl+c++`. | [:octicons-link-external-16: Keys](https://facelessuser.github.io/pymdown-extensions/extensions/keys/) |
| `pymdownx.magiclink` | Conversió automàtica d'URL. Veure [Magic Links](../features/magic_links.md). | [:octicons-link-external-16: MagicLink](https://facelessuser.github.io/pymdown-extensions/extensions/magiclink/) |
| `pymdownx.saneheaders` | Comportament millorat dels títols. | [:octicons-link-external-16: SaneHeaders](https://facelessuser.github.io/pymdown-extensions/extensions/saneheaders/) |
| `pymdownx.snippets` | Inclusió de fragments d'altres fitxers amb `--8<--`. | [:octicons-link-external-16: Snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) |
| `pymdownx.superfences` | Blocs de codi avançats, niats i amb fences personalitzats (Mermaid, math). | [:octicons-link-external-16: SuperFences](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/) |
| `pymdownx.tabbed` | Pestanyes de contingut. | [:octicons-link-external-16: Tabbed](https://facelessuser.github.io/pymdown-extensions/extensions/tabbed/) |
| `pymdownx.tasklist` | Llistes de tasques amb `- [x]`. Veure [Llistes](../features/llistes.md). | [:octicons-link-external-16: Tasklist](https://facelessuser.github.io/pymdown-extensions/extensions/tasklist/) |

## Altres extensions

Extensions distribuïdes en paquets independents.

| Extensió | Paquet | Descripció |
|----------|--------|------------|
| `span_attr` | [`markdown-span-attr`](https://pypi.org/project/markdown-span-attr/) | Atributs HTML inline amb `[text]{ .class }`. |
| `inline_blocks` | [`pymdownx-inline-blocks`](https://pypi.org/project/pymdownx-inline-blocks/) | Versió inline dels blocs `pymdownx.blocks`. |
| `markdown_grid_tables` | [`markdown_grid_tables`](https://pypi.org/project/markdown-grid-tables/) | Taules de quadrícula amb fusió de cel·les. Veure [Taules](../features/taules.md). |
| `rubric` | [`pymdown-rubric-extension`](https://pypi.org/project/pymdown-rubric-extension/) | Component de rúbriques d'avaluació. Veure [Rúbrica](../features/rubrica.md). |
| `pymdown_multimd_table` | [`pymdown-multimd-table`](https://pypi.org/project/pymdown-multimd-table/) | Taules amb cel·les multilínia, `rowspan` i `colspan`. Veure [Taules](../features/taules.md). |

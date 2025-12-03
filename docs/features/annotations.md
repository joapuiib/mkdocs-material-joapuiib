---
title: Annotations
icon: material/plus-circle
---
# Annotations
!!! docs "Reference [:octicons-link-external-16: Annotations - :simple-materialformkdocs: Material for MkDocs](https://squidfunk.github.io/mkdocs-material/reference/annotations/)"

## Annotations in paragraphs
Lorem ipsum dolor sit amet, consectetur adipiscing elit. (1)
Praesent id metus diam. Aliquam condimentum libero eu tortor.
{ .annotate .spell-ignore }

1.  Annotations can be used in paragraphs.

## Annotations in admonitions
!!! note annotate "Note (1)"
    This is a note. (2)

1.  Annotations can be used in admonitions titles
2.  Annotations can be used in admonitions.

## Annotations in code blocks
```python
def hello():
    print("Hello, world!") # (1)!
```

1.  Annotations can be used in code blocks.

````md
```python
def hello():
    print("Hello, world!") # (1)!
```

1.  Annotations can be used in code blocks.
````

## Footnotes tooltip
També s'han habilitat per defecte les notes a peu de pàgina,
que mostren el seu contingut en una finestra emergent quan es passa el cursor per sobre.[^1]

[^1]: Aquesta és una nota a peu de pàgina que es mostra en una finestra emergent.

---
title: Anotacions
icon: material/plus-circle
---

# Anotacions

> Referència: [:octicons-link-external-16: Annotations &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/annotations.html)

## Anotacions en paràgrafs

Lorem ipsum dolor sit amet, consectetur adipiscing elit. (1)
Praesent id metus diam. Aliquam condimentum libero eu tortor.
{ .annotate .spell-ignore }

1.  Les anotacions es poden fer servir dins de paràgrafs.

## Anotacions en admonicions

!!! note annotate "Nota (1)"
    Açò és una nota. (2)

1.  Les anotacions es poden fer servir als títols d'admonicions.
2.  Les anotacions es poden fer servir dins d'admonicions.

## Anotacions en blocs de codi

```python
def hello():
    print("Hello, world!") # (1)!
```

1.  Les anotacions es poden fer servir dins de blocs de codi.

````md
```python
def hello():
    print("Hello, world!") # (1)!
```

1.  Les anotacions es poden fer servir dins de blocs de codi.
````

## Notes a peu de pàgina amb tooltip

També s'han habilitat per defecte les notes a peu de pàgina, que mostren el seu contingut en una finestra emergent quan es passa el cursor per sobre.[^1]

[^1]: Aquesta és una nota a peu de pàgina que es mostra en una finestra emergent.

---
title: Codi col·lapsable
icon: material/arrow-collapse-vertical
---

# Codi col·lapsable

Extensió que afegeix un bloc `collapse-code` per a embolicar blocs de codi llargs amb un toggle d'expandir i col·lapsar.

## Configuració

```yml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.collapse_code:
      expand_text: Expand
      collapse_text: Collapse
      expand_title: expand
      collapse_title: collapse
```

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `expand_text` | `str` | `Expand` | Text del botó d'expandir. |
| `collapse_text` | `str` | `Collapse` | Text del botó de col·lapsar. |
| `expand_title` | `str` | `expand` | Atribut `title` del botó d'expandir. |
| `collapse_title` | `str` | `collapse` | Atribut `title` del botó de col·lapsar. |

## Ús

````md
/// collapse-code
```python
def hello():
    print("Hello, world!")
```
///
````

/// collapse-code
```python
def hello():
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
    print("Hello, world!")
```
///

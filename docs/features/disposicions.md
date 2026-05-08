---
title: Disposicions
icon: octicons/table-16
---

# Disposicions

> Referència: [:octicons-link-external-16: Grids &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/grids.html)

## Columnes

La disposició en columnes la proporciona la classe `.columns`.

??? info
    Internament és un contenidor flexbox amb les propietats següents:
    ```css
    .columns {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        align-items: center;
    }
    ```

```md
/// html | div.columns
| Columna 1 | Columna 2 |
|-----------|-----------|
| Contingut | Contingut |
| Contingut | Contingut |
| Contingut | Contingut |

![Placeholder](https://via.placeholder.com/150)
///
```
/// html | div.result
//// html | div.columns
| Columna 1 | Columna 2 |
|-----------|-----------|
| Contingut | Contingut |
| Contingut | Contingut |
| Contingut | Contingut |

![Placeholder](https://via.placeholder.com/150)
////
///

---
title: Section icons
icon: lucide/pencil
---

# Section icons

Plugin que registra dos filtres Jinja per a extreure i netejar la icona del títol d'una secció a la navegació.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/sectionicons
```

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `enabled` | `bool` | `true` | Activa o desactiva el plugin. |

## Filtres

### `extract_icon`

Extreu el nom de la icona d'una cadena amb format `:icon:` o `:icon: Text`. Retorna `None` si no n'hi ha.

```jinja
{% raw %}{{ ":lucide/database: Bases de dades" | extract_icon }}{% endraw %}
{# → "lucide/database" #}
```

### `remove_icon`

Retorna el text d'una cadena amb format `:icon: Text`, sense la icona. Si no hi ha icona, retorna la cadena íntegra.

```jinja
{% raw %}{{ ":lucide/database: Bases de dades" | remove_icon }}{% endraw %}
{# → "Bases de dades" #}
```

## Ús a la navegació

La sintaxi `:icon: Text` es pot fer servir als títols de seccions a `.nav.yml` (compatible amb [awesome-nav](https://lukasgeiter.github.io/mkdocs-awesome-nav/)) per separar la icona del títol des de les plantilles.

```yml title=".nav.yml"
nav:
    - "*"
    - ":lucide/pencil: Secció amb icona":
        - pagina-1.md
        - pagina-2.md
```

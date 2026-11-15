---
title: Environment
icon: lucide/server
---

# Environment

Plugin que afegeix una variable `build` al context Jinja de les plantilles, indicant si s'està construint el lloc o servint-lo amb `mkdocs serve`.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/environment
```

## Variables disponibles

| Variable | Tipus | Descripció |
|----------|-------|-------------|
| `build` | `bool` | `true` si l'ordre és `build` o `gh-deploy`; `false` durant `serve`. |

## Ús a les plantilles

```jinja
{% raw %}{% if build %}
  <!-- Codi només per a producció -->
{% else %}
  <!-- Codi només per a desenvolupament -->
{% endif %}{% endraw %}
```

Útil per a injectar scripts d'analítica, comentaris o altres recursos només quan es publica el lloc.

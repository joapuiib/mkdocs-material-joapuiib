---
title: Environment
icon: material/server-network
---

# Environment

Plugin que afegeix una variable `build` al context Jinja de les plantilles, indicant si s'està construint el lloc o servint-lo amb `mkdocs serve`.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/enviorment
```

!!! note
    El nom del plugin està registrat com a `enviorment` (sic). Es manté per compatibilitat.

## Variables disponibles

| Variable | Tipus | Descripció |
|----------|-------|-------------|
| `build` | `bool` | `true` si la comanda és `build` o `gh-deploy`; `false` durant `serve`. |

## Ús a les plantilles

```jinja
{% raw %}{% if build %}
  <!-- Codi sols per a producció -->
{% else %}
  <!-- Codi sols per a desenvolupament -->
{% endif %}{% endraw %}
```

Útil per a injectar scripts d'analítica, comentaris o altres recursos sols quan es publica el lloc.

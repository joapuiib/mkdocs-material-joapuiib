---
title: Filters
icon: material/filter
---

# Filters

Plugin que registra filtres Jinja personalitzats per a les plantilles del tema.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/filters
```

## Filtres disponibles

### `remove_accents`

Elimina els accents d'una cadena.

```
{{ '{{ "áéíóúàèìòù" | remove_accents }}' }}
```
/// html | div.result
```text
{{ "áéíóúàèìòù" | remove_accents }}
```
///

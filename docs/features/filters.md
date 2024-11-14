---
title: Filters
---
# Filters

Custom Jinja filters are provided by `material-joapuiib/filters` plugin.

```yml title="mkdocs.yml"
plugins:
  - material-joapuiib/filters
```


## `remove_accents`
This filter removes accents from a string.

```
{{ '{{ "áéíóúàèìòù" | remove_accents }}' }}
```
/// html | div.result
```text
{{ "áéíóúàèìòù" | remove_accents }}
```
///

---
title: Filters
icon: material/filter
---

# Filters

Custom Jinja filters are provided by `material-joapuiib/filters` plugin.

```yml title="properdocs.yml"
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

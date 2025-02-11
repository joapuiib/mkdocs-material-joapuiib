---
title: Badges
---
## Badges

### Configuration

```yaml
plugins:
  - badges:
      types:
        package:
          icon: material-folder-zip
          title: Package
        eval:
          icon: material-check
          title: Avaluació
        tag:
          icon: material-tag
          title: Etiqueta
        branch:
          icon: material-source-branch
          title: Branca
```


### Definition

| Title | Definition | Rendered |
| ----- | ---------- | -------- |
| __Generic__ | ``\[badge Text1|Text2]`` | [badge Text1|Text2] |
| __Package__ | ``\[badge:package `ud1.examples`]`` | [badge:package `ud1.examples`] |
| __Avaluació__ | ``\[badge:eval __Bloc 1: Títol__|20%]`` | [badge:eval __Bloc 1: Títol__|20%] |
| __Tag__ | ``\[badge:tag `Example`]`` | [badge:tag `Example`] |
| __Branch__ | ``\[badge:branch `main`]`` | [badge:branch `main`] |

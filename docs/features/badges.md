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
        commit:
          icon: material-source-commit
          title: Commit
        remote-branch:
          icon: material-source-branch-sync
          title: Branca remota
```


### Definition

| Title | Definition | Rendered |
| ----- | ---------- | -------- |
| __Generic__ | ``\[badge Text1|Text2]`` | [badge Text1|Text2] |
| __Package__ | ``\[badge:package `ud1.examples`]`` | [badge:package `ud1.examples`] |
| __Avaluació__ | ``\[badge:eval __Bloc 1: Títol__|20%]`` | [badge:eval __Bloc 1: Títol__|20%] |
| __Tag__ | ``\[badge:tag `Example`]`` | [badge:tag `Example`] |
| __Branch__ | ``\[badge:branch `main`]`` | [badge:branch `main`] |
| __Commit__ | ``\[badge:commit `a1b2c3d4`]`` | [badge:commit `a1b2c3d4`] |
| __Remote branch__ | ``\[badge:remote-branch `origin/main`]`` | [badge:remote-branch `origin/main`] |

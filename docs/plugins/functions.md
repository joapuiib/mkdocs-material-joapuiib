---
title: Functions
icon: material/function
---

# Functions

Plugin que registra funcions invocables des de Markdown amb la sintaxi `!nom_funcio arg1 arg2`.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/functions:
      load_file:
        files_dir: files
```

## Sintaxi

```markdown
!nom_funcio arg1 arg2
```

## Funcions disponibles

### `load_file`

Carrega el contingut d'un fitxer relatiu al directori `files_dir`.

```
\!load_file HelloWorld.java
```

/// html | div.result
!load_file HelloWorld.java
///

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `files_dir` | `str` | `files` | Directori on es troben els fitxers a carregar. |

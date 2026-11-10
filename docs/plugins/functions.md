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

#### Modificadors

Els modificadors són transformacions reutilitzables definides a la configuració
i aplicades amb `+nom`. Cada modificador pot tenir:

| Clau | Descripció |
|------|------------|
| `filter` | Filtre de [snippets](../extensions/extensions_de_tercers.md) (p. ex. `sed ...`) aplicat al contingut. Requereix `material_joapuiib.extensions.snippets`. |
| `title_pattern` / `title_replace` | Substitució (regex) sobre el títol per defecte, quan no s'indica explícitament. |

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/functions:
      load_file:
        files_dir: files
        modifiers:
          strip_error:
            filter: sed /public class/s/Error//
            title_pattern: 'Error(?=\.java$)'
            title_replace: ''
```

```
\!load_file src/ud1/exercises/DebugCollatzError.java +strip_error
```

Es poden combinar diversos modificadors (`+a +b`); els filtres s'encadenen en ordre.

---
title: Functions
---
# Functions

Functions are provided by `material-joapuiib/functions` plugin.

```yml title="mkdocs.yml"
plugins:
  - material-joapuiib/functions:
      load_file:
        files_dir: files
```

To call a function, use the following syntax:

```markdown
!function_name arg1 arg2
```

## Load file
```
\!load_file HelloWorld.java
```

/// html | div.result
!load_file HelloWorld.java
///

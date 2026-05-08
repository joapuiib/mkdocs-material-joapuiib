---
title: Taules
icon: material/table
---

# Taules

> Referència: [:octicons-link-external-16: Data tables &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/data-tables.html)

## Taules de quadrícula

```markdown
+---------------------+----------+
| Camp 1              | Camp 2   |
+==========+==========+==========+
| cel 1    | cel 2    | cel 3    |
+----------+          +----------+
| cel 4    |          | cel 6    |
+----------+----------+----------+
```

+---------------------+----------+
| Camp 1              | Camp 2   |
+==========+==========+==========+
| cel 1    | cel 2    | cel 3    |
+----------+          +----------+
| cel 4    |          | cel 6    |
+----------+----------+----------+

## Taules ordenables

Embolica una taula en un `<div>` amb la classe `table-sortable` per fer-la ordenable.

```markdown
/// html | div.table-sortable
| Nom  | Edat | País    |
|------|------|---------|
| Joan | 27   | Espanya |
| Anna | 23   | Canadà  |
| Pau  | 45   | Regne Unit |
///
```

/// html | div.table-sortable
| Nom  | Edat | País    |
|------|------|---------|
| Joan | 27   | Espanya |
| Anna | 23   | Canadà  |
| Pau  | 45   | Regne Unit |
///

## Taules MultiMD

```yaml title="properdocs.yml"
markdown_extensions:
  - pymdown_multimd_table:
      rowspan: true
      attr_list: true
      multiline: true
```

- `rowspan` (`^^`) i `colspan` (`||`) permeten crear cel·les que ocupen diverses files o columnes.

    ```markdown
    | A      | B  | C  |
    | ------ | -- | -- |
    | alt    | 1  ||
    | ^^     | 2  | y  |
    ```

    | A      | B  | C  |
    | ------ | -- | -- |
    | alt    | 1  ||
    | ^^     | 2  | y  |

- Les cel·les multilínia s'escriuen amb una barra inversa (`\`) al final de línia.

    ```markdown
    | Codi            | Sortida  |
    | --------------- | -------  |
    | ```             | - elem 1 |\
    | print("hola")   | - elem 2 |\
    | ```             |          |
    ```

    | Codi            | Sortida  |
    | --------------- | -------  |
    | ```             | - elem 1 |\
    | print("hola")   | - elem 2 |\
    | ```             |          |

- L'opció `attr_list` permet afegir atributs a les cel·les amb claus (`{}`).

    ```markdown
    | Nom   | Edat          |
    | ----- | ------------- |
    | Joan  | 27            | {.red}
    | Anna  | 23   {.green} |
    ```

    | Nom   | Edat          |
    | ----- | ------------- |
    | Joan  | 27            | {.red}
    | Anna  | 23   {.green} |

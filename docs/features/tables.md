---
title: Tables
icon: material/table
---

# Tables

## Grid Tables

```markdown
+---------------------+----------+
| Header 1            | Header 2 |
+==========+==========+==========+
| cell 1   | cell 2   | cell 3   |
+----------+          +----------+
| cell 4   |          | cell 6   |
+----------+----------+----------+
```

+---------------------+----------+
| Header 1            | Header 2 |
+==========+==========+==========+
| cell 1   | cell 2   | cell 3   |
+----------+          +----------+
| cell 4   |          | cell 6   |
+----------+----------+----------+

## Sortable Tables

Use a `div` element with the class `table-sortable` to make a table sortable.

```markdown
/// html | div.table-sortable
| Name | Age | Country |
|------|-----|---------|
| John | 27  | USA     |
| Jane | 23  | Canada  |
| Doe  | 45  | UK      |
///
```

/// html | div.table-sortable
| Name | Age | Country |
|------|-----|---------|
| John | 27  | USA     |
| Jane | 23  | Canada  |
| Doe  | 45  | UK      |
///


## Multimd Tables
```yaml title="properdocs.yml"
markdown_extensions:
  - pymdown_multimd_table:
      rowspan: true
      attr_list: true
      multiline: true
```

- `rowspan` (`^^`) and `colspan` (`||`) can be used to create multi-row and multi-column cells.

    ```markdown
    | A      | B  | C  |
    | ------ | -- | -- |
    | tall   | 1  ||
    | ^^     | 2  | y  |
    ```

    | A      | B  | C  |
    | ------ | -- | -- |
    | tall   | 1  ||
    | ^^     | 2  | y  |

- Multiline cells can be created using a backslash (`\`) at the end of a line.

    ```markdown
    | Code            | Output   |
    | --------------- | -------  |
    | ```             | - item 1 |\
    | print("hello")  | - item 2 |\
    | ```             |          |
    ```

    | Code            | Output   |
    | --------------- | -------  |
    | ```             | - item 1 |\
    | print("hello")  | - item 2 |\
    | ```             |          |

- The `attr_list` option allows you to add attributes to table cells using curly braces (`{}`).

    ```markdown
    | Name  | Age           |
    | ----- | ------------- |
    | John  | 27            | {.red}
    | Jane  | 23   {.green} |
    ```

    | Name  | Age           |
    | ----- | ------------- |
    | John  | 27            | {.red}
    | Jane  | 23   {.green} |

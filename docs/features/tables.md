---
title: Tables
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

Use `class="md-datatable sortable"` to make a table sortable
and also style it with the default theme.

<table class="md-datatable sortable">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Country</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John</td>
            <td>27</td>
            <td>USA</td>
        </tr>
        <tr>
            <td>Jane</td>
            <td>23</td>
            <td>Canada</td>
        </tr>
        <tr>
            <td>Doe</td>
            <td>45</td>
            <td>UK</td>
        </tr>
    </tbody>
</table>

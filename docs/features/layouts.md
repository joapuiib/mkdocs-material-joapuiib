---
title: Layouts
---

## Layout

### Column

Column layout is provided by the `.columns` class.

??? info
    Basically, it's a flexbox container with
    the following properties:
    ```css
    .columns {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        align-items: center;
    }
    ```

```md
/// html | div.columns
| Column 1 | Column 2 |
|----------|----------|
| Content  | Content  |
| Content  | Content  |
| Content  | Content  |

![Placeholder](https://via.placeholder.com/150)
///
```
/// html | div.result
//// html | div.columns
| Column 1 | Column 2 |
|----------|----------|
| Content  | Content  |
| Content  | Content  |
| Content  | Content  |

![Placeholder](https://via.placeholder.com/150)
////
///

---
title: Captions
icon: material/tooltip-text-outline
---

# Captions

> Reference [:octicons-link-external-16: Block Caption - PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/caption/)

This is the figure.
/// caption
This is the caption.
///

??? example ":simple-markdown: Markdown"
    ```markdown
    This is the figure.
    /// caption
    This is the caption.
    ///
    ```

## Image caption

![placeholder](img/placeholder-600x400.png)
/// attribution
Attribution
///
/// figure-caption
Caption for image
///

![placeholder](img/placeholder-600x400.png)
/// figure-caption | ^1
Virtual nested caption
///

??? example ":simple-markdown: Markdown"
    ```markdown
    ![placeholder](img/placeholder-600x400.png)
    /// attribution
    Attribution
    ///
    /// figure-caption
    Caption for image
    ///

    ![placeholder](img/placeholder-600x400.png)
    /// figure-caption | ^1
    Virtual nested caption
    ///
    ```

## Shadowed image caption

![placeholder](img/placeholder-600x400.png)
/// shadow-figure-caption
Shadow :material-box-shadow: image caption
///

??? example ":simple-markdown: Markdown"
    ```markdown
    ![placeholder](img/placeholder-600x400.png)
    /// shadow-figure-caption
    Shadow :material-box-shadow: image caption
    ///
    ```

## Table caption

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
/// attribution
Attribution
///
/// table-caption
Caption for table
///

??? example ":simple-markdown: Markdown"
    ```markdown
    | Header 1 | Header 2 |
    |----------|----------|
    | Cell 1   | Cell 2   |
    /// attribution
    Attribution
    ///
    /// table-caption
    Caption for table
    ///
    ```

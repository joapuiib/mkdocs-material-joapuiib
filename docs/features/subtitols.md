---
title: Subtítols
icon: material/tooltip-text-outline
---

# Subtítols

> Referència: [:octicons-link-external-16: Block Caption &mdash; PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/caption/)

Aquesta és la figura.
/// caption
Aquest és el subtítol.
///

??? example ":simple-markdown: Markdown"
    ```markdown
    Aquesta és la figura.
    /// caption
    Aquest és el subtítol.
    ///
    ```

## Subtítol d'imatge

![placeholder](img/placeholder-600x400.png)
/// attribution
Atribució
///
/// figure-caption
Subtítol de la imatge
///

![placeholder](img/placeholder-600x400.png)
/// figure-caption | ^1
Subtítol niat virtual
///

??? example ":simple-markdown: Markdown"
    ```markdown
    ![placeholder](img/placeholder-600x400.png)
    /// attribution
    Atribució
    ///
    /// figure-caption
    Subtítol de la imatge
    ///

    ![placeholder](img/placeholder-600x400.png)
    /// figure-caption | ^1
    Subtítol niat virtual
    ///
    ```

## Subtítol d'imatge amb ombra

![placeholder](img/placeholder-600x400.png)
/// shadow-figure-caption
Subtítol :material-box-shadow: amb ombra
///

??? example ":simple-markdown: Markdown"
    ```markdown
    ![placeholder](img/placeholder-600x400.png)
    /// shadow-figure-caption
    Subtítol :material-box-shadow: amb ombra
    ///
    ```

## Subtítol de taula

| Capçalera 1 | Capçalera 2 |
|-------------|-------------|
| Cel·la 1    | Cel·la 2    |
/// attribution
Atribució
///
/// table-caption
Subtítol de la taula
///

??? example ":simple-markdown: Markdown"
    ```markdown
    | Capçalera 1 | Capçalera 2 |
    |-------------|-------------|
    | Cel·la 1    | Cel·la 2    |
    /// attribution
    Atribució
    ///
    /// table-caption
    Subtítol de la taula
    ///
    ```

---
title: Imatges amb zoom
icon: material/image
---

# Imatges amb zoom

> Referència: [:octicons-link-external-16: GLightBox plugin](https://blueswen.github.io/mkdocs-glightbox/)

El tema integra el plugin de MkDocs [GLightBox](https://blueswen.github.io/mkdocs-glightbox/), que
permet ampliar qualsevol imatge fent-hi clic. La imatge s'obri en una finestra emergent
(_lightbox_), on també es mostren el títol i la descripció de la imatge.

## Llegendes de la imatge

Les llegendes es defineixen com a tipus de l'extensió `pymdownx.blocks.caption`. El _lightbox_ no
reconeix els blocs pel seu nom, sinó per la __classe__ que afigen a l'element generat. Per tant,
qualsevol tipus de llegenda es pot integrar amb GLightBox afegint-li una d'aquestes classes:

- __`glightbox-title`__: el text de la llegenda es mostra com a títol en el _lightbox_.
- __`glightbox-description`__: el text de la llegenda es mostra com a descripció en el _lightbox_.

Una possible configuració és la següent:

```yaml title="properdocs.yml"
markdown_extensions:
  - pymdownx.blocks.caption:
      auto: true
      types:
        - name: figure-caption
          prefix: "Figura {}. "
          classes: "glightbox-title"
        - name: shadow-figure-caption
          prefix: "Figura {}. "
          classes: "shadow glightbox-title"
        - name: figure-description
          classes: "description glightbox-description"
```


![Kenting, Taiwan](img/yuhan-chang-kenting.jpg)
/// figure-description : Platja de Kenting, al sud de l'illa de Taiwan.
/// figure-caption | .spell-ignore : Kenting, Taiwan

??? example ":simple-markdown: Markdown"
    ```markdown
    ![Kenting, Taiwan](img/yuhan-chang-kenting.jpg)
    /// figure-description : Platja de Kenting, al sud de l'illa de Taiwan.
    /// figure-caption : Kenting, Taiwan
    ```

## Títol i descripció només en el _lightbox_

Si el títol o la descripció només s'han de mostrar en la finestra ampliada, es poden indicar
amb els atributs `data-title` i `data-description` de la imatge. Aquests atributs tenen prioritat
sobre les llegendes de la imatge.

![Kenting, Taiwan](img/yuhan-chang-kenting.jpg){ data-title="Kenting, Taiwan" data-description="Platja de Kenting, al sud de l'illa de Taiwan." }

??? example ":simple-markdown: Markdown"
    ```markdown
    ![Kenting, Taiwan](img/yuhan-chang-kenting.jpg){ data-title="Kenting, Taiwan" data-description="Platja de Kenting, al sud de l'illa de Taiwan." }
    ```

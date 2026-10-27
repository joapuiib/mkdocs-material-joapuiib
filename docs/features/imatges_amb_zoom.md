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

Les llegendes que s'escriuen davall de la imatge també es mostren dins de la finestra ampliada.
D'aquesta manera, el text només s'escriu una vegada i es veu igual en la pàgina i en el _lightbox_.

- __`figure-caption`__: llegenda numerada de la figura. Es mostra com a __títol__ en el _lightbox_.
    També funciona amb `shadow-figure-caption`.
- __`description`__: descripció més extensa de la imatge, amb una lletra més xicoteta que la
    llegenda. Es mostra com a __descripció__ en el _lightbox_.
- __`attribution`__: autoria de la imatge. Es mostra al final de la descripció en el _lightbox_.

![Kenting, Taiwan](img/yuhan-chang-kenting.jpg)
/// attribution : [Yuhan Chang](https://unsplash.com/photos/ROWXoqmqyjk)
/// description : Platja de Kenting, al sud de l'illa de Taiwan.
/// figure-caption | .spell-ignore : Kenting, Taiwan

??? example ":simple-markdown: Markdown"
    ```markdown
    ![Kenting, Taiwan](img/yuhan-chang-kenting.jpg)
    /// attribution : [Yuhan Chang](https://unsplash.com/photos/ROWXoqmqyjk)
    /// description : Platja de Kenting, al sud de l'illa de Taiwan.
    /// figure-caption | .spell-ignore : Kenting, Taiwan
    ```

    Cada bloc embolcalla l'anterior, de manera que en la pàgina les llegendes es mostren en el
    mateix ordre en què s'escriuen: primer l'autoria, després la descripció i, al final, la llegenda.

## Títol i descripció només en el _lightbox_

Si el títol o la descripció només s'han de mostrar en la finestra ampliada, es poden indicar
amb els atributs `data-title` i `data-description` de la imatge. Aquests atributs tenen prioritat
sobre les llegendes de la imatge.

![Kenting, Taiwan](img/yuhan-chang-kenting.jpg){ data-title="Kenting, Taiwan" data-description="Platja de Kenting, al sud de l'illa de Taiwan." }

??? example ":simple-markdown: Markdown"
    ```markdown
    ![Kenting, Taiwan](img/yuhan-chang-kenting.jpg){ data-title="Kenting, Taiwan" data-description="Platja de Kenting, al sud de l'illa de Taiwan." }
    ```

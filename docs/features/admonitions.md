---
title: Admonitions
---
## Built-in admonitions
!!! note
    Alerta d'annotació `note`

!!! abstract
    Alerta de resum `abstract`

!!! info
    Alerta d'informació `info`

!!! tip
    Alerta de consell `tip`

!!! success
    Alerta d'èxit `success`

!!! question
    Alerta de pregunta `question`

!!! warning
    Alerta d'avís `warning`

!!! failure
    Alerta de fracàs `failure`

!!! danger
    Alerta de perill `danger`

!!! bug
    Alerta de problema `bug`

!!! example
    Alerta d'exemple `example`

!!! quote
    Alerta de cita `quote`

## Admonition types
!!! info "Títol de l'alerta"
    Es pot afegir un títol a l'alerta.

    ```markdown
    !!! info "Títol de l'alerta"
        Text de l'alerta.
    ```

!!! note ""
    Alerta sense títol.

    ```markdown
    !!! note ""
        Text de l'alerta.
    ```

??? note "Collapsible note"
    Es pot afegir un botó per a col·lapsar l'alerta.

    ```markdown
    ??? note "Collapsible note"
        Text de l'alerta.
    ```

???+ note "Collapsible note oberta"
    Es pot afegir un botó per a col·lapsar l'alerta.

    ```markdown
    ???+ note "Collapsible note"
        Text de l'alerta.
    ```

!!! note "Nested admonitions"
    Les alertes es poden anidar.

    ???+ info "Nested admonitions"
        Les alertes es poden anidar.


    ```markdown
    !!! note "Nested admonitions"
        Les alertes es poden anidar.

        ??? info "Nested admonitions"
            Les alertes es poden anidar.
    ```


## Custom admonitions
!!! prep
    Alerta de preparació `prep`

!!! important
    Alerta de important `important`

!!! solution
    Alerta de solució `solution`

!!! recommend
    Alerta de recomanació `recommend`

!!! notice
    Alerta de notícia `notice`

!!! spoiler
    Alerta de spoiler `spoiler`

!!! docs
    Alerta de documentació `docs`


---
title: Admonicions
icon: lucide/triangle-alert
---

# Admonicions

> Referència: [:lucide-external-link: Admonitions &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/admonitions.html)

## Admonicions de MaterialX

Tipus que inclou el tema MaterialX.

!!! note
    Admonició de tipus `note`

!!! abstract
    Admonició de tipus `abstract`

!!! info
    Admonició de tipus `info`

!!! tip
    Admonició de tipus `tip`

!!! success
    Admonició de tipus `success`

!!! question
    Admonició de tipus `question`

!!! warning
    Admonició de tipus `warning`

!!! failure
    Admonició de tipus `failure`

!!! danger
    Admonició de tipus `danger`

!!! bug
    Admonició de tipus `bug`

!!! example
    Admonició de tipus `example`

!!! quote
    Admonició de tipus `quote`

## Admonicions d'aquest tema

Tipus que afig aquest tema.

!!! spoiler
    Admonició de tipus `spoiler`

!!! recommend
    Admonició de tipus `recommend`

!!! prep
    Admonició de tipus `prep`

!!! important
    Admonició de tipus `important`

!!! solution
    Admonició de tipus `solution`

!!! construction
    Admonició de tipus `construction`

!!! notice
    Admonició de tipus `notice`

!!! picture
    Admonició de tipus `picture`

!!! deprecated
    Admonició de tipus `deprecated`

!!! docs
    Admonició de tipus `docs`

!!! extension
    Admonició de tipus `extension`

## Afegir admonicions addicionals

Des de la configuració, `theme.admonition` defineix la icona i el color d'un tipus nou (ací, `pregunta-examen`) o canvia els d'un tipus existent:

```yaml title="properdocs.yml"
theme:
  admonition:
    pregunta-examen:
      icon: lucide/circle-help
      color: '#ff6f00'
    example:
      icon: lucide/list
```

La icona pot ser qualsevol de les incloses al tema, com les de [Lucide](https://lucide.dev/icons/), o una icona personalitzada. S'utilitza com qualsevol altra admonició:

```markdown
!!! pregunta-examen "Títol opcional"
    Contingut de l'admonició.
```

!!! pregunta-examen "Títol opcional"
    Contingut de l'admonició.

### Títol traduït

Si no s'indica un títol, l'admonició mostra el nom del tipus. Per traduir-lo, s'afig en el plugin `i18n`:

```yaml title="properdocs.yml"
plugins:
  - i18n:
      languages:
        - locale: ca
          default: true
          name: Valencià
          admonition_translations:
            pregunta-examen: Pregunta d'examen
```

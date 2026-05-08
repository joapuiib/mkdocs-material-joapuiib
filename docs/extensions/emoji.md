---
title: Emoji
icon: material/emoticon-happy
---

# Emoji

Índex d'emojis personalitzat compatible amb [`pymdownx.emoji`](https://facelessuser.github.io/pymdown-extensions/extensions/emoji/) que afegeix les icones del directori `.icons/` del tema.

> Referència: [:octicons-link-external-16: Icons, Emojis &mdash; MaterialX](https://jaywhj.github.io/mkdocs-materialx/reference/icons-emojis.html)

## Configuració

```yml title="properdocs.yml"
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:material_joapuiib.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
```

L'índex `material_joapuiib.extensions.emoji.twemoji` carrega les icones de Twemoji (incloses per Material) i hi afegeix les icones empaquetades dins del tema (`material_joapuiib/templates/.icons/`).

## Icones personalitzades

Es poden afegir directoris d'icones addicionals via `custom_icons`:

```yml title="properdocs.yml"
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:material_joapuiib.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
      options:
        custom_icons:
          - overrides/.icons
```

## Ús

Les icones s'invoquen amb la sintaxi `:nom-icona:` dins del Markdown:

```md
:material-database:
:fontawesome-brands-github:
:octicons-link-external-16:
```

Veure la [documentació d'icones](../features/icones/icones.md) per al llistat complet.

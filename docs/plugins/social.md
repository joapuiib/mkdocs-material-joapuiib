---
title: Social cards
icon: material/share-variant
---

# Social cards

Plugin que activa una disposició de targeta social compartida per a tots els llocs basats en aquest tema. Configura el plugin [`materialx/social`](https://jaywhj.github.io/mkdocs-materialx/plugins/social.html) perquè utilitze una disposició empaquetada amb el tema, amb colors derivats de la paleta i suport per a la pàgina d'inici.

Exemple en viu &mdash; la targeta social d'aquest mateix lloc es genera amb aquest plugin:

<img src="../../assets/images/social/index.png" alt="Targeta social de Material joapuiib" loading="lazy">


## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/social
  - materialx/social:
      enabled: !ENV [CI, false]
```

L'ordre importa: `material-joapuiib/social` ha d'aparèixer abans de `materialx/social` perquè la disposició s'enllace correctament.

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `enabled` | `bool` | `true` | Activa o desactiva el plugin. |

A `materialx/social`, mantén [les seues opcions habituals](https://jaywhj.github.io/mkdocs-materialx/plugins/social.html). `cards_layout_dir` i `cards_layout` es defineixen automàticament; només cal sobreescriure'ls si vols una disposició personalitzada.

## Què s'hi inclou

- **Logotip** (extret de `theme.icon.logo`).
- **Nom del lloc** com a xip a la part superior. Ocult a la pàgina d'inici (vegeu més avall).
- **Títol de la pàgina** gran (3 línies, ajust automàtic).
- **Descripció** en gris suau (2 línies, opcional).
- **Peu** amb autor i URL del lloc.
- **Marca d'aigua** decorativa amb la icona del lloc.
- **Barra d'accent** superior i divisor sota la capçalera.

### Pàgina d'inici

A la pàgina d'inici, el nom del lloc reemplaça el títol de la pàgina i s'amaga el xip superior.
Així s'evita que aparega el text genèric "Inici" i el nom del lloc pren tot el protagonisme.

## Personalització
Per a personalitzacions més fines, defineix `extra.social_card`. Totes les claus són opcionals:

| Clau | Tipus | Per defecte | Descripció |
|------|-------|-------------|-------------|
| `accent_color` | hex | `theme.palette.primary` (o `#4051b5`) | Barra superior, divisor, xip del logo i color de la marca d'aigua. |
| `background_color` | hex | `#1e2029` | Fons de la targeta (compatible amb l'esquema `slate`). |
| `text_color` | hex | `#ffffff` | Nom del lloc i títol de la pàgina. |
| `muted_color` | hex | `#b8bcc4` | Descripció de la pàgina. |
| `footer_color` | hex | `accent_color` | Línia del peu (autor + URL). |
| `watermark_icon` | string | `theme.icon.logo` | Identificador d'icona ([Material](https://pictogrammers.com/library/mdi/), [Simple Icons](https://simpleicons.org/), etc.) per a la marca d'aigua decorativa. |

```yml title="properdocs.yml"
extra:
  social_card:
    accent_color: "#009485"
    watermark_icon: material/rocket-launch
```

<img src="../img/social-custom.png" alt="Targeta social personalitzada amb paleta teal i icona de coet" loading="lazy">

### Personalització per pàgina

Igual que amb `materialx/social`, el `front matter` accepta les claus de [Layout overrides](https://jaywhj.github.io/mkdocs-materialx/plugins/social.html#per-page-customization):

```yml
---
title: Pàgina especial
description: Descripció més detallada per a la targeta social.
social:
  cards_layout_options:
    title: Títol substituït
    description: Descripció substituïda
---
```

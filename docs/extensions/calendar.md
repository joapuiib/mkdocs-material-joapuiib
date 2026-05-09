---
title: Calendar
icon: material/calendar-month
---

# Calendar

Extensió de [Pymdownx Blocks][blocks] que renderitza calendaris a partir d'una configuració TOML embeguda dins d'un bloc `/// calendar`. Suporta dies festius, rangs amb classes CSS, anotacions per dia, _tooltips_ i localització.

[blocks]: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/

## Configuració

Afegeix l'extensió a `markdown_extensions` dins de `properdocs.yml`:

```yaml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.calendar:
      locale: ca
```

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `locale` | string | `"en"` | Codi de llengua per defecte aplicat als blocs que no en defineixen un. Valor especial `"auto"` per agafar l'idioma de la pàgina (vegeu [_Localització_](#localitzacio)). |

L'extensió activa automàticament el gestor de blocs de `pymdownx`; els estils ja venen inclosos al tema.

## Sintaxi

El cos del bloc és [TOML](https://toml.io); les dates es declaren com a _local-date_ (`YYYY-MM-DD`).

| Camp | Tipus | Per defecte | Descripció |
|------|-------|-------------|-------------|
| `start` | data | _obligatori_ | Primer dia del període. |
| `end` | data | _obligatori_ | Últim dia (inclusiu, `>= start`). |
| `weekends` | `"show"` \| `"plain"` \| `"hide"` | `"show"` | Tractament de dissabtes i diumenges. |
| `locale` | string | _hereta_ | Codi de llengua. |
| `month_names` | llista de 12 strings | — | Noms de mes personalitzats. |
| `weekday_labels` | llista de 7 strings | — | Noms de dia personalitzats. |
| `[holiday]` | taula | — | Configuració de festius (dates, plain, tooltip). Veure [_Festius_](#festius). |
| `ranges` | array of tables | `[]` | Rangs amb classe i tooltip. |
| `days` | array of tables | `[]` | Anotacions per dia individual. |

````markdown
/// calendar
start = 2026-01-01
end = 2026-01-31
///
````

/// calendar
start = 2026-01-01
end = 2026-01-31
///

## Festius

Els festius es configuren dins d'una taula `[holiday]`:

| Camp | Tipus | Per defecte | Descripció |
|------|-------|-------------|-------------|
| `dates` | llista de dates / parells `[from, to]` | `[]` | Llista barrejada de dates simples i rangs. Tots els dies expandits reben la classe `holiday`. |
| `plain` | booleà | `false` | Si `true`, les classes/tooltips de `[[ranges]]` no s'apliquen sobre festius. |
| `tooltip` | string | `""` | Text de tooltip aplicat a cada dia festiu. |

````markdown
/// calendar
start = 2026-04-01
end = 2026-04-30

[holiday]
plain = true
tooltip = "Festiu"
dates = [
  2026-04-25,
  [2026-04-02, 2026-04-06],
]

[[ranges]]
from = 2026-04-01
to = 2026-04-15
class = "blue"
tooltip = "Sprint Q2"
///
````

/// calendar
start = 2026-04-01
end = 2026-04-30

[holiday]
plain = true
tooltip = "Festiu"
dates = [
  2026-04-25,
  [2026-04-02, 2026-04-06],
]

[[ranges]]
from = 2026-04-01
to = 2026-04-15
class = "blue"
tooltip = "Sprint Q2"
///

## Rangs

Cada `[[ranges]]` aplica una classe CSS (i opcionalment un _tooltip_) a un interval inclusiu.

| Camp | Tipus | Descripció |
|------|-------|-------------|
| `from` | data | Inici (inclusiu). |
| `to` | data | Final (inclusiu, `>= from`). |
| `class` | string | Classe CSS aplicada a cada dia. |
| `tooltip` | string (opc.) | Text de tooltip (Markdown) repetit a cada dia del rang. |
| `label` | string (opc.) | Etiqueta curta repetida a cada dia del rang. |

Quan diversos rangs es solapen, totes les classes s'apliquen i els _tooltips_ es combinen en un mateix popover amb un punt per font.

````markdown
/// calendar
start = 2026-02-01
end = 2026-02-28

[[ranges]]
from = 2026-02-02
to = 2026-02-13
class = "blue"
tooltip = "Sprint A"

[[ranges]]
from = 2026-02-09
to = 2026-02-20
class = "green"
tooltip = "Suport sprint"
///
````

/// calendar
start = 2026-02-01
end = 2026-02-28

[[ranges]]
from = 2026-02-02
to = 2026-02-13
class = "blue"
tooltip = "Sprint A"

[[ranges]]
from = 2026-02-09
to = 2026-02-20
class = "green"
tooltip = "Suport sprint"
///

## Anotacions per dia

`[[days]]` afegeix classe i/o _tooltip_ a un dia concret sense haver de declarar un `[[ranges]]` d'un sol dia:

| Camp | Tipus | Obligatori | Descripció |
|------|-------|------------|-------------|
| `date` | data | sí | Dia que rep l'anotació. |
| `class` | string | no | Classe CSS afegida a la cel·la. |
| `tooltip` | string | no | Text de tooltip (Markdown). |
| `label` | string | no | Etiqueta curta visible a la cantonada de la cel·la. Pintat amb la classe del `class`. |

Les anotacions per dia s'apliquen sempre, també sobre festius i caps de setmana en mode `plain`.

````markdown
/// calendar
start = 2026-03-01
end = 2026-03-31

[[days]]
date = 2026-03-09
class = "purple"
tooltip = "Demo stakeholders"

[[days]]
date = 2026-03-23
label = "R"
tooltip = "Recordatori: informe"
///
````

/// calendar
start = 2026-03-01
end = 2026-03-31

[[days]]
date = 2026-03-09
class = "purple"
tooltip = "Demo stakeholders"

[[days]]
date = 2026-03-23
label = "R"
tooltip = "Recordatori: informe"
///

## Tooltips

Cada `[[ranges]]`, `[[days]]` i `[holiday].tooltip` admet **Markdown complet**: negretes, links, codi inline, etc. El tema renderitza les cadenes amb un `markdown.Markdown` independent i les emet en una `<div class="md-tooltip2">` paral·lela al calendari, reaprofitant l'estil de tooltip de Material. Un script lleuger (`calendar-tooltips.js`) gestiona obrir/tancar al passar el ratolí o donar-li focus per teclat.

Quan diversos rangs/anotacions toquen el mateix dia, totes les cadenes s'apilen com a paràgrafs separats dins el mateix tooltip.

Cap configuració extra al `properdocs.yml`: ni `attr_list`, ni `content.tooltips`, ni cap altre afegit. Tot ja ve cobert pel tema.

````markdown
/// calendar
start = 2026-02-01
end = 2026-02-28

[holiday]
tooltip = "Festiu *nacional* — `oficina tancada`"
dates = [2026-02-14]

[[ranges]]
from = 2026-02-09
to = 2026-02-13
class = "blue"
tooltip = "Sprint **12** — feature freeze el [divendres](https://example.org)"

[[days]]
date = 2026-02-20
class = "purple"
tooltip = "Demo amb stakeholders. Recordeu portar el `prototype.zip`."
///
````

/// calendar
start = 2026-02-01
end = 2026-02-28

[holiday]
tooltip = "Festiu *nacional* — `oficina tancada`"
dates = [2026-02-14]

[[ranges]]
from = 2026-02-09
to = 2026-02-13
class = "blue"
tooltip = "Sprint **12** — feature freeze el [divendres](https://example.org)"

[[days]]
date = 2026-02-20
class = "purple"
tooltip = "Demo amb stakeholders. Recordeu portar el `prototype.zip`."
///

Passa el ratolí (o pitja Tab) sobre els dies acolorits per veure el contingut formatat.

## Caps de setmana

| Mode | Cel·les Sat/Sun | Classe `weekend` | Classes de `[[ranges]]` | Columnes |
|------|-----------------|------------------|-------------------------|----------|
| `show` (per defecte) | sí | sí | sí | 7 |
| `plain` | sí | sí | **no** | 7 |
| `hide` | no | — | n/a | 5 |

Mode `plain` deixa Sat/Sun sense la classe del rang (útil per a sprints Dl–Dv):

````markdown
/// calendar
start = 2026-01-01
end = 2026-01-31
weekends = "plain"

[[ranges]]
from = 2026-01-05
to = 2026-01-30
class = "blue"
tooltip = "Sprint laboral"
///
````

/// calendar
start = 2026-01-01
end = 2026-01-31
weekends = "plain"

[[ranges]]
from = 2026-01-05
to = 2026-01-30
class = "blue"
tooltip = "Sprint laboral"
///

Mode `hide` retalla la graella a 5 columnes:

````markdown
/// calendar
start = 2026-04-01
end = 2026-04-30
weekends = "hide"
///
````

/// calendar
start = 2026-04-01
end = 2026-04-30
weekends = "hide"
///

## Localització

Locales empaquetats: `en`, `ca`, `es`, `fr`, `de`, `pt`, `it`, `gl`, `eu`. Precedència: `month_names` / `weekday_labels` inline > camp `locale` > opció de l'extensió > anglès.

### `locale: auto`

Si el lloc usa el plugin [`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n) (o l'integració d'i18n de Material), pots configurar `locale: auto` a l'extensió i cada calendari hereta l'idioma de la pàgina:

```yaml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.calendar:
      locale: auto
```

Quan no hi ha context de pàgina (p. ex. tests aïllats), `auto` cau a anglès.

````markdown
/// calendar
start = 2026-06-01
end = 2026-06-30
locale = "fr"

[holiday]
dates = [2026-06-21]
///
````

/// calendar
start = 2026-06-01
end = 2026-06-30
locale = "fr"

[holiday]
dates = [2026-06-21]
///

Sobreescriptura puntual:

```toml
locale = "ca"
month_names = ["Gen","Feb","Mar","Abr","Mai","Jun","Jul","Ago","Set","Oct","Nov","Des"]
weekday_labels = ["L","M","X","J","V","S","D"]
```

Si tens [`babel`](https://babel.pocoo.org) instal·lat, qualsevol codi que reconega Babel (per exemple `nl_NL`) es resol automàticament.

## Inclusió de fitxers (`!include`)

Per compartir festius o rangs entre diversos calendaris (sprints d'equip, calendari escolar comú, etc.) pots extreure'ls a un fitxer TOML i incloure'l amb `!include "ruta"`:

```toml title="docs/data/festius_2026.toml"
[holiday]
plain = true
tooltip = "Festiu"
dates = [
  2026-01-01,
  2026-01-06,
  [2026-04-02, 2026-04-06],
  2026-12-25,
]
```

````markdown
/// calendar
start = 2026-01-01
end = 2026-12-31
weekends = "hide"

!include "data/festius_2026.toml"
///
````

Notes:

- La ruta és relativa al fitxer Markdown que conté el bloc.
- Els includes poden anidar-se (un fitxer inclòs pot incloure'n d'altres) fins a 16 nivells; els cicles es detecten i emeten un error.
- La directiva ha d'aparèixer sola en una línia. `!include` enmig d'una línia es deixa intacte.
- El fitxer inclòs es concatena textualment abans de parsejar el TOML; ha de ser TOML vàlid en el seu lloc.

## Colors disponibles

8 classes de color preestablertes per `class` a `ranges` o `days`. Light/dark mode automàtic.

| Classe | Mostra | Variables CSS |
|--------|--------|---------------|
| `red` | <span class="md-calendar-swatch red">Aa</span> | `--md-cal-hue-red-bg` / `-fg` |
| `orange` | <span class="md-calendar-swatch orange">Aa</span> | `--md-cal-hue-orange-bg` / `-fg` |
| `yellow` | <span class="md-calendar-swatch yellow">Aa</span> | `--md-cal-hue-yellow-bg` / `-fg` |
| `green` | <span class="md-calendar-swatch green">Aa</span> | `--md-cal-hue-green-bg` / `-fg` |
| `teal` | <span class="md-calendar-swatch teal">Aa</span> | `--md-cal-hue-teal-bg` / `-fg` |
| `blue` | <span class="md-calendar-swatch blue">Aa</span> | `--md-cal-hue-blue-bg` / `-fg` |
| `purple` | <span class="md-calendar-swatch purple">Aa</span> | `--md-cal-hue-purple-bg` / `-fg` |
| `pink` | <span class="md-calendar-swatch pink">Aa</span> | `--md-cal-hue-pink-bg` / `-fg` |

Sobreescriu les variables a `extra.css` per retunejar el to.

````markdown
/// calendar
start = 2026-05-01
end = 2026-05-31
weekends = "plain"

[[ranges]]
from = 2026-05-04
to = 2026-05-08
class = "red"

[[ranges]]
from = 2026-05-11
to = 2026-05-15
class = "orange"

[[ranges]]
from = 2026-05-18
to = 2026-05-22
class = "yellow"

[[ranges]]
from = 2026-05-25
to = 2026-05-29
class = "green"
///
````

/// calendar
start = 2026-05-01
end = 2026-05-31
weekends = "plain"

[[ranges]]
from = 2026-05-04
to = 2026-05-08
class = "red"

[[ranges]]
from = 2026-05-11
to = 2026-05-15
class = "orange"

[[ranges]]
from = 2026-05-18
to = 2026-05-22
class = "yellow"

[[ranges]]
from = 2026-05-25
to = 2026-05-29
class = "green"
///

## Estils

Per afinar mides o colors sense modificar el tema, sobreescriu les variables CSS al teu `extra_css`:

```css title="docs/assets/extra.css"
:root {
  --md-cal-cell-size: 2.5rem;
  --md-cal-holiday: #c0392b;
}
```

Variables disponibles: `--md-cal-cell-size`, `--md-cal-gap`, `--md-cal-bg`, `--md-cal-fg`, `--md-cal-border`, `--md-cal-muted`, `--md-cal-weekend`, `--md-cal-holiday`, `--md-cal-out`, més la paleta `--md-cal-hue-*-bg/fg`.

## Errors

Quan la configuració és invàlida, l'extensió emet un missatge llegible en lloc de fer caure la _build_:

````markdown
/// calendar
start = 2026-02-01
end = 2026-01-01
///
````

/// calendar
start = 2026-02-01
end = 2026-01-01
///

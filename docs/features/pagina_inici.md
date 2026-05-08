---
title: Pàgina d'inici
icon: material/home-variant
---

# Pàgina d'inici

Plantilla d'estil per a crear pàgines d'inici (landing) modernes i consistents.

## Activació

Afegeix `landing: true` al front matter. Es recomana també amagar la navegació lateral i el TOC.

```yaml title="docs/index.md (front matter)"
---
title: Títol del lloc
icon: material/home
hide:
    - navigation
    - toc
landing: true
---
```

## Estructura

```markdown
/// html | div.landing-hero
ETIQUETA SUPERIOR
{ .eyebrow }

# Títol principal

Subtítol descriptiu.
{ .subtitle }

[:octicons-arrow-right-24: Acció principal](primer.md){ .md-button .md-button--primary } [Acció secundària](segon.md){ .md-button }
{ .actions }
///

Paràgraf d'introducció opcional.

/// html | div.grid.cards
-   :material-icon:{ .lg .middle } __Targeta 1__

    ---

    Descripció breu.

    [:octicons-arrow-right-24: Veure-ho](pagina.md)

-   :material-icon:{ .lg .middle } __Targeta 2__

    ---

    Descripció breu.

    [:octicons-arrow-right-24: Veure-ho](altra.md)
///
```

## Components del hero

| Element | Sintaxi |
|---------|---------|
| Etiqueta superior | `Text { .eyebrow }` |
| Títol | `# Text` |
| Subtítol | `Text { .subtitle }` |
| Botons | `[Text](url){ .md-button .md-button--primary }` agrupats amb `{ .actions }` |

## Exemple

```markdown title="docs/index.md"
--8<-- "docs/index.md"
```

---
title: Numeració de capçaleres
icon: material/format-list-numbered
---

# Numeració de capçaleres

Extensió de Python-Markdown que afegeix números de secció als títols de l'HTML generat. Els números segueixen el format `1.`, `1.1.`, `1.1.1.`, etc.

## Configuració

Afegeix l'extensió a `markdown_extensions` al fitxer de configuració:

```yaml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.heading_numbers
  - toc:
      slugify: !!python/name:material_joapuiib.extensions.heading_numbers.slugify_without_numbers
```

Configurar el `slugify` de `toc` és opcional però recomanable: elimina els números dels àncores dels títols perquè els enllaços no canvien si la numeració canvia.

## Opcions

| Opció | Tipus | Per defecte | Descripció |
|-------|-------|-------------|-------------|
| `start_level` | `int` | `1` | Primer nivell de capçalera a numerar. `1` = h1, `2` = h2, etc. |

### Exemple: començar a h2

```yaml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.heading_numbers:
      start_level: 2
  - toc:
      slugify: !!python/name:material_joapuiib.extensions.heading_numbers.slugify_without_numbers
```

Amb `start_level: 2`, les h1 no es numeren i les h2 comencen a `1.`.

## Format de numeració

| Capçalera | Número |
|-----------|--------|
| `# H1`   | `1.`   |
| `## H2`  | `1.1.` |
| `### H3` | `1.1.1.` |

Els comptadors es reinicien quan apareix una capçalera de nivell superior. Per exemple:

```markdown
# Introducció         → 1. Introducció
## Context            → 1.1. Context
## Motivació          → 1.2. Motivació
# Mètodes             → 2. Mètodes
## Recollida de dades → 2.1. Recollida de dades
### Instruments       → 2.1.1. Instruments
## Anàlisi            → 2.2. Anàlisi
```

## Sortida HTML

Cada número s'embolica en un element `<span class="heading-number">`, que permet aplicar estils CSS:

```html
<h2 id="context">
  <span class="heading-number">1.1. </span>Context
</h2>
```

## Integració amb el TOC

Els números també apareixen a les entrades del table of contents. Quan `slugify_without_numbers` està configurat, l'`id` del títol es genera a partir del text sense el prefix numèric, de manera que `## Context` té `id="context"` independentment de la seua numeració.

---
template: slides.html
title: Diapositives
icon: material/presentation
---

# Diapositives

### Presentacions amb Reveal.js a partir de Markdown

---

## Ús

Per convertir una pàgina en una presentació, indica `template: slides.html` al *front matter*:

- `template: slides.html`
- `title`: títol de la pàgina i de la pestanya del navegador
- `icon`: icona mostrada al menú de navegació
- `print_title` *(opcional)*: títol usat en exportar a PDF, sense canviar el títol normal de la pàgina

--

### Extensions del tema

El contingut es processa amb el mateix conversor de Markdown que la resta del lloc: admonicions, icones, pestanyes, taules, matemàtiques... tot allò documentat a [Característiques](index.md) funciona també dins de les diapositives.

!!! tip "Prova-ho"
    Aquesta admonició :material-check: es renderitza igual que en qualsevol altra pàgina.

---

## Diapositives horitzontals

Separa diapositives horitzontals amb una línia sola amb `---`, amb una línia en blanc abans i després. Cada `#`, `##`... nou dins de la mateixa diapositiva es mostra tal qual, no crea diapositives noves.

```md
# Diapositiva 1

---

# Diapositiva 2
```

--

### Diapositives verticals

Dins d'un mateix bloc horitzontal, separa diapositives verticals amb una línia sola amb `--`. Naveguen amb les fletxes ↑/↓ i apareixen penjant de l'horitzontal a la vista general (`O`).

```md
## Diapositiva 2a

--

## Diapositiva 2b
```

---

## Notes del ponent

Escriu `Note:` a l'inici d'una línia: tot el que hi haja a partir d'eixe punt, fins al final de la diapositiva, es converteix en notes del ponent i no es mostra al públic.

Prem `S` per obrir la vista de l'orador i veure-les.

Note:
Estes són les notes d'esta diapositiva. Sols les veu qui prem `S`.

---

## Fragments

Els elements amb classe `fragment` apareixen un a un en avançar la presentació:

```md
<div class="fragment">
Primer fragment.
</div>

<div class="fragment">
Segon fragment.
</div>
```

<div class="fragment">
Primer fragment.
</div>

<div class="fragment">
Segon fragment.
</div>

--

### Combinar passos

Niant fragments es poden encadenar efectes en passos successius: `highlight-red` (i les altres variants `highlight-*`) no s'amaguen per defecte, sols canvien de color en arribar al seu pas, així que niat dins d'un fragment normal primer apareix i després es ressalta:

```md
<div class="fragment">
<span class="fragment highlight-red">Tercer pas: primer apareix, després es posa roig.</span>
</div>
```

<div class="fragment">
<span class="fragment highlight-red">Tercer pas: primer apareix, després es posa roig.</span>
</div>

---

## Matemàtiques

Fórmules amb KaTeX, igual que a [Matemàtiques](matematiques.md):

<div class="fragment">
$$f(a)=\frac{1}{2\pi i}\oint_\gamma \frac{f(z)}{z-a}\,dz$$
</div>

---

## Blocs de codi

Els blocs de codi normals es ressalten amb Pygments com a la resta del lloc, vegeu [Blocs de codi](blocs_de_codi.md):

```python
def saluda(nom):
    print(f"Hola, {nom}!")
```

--

### Revelat progressiu de línies

Afig `{data-line-numbers="1-2|3|4"}` a la línia del bloc de codi per revelar-ne les línies progressivament en avançar la presentació:

```js {data-line-numbers="1-2|3|4"}
let a = 1;
let b = 2;
let c = x => 1 + 2 + x;
c(3);
```

---

## Exportar a PDF

Prem el botó :fontawesome-regular-file-pdf: de la barra d'eines, o `Ctrl` + `P`: s'obri la mateixa presentació en una pestanya nova amb les diapositives en disposició d'impressió, i s'inicia el diàleg d'impressió del navegador en acabar de carregar.

---

## Navegació

- ← → ↑ ↓ / `Espai`: moure's entre diapositives
- `F`: pantalla completa
- `O` o `Esc`: vista general de totes les diapositives
- `S`: vista de l'orador (amb notes i temporitzador)

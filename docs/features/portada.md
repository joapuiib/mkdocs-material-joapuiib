---
template: document.html
icon: material/file-star-outline
title: Portada
print_title: cover-document
cover:
  icon: material/file-star-outline
  subtitle: Subtítol personalitzat
  curs: '2024 – 2025'
  original_author: Carme
  license:
    type: Copyright
    text: "Tots els drets reservats &copy; 2021"
    image: False
---

# Portada

Plantilla de portada per a documents imprimibles. La pàgina utilitza la plantilla `document.html` i pren les metadades del front matter per generar la capçalera i el peu del document.

<style>
.md-typeset .mdx-switch button>code {
    background-color: var(--md-primary-fg-color);
    color: var(--md-primary-bg-color);
    display: block;
}
.md-typeset .mdx-switch button:focus, .md-typeset .mdx-switch button:hover {
    opacity: .75;
}
.md-typeset .mdx-switch button {
    cursor: pointer;
    transition: opacity .25s;
}
</style>
<div class="mdx-switch">
  <button data-md-color-primary="red"><code>red</code></button>
  <button data-md-color-primary="pink"><code>pink</code></button>
  <button data-md-color-primary="purple"><code>purple</code></button>
  <button data-md-color-primary="deep-purple"><code>deep purple</code></button>
  <button data-md-color-primary="indigo"><code>indigo</code></button>
  <button data-md-color-primary="blue"><code>blue</code></button>
  <button data-md-color-primary="light-blue"><code>light blue</code></button>
  <button data-md-color-primary="cyan"><code>cyan</code></button>
  <button data-md-color-primary="teal"><code>teal</code></button>
  <button data-md-color-primary="green"><code>green</code></button>
  <button data-md-color-primary="light-green"><code>light green</code></button>
  <button data-md-color-primary="lime"><code>lime</code></button>
  <button data-md-color-primary="yellow"><code>yellow</code></button>
  <button data-md-color-primary="amber"><code>amber</code></button>
  <button data-md-color-primary="orange"><code>orange</code></button>
  <button data-md-color-primary="deep-orange"><code>deep orange</code></button>
  <button data-md-color-primary="brown"><code>brown</code></button>
  <button data-md-color-primary="grey"><code>grey</code></button>
  <button data-md-color-primary="blue-grey"><code>blue grey</code></button>
  <button data-md-color-primary="black"><code>black</code></button>
  <button data-md-color-primary="white"><code>white</code></button>
</div>

<script>
  var buttons = document.querySelectorAll("button[data-md-color-primary]")
  buttons.forEach(function(button) {
    button.addEventListener("click", function() {
      var attr = this.getAttribute("data-md-color-primary")
      document.body.setAttribute("data-md-color-primary", attr)
      var name = document.querySelector("#__code_1 code span.l")
      name.textContent = attr.replace("-", " ")
    })
  })
</script>

## Configuració

Tots els paràmetres de la portada es poden definir per defecte a `mkdocs.yml`, dins de `theme.cover`. S'aplicaran a totes les pàgines que mostren portada.

```yml title="mkdocs.yml"
theme:
  cover:
    icon: material/file-star-outline
    logo: img/cover/logo.svg
    background: true
    subtitle: Subtítol per defecte
    curs: '2024 – 2025'
    author: Joan Puigcerver
    email: joan@example.com
    original_author: Carme
    license:
      type: Copyright
      text: "Tots els drets reservats &copy; 2021"
      link: https://example.com/license
      image: img/license/copyright.png
```

## Front matter

Qualsevol paràmetre es pot sobreescriure per a una pàgina concreta dins del bloc `cover` del *front matter*. Els valors del *front matter* tenen prioritat sobre els definits a `mkdocs.yml`.

```yml
---
template: document.html
title: Cover
print_title: cover-document
cover:
  icon: material/file-star-outline
  logo: 'img/cover/other-logo.png'
  subtitle: Custom subtitle
  curs: '24/25'
  original_author: Carmen
  license:
    type: Copyright
    text: "All rights reserved &copy; 2021"
    image: False
---
```

`print_title` permet definir el títol que s'utilitzarà en imprimir o guardar la pàgina en PDF, sense canviar el títol normal de la pàgina al navegador. No forma part de `cover`, ja que també afecta el títol de la pestanya del navegador.

Per amagar la portada en una pàgina concreta encara que estiga activada per defecte a `theme.cover`, n'hi ha prou amb definir `cover: false` al *front matter*.

## Paràmetres

| Paràmetre               | Descripció                                                              | Si no està definit enlloc                                  |
| ------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `cover.title`            | Títol mostrat a la portada.                                              | S'utilitza el títol de la pàgina                              |
| `cover.icon`             | Icona mostrada al costat del títol.                                      | No es mostra cap icona                                        |
| `cover.logo`             | Logotip mostrat a la portada (imatge o SVG).                             | No es mostra cap logotip                                      |
| `cover.background`       | Activa el fons decoratiu de la portada.                                  | No es mostra el fons                                          |
| `cover.subtitle`         | Subtítol (text o llista de textos) mostrat sota el títol.                | No es mostra cap subtítol                                     |
| `cover.curs`             | Curs acadèmic mostrat en una targeta.                                    | No es mostra la targeta de curs                               |
| `cover.author`           | Autor mostrat en una targeta.                                            | S'utilitza `site_author`; si tampoc no está definit, no es mostra la targeta |
| `cover.email`            | Correu electrònic mostrat en una targeta.                                | S'utilitza `site_email`; si tampoc no está definit, no es mostra l'adreça |
| `cover.original_author`  | Autor original de l'obra derivada.                                       | No es mostra l'avís d'obra derivada                            |
| `cover.license.type`     | Nom de la llicència.                                                     | S'utilitza `theme.license.type`; si tampoc no está definit, la targeta es mostra sense nom de llicència |
| `cover.license.text`     | Text descriptiu de la llicència.                                         | S'utilitza `theme.license.text`; si tampoc no está definit, no es mostra cap text descriptiu |
| `cover.license.link`     | Enllaç de destí de la imatge de llicència.                               | S'utilitza `theme.license.link`; si tampoc no está definit, la imatge (si es mostra) no enllaça enlloc |
| `cover.license.image`    | Imatge/logotip de la llicència.                                          | S'utilitza `theme.license.image`; si tampoc no está definit, no es mostra cap imatge de llicència |

Si ni `theme.cover` (a `mkdocs.yml`) ni cap pàgina defineixen `cover` al *front matter*, la portada no es mostra en absolut.

`theme.license.*` és la configuració global de llicència, usada també al peu de pàgina de drets d'autor.

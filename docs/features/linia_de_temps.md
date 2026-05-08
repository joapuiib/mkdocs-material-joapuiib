---
title: Línia de temps
icon: material/timeline
---

# Línia de temps

Component per a mostrar esdeveniments en ordre cronològic. Suporta variants amb diferents colors, estils de línia (`dashed`, `dotted`) i marcadors (`check`, `cross`).
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

/// html | div.timeline.dashed
### Línia discontínua
Element de línia de temps amb línia discontínua.
///

/// html | div.timeline.primary
### Element marcat
Element de línia de temps amb una marca de verificació.
///

/// html | div.timeline.info.dotted
### Element informatiu amb línia puntejada
Element amb color `info` i línia puntejada.
///

/// html | div.timeline.error.cross
### Element d'error
Element amb color d'error i una creu com a marcador.
///

/// html | div.timeline.success
### Element d'èxit
Element amb color d'èxit.
///


??? example ":simple-markdown: Markdown"
    ```md
    /// html | div.timeline.dashed
    ### Línia discontínua
    Element de línia de temps amb línia discontínua.
    ///

    /// html | div.timeline.check.light
    ### Element marcat
    Element de línia de temps amb una marca de verificació.
    ///

    /// html | div.timeline.info.dotted
    ### Element informatiu amb línia puntejada
    Element amb color `info` i línia puntejada.
    ///

    /// html | div.timeline.error.cross
    ### Element d'error
    Element amb color d'error i una creu com a marcador.
    ///

    /// html | div.timeline.success
    ### Element d'èxit
    Element amb color d'èxit.
    ///
    ```


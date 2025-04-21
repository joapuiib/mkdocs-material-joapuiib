---
title: Time line
icon: material/timeline
---

## Time line
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
### Dashed line
This is a timeline item with a dashed line.
///

/// html | div.timeline.check
### Checked item
This is a timeline item with a check mark.
///

/// html | div.timeline.info.dotted
### Info item with dotted line
This is a timeline item with an info color and dotted line.
///

/// html | div.timeline.error.cross
### Error and dotted item
This is a timeline item with an error and a cross mark.
///

/// html | div.timeline.success
### Success item
This is a timeline item with a success color.
///


??? example ":simple-markdown: MarkDown"
    ```md
    /// html | div.timeline.dashed
    ### Dashed line
    This is a timeline item with a dashed line.
    ///

    /// html | div.timeline.check.light
    ### Checked item
    This is a timeline item with a check mark.
    ///

    /// html | div.timeline.info.dotted
    ### Info item with dotted line
    This is a timeline item with an info color and dotted line.
    ///

    /// html | div.timeline.error.cross
    ### Error and dotted item
    This is a timeline item with an error and a cross mark.
    ///

    /// html | div.timeline.success
    ### Success item
    This is a timeline item with a success color.
    ///
    ```


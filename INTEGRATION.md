# Caption integration with `pymdownx.blocks.caption` extension

[`pymdownx.blocks.caption`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/caption/) is a new extension that provides a Markdown syntax to generate `<figure>` with captions.

```
  - pymdownx.blocks.caption:
      auto: true
      types:
        - caption
        - name: figure-caption
          prefix: "Figure {}."
          classes: "glightbox-title"
        - name: "table-caption"
          prefix: "Table {}."
        - name: "attribution-caption"
          classes: "glightbox-attribution"
        - name: "description-caption"
          classes: "glightbox-description"
```

```
![Image](https://via.placeholder.com/150)
/// description-caption
Some description
///
/// figure-caption
Some caption
///
```

This will produce:

```html
<figure id="__figure-caption_2" class="glightbox-title">
<figure class="glightbox-description">
<p><a class="glightbox" href="https://via.placeholder.com/150" data-type="image" data-width="auto" data-height="auto" data-desc-position="bottom"><img alt="Image" src="https://via.placeholder.com/150"></a></p>
<figcaption>
<p>Some description</p>
</figcaption>
</figure>
<figcaption>
<p><span class="caption-prefix">Figure 2.</span> Some caption</p>
</figcaption>
</figure>
```

I see there's a [Caption]( https://blueswen.github.io/mkdocs-glightbox/caption/caption/) support in this plugin.

```md
![Madeira, Portugal](../images/gallery/blueswen-madeira.jpeg){ data-title="Madeira, Portugal." data-description="Madeira, an autonomous region of Portugal, is an archipelago comprising 4 islands off the northwest coast of Africa. - Google" }
```

Would it be possible to integrate this plugin captions with the `pymdownx.blocks.caption` extension?

This extension provides a way of setting classes to `<figure>` elements. Maybe a class naming convention (similar to `data-description`) could be used to extract the information from the `<figure>` elements, similar to [Advanced descrition](https://blueswen.github.io/mkdocs-glightbox/caption/caption/#advanced-description)

In the example before:

- `figure.glightbox-title > figcaption` content would be the title of the caption, equivalent to `data-title`.
- `figure.glightbox-description > figcaption` content would be the description of the caption, equivalent to `data-description`.

As a proposal, `attribution` could be added as another type of information in glightbox captions.

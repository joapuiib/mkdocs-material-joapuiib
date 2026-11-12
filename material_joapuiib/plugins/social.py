"""Social cards plugin using the bundled social-card layout.

Extends ``materialx/social`` so that listing only ``material-joapuiib/social``
in ``mkdocs.yml`` generates the cards, with the generalized layout shipped at
``material_joapuiib/templates/layouts/social.yml``. Accepts the same options
as ``materialx/social``; per-site overrides happen through
``extra.social_card.*`` (see the layout file for the full key list).

If the author has already pointed ``cards_layout_dir`` or ``cards_layout`` at
a non-default value, we leave it alone — the bundled layout is only a default.
"""
from __future__ import annotations

import os
from io import BytesIO

from material.plugins.social.plugin import SocialPlugin as _SocialPlugin
from mkdocs.config.defaults import MkDocsConfig


_LAYOUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
    "layouts",
)

_DEFAULT_LAYOUT_DIR = "layouts"
_DEFAULT_LAYOUT_NAME = "default"
_BUNDLED_LAYOUT_NAME = "social"


class SocialPlugin(_SocialPlugin):
    """``materialx/social`` defaulting to the bundled layout."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        if not self.config.cards_layout_dir or self.config.cards_layout_dir == _DEFAULT_LAYOUT_DIR:
            self.config.cards_layout_dir = _LAYOUT_DIR

        if self.config.cards_layout == _DEFAULT_LAYOUT_NAME:
            self.config.cards_layout = _BUNDLED_LAYOUT_NAME

        return super().on_config(config)

    def _render_icon(self, layer, input, config: MkDocsConfig):
        """Render stroke-based icons (Lucide) in the layer color.

        The parent class colors an icon by adding ``fill="..."`` to its root
        ``<svg>``. Lucide icons already declare ``fill="none"`` there and draw
        with ``stroke="currentColor"``, so the duplicated attribute breaks the
        SVG. For those icons, color the stroke instead.
        """
        icon = layer.icon
        if not icon.value or not icon.color:
            return super()._render_icon(layer, input, config)

        data = self._resolve_icon(icon.value, config)
        if 'stroke="currentColor"' not in data:
            return super()._render_icon(layer, input, config)

        from cairosvg import svg2png
        from material.plugins.social.plugin import _resize_contain
        from PIL import Image, ImageColor

        (r, g, b, *a) = ImageColor.getrgb(icon.color)
        opacity = a[0] / 255 if a else 1
        data = data.replace(
            'stroke="currentColor"', f'stroke="rgba({r}, {g}, {b}, {opacity})"'
        )

        image = Image.open(BytesIO(svg2png(data.encode("utf-8"), output_width=input.width)))
        input.alpha_composite(_resize_contain(image.convert("RGBA"), input))
        return input

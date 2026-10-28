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

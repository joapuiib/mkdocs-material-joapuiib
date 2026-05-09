"""Wire `materialx/social` to the bundled social-card layout.

When this plugin is listed in ``mkdocs.yml``, it locates the
``materialx/social`` plugin in the same config and rewrites its
``cards_layout_dir`` so the generalized layout shipped at
``material_joapuiib/templates/layouts/social.yml`` is picked up. Sites
opt in just by adding this plugin; per-site overrides happen through
``extra.social_card.*`` (see the layout file for the full key list).

If the author has already pointed ``cards_layout_dir`` at a non-default
directory, we leave it alone — this plugin is additive, not coercive.
"""
from __future__ import annotations

import os
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin


_LAYOUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
    "layouts",
)

_DEFAULT_LAYOUT_DIR = "layouts"
_DEFAULT_LAYOUT_NAME = "default"
_BUNDLED_LAYOUT_NAME = "social"


class SocialPlugin(BasePlugin):
    """Point ``materialx/social`` at the bundled layout directory."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        social = self._find_social_plugin(config)
        if social is None:
            return config

        current_dir = social.config.get("cards_layout_dir", _DEFAULT_LAYOUT_DIR)
        if current_dir == _DEFAULT_LAYOUT_DIR or not current_dir:
            social.config["cards_layout_dir"] = _LAYOUT_DIR

        current_layout = social.config.get("cards_layout", _DEFAULT_LAYOUT_NAME)
        if current_layout == _DEFAULT_LAYOUT_NAME:
            social.config["cards_layout"] = _BUNDLED_LAYOUT_NAME

        return config

    @staticmethod
    def _find_social_plugin(config: MkDocsConfig) -> Any | None:
        for name in ("materialx/social", "material/social"):
            plugin = config.plugins.get(name)
            if plugin is not None:
                return plugin
        return None

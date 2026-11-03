"""``/// access`` block: protect part of a page (see the access plugin).

The block only marks the section and carries its options; the
``material-joapuiib/access`` plugin encrypts it at build time. The extension is
registered automatically by the plugin.

    /// access
        allow: professors
        password: "1234"
        end: 2026-11-10T11:00

    Protected content.
    ///
"""
import json
import xml.etree.ElementTree as etree

from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_string

OPTION_KEYS = ("allow", "deny", "bypass", "password", "bypass_password", "start", "end")


class AccessSection(Block):
    NAME = "access"
    ARGUMENT = False
    OPTIONS = {key: ("", type_string) for key in OPTION_KEYS}

    def on_create(self, parent):
        options = {k: self.options[k] for k in OPTION_KEYS if self.options.get(k)}
        return etree.SubElement(parent, "div", {
            "class": "access-section",
            "data-access-section": json.dumps(options),
        })


class AccessSectionExtension(BlocksExtension):
    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(AccessSection, self.getConfigs())


def makeExtension(*args, **kwargs):
    return AccessSectionExtension(*args, **kwargs)

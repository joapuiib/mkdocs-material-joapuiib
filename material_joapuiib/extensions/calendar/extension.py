"""Python-Markdown / pymdownx.blocks extension entry point."""
from __future__ import annotations

from pymdownx.blocks import BlocksExtension

from .block import CalendarBlock


class CalendarExtension(BlocksExtension):
    """Register the `calendar` block with the pymdownx blocks manager.

    Configuration
    -------------
    locale:
        Default locale code applied to every calendar that does not specify
        one inline. Defaults to ``"en"``. Use ``"auto"`` to pick the locale
        from the current MkDocs page (set by the i18n plugin). Bundled codes
        are listed in :mod:`material_joapuiib.extensions.calendar.i18n`.
    """

    def __init__(self, *args, **kwargs):
        self.config = {
            "locale": [
                "en",
                "Default locale code (e.g. 'en', 'ca', 'es') or 'auto' to "
                "follow the MkDocs page locale.",
            ],
        }
        super().__init__(*args, **kwargs)

    def extendMarkdownBlocks(self, md, block_mgr) -> None:  # noqa: N802 (markdown API)
        block_mgr.register(CalendarBlock, self.getConfigs())


def makeExtension(*args, **kwargs) -> CalendarExtension:  # noqa: N802 (markdown API)
    return CalendarExtension(*args, **kwargs)

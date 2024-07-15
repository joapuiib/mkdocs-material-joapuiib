from mkdocs.plugins import BasePlugin

import typing
import logging

# Set up logging
log = logging.getLogger("mkdocs.material-joapuiib.plugins.publish")

class PublishPlugin(BasePlugin):
    """
    This plugin allows you to publish or unpublish pages by setting
    the `published` metadata key to `true` or `false`.

    If the `published` key is not set, the page is considered published.

    TODO: Remove the page from the navigation if it is not published.
    """

    def __init__(self):
        self.enabled = True

    def is_page_published(self, meta):
        if 'published' in meta:
            return meta['published'] == True
        return True

    def on_post_page(self, output, *, page, config):
        if not self.is_page_published(page.meta):
            return ''

        return output

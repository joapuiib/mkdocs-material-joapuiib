import os, logging, typing
from typing import Optional

from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Section
from mkdocs.structure.files import Files
from mkdocs.config.defaults import MkDocsConfig

class PublishPlugin(BasePlugin):
    log = logging.getLogger('mkdocs')

    def __init__(self):
        self.enabled = True
        self.is_building = False


    def on_startup(self, *, command: str, dirty: bool):
        self.is_building = command in ['build', 'gh-deploy']


    def is_page_published(self, meta: typing.Dict) -> bool:
        if 'publish' in meta:
            return meta['publish'] == True

        return True


    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        if not self.is_building and not self.is_page_published(page.meta):
            if page.meta.get('title'):
                page.meta["title"] = '[Unpublished] ' + page.meta["title"]

        return markdown


    def on_page_context(self, context: dict, page: Page, config: MkDocsConfig, nav: list) -> dict:
        published = self.is_page_published(page.meta)

        context_nav = context.get('nav')

        if context_nav and self.is_building:
            self.delete_unpublished_page_from_nav(context_nav)


    def delete_unpublished_page_from_nav(self, nav: list):
        for item in nav:
            if item.is_section:
                self.delete_unpublished_page_from_section(item)


    def delete_unpublished_page_from_section(self, section: Section):
        for item in section.children:
            if item.is_section:
                self.delete_unpublished_page_from_section(item)
            elif item.is_page:
                published = self.is_page_published(item.meta)
                if not published:
                    section.children.remove(item)


    def on_post_page(self, output: str, *, page: Page, config: MkDocsConfig) -> Optional[str]:
        if self.is_building and not self.is_page_published(page.meta):
            return ''

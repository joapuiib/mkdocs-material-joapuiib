import re

import markdown

from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.pages import _RawHTMLPreprocessor, _RelativePathTreeprocessor

log = get_plugin_logger("[slides]")


class SlidesPlugin(BasePlugin):
    """
    Pre-splits and renders `template: slides.html` pages through mkdocs' own
    markdown pipeline, one chunk per reveal.js section, so slide content gets
    the full set of configured markdown_extensions (admonitions, icons, ...)
    instead of reveal.js's bundled client-side markdown-it parser.
    """

    def on_page_markdown(self, markdown_text, page, config, files):
        if page.meta.get('template') != 'slides.html':
            return markdown_text

        page.slides = self._render_slides(markdown_text, page, config, files)
        return markdown_text

    def _render_slides(self, text, page, config, files):
        md = markdown.Markdown(
            extensions=config['markdown_extensions'],
            extension_configs=config['mdx_configs'] or {},
        )
        _RawHTMLPreprocessor()._register(md)
        _RelativePathTreeprocessor(page.file, files, config)._register(md)

        slides = []
        for horizontal_lines in self._split(text, '---'):
            vertical = []
            for vertical_lines in self._split('\n'.join(horizontal_lines), '--'):
                content_lines, note_lines = self._extract_notes(vertical_lines)

                md.reset()
                html = md.convert('\n'.join(content_lines).strip('\n'))

                if note_lines is not None:
                    md.reset()
                    notes_html = md.convert('\n'.join(note_lines).strip('\n'))
                    html += f'<aside class="notes">{notes_html}</aside>'

                vertical.append(html)
            slides.append(vertical)
        return slides

    @staticmethod
    def _extract_notes(lines):
        """
        Splits speaker notes off a slide's lines: everything from the first
        line starting with `Note:` to the end becomes the notes, everything
        before it stays as slide content. Returns (content_lines, note_lines),
        with note_lines being None when there is no `Note:` marker.
        """
        for i, line in enumerate(lines):
            if line.startswith('Note:'):
                note_lines = [line[len('Note:'):].lstrip()] + lines[i + 1:]
                return lines[:i], note_lines
        return lines, None

    _FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})')

    @classmethod
    def _split(cls, text, marker):
        """
        Splits `text` into groups of lines on any line whose stripped
        content is exactly `marker` (mirrors reveal.js's default
        data-separator behavior, applied before markdown conversion instead
        of after). Lines inside a fenced code block are never treated as a
        separator, so a slide can show `---`/`--` as a literal example.
        """
        groups = [[]]
        in_fence = False
        for line in text.replace('\r\n', '\n').split('\n'):
            if cls._FENCE_RE.match(line):
                in_fence = not in_fence
            if not in_fence and line.strip() == marker:
                groups.append([])
            else:
                groups[-1].append(line)
        return groups

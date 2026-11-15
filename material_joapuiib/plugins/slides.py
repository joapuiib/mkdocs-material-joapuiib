import re

import markdown
from markdown.extensions.toc import unique

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

        # md.reset() between slides also resets the toc extension's record of
        # used heading ids, so a heading repeated across slides would get the
        # same id on every slide, while the page TOC (built from the whole
        # page) numbers the repeats `_1`, `_2`... Track ids across slides so
        # both agree.
        used_ids = set()

        # Each slide as [content_html, notes_html or None], grouped in
        # vertical stacks. Notes are joined to the content at the end, so
        # `next_notes` can read the notes of the following slide first.
        slides = []
        for horizontal_lines in self._split(text, '---'):
            vertical = []
            for vertical_lines in self._split('\n'.join(horizontal_lines), '--'):
                content_lines, note_lines = self._extract_notes(vertical_lines)

                md.reset()
                html = md.convert('\n'.join(content_lines).strip('\n'))
                html = self._unique_heading_ids(html, used_ids)

                notes_html = None
                if note_lines is not None:
                    md.reset()
                    notes_html = md.convert('\n'.join(note_lines).strip('\n'))

                vertical.append([html, notes_html])
            slides.append(vertical)

        if page.meta.get('next_notes'):
            self._append_next_notes(slides)

        return [
            [
                html + (f'<aside class="notes">{notes}</aside>' if notes is not None else '')
                for html, notes in vertical
            ]
            for vertical in slides
        ]

    @staticmethod
    def _append_next_notes(slides):
        """
        Appends the notes of the next slide, faded and after a rule, to the
        notes of every slide, so the speaker view shows what comes next.
        "Next" follows the deck's linear order: down a vertical stack, then
        on to the first slide of the next stack. Slides whose next slide has
        no notes are left as they are. Styles are inline because reveal.js's
        speaker view copies the notes into its own window, without the
        page's stylesheets.
        """
        flat = [slide for vertical in slides for slide in vertical]
        own_notes = [notes for _, notes in flat]
        for slide, next_notes in zip(flat, own_notes[1:]):
            if next_notes is None:
                continue
            slide[1] = (
                (slide[1] or '')
                + '<hr><div style="opacity: 0.5;">'
                + '<p><strong>Next:</strong></p>'
                + next_notes
                + '</div>'
            )

    _HEADING_RE = re.compile(r'<h([1-6])\b[^>]*>.*?</h\1>', re.DOTALL)
    _HEADING_ID_RE = re.compile(r'^(<h[1-6]\b[^>]*\bid=")([^"]+)(")')

    @classmethod
    def _unique_heading_ids(cls, html, used_ids):
        """
        Renames the id of every heading in `html` that is already in
        `used_ids`, using the same `_1`, `_2`... suffixes as the toc
        extension, and points its permalink (`href="#id"`) to the new id.
        """
        def replace(match):
            heading = match.group(0)
            id_match = cls._HEADING_ID_RE.match(heading)
            if not id_match:
                return heading
            old_id = id_match.group(2)
            new_id = unique(old_id, used_ids)
            if new_id == old_id:
                return heading
            heading = cls._HEADING_ID_RE.sub(rf'\g<1>{new_id}\g<3>', heading, count=1)
            return heading.replace(f'href="#{old_id}"', f'href="#{new_id}"')

        return cls._HEADING_RE.sub(replace, html)

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

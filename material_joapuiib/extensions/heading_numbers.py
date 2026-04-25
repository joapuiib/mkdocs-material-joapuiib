"""Heading numbers Python-Markdown extension.

Prepends section numbers (1., 1.1., 1.1.1., ...) to heading elements.
Numbers appear in the TOC but can be excluded from anchors by configuring
the toc extension with the provided slugify_without_numbers function.
"""
import re
import xml.etree.ElementTree as etree

from markdown import Extension
from markdown.treeprocessors import Treeprocessor

HEADING_RE = re.compile(r'^h([1-6])$')
HEADING_NUMBER_RE = re.compile(r'^[\d]+(?:\.[\d]+)*\.\s+')


def slugify_without_numbers(value: str, separator: str, unicode: bool = False) -> str:
    """Slugify that strips heading number prefixes before creating the anchor."""
    from markdown.extensions.toc import slugify
    value = HEADING_NUMBER_RE.sub('', value)
    return slugify(value, separator, unicode)


class HeadingNumbersTreeprocessor(Treeprocessor):
    """Prepend section numbers to heading elements."""

    def __init__(self, md, config):
        super().__init__(md)
        self.start_level = config['start_level']

    def run(self, root):
        num_levels = 6 - self.start_level + 1
        counters = [0] * num_levels

        for el in root.iter():
            m = HEADING_RE.match(el.tag)
            if not m:
                continue
            level = int(m.group(1))
            if level < self.start_level:
                # Heading above start level resets all counters
                counters = [0] * num_levels
                continue

            idx = level - self.start_level
            counters[idx] += 1
            for i in range(idx + 1, num_levels):
                counters[i] = 0

            number = '.'.join(str(counters[i]) for i in range(idx + 1)) + '. '

            span = etree.Element('span')
            span.set('class', 'heading-number')
            span.text = number
            span.tail = el.text or ''
            el.text = None
            el.insert(0, span)

        return root


class HeadingNumbersExtension(Extension):
    """Heading numbers extension."""

    def __init__(self, **kwargs):
        self.config = {
            'start_level': [1, 'Starting heading level (1-6). Default: 1 (h1).'],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        processor = HeadingNumbersTreeprocessor(md, self.getConfigs())
        # Priority 10: run before toc (priority 5) so numbers appear in TOC entries
        md.treeprocessors.register(processor, 'heading_numbers', 10)
        md.registerExtension(self)


def makeExtension(**kwargs):
    return HeadingNumbersExtension(**kwargs)

import re
import os
from mkdocs.plugins import BasePlugin

class FunctionsPlugin(BasePlugin):
    RE = re.compile(r'^!([a-z_]+) ([^\n]+)')

    def on_page_markdown(self, markdown, page, config, files):
        new_markdown = []
        for line in markdown.split('\n'):
            match = self.RE.match(line)
            if match:
                function = match.group(1)
                args = match.group(2)
                args = self.parse_args(args)
                line = self.call_function(page, function, args)
            new_markdown.append(line)

        return '\n'.join(new_markdown)


    def parse_args(self, args):
        matches = re.findall(r'"([^"]*)"|(\S+)', args)
        return [match[0] or match[1] for match in matches]


    def call_function(self, page, function, args):
        """
        Checks if the function exists and calls it
        """
        if hasattr(self, function):
            function_config = self.config.get(function, {})
            return getattr(self, function)(page, function_config, args)
        return ''


    def load_file(self, page, config, paths):
        files_dir = config.get('files_dir', '')

        output = []

        for path in paths:
            filename = os.path.basename(path)
            language = os.path.splitext(filename)[1][1:]

            relative_path_from_docs = os.path.relpath(
                '.',
                os.path.dirname(page.file.src_uri)
            )

            relative_path = os.path.join(relative_path_from_docs, files_dir, path)
            absolute_path = os.path.join("docs", files_dir, path)

            template = (
                f'- [`{filename}`]({relative_path}){{download="{filename}"}}',
                f'/// collapse-code',
                f'```{language} title="{filename}"',
                f'--8<-- "{absolute_path}"',
                f'```',
                f'///',
            )
            template = '\n'.join(template) + '\n'
            output.append(template)

        return "\n".join(output)


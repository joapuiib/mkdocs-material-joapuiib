"""Snippets extension with filters.

Drop-in replacement for ``pymdownx.snippets`` that accepts a filter after a
``|`` inside the snippet string. The filter is applied to the selected snippet
content (whole file, section or line ranges) before nested snippets are
processed:

    --8<-- "includes/abbreviations.md | sed s/^\\*/* /"
    --8<-- "includes/abbreviations.md:abbr | sed s/^\\*/* /"
    --8<-- "includes/abbreviations.md:3:10 | sed s/^\\*/* /"

In whole-file mode, filters also see the ``--8<-- [start:x]``/``[end:x]``
section marker lines; they are removed afterwards, as usual.

Filters can be chained; each one receives the output of the previous one:

    --8<-- "includes/abbreviations.md:abbr | sed /^$/d | sed s/^\\*/* /"

A ``|`` only separates filters when it has whitespace on both sides (the first
``|`` after the path always does). A ``|`` without surrounding spaces is part of
the arguments, so ``sed s|a|b|`` or ``sed s/x|y/z/`` work as expected. To match
`` | `` inside a regex, write it as `` [|] ``.

The first word of each filter is its name; the rest is passed to it as
``args`` (a raw string, without surrounding whitespace). A filter is a
function::

    def my_filter(lines: list[str], args: str) -> list[str]: ...

Register filters with the ``filters`` option (``sed`` is built in and can be
overridden):

    markdown_extensions:
      - material_joapuiib.extensions.snippets:
          filters:
            upper: !!python/name:my_module.upper

The built-in ``sed`` filter supports these commands (separated by ``;`` or
newlines):

* ``[addr]s/regex/replacement/[flags]``: substitution. Flags: ``g`` (all
  occurrences), ``i``/``I`` (ignore case), ``N`` (only the Nth occurrence,
  or the Nth and following ones together with ``g``). Any delimiter can be
  used (``s|a|b|``).
* ``[addr]d``: delete the line.

``addr`` is an optional ``/regex/`` (or ``\\cregexc``) restricting the command
to matching lines; append ``!`` to negate it.

Regular expressions use Python syntax (``re`` module), not POSIX BRE: escape
``*``, ``+``, ``?``, ``(``... when you mean them literally. In replacements,
``&`` is the whole match, ``\\1``..``\\9`` are groups and ``\\n`` is a newline.

Only the sed subset above is implemented in Python; no external command is
ever executed.

The extension overrides ``SnippetPreprocessor.parse_snippet_target`` (to split
off the filters) and ``SnippetPreprocessor.process_snippet_lines`` (to apply
them). These extension points are not in a pymdown-extensions release yet
(see facelessuser/pymdown-extensions#2726); a clear error is raised if they
are missing.
"""
import re

from pymdownx.snippets import SnippetExtension, SnippetPreprocessor


class SnippetFilterError(Exception):
    """Invalid snippet filter script."""


# --------------------------------------------------------------------------
# sed subset
# --------------------------------------------------------------------------

def _read_delimited(script, i, delim):
    """Read until an unescaped ``delim``. Return (raw_text, index_after_delim)."""
    out = []
    n = len(script)
    while i < n:
        c = script[i]
        if c == '\\' and i + 1 < n:
            out.append(script[i:i + 2])
            i += 2
            continue
        if c == delim:
            return ''.join(out), i + 1
        out.append(c)
        i += 1
    raise SnippetFilterError(f"Unterminated expression (missing '{delim}') in filter: {script!r}")


def _regex(raw, delim, flags, script):
    """Compile a sed regex, turning ``\\<delim>`` into a literal delimiter."""
    out = []
    i = 0
    while i < len(raw):
        if raw[i] == '\\' and i + 1 < len(raw):
            out.append(re.escape(delim) if raw[i + 1] == delim else raw[i:i + 2])
            i += 2
        else:
            out.append(raw[i])
            i += 1
    pattern = ''.join(out)
    if not pattern:
        raise SnippetFilterError(f"Empty regular expression in filter: {script!r}")
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        raise SnippetFilterError(f"Invalid regular expression {pattern!r} in filter {script!r}: {e}") from e


def _template(raw, delim):
    """Convert a sed replacement into a Python ``re`` template."""
    out = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == '\\' and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt == delim or nxt == '&':
                out.append(nxt)
            else:
                out.append(raw[i:i + 2])
            i += 2
        elif c == '&':
            out.append(r'\g<0>')
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def parse_sed(script):
    """Parse a sed-like script into a list of commands."""

    commands = []
    n = len(script)
    i = 0
    while True:
        while i < n and script[i] in ' \t\n;':
            i += 1
        if i >= n:
            break

        # Optional address
        address = None
        negate = False
        if script[i] == '/' or (script[i] == '\\' and i + 1 < n):
            if script[i] == '\\':
                delim = script[i + 1]
                i += 2
            else:
                delim = '/'
                i += 1
            raw, i = _read_delimited(script, i, delim)
            address = _regex(raw, delim, 0, script)
            while i < n and script[i] in ' \t':
                i += 1
            if i < n and script[i] == '!':
                negate = True
                i += 1
            while i < n and script[i] in ' \t':
                i += 1

        if i >= n:
            raise SnippetFilterError(f"Missing command after address in filter: {script!r}")

        cmd = script[i]
        i += 1
        if cmd == 'd':
            commands.append({'cmd': 'd', 'address': address, 'negate': negate})

        elif cmd == 's':
            if i >= n or script[i] in '\\\n':
                raise SnippetFilterError(f"Invalid delimiter for 's' in filter: {script!r}")
            delim = script[i]
            raw_re, i = _read_delimited(script, i + 1, delim)
            raw_repl, i = _read_delimited(script, i, delim)

            global_ = False
            re_flags = 0
            digits = ''
            while i < n and script[i] not in ' \t\n;':
                f = script[i]
                if f == 'g':
                    global_ = True
                elif f in 'iI':
                    re_flags |= re.IGNORECASE
                elif f.isdigit():
                    digits += f
                else:
                    raise SnippetFilterError(f"Unknown flag '{f}' for 's' in filter: {script!r}")
                i += 1
            nth = int(digits) if digits else 1
            if nth < 1:
                raise SnippetFilterError(f"Occurrence number must be >= 1 in filter: {script!r}")

            commands.append({
                'cmd': 's',
                'address': address,
                'negate': negate,
                'regex': _regex(raw_re, delim, re_flags, script),
                'template': _template(raw_repl, delim),
                'global': global_,
                'nth': nth,
            })

        else:
            raise SnippetFilterError(f"Unsupported command '{cmd}' in filter: {script!r}")

    if not commands:
        raise SnippetFilterError(f"Empty filter: {script!r}")
    return commands


def _substitute(command, line, script):
    """Apply an ``s`` command to a single line."""

    count = 0
    nth = command['nth']
    global_ = command['global']

    def repl(m):
        nonlocal count
        count += 1
        if count == nth or (global_ and count > nth):
            return m.expand(command['template'])
        return m.group(0)

    try:
        return command['regex'].sub(repl, line)
    except (re.error, IndexError) as e:
        raise SnippetFilterError(f"Invalid replacement in filter {script!r}: {e}") from e


def apply_sed(script, lines):
    """Apply a sed-like script to a list of lines."""

    commands = parse_sed(script)
    result = []
    for line in lines:
        # A substitution may introduce newlines: keep working on a list.
        current = [line]
        for command in commands:
            next_lines = []
            for item in current:
                address = command['address']
                selected = address is None or (address.search(item) is not None) != command['negate']
                if not selected:
                    next_lines.append(item)
                elif command['cmd'] == 'd':
                    continue
                else:
                    next_lines.extend(_substitute(command, item, script).split('\n'))
            current = next_lines
            if not current:
                break
        result.extend(current)
    return result


def sed_filter(lines, args):
    """Built-in ``sed`` filter."""

    return apply_sed(args, lines)


BUILTIN_FILTERS = {
    'sed': sed_filter,
}

RE_FILTER = re.compile(r'(?s)^[ \t]*(?P<name>[A-Za-z_][-\w]*)(?:[ \t]+(?P<args>.*))?$')

# Separator between chained filters: a pipe with whitespace on both sides.
RE_FILTER_SEPARATOR = re.compile(r'[ \t]+\|[ \t]+')


# --------------------------------------------------------------------------
# Snippets integration
# --------------------------------------------------------------------------

def _check_pymdownx():
    """Fail clearly if pymdown-extensions lacks the snippet extension points."""

    missing = [
        name for name in ('parse_snippet_target', 'process_snippet_lines')
        if not hasattr(SnippetPreprocessor, name)
    ]
    if missing:
        raise RuntimeError(
            "material_joapuiib.extensions.snippets requires a pymdown-extensions version whose "
            f"SnippetPreprocessor provides: {', '.join(missing)}"
        )


class FilteringSnippetPreprocessor(SnippetPreprocessor):
    """Snippet preprocessor that applies filters."""

    def __init__(self, config, md):
        _check_pymdownx()
        super().__init__(config, md)
        self.filter_funcs = dict(BUILTIN_FILTERS)
        for name, func in (config.get('filters') or {}).items():
            if not callable(func):
                raise SnippetFilterError(f"Snippet filter '{name}' is not callable: {func!r}")
            self.filter_funcs[name] = func

    def parse_filters(self, spec, path):
        """Parse ``name args | name args | ...`` into ``[(name, args), ...]``."""

        chain = []
        # Pad with spaces so a leading or trailing ``|`` produces an empty (invalid) filter.
        for part in RE_FILTER_SEPARATOR.split(' ' + spec.strip() + ' '):
            m = RE_FILTER.match(part.strip())
            if m is None:
                raise SnippetFilterError(f"Invalid filter {part.strip()!r} (expected 'name args') in snippet: {path!r}")
            name = m.group('name')
            args = (m.group('args') or '').strip()
            if name not in self.filter_funcs:
                raise SnippetFilterError(
                    f"Unknown snippet filter '{name}' in {path!r} "
                    f"(available: {', '.join(sorted(self.filter_funcs))})"
                )
            if self.filter_funcs[name] is sed_filter:
                parse_sed(args)  # Fail early on invalid scripts
            chain.append((name, args))
        return chain

    def parse_snippet_target(self, path):
        """Split off the ``| filters`` suffix before upstream parses the path."""

        target_path, sep, spec = path.partition('|')
        target = super().parse_snippet_target(target_path.strip())
        if target is not None:
            target['filters'] = self.parse_filters(spec, path) if sep else []
        return target

    def process_snippet_lines(self, lines, target):
        """Apply the filter chain to the selected lines."""

        lines = super().process_snippet_lines(lines, target)
        for name, args in target.get('filters', ()):
            lines = self.filter_funcs[name](list(lines), args)
            if not isinstance(lines, list) or not all(isinstance(item, str) for item in lines):
                raise SnippetFilterError(f"Snippet filter '{name}' must return a list of strings")
        return lines


class FilteringSnippetExtension(SnippetExtension):
    """Snippets extension with filters."""

    def __init__(self, *args, **kwargs):
        filters = kwargs.pop('filters', {})
        super().__init__(*args, **kwargs)
        self.config['filters'] = [
            {},
            "Extra snippet filters as {name: callable(lines, args) -> lines} - Default: {}"
        ]
        self.setConfig('filters', filters)

    def extendMarkdown(self, md):
        self.md = md
        md.registerExtension(self)
        snippet = FilteringSnippetPreprocessor(self.getConfigs(), md)
        md.preprocessors.register(snippet, "snippet", 32)


def makeExtension(*args, **kwargs):
    return FilteringSnippetExtension(*args, **kwargs)

"""Access control for MkDocs: passwords, users, groups and time windows.

Content is encrypted at build time and decrypted in the browser
(see ``templates/javascript/access.js``). Time windows are soft: they are
enforced by the visitor's clock, not cryptographically.
"""
from __future__ import annotations

import html
import json
import logging
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import material
import yaml
from mkdocs import plugins
from mkdocs.config import base
from mkdocs.config import config_options as opt
from mkdocs.exceptions import PluginError
from mkdocs.structure.toc import TableOfContents

from . import crypto
from . import sections
from .rules import (
    AccessConfigError, Directory, PageAccess, NAV_MODES,
    normalize_username, parse_rules, resolve, resolve_section,
)
from .strings import DEFAULT_STRINGS

_ICONS = {"start": "clock", "end": "flag"}


def _load_icons() -> dict[str, str]:
    base_dir = Path(material.__file__).parent / "templates" / ".icons" / "lucide"
    return {k: (base_dir / f"{v}.svg").read_text(encoding="utf-8").strip()
            for k, v in _ICONS.items()}

log = logging.getLogger("mkdocs.plugins.material-joapuiib.access")

EXCLUDABLE = ("search", "social")
SECTION_EXTENSION = "material_joapuiib.extensions.access_section"


class AccessConfig(base.Config):
    enabled = opt.Type(bool, default=True)
    salt = opt.Type(str, default="")
    timezone = opt.Type(str, default="UTC")
    iterations = opt.Type(int, default=600_000)
    serve_iterations = opt.Type(int, default=1_000)
    serve = opt.Choice(("reveal", "gate"), default="reveal")
    users = opt.Type(dict, default={})
    users_file = opt.Optional(opt.Type(str))
    groups = opt.Type(dict, default={})
    rules = opt.Type(list, default=[])
    nav = opt.Choice(NAV_MODES, default="lock")
    exclude = opt.ListOfItems(opt.Choice(EXCLUDABLE), default=["search", "social"])
    remember_days = opt.Type(int, default=30)
    share_links = opt.Type(bool, default=True)
    strings = opt.Type(dict, default={})


def _prune_toc(items, hidden: set[str]) -> list:
    """Drop TOC entries (not their other children) whose anchor is hidden."""
    kept = []
    for item in items:
        children = _prune_toc(item.children, hidden)
        if item.id in hidden:
            kept.extend(children)
        else:
            item.children = children
            kept.append(item)
    return kept


class AccessPlugin(plugins.BasePlugin[AccessConfig]):

    def __init__(self):
        self.serving = False
        self.dirty = False
        self.grants: dict[str, dict[str, tuple[bytes, bool]]] = {}
        self.protected_count = 0

    # ------------------------------------------------------------------ setup

    def on_startup(self, *, command, dirty):
        self.serving = command == "serve"
        self.dirty = dirty

    def on_config(self, config):
        if not self.config.enabled:
            return config
        try:
            self._setup(config)
        except AccessConfigError as exc:
            raise PluginError(f"access: {exc}") from exc
        if SECTION_EXTENSION not in config.markdown_extensions:
            config.markdown_extensions.append(SECTION_EXTENSION)
        return config

    def _setup(self, config) -> None:
        cfg = self.config
        users = dict(cfg.users)
        if cfg.users_file:
            path = Path(config.config_file_path).parent / cfg.users_file
            with open(path, encoding="utf-8") as fh:
                users.update(yaml.safe_load(fh) or {})

        self.directory = Directory.build(users, cfg.groups)
        self.rules = parse_rules(cfg.rules)
        try:
            self.tz = ZoneInfo(cfg.timezone)
        except Exception as exc:
            raise AccessConfigError(f"unknown timezone {cfg.timezone!r}") from exc

        self.site_salt = cfg.salt or config.site_name
        self.iterations = cfg.serve_iterations if self.serving else cfg.iterations
        self.reveal = self.serving and cfg.serve == "reveal"
        salt_user = crypto.make_salt(self.site_salt, "user")
        self.salt_pw = crypto.make_salt(self.site_salt, "pw")
        self.user_keys = {
            name: crypto.derive_key(
                crypto.user_secret(name, password), salt_user, self.iterations)
            for name, password in self.directory.passwords.items()
        }
        self._pw_keys: dict[str, bytes] = {}

        config.extra["access"] = {
            "iterations": self.iterations,
            "salt": self.site_salt,
            "timezone": cfg.timezone,
            "saltUser": crypto.b64(salt_user),
            "saltPw": crypto.b64(self.salt_pw),
            "users": bool(self.directory.passwords),
            "rememberDays": cfg.remember_days,
            "share": cfg.share_links,
            "dev": self.serving,
            "reveal": self.reveal,
            "strings": {**DEFAULT_STRINGS, **cfg.strings},
            "icons": _load_icons(),
        }

    def _pw_key(self, password: str) -> bytes:
        if password not in self._pw_keys:
            self._pw_keys[password] = crypto.derive_key(
                password, self.salt_pw, self.iterations)
        return self._pw_keys[password]

    # ------------------------------------------------------------------ build

    def on_pre_build(self, *, config):
        if not self.config.enabled:
            return
        if not self.dirty:
            self.grants.clear()
        self.protected_count = 0

    def on_files(self, files, *, config):
        """Drop ``author`` pages (matched by config rules) from real builds."""
        if not self.config.enabled or self.serving:
            return files
        for file in list(files.documentation_pages()):
            try:
                access = resolve(
                    self.directory, self.rules, file.src_uri, None, self.tz)
            except AccessConfigError:
                continue  # reported properly when the page is processed
            if access.author:
                files.remove(file)
        return files

    def on_page_markdown(self, markdown, *, page, config, files):
        if not self.config.enabled:
            return markdown
        try:
            access = resolve(
                self.directory, self.rules, page.file.src_uri,
                page.meta.get("access"), self.tz)
        except AccessConfigError as exc:
            raise PluginError(f"access: {exc}") from exc

        access.nav = access.nav or self.config.nav
        page.access = access
        if access.protected:
            for what in self.config.exclude:
                if what == "search":
                    page.meta["search"] = {
                        **(page.meta.get("search") or {}), "exclude": True}
                elif what == "social":
                    page.meta["social"] = {
                        **(page.meta.get("social") or {}), "cards": False}
        return markdown

    @plugins.event_priority(-100)
    def on_page_content(self, content, *, page, config, files):
        if not self.config.enabled:
            return content
        strings = {**DEFAULT_STRINGS, **self.config.strings}
        uri = page.file.src_uri

        # Sections first: their headings must not leak into the TOC.
        hidden_ids: set[str] = set()
        counter = iter(range(1, 10_000))

        def protect_section(inner: str, options: dict) -> str:
            n = next(counter)
            where = f"{uri} (section {n})"
            try:
                access = resolve_section(self.directory, options, self.tz, where)
            except AccessConfigError as exc:
                raise PluginError(f"access: {exc}") from exc
            hidden_ids.update(sections.heading_ids(inner))
            self.protected_count += 1
            pid = crypto.page_id(self.site_salt, f"{uri}#{n}")
            return self._container(inner, access, pid, strings, kind="section")

        try:
            content = sections.transform(content, protect_section)
        except ValueError as exc:
            raise PluginError(f"access: {uri}: {exc}") from exc
        if hidden_ids:
            page.toc = TableOfContents(_prune_toc(page.toc.items, hidden_ids))

        access = getattr(page, "access", None)
        if access is None or not access.protected:
            return content

        self.protected_count += 1
        page.toc = TableOfContents([])
        pid = crypto.page_id(self.site_salt, uri)

        if access.author and not self.serving:
            self.grants.pop(pid, None)
            body = html.escape(strings["author_only"])
            return (f'<div class="access access--author">'
                    f'<h1>{html.escape(page.title or "")}</h1><p>{body}</p></div>')
        return self._container(content, access, pid, strings, title=page.title or "")

    def _container(self, content: str, access: PageAccess, pid: str,
                   strings: dict, title: str | None = None,
                   kind: str = "page") -> str:
        """Encrypt ``content`` and return the placeholder markup."""
        cek = crypto.new_key()
        payload = {
            "v": 1,
            "c": crypto.b64(crypto.encrypt(cek, content.encode("utf-8"))),
            "w": [],
        }
        for pw in access.passwords:
            wrapped = crypto.encrypt(self._pw_key(pw), cek)
            payload["w"].append({"w": crypto.b64(wrapped), "b": 0})
        for pw in access.bypass_passwords:
            wrapped = crypto.encrypt(self._pw_key(pw), cek)
            payload["w"].append({"w": crypto.b64(wrapped), "b": 1})
        if access.open:
            payload["o"] = crypto.b64(cek)

        self.grants[pid] = {
            user: (cek, bypass) for user, bypass in access.users.items()}

        attrs = {
            "data-access-page": pid,
            # Not a <script>: instant navigation runs again every script in the
            # container, keeping only its text, so JSON would run as JavaScript.
            "data-access-payload": json.dumps(payload, separators=(",", ":")),
            "data-access-kind": kind if kind != "page" else None,
            "data-access-users": "1" if access.users else None,
            "data-access-pw": "1" if payload["w"] else None,
            "data-access-start": access.start.isoformat() if access.start else None,
            "data-access-end": access.end.isoformat() if access.end else None,
            "data-access-dev": crypto.b64(cek) if self.serving else None,
            "data-access-author": "1" if access.author else None,
        }
        attr_html = " ".join(
            f'{k}="{html.escape(v)}"' for k, v in attrs.items() if v)
        classes = "access" + (" access--section" if kind == "section" else "")
        heading = f"<h1>{html.escape(title)}</h1>" if title is not None else ""
        return (
            f'<div class="{classes}" {attr_html}>'
            f'<div class="access__locked">{heading}'
            f'<div class="access__ui"></div>'
            f'<noscript><p>{html.escape(strings["no_js"])}</p></noscript></div>'
            f'<div class="access__content" hidden></div>'
            f'</div>'
        )

    def on_post_build(self, *, config):
        if not self.config.enabled:
            return
        out = Path(config.site_dir) / "access" / "keyrings"
        out.mkdir(parents=True, exist_ok=True)
        for name, key in self.user_keys.items():
            pages = {
                pid: {"k": crypto.b64(cek), "b": int(bypass)}
                for pid, users in self.grants.items()
                for user, (cek, bypass) in users.items()
                if user == name
            }
            keyring = {
                "v": 1,
                "user": name,
                "groups": sorted(self.directory.user_groups[name]),
                "pages": pages,
            }
            blob = crypto.encrypt(key, json.dumps(keyring).encode("utf-8"))
            uid = crypto.user_id(self.site_salt, name)
            (out / f"{uid}.bin").write_bytes(blob)

        if self.serving:
            dev = {
                "users": {
                    name: {
                        "key": crypto.b64(key),
                        "groups": sorted(self.directory.user_groups[name]),
                    }
                    for name, key in self.user_keys.items()
                },
            }
            (out.parent / "dev.json").write_text(json.dumps(dev), encoding="utf-8")
        log.info("access: %d protected page(s), %d user(s)",
                 self.protected_count, len(self.user_keys))

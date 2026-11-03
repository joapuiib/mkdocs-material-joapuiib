"""Pure access-rule resolution: users, groups, patterns, time windows.

No crypto and no MkDocs types here, so everything is unit-testable.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

import pathspec

ALL_USERS = "*"
NAV_MODES = ("show", "lock", "hide")


class AccessConfigError(Exception):
    """Invalid access configuration."""


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def normalize_username(name: str) -> str:
    return str(name).strip().lower()


def parse_datetime(value, tz: ZoneInfo) -> dt.datetime | None:
    """Return an aware datetime. Naive values are read in ``tz``."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        result = value
    elif isinstance(value, dt.date):
        result = dt.datetime(value.year, value.month, value.day)
    else:
        try:
            result = dt.datetime.fromisoformat(str(value).strip())
        except ValueError as exc:
            raise AccessConfigError(f"invalid datetime {value!r}") from exc
    if result.tzinfo is None:
        result = result.replace(tzinfo=tz)
    return result


# --------------------------------------------------------------------------
# Users and groups
# --------------------------------------------------------------------------

@dataclass
class Directory:
    """Users and their effective groups (after inheritance)."""

    passwords: dict[str, str] = field(default_factory=dict)
    user_groups: dict[str, set[str]] = field(default_factory=dict)
    group_names: set[str] = field(default_factory=set)

    @classmethod
    def build(cls, users: dict | None, groups: dict | None) -> "Directory":
        users = users or {}
        groups = groups or {}

        group_names = {normalize_username(g) for g in groups}
        parents: dict[str, list[str]] = {}
        for name, spec in groups.items():
            spec = spec or {}
            parents[normalize_username(name)] = [
                normalize_username(p) for p in _as_list(spec.get("inherits"))
            ]
        for name, plist in parents.items():
            for parent in plist:
                if parent not in group_names:
                    raise AccessConfigError(
                        f"group {name!r} inherits unknown group {parent!r}")

        closure: dict[str, set[str]] = {}

        def expand(group: str, stack: tuple[str, ...]) -> set[str]:
            if group in closure:
                return closure[group]
            if group in stack:
                cycle = " -> ".join(stack + (group,))
                raise AccessConfigError(f"group inheritance cycle: {cycle}")
            result = {group}
            for parent in parents.get(group, []):
                result |= expand(parent, stack + (group,))
            closure[group] = result
            return result

        for group in group_names:
            expand(group, ())

        directory = cls(group_names=group_names)
        for raw_name, spec in users.items():
            name = normalize_username(raw_name)
            spec = spec or {}
            if name in directory.passwords:
                raise AccessConfigError(f"duplicate user {name!r}")
            if name in group_names:
                raise AccessConfigError(
                    f"{name!r} is both a user and a group")
            if name == ALL_USERS:
                raise AccessConfigError(f"{ALL_USERS!r} is reserved")
            password = spec.get("password")
            if password is None or str(password) == "":
                raise AccessConfigError(f"user {name!r} has no password")
            directory.passwords[name] = str(password)
            effective: set[str] = set()
            for group in _as_list(spec.get("groups")):
                group = normalize_username(group)
                if group not in group_names:
                    raise AccessConfigError(
                        f"user {name!r} is in unknown group {group!r}")
                effective |= closure[group]
            directory.user_groups[name] = effective
        return directory

    @property
    def users(self) -> list[str]:
        return sorted(self.passwords)

    def expand(self, principals) -> set[str]:
        """Resolve user/group names (and ``*``) to a set of usernames."""
        result: set[str] = set()
        for raw in _as_list(principals):
            name = normalize_username(raw)
            if name == ALL_USERS:
                result |= set(self.passwords)
            elif name in self.passwords:
                result.add(name)
            elif name in self.group_names:
                result |= {u for u, g in self.user_groups.items() if name in g}
            else:
                raise AccessConfigError(f"unknown user or group {raw!r}")
        return result


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

RULE_KEYS = {
    "allow", "deny", "bypass", "password", "bypass_password",
    "start", "end", "nav", "author",
}


@dataclass
class Rule:
    spec: pathspec.GitIgnoreSpec
    options: dict


def parse_rules(rules: list | None) -> list[Rule]:
    parsed = []
    for i, raw in enumerate(rules or []):
        if not isinstance(raw, dict) or "pattern" not in raw:
            raise AccessConfigError(f"rule #{i + 1} needs a 'pattern'")
        unknown = set(raw) - RULE_KEYS - {"pattern"}
        if unknown:
            raise AccessConfigError(
                f"rule #{i + 1}: unknown keys {sorted(unknown)}")
        patterns = [str(p) for p in _as_list(raw["pattern"])]
        spec = pathspec.GitIgnoreSpec.from_lines(patterns)
        parsed.append(Rule(spec, {k: v for k, v in raw.items() if k != "pattern"}))
    return parsed


@dataclass
class PageAccess:
    """Resolved access for one page."""

    users: dict[str, bool] = field(default_factory=dict)  # name -> bypass
    passwords: list[str] = field(default_factory=list)
    bypass_passwords: list[str] = field(default_factory=list)
    start: dt.datetime | None = None
    end: dt.datetime | None = None
    nav: str | None = None
    author: bool = False
    has_deny: bool = False
    restricted: bool = False  # some allow/bypass/password was requested

    @property
    def windowed(self) -> bool:
        return self.start is not None or self.end is not None

    @property
    def protected(self) -> bool:
        return self.restricted or self.windowed or self.author

    @property
    def open(self) -> bool:
        """Time-window only: nobody to authenticate, the clock is the gate."""
        return self.windowed and not self.restricted and not self.author


def _apply(access: PageAccess, directory: Directory, options: dict,
           tz: ZoneInfo, where: str) -> None:
    allow = directory.expand(options.get("allow"))
    bypass = directory.expand(options.get("bypass"))
    deny = directory.expand(options.get("deny"))

    for user in allow:
        access.users.setdefault(user, False)
    for user in bypass:
        access.users[user] = True  # bypass implies allow
    for user in deny:
        access.users.pop(user, None)

    if "deny" in options:
        access.has_deny = True
    if any(options.get(k) for k in ("allow", "bypass", "password", "bypass_password")):
        access.restricted = True

    for pw in _as_list(options.get("password")):
        if str(pw) not in access.passwords:
            access.passwords.append(str(pw))
    for pw in _as_list(options.get("bypass_password")):
        if str(pw) not in access.bypass_passwords:
            access.bypass_passwords.append(str(pw))

    if "start" in options:
        access.start = parse_datetime(options["start"], tz)
    if "end" in options:
        access.end = parse_datetime(options["end"], tz)
    if "nav" in options:
        if options["nav"] not in NAV_MODES:
            raise AccessConfigError(
                f"{where}: nav must be one of {NAV_MODES}")
        access.nav = options["nav"]
    if "author" in options:
        access.author = bool(options["author"])


def resolve(directory: Directory, rules: list[Rule], src_uri: str,
            page_access: dict | None, tz: ZoneInfo) -> PageAccess:
    """Resolve access for ``src_uri``: config rules in order, then front matter."""
    access = PageAccess()
    for rule in rules:
        if rule.spec.match_file(src_uri):
            _apply(access, directory, rule.options, tz, f"rule for {src_uri}")
    if page_access:
        unknown = set(page_access) - RULE_KEYS
        if unknown:
            raise AccessConfigError(
                f"{src_uri}: unknown access keys {sorted(unknown)}")
        _apply(access, directory, page_access, tz, src_uri)

    if access.start and access.end and access.end <= access.start:
        raise AccessConfigError(f"{src_uri}: 'end' must be after 'start'")
    if access.has_deny and not access.restricted:
        raise AccessConfigError(
            f"{src_uri}: 'deny' needs an 'allow', 'bypass' or 'password' "
            "on the same page")
    return access


SECTION_KEYS = RULE_KEYS - {"nav", "author"}


def resolve_section(directory: Directory, options: dict, tz: ZoneInfo,
                    where: str) -> PageAccess:
    """Access for a ``/// access`` section: only its own options apply."""
    unknown = set(options) - SECTION_KEYS
    if unknown:
        raise AccessConfigError(
            f"{where}: unknown section options {sorted(unknown)}")
    access = PageAccess()
    _apply(access, directory, options, tz, where)
    if not access.protected:
        raise AccessConfigError(f"{where}: access section without options")
    if access.start and access.end and access.end <= access.start:
        raise AccessConfigError(f"{where}: 'end' must be after 'start'")
    if access.has_deny and not access.restricted:
        raise AccessConfigError(
            f"{where}: 'deny' needs an 'allow', 'bypass' or 'password'")
    return access

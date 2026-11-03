import datetime as dt
from zoneinfo import ZoneInfo

import pytest

from material_joapuiib.plugins.access.rules import (
    AccessConfigError, Directory, parse_rules, resolve,
)

TZ = ZoneInfo("Europe/Madrid")

USERS = {
    "alice": {"password": "a", "groups": ["teachers"]},
    "bob": {"password": "b", "groups": ["dam1"]},
    "carol": {"password": "c", "groups": ["dam1"]},
}
GROUPS = {"teachers": {}, "students": {}, "dam1": {"inherits": ["students"]}}


def directory():
    return Directory.build(USERS, GROUPS)


def run(rules, uri="a/b.md", front=None):
    return resolve(directory(), parse_rules(rules), uri, front, TZ)


def test_group_inheritance():
    d = directory()
    assert d.user_groups["bob"] == {"dam1", "students"}
    assert d.expand("students") == {"bob", "carol"}


def test_inheritance_cycle():
    with pytest.raises(AccessConfigError, match="cycle"):
        Directory.build({}, {"a": {"inherits": ["b"]}, "b": {"inherits": ["a"]}})


def test_unknown_principal():
    with pytest.raises(AccessConfigError, match="unknown"):
        run([{"pattern": "**", "allow": ["nobody"]}])


def test_allow_group_and_user():
    r = run([{"pattern": "a/**", "allow": ["teachers", "bob"]}])
    assert r.users == {"alice": False, "bob": False}
    assert r.protected


def test_unmatched_page_is_public():
    r = run([{"pattern": "other/**", "allow": ["teachers"]}])
    assert not r.protected


def test_deny_removes_and_later_allow_restores():
    rules = [
        {"pattern": "**", "allow": ["dam1"]},
        {"pattern": "a/**", "deny": ["bob"]},
    ]
    assert set(run(rules).users) == {"carol"}
    rules.append({"pattern": "a/b.md", "allow": ["bob"]})
    assert set(run(rules).users) == {"bob", "carol"}


def test_deny_everyone_stays_protected():
    r = run([{"pattern": "**", "allow": ["dam1"]},
             {"pattern": "**", "deny": ["dam1"]}])
    assert r.users == {} and r.protected


def test_deny_without_allow_is_error():
    with pytest.raises(AccessConfigError, match="deny"):
        run([{"pattern": "**", "deny": ["bob"]}])


def test_bypass_implies_allow_and_deny_wins_after():
    r = run([{"pattern": "**", "bypass": ["teachers"]}])
    assert r.users == {"alice": True}
    r = run([{"pattern": "**", "bypass": ["teachers"]},
             {"pattern": "**", "deny": ["alice"]}])
    assert r.users == {}


def test_all_users_wildcard():
    assert set(run([{"pattern": "**", "allow": ["*"]}]).users) == {
        "alice", "bob", "carol"}


def test_front_matter_adds_to_rules():
    r = run([{"pattern": "**", "allow": ["teachers"]}],
            front={"password": "x", "allow": ["bob"]})
    assert r.passwords == ["x"]
    assert set(r.users) == {"alice", "bob"}


def test_window_only_is_open():
    r = run([{"pattern": "**", "start": "2026-11-10T09:00:00"}])
    assert r.open and r.protected
    assert r.start == dt.datetime(2026, 11, 10, 9, tzinfo=TZ)


def test_window_with_password_is_not_open():
    r = run([{"pattern": "**", "password": "x", "end": dt.datetime(2026, 1, 1)}])
    assert not r.open and r.windowed


def test_end_before_start():
    with pytest.raises(AccessConfigError, match="after"):
        run([{"pattern": "**", "password": "x",
              "start": "2026-02-01T00:00", "end": "2026-01-01T00:00"}])


def test_unknown_rule_key():
    with pytest.raises(AccessConfigError, match="unknown keys"):
        parse_rules([{"pattern": "**", "alow": []}])


def test_user_group_name_clash():
    with pytest.raises(AccessConfigError, match="both"):
        Directory.build({"x": {"password": "p"}}, {"x": {}})


def test_gitignore_patterns():
    rules = [{"pattern": ["*_exam.md", "exams/"], "password": "p"}]
    assert run(rules, uri="x/ud1_exam.md").protected
    assert run(rules, uri="exams/q.md").protected
    assert not run(rules, uri="x/other.md").protected

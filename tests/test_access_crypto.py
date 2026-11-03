import pytest

from material_joapuiib.plugins.access import crypto


def test_roundtrip():
    key = crypto.new_key()
    blob = crypto.encrypt(key, "hola món".encode())
    assert crypto.decrypt(key, blob).decode() == "hola món"
    assert len(blob) == crypto.NONCE_SIZE + len("hola món".encode()) + crypto.TAG_SIZE


def test_wrong_key_fails():
    blob = crypto.encrypt(crypto.new_key(), b"x")
    with pytest.raises(ValueError):
        crypto.decrypt(crypto.new_key(), blob)


def test_derive_is_deterministic_and_salted():
    s1, s2 = crypto.make_salt("a", "user"), crypto.make_salt("a", "pw")
    assert s1 != s2
    assert crypto.derive_key("p", s1, 10) == crypto.derive_key("p", s1, 10)
    assert crypto.derive_key("p", s1, 10) != crypto.derive_key("p", s2, 10)


def test_ids_stable():
    assert crypto.user_id("s", "bob") == crypto.user_id("s", "bob")
    assert crypto.user_id("s", "bob") != crypto.user_id("s", "alice")
    assert len(crypto.page_id("s", "a.md")) == 16

"""Crypto primitives shared with ``javascript/access.js`` (WebCrypto).

Wire format for every encrypted blob: ``nonce(12) || ciphertext || tag(16)``,
the layout WebCrypto's AES-GCM expects/produces.
"""
from __future__ import annotations

import base64
import hashlib
import os

from Crypto.Cipher import AES

NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def unb64(data: str) -> bytes:
    return base64.b64decode(data)


def derive_key(secret: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", secret.encode("utf-8"), salt, iterations, KEY_SIZE)


def make_salt(site_salt: str, purpose: str) -> bytes:
    return hashlib.sha256(f"access:{purpose}:{site_salt}".encode()).digest()


def user_secret(username: str, password: str) -> str:
    return f"{username}\x00{password}"


def user_id(site_salt: str, username: str) -> str:
    """Public, non-reversible name of a user's keyring file."""
    digest = hashlib.sha256(f"access:uid:{site_salt}:{username}".encode())
    return digest.hexdigest()[:32]


def page_id(site_salt: str, src_uri: str) -> str:
    digest = hashlib.sha256(f"access:page:{site_salt}:{src_uri}".encode())
    return digest.hexdigest()[:16]


def new_key() -> bytes:
    return os.urandom(KEY_SIZE)


def encrypt(key: bytes, plaintext: bytes) -> bytes:
    nonce = os.urandom(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + ciphertext + tag


def decrypt(key: bytes, blob: bytes) -> bytes:
    nonce, body = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    ciphertext, tag = body[:-TAG_SIZE], body[-TAG_SIZE:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

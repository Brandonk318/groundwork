"""Document vault encryption at rest: per-user key envelope (design + working primitive).

- Each member gets a random 256-bit data key (DEK).
- Files are encrypted with AES-256-GCM under the DEK.
- The DEK is stored only wrapped (AES-GCM) by the server key-encryption key (KEK, GW_VAULT_KEK),
  later swappable for a cloud KMS.
- One-tap wipe deletes the wrapped DEK -> every stored blob becomes unreadable (crypto-shredding),
  in addition to deleting the blobs themselves.
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _kek(kek_b64: str) -> bytes:
    key = base64.b64decode(kek_b64) if kek_b64 else b""
    if len(key) != 32:
        raise RuntimeError("GW_VAULT_KEK must be 32 bytes, base64-encoded")
    return key


def new_wrapped_dek(kek_b64: str, user_id: str) -> bytes:
    dek = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    return nonce + AESGCM(_kek(kek_b64)).encrypt(nonce, dek, user_id.encode())


def unwrap_dek(kek_b64: str, user_id: str, wrapped: bytes) -> bytes:
    return AESGCM(_kek(kek_b64)).decrypt(wrapped[:12], wrapped[12:], user_id.encode())


def encrypt(dek: bytes, plaintext: bytes, doc_id: str) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(dek).encrypt(nonce, plaintext, doc_id.encode())


def decrypt(dek: bytes, blob: bytes, doc_id: str) -> bytes:
    return AESGCM(dek).decrypt(blob[:12], blob[12:], doc_id.encode())

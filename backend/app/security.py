"""Password hashing and tokens (adapted from Trade Circle). Roles: member, family, admin.

Family accounts are SEPARATE logins (family mode); they only ever see what the member shares.
"""
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

ROLES = ("member", "family", "admin")
_hasher = PasswordHasher()
_DUMMY = _hasher.hash("groundwork-timing-equalizer")


def hash_password(pw: str) -> str:
    return _hasher.hash(pw)


def verify_password(pw_hash: str | None, pw: str) -> bool:
    try:
        ok = _hasher.verify(pw_hash or _DUMMY, pw)
    except (VerificationError, InvalidHashError):
        return False
    return ok and pw_hash is not None


def make_token(secret: str, user_id: str, role: str, ttl_minutes: int) -> str:
    if role not in ROLES:
        raise ValueError(role)
    exp = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    return jwt.encode({"sub": user_id, "role": role, "exp": exp}, secret, algorithm="HS256")


def read_token(secret: str, token: str) -> dict:
    return jwt.decode(token, secret, algorithms=["HS256"])

import asyncio
import base64
import os

import pytest
from cryptography.exceptions import InvalidTag

from app import vault_crypto, wipe

KEK = base64.b64encode(os.urandom(32)).decode()


def test_envelope_roundtrip_and_binding():
    wrapped = vault_crypto.new_wrapped_dek(KEK, "u1")
    dek = vault_crypto.unwrap_dek(KEK, "u1", wrapped)
    blob = vault_crypto.encrypt(dek, b"release papers", "doc1")
    assert b"release papers" not in blob
    assert vault_crypto.decrypt(dek, blob, "doc1") == b"release papers"
    with pytest.raises(InvalidTag):
        vault_crypto.unwrap_dek(KEK, "u2", wrapped)  # key bound to its owner


def test_missing_kek_refuses():
    with pytest.raises(RuntimeError):
        vault_crypto.new_wrapped_dek("", "u1")


def test_wipe_deletes_every_user_collection(db):
    async def run():
        for coll, field in wipe.USER_COLLECTIONS.items():
            await db[coll].insert_one({field: "u1", "x": 1})
            await db[coll].insert_one({field: "u2", "x": 1})
        await db.messages.insert_one({"sender_id": "u2", "recipient_id": "u1"})
        await wipe.wipe_user(db, "u1")
        for coll, field in wipe.USER_COLLECTIONS.items():
            assert await db[coll].count_documents({field: "u1"}) == 0, coll
            assert await db[coll].count_documents({field: "u2"}) >= 1, coll
        assert await db.messages.count_documents({"recipient_id": "u1"}) == 0
    asyncio.run(run())

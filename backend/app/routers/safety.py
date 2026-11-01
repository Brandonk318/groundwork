"""Safety group: crisis, relapse, safe-call contacts, vault, wipe. Lock-exempt items never gated."""
import base64, json, uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import safety, tiers, vault_crypto, wipe
from ..deps import get_current_user
from ._stub import stub_router

router = stub_router("safety", exclude={"crisis_button", "relapse_protocol", "safe_call_contacts", "document_vault", "data_wipe"})
DATA = Path(__file__).resolve().parent.parent / "data"

class ContactIn(BaseModel):
    name: str = Field(max_length=80)
    phone: str = Field(max_length=40)
    relationship: str = "sponsor"

class VaultIn(BaseModel):
    title: str = Field(max_length=120)
    content: str = Field(max_length=20000)

@router.get("/crisis", name="safety:crisis")
async def crisis(request: Request):
    return safety.crisis_payload(request.app.state.settings.app_name)

@router.get("/crisis_button", name="safety:crisis_button")
async def crisis_button(request: Request):
    return safety.crisis_payload(request.app.state.settings.app_name)

@router.get("/private_inbox", name="safety:private_inbox")
async def private_inbox(request: Request, user=Depends(get_current_user)):
    """Author-only crisis resource messages. Filtered by the caller's own id; no role can read another's."""
    items = await request.app.state.db.private_inbox.find({"user_id": user["_id"]}).to_list(100)
    return {"messages": [{"id": d["_id"], "kind": d["kind"], "message": d["message"], "read": d["read"], "created_at": d["created_at"]} for d in items]}

@router.post("/private_inbox/{mid}/read", name="safety:private_inbox_read")
async def private_inbox_read(mid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.private_inbox.update_one({"_id": mid, "user_id": user["_id"]}, {"$set": {"read": True}})
    if not r.matched_count: raise HTTPException(404, "not found")
    return {"ok": True}

@router.get("/relapse_protocol/content", name="safety:relapse_content")
async def relapse_content():
    return json.loads((DATA / "relapse_protocol.json").read_text())

@router.get("/relapse_protocol", name="safety:relapse")
async def relapse():
    return json.loads((DATA / "relapse_protocol.json").read_text())

@router.post("/safe_call_contacts", status_code=201)
async def add_contact(body: ContactIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "name": body.name, "phone": body.phone, "relationship": body.relationship}
    await request.app.state.db.safe_contacts.insert_one(doc)
    return {k: v for k, v in doc.items()}

@router.get("/safe_call_contacts")
async def list_contacts(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.safe_contacts.find({"user_id": user["_id"]}).to_list(100)
    return {"contacts": [{k: v for k, v in d.items()} for d in items]}

@router.delete("/safe_call_contacts/{cid}")
async def del_contact(cid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.safe_contacts.delete_one({"_id": cid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {"deleted": True}

@router.post("/data_wipe")
async def data_wipe(request: Request, user=Depends(get_current_user)):
    counts = await wipe.wipe_user(request.app.state.db, user["_id"])
    return {"wiped": True, "counts": counts}

@router.post("/document_vault", status_code=201)
async def vault_put(body: VaultIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "document_vault")
    kek = request.app.state.settings.vault_kek_b64
    if not kek:
        raise HTTPException(503, "vault not configured")
    db = request.app.state.db
    key_doc = await db.vault_keys.find_one({"user_id": user["_id"]})
    if not key_doc:
        wrapped = vault_crypto.new_wrapped_dek(kek, user["_id"])
        await db.vault_keys.insert_one({"user_id": user["_id"], "wrapped_dek_b64": base64.b64encode(wrapped).decode()})
    else:
        wrapped = base64.b64decode(key_doc["wrapped_dek_b64"])
    dek = vault_crypto.unwrap_dek(kek, user["_id"], wrapped)
    doc_id = uuid.uuid4().hex
    blob = vault_crypto.encrypt(dek, body.content.encode(), doc_id)
    await db.vault_docs.insert_one({"_id": doc_id, "user_id": user["_id"], "title": body.title, "blob_b64": base64.b64encode(blob).decode()})
    return {"id": doc_id, "title": body.title}

@router.get("/document_vault")
async def vault_list(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "document_vault")
    items = await request.app.state.db.vault_docs.find({"user_id": user["_id"]}).to_list(100)
    return {"documents": [{"id": d["_id"], "title": d.get("title", "")} for d in items]}

@router.get("/document_vault/{doc_id}")
async def vault_get(doc_id: str, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "document_vault")
    kek = request.app.state.settings.vault_kek_b64
    if not kek:
        raise HTTPException(503, "vault not configured")
    db = request.app.state.db
    doc = await db.vault_docs.find_one({"_id": doc_id, "user_id": user["_id"]})
    if not doc:
        raise HTTPException(404, "not found")
    key_doc = await db.vault_keys.find_one({"user_id": user["_id"]})
    dek = vault_crypto.unwrap_dek(kek, user["_id"], base64.b64decode(key_doc["wrapped_dek_b64"]))
    plain = vault_crypto.decrypt(dek, base64.b64decode(doc["blob_b64"]), doc_id)
    return {"id": doc_id, "title": doc.get("title", ""), "content": plain.decode()}

@router.delete("/document_vault/{doc_id}")
async def vault_del(doc_id: str, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "document_vault")
    r = await request.app.state.db.vault_docs.delete_one({"_id": doc_id, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {"deleted": True}

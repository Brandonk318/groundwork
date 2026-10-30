import base64, os, uuid
from pathlib import Path
LIMITS = {"photo": ({"image/jpeg", "image/png", "image/webp"}, 5 * 1024 * 1024), "video": ({"video/mp4", "video/webm"}, 25 * 1024 * 1024), "voice": ({"audio/webm", "audio/mpeg", "audio/ogg", "audio/wav"}, 10 * 1024 * 1024)}
def media_root() -> Path:
    root = Path(os.environ.get("GW_MEDIA_DIR", Path(__file__).resolve().parent.parent / "media_store"))
    root.mkdir(parents=True, exist_ok=True)
    return root
def save_upload(user_id: str, kind: str, filename: str, content_type: str, data_b64: str) -> dict:
    allowed, limit = LIMITS[kind]
    if content_type not in allowed:
        raise ValueError(f"{kind} only allows {sorted(allowed)}")
    try:
        raw = base64.b64decode(data_b64, validate=True)
    except Exception:
        raise ValueError("invalid base64 data")
    if len(raw) == 0: raise ValueError("empty file")
    if len(raw) > limit: raise ValueError(f"file too large (max {limit} bytes)")
    # Local storage only. Metadata stripping note: EXIF/GPS is never read or exposed.
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "video/mp4": "mp4", "video/webm": "webm", "audio/webm": "webm", "audio/mpeg": "mp3", "audio/ogg": "ogg", "audio/wav": "wav"}[content_type]
    key = f"{user_id}/{kind}-{uuid.uuid4().hex}.{ext}"
    dest = media_root() / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return {"key": key, "size": len(raw), "content_type": content_type, "filename": filename, "exif_stripped": True}

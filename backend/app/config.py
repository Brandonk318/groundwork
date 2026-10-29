"""Settings. The product name lives in ONE place: APP_NAME (env GW_APP_NAME).

Rename the product by changing DEFAULT_APP_NAME here (backend) and
frontend/src/brand.js (frontend). Nothing else hard-codes the name.
"""
import os
from dataclasses import dataclass

DEFAULT_APP_NAME = "Groundwork"  # finalists: Groundwork / Commissary Club ("Refresh" is taken)


@dataclass(frozen=True)
class Settings:
    jwt_secret: str
    app_name: str = DEFAULT_APP_NAME
    mongo_url: str = "mongodb://localhost:27017"
    db_name: str = "groundwork"
    token_ttl_minutes: int = 12 * 60
    timezone: str = "America/Chicago"
    # Key-encryption key for the document vault envelope (base64, 32 bytes).
    # Dev/test only default is empty -> vault endpoints refuse to run.
    vault_kek_b64: str = ""
    crisis_line: str = "988"
    emergency_line: str = "911"


def load_settings() -> Settings:
    secret = os.environ.get("GW_JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("GW_JWT_SECRET must be set to at least 32 characters")
    return Settings(
        jwt_secret=secret,
        app_name=os.environ.get("GW_APP_NAME", DEFAULT_APP_NAME),
        mongo_url=os.environ.get("GW_MONGO_URL", "mongodb://localhost:27017"),
        db_name=os.environ.get("GW_DB_NAME", "groundwork"),
        vault_kek_b64=os.environ.get("GW_VAULT_KEK", ""),
    )

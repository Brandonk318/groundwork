from fastapi import Depends, HTTPException, Request, status
from . import security

async def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "login required")
    try:
        payload = security.read_token(request.app.state.settings.jwt_secret, auth[7:])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    user = await request.app.state.db.users.find_one({"_id": payload["sub"]})
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return user

def db_of(request: Request):
    return request.app.state.db

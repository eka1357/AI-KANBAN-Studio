import secrets
from fastapi import Request, HTTPException, status
from typing import Dict, Optional
from database import get_user_id, get_user_by_id

# Simple in-memory session store for MVP
# In production, use Redis or DB-backed sessions
SESSIONS: Dict[str, int] = {}

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user_id
    return token

def destroy_session(token: str):
    if token in SESSIONS:
        del SESSIONS[token]

async def get_current_user(request: Request) -> int:
    token = request.cookies.get("session")
    if not token or token not in SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    user_id = SESSIONS[token]
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user_id

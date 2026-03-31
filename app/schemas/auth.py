from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class MSCallbackRequest(BaseModel):
    """Payload sent by the frontend after receiving the MS authorization code."""
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    """JWT response returned to the frontend on successful authentication."""
    access_token: str
    token_type: str = "bearer"
    # Embedded user profile — avoids a second /auth/me round-trip on login
    user_id: int
    public_id: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    role: Optional[Dict[str, Any]] = None
    is_external: bool = False
    is_synced: bool = False


# Legacy schemas kept for backward compat
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

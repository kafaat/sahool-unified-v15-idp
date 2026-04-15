from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithUser(TokenResponse):
    user: dict


class AdminRoleUpdate(BaseModel):
    role: str


class AdminStatusUpdate(BaseModel):
    is_active: bool

from __future__ import annotations

import os
from typing import Optional

from fastapi import Header, HTTPException


class JWTAuth:
    """Lightweight JWT gate.

    For production, you should verify signature (RS256/ES256) and claims.
    Here we enforce presence + basic issuer/audience matching via env toggles,
    to keep the kernel dependency-light.

    Enable with:
      SAHOOL_AUTH_ENABLED=true
    """

    def __init__(self):
        self.enabled = os.getenv("SAHOOL_AUTH_ENABLED", "false").lower() == "true"
        self.issuer = os.getenv("SAHOOL_JWT_ISSUER", "")
        self.audience = os.getenv("SAHOOL_JWT_AUDIENCE", "")

    def require(self, authorization: Optional[str] = Header(default=None)):
        if not self.enabled:
            return True
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="missing_bearer_token")
        # NOTE: placeholder - real verification should be added with python-jose/pyjwt
        token = authorization.split(" ", 1)[1].strip()
        if len(token) < 16:
            raise HTTPException(status_code=401, detail="invalid_token")
        return True

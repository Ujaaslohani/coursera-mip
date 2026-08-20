import os

import jwt
from fastapi import Depends, Header, HTTPException, status

JWT_ALGORITHM = "HS256"

# Role -> Permission map, per doc §5.4 'Security, Logging, and Observability':
# 'The platform must enforce role-based access control before retrieval and
# before LLM synthesis.' `admin` holds every permission; every other role is
# scoped to the part of the workflow it actually owns.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"*"},
    "content-team": {"assets:write", "processing:write"},
    "educator": {"query:run", "insights:read"},
    "reviewer": {"query:run", "insights:read", "review:write"},
    "analyst": {"metrics:read", "audit:read"},
}


class CurrentUser:
    def __init__(self, user_id: str, roles: list[str], permitted_sources: list[str]):
        self.user_id = user_id
        self.roles = roles
        self.permitted_sources = permitted_sources


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    """Enforced on every route per doc §7.3: 'Authentication should be enforced
    for all endpoints. Backend services should validate access permissions
    before retrieval and before sending context to an LLM.'

    Verifies a self-issued HS256 JWT against JWT_SECRET — there is no external
    identity provider for this project. Mint a dev token with
    backend/scripts/mint_dev_token.py.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token")

    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET is not configured")

    try:
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing 'sub' claim")

    return CurrentUser(
        user_id=user_id,
        roles=payload.get("roles", []),
        permitted_sources=payload.get("permitted_sources", []),
    )


def require_permission(user: CurrentUser, source_id: str) -> None:
    if "*" in user.permitted_sources or source_id in user.permitted_sources:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not permitted to access source {source_id}")


def user_permissions(user: CurrentUser) -> set[str]:
    perms: set[str] = set()
    for role in user.roles:
        perms |= ROLE_PERMISSIONS.get(role, set())
    return perms


def require_role_permission(permission: str):
    """FastAPI dependency factory — e.g. Depends(require_role_permission("review:write")).
    RBAC gate on top of get_current_user: authentication proves *who* the
    caller is, this proves they're *allowed* to do this particular action.
    """

    def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        perms = user_permissions(user)
        if "*" in perms or permission in perms:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"role(s) {user.roles} lack permission '{permission}'",
        )

    return _dependency

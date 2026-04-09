"""Admin-only routes: list/get/update-role/status/delete users."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...models.token import AdminRoleUpdate, AdminStatusUpdate
from ..deps import require_role

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

_VALID_ROLES = {"admin", "user", "moderator"}


def _require_admin():
    return Depends(require_role("admin"))


# ── List users ────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    _: dict = Depends(require_role("admin")),
):
    if page < 1:
        page = 1
    if per_page > 100:
        per_page = 100
    offset = (page - 1) * per_page

    pool = request.app.state.db
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        rows = await conn.fetch(
            """
            SELECT u.id, u.email, u.name, u.is_active, u.created_at,
                   COALESCE(r.name, 'user') AS role
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.id
            LEFT JOIN roles r ON r.id = ur.role_id
            ORDER BY u.created_at DESC
            LIMIT $1 OFFSET $2
            """,
            per_page, offset,
        )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "users": [
            {
                "id": str(r["id"]),
                "email": r["email"],
                "name": r["name"],
                "role": r["role"],
                "is_active": r["is_active"],
                "created_at": r["created_at"].isoformat(),
            }
            for r in rows
        ],
    }


# ── Get single user ───────────────────────────────────────────────────────────

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    request: Request,
    _: dict = Depends(require_role("admin")),
):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT u.id, u.email, u.name, u.is_active, u.created_at,
                   COALESCE(r.name, 'user') AS role
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.id
            LEFT JOIN roles r ON r.id = ur.role_id
            WHERE u.id = $1
            LIMIT 1
            """,
            uuid.UUID(user_id),
        )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return {
        "id": str(row["id"]),
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
        "is_active": row["is_active"],
        "created_at": row["created_at"].isoformat(),
    }


# ── Update role ───────────────────────────────────────────────────────────────

@router.patch("/users/{user_id}/role")
async def update_role(
    user_id: str,
    body: AdminRoleUpdate,
    request: Request,
    _: dict = Depends(require_role("admin")),
):
    if body.role not in _VALID_ROLES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Role must be one of: {', '.join(_VALID_ROLES)}",
        )

    pool = request.app.state.db
    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE id = $1", uuid.UUID(user_id)
            )
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            role_id = await conn.fetchval(
                "SELECT id FROM roles WHERE name = $1", body.role
            )
            # Remove all existing roles for this user
            await conn.execute(
                "DELETE FROM user_roles WHERE user_id = $1", uuid.UUID(user_id)
            )
            # Assign new role
            await conn.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES ($1, $2)",
                uuid.UUID(user_id), role_id,
            )

    return {"message": f"Role updated to '{body.role}'"}


# ── Update status (activate / deactivate) ────────────────────────────────────

@router.patch("/users/{user_id}/status")
async def update_status(
    user_id: str,
    body: AdminStatusUpdate,
    request: Request,
    _: dict = Depends(require_role("admin")),
):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE users SET is_active = $1, updated_at = NOW() WHERE id = $2 RETURNING id",
            body.is_active, uuid.UUID(user_id),
        )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return {"message": f"User {'activated' if body.is_active else 'deactivated'}"}


# ── Delete user ───────────────────────────────────────────────────────────────

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role("admin")),
):
    if current_user["user_id"] == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot delete your own account")

    pool = request.app.state.db
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM users WHERE id = $1", uuid.UUID(user_id)
        )
    if result == "DELETE 0":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

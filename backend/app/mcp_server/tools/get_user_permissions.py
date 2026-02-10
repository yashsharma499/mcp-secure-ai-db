from typing import List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user_permission import UserPermission


def get_user_permissions(
    *,
    db: Session,
    user_id: int
) -> List[Dict[str, Any]]:
    try:
        rows = (
            db.query(UserPermission)
            .filter(UserPermission.user_id == user_id)
            .order_by(UserPermission.table_name)
            .all()
        )

        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "table_name": r.table_name,
                "can_read": r.can_read,
                "can_write": r.can_write,
                "allowed_columns": r.allowed_columns
            }
            for r in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user permissions"
        )

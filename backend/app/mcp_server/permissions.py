from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user_permission import UserPermission


class PermissionDeniedError(Exception):
    pass


def load_user_permissions(db: Session, user_id: int) -> Dict[str, UserPermission]:
    try:
        rows = (
            db.query(UserPermission)
            .filter(UserPermission.user_id == user_id)
            .all()
        )

        return {row.table_name: row for row in rows}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user permissions"
        )


def require_table_permission(
    permissions: Dict[str, UserPermission],
    table_name: str,
    operation: str
) -> UserPermission:
    try:
        perm = permissions.get(table_name)
        if not perm:
            raise PermissionDeniedError("No permission for table")

        if operation == "read" and not perm.can_read:
            raise PermissionDeniedError("Read access denied")

        if operation == "write" and not perm.can_write:
            raise PermissionDeniedError("Write access denied")

        return perm

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission validation failed"
        )


def filter_allowed_columns(
    requested_columns: Optional[List[str]],
    permission: UserPermission
) -> Optional[List[str]]:
    try:
        if permission.allowed_columns is None:
            return requested_columns

        allowed = set(permission.allowed_columns)

        if not requested_columns:
            return list(allowed)

        filtered = [c for c in requested_columns if c in allowed]

        if not filtered:
            raise PermissionDeniedError("No allowed columns in request")

        return filtered

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Column permission validation failed"
        )

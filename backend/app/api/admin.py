from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_admin
from app.schemas.user import (
    UserPermissionCreate,
    UserPermissionUpdate,
    UserPermissionResponse
)
from app.db.models.user_permission import UserPermission
from app.db.models.user import User

router = APIRouter(tags=["admin"])


@router.get(
    "/users",
    response_model=list[dict]
)
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    try:
        users = (
            db.query(User.id, User.email, User.role)
            .order_by(User.id)
            .all()
        )

        return [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role
            }
            for u in users
        ]

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load users"
        )


@router.post(
    "/permissions",
    response_model=UserPermissionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user_permission(
    payload: UserPermissionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    try:
        user = db.get(User, payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        permission = UserPermission(
            user_id=payload.user_id,
            table_name=payload.table_name,
            can_read=payload.can_read,
            can_write=payload.can_write,
            allowed_columns=payload.allowed_columns
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        return permission

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission for this user and table already exists"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission"
        )


@router.get(
    "/permissions",
    response_model=list[UserPermissionResponse]
)
def list_user_permissions(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    try:
        query = db.query(UserPermission)
        if user_id is not None:
            query = query.filter(UserPermission.user_id == user_id)

        return query.order_by(
            UserPermission.user_id,
            UserPermission.table_name
        ).all()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load permissions"
        )


@router.put(
    "/permissions/{permission_id}",
    response_model=UserPermissionResponse
)
def update_user_permission(
    permission_id: int,
    payload: UserPermissionUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    try:
        permission = db.get(UserPermission, permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        if payload.can_read is not None:
            permission.can_read = payload.can_read

        if payload.can_write is not None:
            permission.can_write = payload.can_write

        if payload.allowed_columns is not None:
            permission.allowed_columns = payload.allowed_columns

        db.commit()
        db.refresh(permission)

        return permission

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission"
        )


@router.delete(
    "/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    try:
        permission = db.get(UserPermission, permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        db.delete(permission)
        db.commit()
        return None

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission"
        )

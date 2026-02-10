from typing import Dict, Any, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.mcp_server.audit import fetch_audit_history


def audit_query_history(
    *,
    db: Session,
    user_id: int | None = None,
    table_name: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:

    if limit <= 0 or limit > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid limit"
        )

    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid offset"
        )

    try:
        return fetch_audit_history(
            db=db,
            user_id=user_id,
            table_name=table_name,
            limit=limit,
            offset=offset
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit history"
        )

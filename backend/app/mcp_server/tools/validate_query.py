from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query


def validate_query(
    *,
    db: Session,
    engine: Engine,
    user_id: int,
    sql: str
) -> Dict[str, Any]:
    try:
        permissions = load_user_permissions(db, user_id)

        result = core_validate_query(
            sql=sql,
            permissions=permissions,
            engine=engine
        )

        return {
            "operation": result.operation,
            "table": result.table,
            "columns": result.columns,
            "limit": result.limit
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query validation failed"
        )

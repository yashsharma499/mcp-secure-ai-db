from typing import List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query
from app.mcp_server.executor import run_read
from app.mcp_server.audit import log_audit


def run_read_query(
    *,
    db: Session,
    engine: Engine,
    user_id: int,
    sql: str
) -> List[Dict[str, Any]]:
    try:
        permissions = load_user_permissions(db, user_id)

        validation = core_validate_query(
            sql=sql,
            permissions=permissions,
            engine=engine
        )

        if validation.operation != "read":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a read query"
            )

        result = run_read(
            db=db,
            engine=engine,
            sql=sql,
            validation=validation
        )

        log_audit(
            db=db,
            user_id=user_id,
            operation="read",
            table_name=validation.table,
            sql_text=sql,
            status="success"
        )

        return result

    except HTTPException:
        raise
    except Exception:
        try:
            log_audit(
                db=db,
                user_id=user_id,
                operation="read",
                table_name="unknown",
                sql_text=sql,
                status="failed"
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Read execution failed"
        )

from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query
from app.mcp_server.executor import run_write
from app.mcp_server.audit import log_audit


def _is_unique_violation(exc: Exception) -> bool:
    orig = getattr(exc, "orig", None)

    if orig is None:
        return False

    code = getattr(orig, "pgcode", None)
    if code == "23505":
        return True

    diag = getattr(orig, "diag", None)
    if diag and getattr(diag, "sqlstate", None) == "23505":
        return True

    return False


def run_write_query(
    *,
    db: Session,
    engine: Engine,
    user_id: int,
    sql: str
) -> Dict[str, Any]:

    permissions = load_user_permissions(db, user_id)

    validation = core_validate_query(
        sql=sql,
        permissions=permissions,
        engine=engine
    )

    if validation.operation != "write":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a write query"
        )

    try:
        result = run_write(
            db=db,
            engine=engine,
            sql=sql,
            validation=validation
        )

        log_audit(
            db=db,
            user_id=user_id,
            operation="write",
            table_name=validation.table,
            sql_text=sql,
            status="success"
        )

        return result

    except Exception as e:
        db.rollback()

        try:
            log_audit(
                db=db,
                user_id=user_id,
                operation="write",
                table_name=validation.table,
                sql_text=sql,
                status="failed"
            )
        except Exception:
            pass

        if _is_unique_violation(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A record with the same email already exists."
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Write execution failed"
        )

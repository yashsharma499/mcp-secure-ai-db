from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query


def _is_unique_violation(exc: Exception) -> bool:
    orig = getattr(exc, "orig", None)

    if orig is None:
        return False

    code = getattr(orig, "pgcode", None)
    if code:
        return code == "23505"

    diag = getattr(orig, "diag", None)
    if diag and getattr(diag, "sqlstate", None):
        return diag.sqlstate == "23505"

    return False


def dry_run_query(
    *,
    db: Session,
    engine: Engine,
    user_id: int,
    sql: str
) -> Dict[str, Any]:

    try:
        permissions = load_user_permissions(db, user_id)

        validation = core_validate_query(
            sql=sql,
            permissions=permissions,
            engine=engine
        )

        plan = db.execute(text(f"EXPLAIN {sql}")).fetchall()

        return {
            "operation": validation.operation,
            "table": validation.table,
            "plan": [str(r[0]) for r in plan]
        }

    except IntegrityError as e:
        db.rollback()

        if _is_unique_violation(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with the same unique value already exists."
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation."
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dry run failed"
        )

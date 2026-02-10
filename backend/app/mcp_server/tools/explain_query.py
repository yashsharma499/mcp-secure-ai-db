from typing import Dict, Any, List

from fastapi import HTTPException, status
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query


def explain_query(
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

        result = db.execute(text(f"EXPLAIN {sql}"))
        rows = result.fetchall()

        plan: List[str] = []
        for r in rows:
            plan.append(str(r[0]))

        return {
            "operation": validation.operation,
            "table": validation.table,
            "plan": plan
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explain query failed"
        )

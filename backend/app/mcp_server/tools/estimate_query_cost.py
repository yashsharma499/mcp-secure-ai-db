from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.mcp_server.permissions import load_user_permissions
from app.mcp_server.validator import validate_query as core_validate_query


def estimate_query_cost(
    *,
    db: Session,
    engine: Engine,
    user_id: int,
    sql: str
) -> Dict[str, Any]:
    if not sql or not isinstance(sql, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required"
        )

    try:
        permissions = load_user_permissions(db, user_id)

        validation = core_validate_query(
            sql=sql,
            permissions=permissions,
            engine=engine
        )

        result = db.execute(
            text(f"EXPLAIN (FORMAT JSON) {sql}")
        ).fetchone()

        if not result or not result[0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to estimate query cost"
            )

        plan_root = result[0][0]
        plan = plan_root.get("Plan", {})

        return {
            "operation": validation.operation,
            "table": validation.table,
            "startup_cost": plan.get("Startup Cost"),
            "total_cost": plan.get("Total Cost"),
            "plan_rows": plan.get("Plan Rows")
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cost estimation failed"
        )

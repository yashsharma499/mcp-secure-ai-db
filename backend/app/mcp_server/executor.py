from typing import Any, List, Dict
import re

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.mcp_server.validator import QueryValidationResult


def _rewrite_select_columns(sql: str, columns: List[str]) -> str:
    select_part = ", ".join(columns)

    pattern = re.compile(
        r"select\s+.+?\s+from\s",
        re.IGNORECASE | re.DOTALL
    )

    if not pattern.search(sql):
        raise ValueError("Invalid SELECT query")

    return pattern.sub(
        f"select {select_part} from ",
        sql,
        count=1
    )


def run_read(
    *,
    db: Session,
    engine: Engine,
    sql: str,
    validation: QueryValidationResult
) -> List[Dict[str, Any]]:
    try:
        base_sql = validation.sql.strip().rstrip(";")
        upper = base_sql.upper()

        is_aggregation = any(
            fn in upper for fn in ("COUNT(", "SUM(", "AVG(", "MIN(", "MAX("))
        

        if not is_aggregation and validation.columns:
            base_sql = _rewrite_select_columns(
                base_sql,
                validation.columns
            )

        if not is_aggregation:
            if re.search(r"\blimit\b", base_sql, re.IGNORECASE):
                base_sql = re.sub(
                    r"\blimit\s+\d+",
                    f"LIMIT {validation.limit}",
                    base_sql,
                    flags=re.IGNORECASE
                )
            else:
                base_sql = f"{base_sql} LIMIT {validation.limit}"

        result = db.execute(text(base_sql))
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def run_write(
    *,
    db: Session,
    engine: Engine,
    sql: str,
    validation: QueryValidationResult
) -> Dict[str, Any]:
    try:
        result = db.execute(text(validation.sql))
        return {"rows_affected": result.rowcount}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

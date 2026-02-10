import re
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.db.models.user_permission import UserPermission
from app.mcp_server.permissions import require_table_permission, filter_allowed_columns


READ_LIMIT_DEFAULT = 200


class QueryValidationResult:
    def __init__(
        self,
        operation: str,
        table: str,
        columns: Optional[List[str]],
        limit: int,
        sql: str,
    ):
        self.operation = operation
        self.table = table
        self.columns = columns
        self.limit = limit
        self.sql = sql


def _normalize_identifier(value: str) -> str:
    return value.strip().lower()


def _parse_simple_select(sql: str) -> Tuple[str, Optional[List[str]], Optional[int]]:
    pattern = re.compile(
        r"select\s+(?P<cols>[\w\*,\s\(\)]+)\s+from\s+(?P<table>\w+)"
        r"(?:\s+where\s+.+?)?"
        r"(?:\s+order\s+by\s+.+?)?"
        r"(?:\s+limit\s+(?P<limit>\d+))?\s*$",
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.match(sql.strip())
    if not match:
        raise ValueError("Only simple SELECT queries are supported")

    cols_raw = match.group("cols").strip()
    table = _normalize_identifier(match.group("table"))
    limit = match.group("limit")

    if cols_raw == "*":
        columns = None
    else:
        columns = [_normalize_identifier(c.strip()) for c in cols_raw.split(",")]

    return table, columns, int(limit) if limit else None


def _detect_operation(sql: str) -> str:
    token = sql.strip().split()[0].lower()

    if token == "select":
        return "read"

    if token in {"insert", "update", "delete"}:
        return "write"

    raise ValueError("Unsupported SQL operation")


def _block_destructive(sql: str):
    lowered = sql.lower()

    if " drop " in lowered or lowered.startswith("drop"):
        raise ValueError("Destructive statements are not allowed")

    if " truncate " in lowered or lowered.startswith("truncate"):
        raise ValueError("Destructive statements are not allowed")

    if " alter " in lowered or lowered.startswith("alter"):
        raise ValueError("Destructive statements are not allowed")


def _has_unsafe_boolean(sql: str) -> bool:
    lowered = sql.lower()
    return bool(re.search(r"\bor\s+1\s*=\s*1\b", lowered))


def _is_aggregation_select(sql: str) -> bool:
    upper = sql.upper()
    return any(fn in upper for fn in ("COUNT(", "SUM(", "AVG(", "MIN(", "MAX("))


def _extract_write_table(sql: str) -> Optional[str]:
    tokens = re.split(r"\s+", sql.strip())
    if not tokens:
        return None

    lower_tokens = [t.lower() for t in tokens]
    first = lower_tokens[0]

    if first == "update" and len(tokens) >= 2:
        return _normalize_identifier(tokens[1])

    if first == "insert" and "into" in lower_tokens:
        i = lower_tokens.index("into")
        if i + 1 < len(tokens):
            return _normalize_identifier(tokens[i + 1])

    if first == "delete" and len(tokens) >= 3 and lower_tokens[1] == "from":
        return _normalize_identifier(tokens[2])

    return None


def validate_query(
    *,
    sql: str,
    permissions: Dict[str, UserPermission],
    engine: Engine,
) -> QueryValidationResult:

    if not sql or not isinstance(sql, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL is required",
        )

    try:
        _block_destructive(sql)

        if _has_unsafe_boolean(sql):
            raise ValueError("Unsafe boolean expression detected")

        operation = _detect_operation(sql)
        inspector = inspect(engine)

        
        if operation == "read":
            table, columns, limit = _parse_simple_select(sql)

            if not inspector.has_table(table):
                raise ValueError("Table does not exist")

            perm = require_table_permission(
                permissions=permissions,
                table_name=table,
                operation="read",
            )

            
            if not _is_aggregation_select(sql):
                if columns is not None and perm.allowed_columns is not None:
                    requested = {c.lower() for c in columns}
                    allowed = {c.lower() for c in perm.allowed_columns}

                    if not requested.issubset(allowed):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this operation on the requested data."
                        )

                allowed_columns = filter_allowed_columns(columns, perm)
            else:
                allowed_columns = None

            enforced_limit = limit or READ_LIMIT_DEFAULT
            if enforced_limit > READ_LIMIT_DEFAULT:
                enforced_limit = READ_LIMIT_DEFAULT

            return QueryValidationResult(
                operation="read",
                table=table,
                columns=allowed_columns,
                limit=enforced_limit,
                sql=sql,
            )

       

        table = _extract_write_table(sql)

        if not table or not inspector.has_table(table):
            raise ValueError("Unable to determine target table")

        require_table_permission(
            permissions=permissions,
            table_name=table,
            operation="write",
        )

        lowered = sql.lower()

        if lowered.startswith("update") and " where " not in lowered:
            raise ValueError("Unsafe update without WHERE clause")

        if lowered.startswith("delete") and " where " not in lowered:
            raise ValueError("Unsafe delete without WHERE clause")

        return QueryValidationResult(
            operation="write",
            table=table,
            columns=None,
            limit=0,
            sql=sql,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

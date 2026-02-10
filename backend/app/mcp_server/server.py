from typing import Dict, Any, List

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session, engine
from app.mcp_server.auth import authenticate_jwt
from app.mcp_server.audit import ensure_audit_table
from app.mcp_server.tools.get_schema import get_schema
from app.mcp_server.tools.get_user_permissions import get_user_permissions
from app.mcp_server.tools.validate_query import validate_query
from app.mcp_server.tools.dry_run_query import dry_run_query
from app.mcp_server.tools.run_read_query import run_read_query
from app.mcp_server.tools.run_write_query import run_write_query
from app.mcp_server.tools.explain_query import explain_query
from app.mcp_server.tools.estimate_query_cost import estimate_query_cost
from app.mcp_server.tools.audit_query_history import audit_query_history

mcp_router = APIRouter(tags=["mcp"])

ensure_audit_table(engine)


TOOLS_CATALOG: List[Dict[str, Any]] = [
    {
        "name": "get_schema",
        "description": "Return database tables and columns visible to the user",
        "method": "GET",
        "path": "/mcp/tools/get_schema",
        "arguments": {},
    },
    {
        "name": "get_user_permissions",
        "description": "Return effective table and column permissions for the current user",
        "method": "GET",
        "path": "/mcp/tools/get_user_permissions",
        "arguments": {},
    },
    {
        "name": "validate_query",
        "description": "Validate SQL for safety, schema correctness and permissions",
        "method": "POST",
        "path": "/mcp/tools/validate_query",
        "arguments": {"sql": "string"},
    },
    {
        "name": "dry_run_query",
        "description": "Perform a dry run of a SQL query without modifying data",
        "method": "POST",
        "path": "/mcp/tools/dry_run_query",
        "arguments": {"sql": "string"},
    },
    {
        "name": "run_read_query",
        "description": "Execute a read-only SQL query",
        "method": "POST",
        "path": "/mcp/tools/run_read_query",
        "arguments": {"sql": "string"},
    },
    {
        "name": "run_write_query",
        "description": "Execute a write SQL query after validation and safety checks",
        "method": "POST",
        "path": "/mcp/tools/run_write_query",
        "arguments": {"sql": "string"},
    },
    {
        "name": "explain_query",
        "description": "Return execution plan for a SQL query",
        "method": "POST",
        "path": "/mcp/tools/explain_query",
        "arguments": {"sql": "string"},
    },
    {
        "name": "estimate_query_cost",
        "description": "Estimate execution cost for a SQL query",
        "method": "POST",
        "path": "/mcp/tools/estimate_query_cost",
        "arguments": {"sql": "string"},
    },
    {
        "name": "audit_query_history",
        "description": "Return query execution audit history",
        "method": "GET",
        "path": "/mcp/tools/audit_query_history",
        "arguments": {
            "user_id": "int | optional",
            "limit": "int | optional",
        },
    },
]


def _get_db():
    try:
        with get_db_session() as db:
            yield db
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def _get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(_get_db),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.split(" ", 1)[1].strip()
    return authenticate_jwt(token, db)


@mcp_router.get("/tools")
def mcp_list_tools(
    user=Depends(_get_current_user),
):
    return {
        "tools": TOOLS_CATALOG
    }


@mcp_router.get("/tools/get_schema")
def mcp_get_schema(
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    return get_schema(db=db, engine=engine)


@mcp_router.get("/tools/get_user_permissions")
def mcp_get_user_permissions(
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    return get_user_permissions(db=db, user_id=user.id)


@mcp_router.post("/tools/validate_query")
def mcp_validate_query(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return validate_query(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.post("/tools/dry_run_query")
def mcp_dry_run_query(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return dry_run_query(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.post("/tools/run_read_query")
def mcp_run_read_query(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return run_read_query(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.post("/tools/run_write_query")
def mcp_run_write_query(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return run_write_query(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.post("/tools/explain_query")
def mcp_explain_query(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return explain_query(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.post("/tools/estimate_query_cost")
def mcp_estimate_query_cost(
    payload: Dict[str, Any],
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    sql = payload.get("sql")
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sql is required",
        )

    return estimate_query_cost(
        db=db,
        engine=engine,
        user_id=user.id,
        sql=sql,
    )


@mcp_router.get("/tools/audit_query_history")
def mcp_audit_query_history(
    user_id: int | None = None,
    table_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(_get_db),
    user=Depends(_get_current_user),
):
    if user.role != "admin":
        user_id = user.id

    return audit_query_history(
        db=db,
        user_id=user_id,
        table_name=table_name,
        limit=limit,
        offset=offset,
    )

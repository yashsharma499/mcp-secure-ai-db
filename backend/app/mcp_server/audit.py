from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    DateTime,
    MetaData,
    Text,
    select
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.models.user import User


_metadata = MetaData()

_audit_table = Table(
    "mcp_audit_logs",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False, index=True),
    Column("operation", String(16), nullable=False, index=True),
    Column("table_name", String(128), nullable=False, index=True),
    Column("sql_text", Text, nullable=False),
    Column("status", String(32), nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
)


def ensure_audit_table(engine: Engine):
    try:
        _metadata.create_all(engine, tables=[_audit_table])
    except Exception as e:
        raise RuntimeError(f"Failed to initialize audit table: {str(e)}") from e


def log_audit(
    *,
    db: Session,
    user_id: int,
    operation: str,
    table_name: str,
    sql_text: str,
    status: str
):
    try:
        db.execute(
            _audit_table.insert().values(
                user_id=user_id,
                operation=operation,
                table_name=table_name,
                sql_text=sql_text,
                status=status,
                created_at=datetime.now(timezone.utc)
            )
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to write audit log"
        )


def fetch_audit_history(
    *,
    db: Session,
    user_id: int | None = None,
    table_name: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    try:
        stmt = (
            select(
                _audit_table.c.id,
                _audit_table.c.user_id,
                User.email.label("user_email"),
                _audit_table.c.operation,
                _audit_table.c.table_name,
                _audit_table.c.sql_text,
                _audit_table.c.status,
                _audit_table.c.created_at
            )
            .outerjoin(User, User.id == _audit_table.c.user_id)
        )

        if user_id is not None:
            stmt = stmt.where(_audit_table.c.user_id == user_id)

        if table_name:
            stmt = stmt.where(
                _audit_table.c.table_name.ilike(f"%{table_name}%")
            )

        stmt = (
            stmt
            .order_by(_audit_table.c.id.desc())
            .offset(offset)
            .limit(limit)
        )

        result = db.execute(stmt)
        rows = result.mappings().all()

        data: List[Dict[str, Any]] = []

        for r in rows:
            row = dict(r)

           
            if row.get("created_at"):
                row["created_at"] = (
                    row["created_at"]
                    .astimezone(timezone.utc)
                    .isoformat()
                )

            data.append(row)

        return data

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load audit history"
        )

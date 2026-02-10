from typing import Dict, List

from fastapi import HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def get_schema(
    *,
    db: Session,
    engine: Engine
) -> Dict[str, List[str]]:
    try:
        bind = engine if engine is not None else db.get_bind()
        inspector = inspect(bind)

        schema: Dict[str, List[str]] = {}

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema[table_name] = [c["name"] for c in columns]

        return schema

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

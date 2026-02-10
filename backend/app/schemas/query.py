from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=10000)


class ValidationResponse(BaseModel):
    operation: str
    table: str
    columns: list[str] | None
    limit: int


class WriteResultResponse(BaseModel):
    rows_affected: int

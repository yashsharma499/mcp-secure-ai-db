from typing import List, Optional
from pydantic import BaseModel, Field, validator


class UserResponse(BaseModel):
    id: int
    email: str
    role: str


class UserPermissionBase(BaseModel):
    user_id: int = Field(..., gt=0)
    table_name: str = Field(..., min_length=1, max_length=128)
    can_read: bool
    can_write: bool
    allowed_columns: Optional[List[str]] = None

    @validator("table_name")
    def normalize_table_name(cls, v: str):
        value = v.strip().lower()
        if not value.isidentifier():
            raise ValueError("Invalid table name")
        return value

    @validator("allowed_columns", always=True)
    def validate_allowed_columns(cls, v, values):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("allowed_columns must be a list")
        normalized = []
        for col in v:
            if not isinstance(col, str):
                raise ValueError("Invalid column name")
            name = col.strip()
            if not name.isidentifier():
                raise ValueError("Invalid column name")
            normalized.append(name)
        if not values.get("can_read") and not values.get("can_write"):
            return None
        return list(dict.fromkeys(normalized))


class UserPermissionCreate(UserPermissionBase):
    pass


class UserPermissionUpdate(BaseModel):
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    allowed_columns: Optional[List[str]] = None

    @validator("allowed_columns")
    def validate_allowed_columns(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("allowed_columns must be a list")
        normalized = []
        for col in v:
            if not isinstance(col, str):
                raise ValueError("Invalid column name")
            name = col.strip()
            if not name.isidentifier():
                raise ValueError("Invalid column name")
            normalized.append(name)
        return list(dict.fromkeys(normalized))


class UserPermissionResponse(BaseModel):
    id: int
    user_id: int
    table_name: str
    can_read: bool
    can_write: bool
    allowed_columns: Optional[List[str]] = None

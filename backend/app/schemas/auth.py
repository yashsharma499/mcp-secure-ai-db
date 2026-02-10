from pydantic import BaseModel, EmailStr, Field, validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @validator("password")
    def validate_password(cls, v: str):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase character")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase character")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    id: int
    email: EmailStr
    role: str


class AuthUserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

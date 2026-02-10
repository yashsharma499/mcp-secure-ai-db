from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="mcp-secure-ai-db")
    environment: str = Field(default="development")

    database_url: str = Field(..., alias="DATABASE_URL")

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256")

    jwt_access_token_expire_minutes: int = Field(default=60)

    
    jwt_refresh_token_expire_minutes: int = Field(default=10080)  # 7 days

    bcrypt_rounds: int = Field(default=12)

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise RuntimeError(f"Configuration error: {str(e)}") from e

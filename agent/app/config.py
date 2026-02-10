from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_name: str = Field(default="mcp-agent")
    environment: str = Field(default="development")

    mcp_base_url: str = Field(..., alias="MCP_BASE_URL")
    mcp_timeout_seconds: int = Field(default=30)

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o")

    memory_store_path: str = Field(default="./memory_store.json")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise RuntimeError(f"Agent configuration error: {str(e)}") from e

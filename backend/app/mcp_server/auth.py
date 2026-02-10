from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token, TokenError
from app.db.models.user import User


class MCPAuthenticationError(Exception):
    pass


def authenticate_jwt(token: str, db: Session) -> User:
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise MCPAuthenticationError("Invalid token payload")

        try:
            user_id_int = int(user_id)
        except Exception:
            raise MCPAuthenticationError("Invalid user identifier")

        user = db.get(User, user_id_int)
        if not user:
            raise MCPAuthenticationError("User not found")

        return user

    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except MCPAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MCP authentication failed"
        )

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from jwt import PyJWTError

from app.core.config import get_settings


_settings = get_settings()


class TokenError(Exception):
    pass



def create_access_token(
    subject: str | int,
    extra_claims: Dict[str, Any] | None = None
) -> str:

    if subject is None:
        raise TokenError("Invalid token subject")

    try:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=_settings.jwt_access_token_expire_minutes
        )

        payload: Dict[str, Any] = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            _settings.jwt_secret_key,
            algorithm=_settings.jwt_algorithm,
        )

    except Exception as e:
        raise TokenError(str(e)) from e



def create_refresh_token(subject: str | int) -> str:
    if subject is None:
        raise TokenError("Invalid token subject")

    try:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=_settings.jwt_refresh_token_expire_minutes
        )

        payload: Dict[str, Any] = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(
            payload,
            _settings.jwt_secret_key,
            algorithm=_settings.jwt_algorithm,
        )

    except Exception as e:
        raise TokenError(str(e)) from e




def _decode(token: str) -> Dict[str, Any]:
    if not token:
        raise TokenError("Token missing")

    try:
        payload = jwt.decode(
            token,
            _settings.jwt_secret_key,
            algorithms=[_settings.jwt_algorithm],
        )

        if "sub" not in payload:
            raise TokenError("Token subject missing")

        if payload.get("type") not in ("access", "refresh"):
            raise TokenError("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise TokenError("Token expired")
    except PyJWTError:
        raise TokenError("Invalid token")
    except Exception as e:
        raise TokenError(str(e)) from e




def decode_access_token(token: str) -> Dict[str, Any]:
    payload = _decode(token)

    if payload.get("type") != "access":
        raise TokenError("Invalid access token")

    return payload


def decode_refresh_token(token: str) -> Dict[str, Any]:
    payload = _decode(token)

    if payload.get("type") != "refresh":
        raise TokenError("Invalid refresh token")

    return payload
